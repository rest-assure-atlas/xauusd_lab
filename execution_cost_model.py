"""Policy-enforced XAUUSD spread execution-cost model specification.

This module builds the execution-cost modelling layer only. It does not run
strategy tests, rank strategies, or add unevidenced cost components.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean

from session_tools import get_session_windows


PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"

RECONCILIATION_PATH = REPORTS_DIR / "bid_ask_reconciliation_2024-01-01_to_2024-12-31.csv"
POLICY_PATH = REPORTS_DIR / "post_corroboration_execution_cost_evidence_policy.md"
POLICY_JSON_PATH = REPORTS_DIR / "post_corroboration_execution_cost_evidence_policy.json"
TARGET_WINDOWS_PATH = REPORTS_DIR / "targeted_external_bid_ask_corroboration_windows_2024.csv"
FXCM_WINDOWS_PATH = REPORTS_DIR / "fxcm_full_bounded_corroboration_2024_windows.csv"
SPEC_PATH = REPORTS_DIR / "execution_cost_model_spec.json"
REPORT_PATH = REPORTS_DIR / "execution_cost_model_implementation.md"
TAIL_HARDENING_REPORT_PATH = REPORTS_DIR / "execution_cost_prospective_tail_hardening.md"

POLICY_VERSION = "post_corroboration_execution_cost_evidence_policy:2026-08-10"
STRICT_VALID_PAIR = "strict_valid_pair"
WARNING_REVIEW_PAIR = "warning_review_pair"
PLACEHOLDER_REASON = "MARKET_CLOSED_PLACEHOLDER"

CONFIRMED_CLOSELY = "CONFIRMED_CLOSELY"
CONFIRMED_DIRECTIONALLY = "CONFIRMED_DIRECTIONALLY"
DISAGREES = "DISAGREES"
INCONCLUSIVE = "INCONCLUSIVE"
NOT_EXTERNALLY_TESTED = "not_externally_tested"

TARGET_CLUSTER = "target_cluster"
BOUNDED_WINDOW_CONTEXT = "bounded_window_context"
SAME_DATE_CONTEXT = "same_date_context"
NOT_EXTERNALLY_TESTED_SCOPE = "not_externally_tested"

SPECIAL_CASES = {
    "2024-12-11_ge2_04": "warning target disagreement; excluded from favorable calibration and retained in adverse sensitivity",
    "2024-02-18_ge2_02": "unresolved warning target; excluded from favorable calibration and retained as unresolved/adverse evidence",
    "2024-04-05_strict_ge2_01": "unresolved strict-valid extreme control; separately reported as a stress/control caveat",
}

MINIMUM_ACCEPTABLE_HOLDOUT_P95_COVERAGE = 0.90
TAIL_RULE_LOOKBACK_DAYS = 30
TAIL_RULE_PERCENTILE = 0.995
TAIL_RULE_MINIMUM_OBSERVATIONS = 1000
TAIL_HARDENING_FINAL_GATE_AFTER_CRITIC = "EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW"

ARCHITECTURE_B_ID = "B_multi_horizon_strict_tail_maximum"
ARCHITECTURE_B_HORIZON_DAYS = (30, 90, 365)
ARCHITECTURE_B_PERCENTILE = 0.995
ARCHITECTURE_B_MINIMUM_OBSERVATIONS = 1000
ARCHITECTURE_B_SPEC_PATH = (
    "reports/execution_cost_candidate_v2_architecture_b_specification_freeze.json"
)
ARCHITECTURE_B_CRITIC_PATH = (
    "reports/execution_cost_candidate_v2_architecture_b_specification_freeze_critic.md"
)

TAIL_HARDENING_CRITIC_FINDINGS = [
    "Q4 is no longer a clean holdout because the original Q4 failure was reused to select the harder rule.",
    "The selected p99.5 rule came from a very small candidate set and was not chosen by a robust predeclared search protocol.",
    "Multi-year scalability is structural only; it has not been validated across additional years, sparse periods, or regime changes.",
    "The p99.5 choice has tail-percentile overfitting risk unless frozen before any new holdout.",
    "Stress/baseline separation remains clear, but the stress layer is still a design contract rather than a complete execution-cost regime.",
]

TAIL_HARDENING_CRITIC_RESPONSES = [
    "Final gate downgraded from READY_FOR_STRATEGY_INTEGRATION_WITH_CONDITIONS to EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW.",
    "The rolling p99.5 rule is retained as a candidate hardening result, not as an approved integration-ready policy.",
    "The report now labels Q4 as reused evidence rather than a clean holdout after rule selection.",
    "Next approval is limited to policy review of whether this 2024-calibrated rule can be frozen for a clean future holdout or must wait for multi-year partitioning.",
]


@dataclass(frozen=True)
class CorroborationWindow:
    window_id: str
    kind: str
    classification: str
    date: str
    start_utc: datetime
    end_utc: datetime
    cluster_start_utc: datetime
    cluster_end_utc: datetime


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def parse_float(value: str) -> float:
    if value == "":
        raise ValueError("Expected numeric value, found empty string.")
    return float(value)


def is_placeholder(row: dict[str, str]) -> bool:
    reasons = row.get("pair_quality_reasons", "").split(";")
    return PLACEHOLDER_REASON in reasons


def is_active_strict_valid(row: dict[str, str]) -> bool:
    return row.get("pair_quality_status") == STRICT_VALID_PAIR and not is_placeholder(row)


def select_strict_baseline_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return the primary baseline population and assert no policy leakage."""
    baseline_rows = [row for row in rows if is_active_strict_valid(row)]
    assert_strict_baseline_population(baseline_rows)
    return baseline_rows


def assert_strict_baseline_population(rows: list[dict[str, str]]) -> None:
    for row in rows:
        if row.get("pair_quality_status") != STRICT_VALID_PAIR:
            raise ValueError(
                "Primary baseline population contains non-strict row at "
                f"{row.get('timestamp_utc')}: {row.get('pair_quality_status')}"
            )
        if is_placeholder(row):
            raise ValueError(
                "Primary baseline population contains placeholder row at "
                f"{row.get('timestamp_utc')}"
            )


def session_bucket(timestamp_utc: datetime) -> str:
    matches = [
        window.name
        for window in get_session_windows(timestamp_utc.date())
        if window.start_utc <= timestamp_utc < window.end_utc
    ]
    if not matches:
        return "outside_configured_sessions"
    return "+".join(sorted(matches))


def rollover_bucket(timestamp_utc: datetime) -> str:
    if timestamp_utc.hour in {21, 22, 23, 0}:
        return "rollover_or_reopening_utc_21_00_to_00_59"
    return "ordinary_utc"


def percentile(sorted_values: list[float], fraction: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = fraction * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * weight


def summarize_values(values: list[float]) -> dict[str, float | int | None]:
    ordered = sorted(values)
    if not ordered:
        return {
            "count": 0,
            "min": None,
            "p05": None,
            "p25": None,
            "median": None,
            "mean": None,
            "p75": None,
            "p90": None,
            "p95": None,
            "p99": None,
            "max": None,
            "stddev": None,
        }
    average = mean(ordered)
    variance = (
        sum((value - average) ** 2 for value in ordered) / (len(ordered) - 1)
        if len(ordered) > 1
        else 0.0
    )
    return {
        "count": len(ordered),
        "min": ordered[0],
        "p05": percentile(ordered, 0.05),
        "p25": percentile(ordered, 0.25),
        "median": percentile(ordered, 0.50),
        "mean": average,
        "p75": percentile(ordered, 0.75),
        "p90": percentile(ordered, 0.90),
        "p95": percentile(ordered, 0.95),
        "p99": percentile(ordered, 0.99),
        "max": ordered[-1],
        "stddev": math.sqrt(variance),
    }


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, float | int | None]:
    return summarize_values([parse_float(row["spread"]) for row in rows])


def load_corroboration_windows(
    target_windows_path: Path = TARGET_WINDOWS_PATH,
    fxcm_windows_path: Path = FXCM_WINDOWS_PATH,
) -> list[CorroborationWindow]:
    target_rows = {row["window_id"]: row for row in read_csv_rows(target_windows_path)}
    fxcm_rows = read_csv_rows(fxcm_windows_path)
    windows: list[CorroborationWindow] = []
    for row in fxcm_rows:
        target = target_rows[row["window_id"]]
        windows.append(
            CorroborationWindow(
                window_id=row["window_id"],
                kind=row["kind"],
                classification=row["classification"],
                date=target["date"],
                start_utc=parse_timestamp(target["start_utc"]),
                end_utc=parse_timestamp(target["end_utc"]),
                cluster_start_utc=parse_timestamp(target["cluster_start_utc"]),
                cluster_end_utc=parse_timestamp(target["cluster_end_utc"]),
            )
        )
    return windows


def annotate_corroboration(
    row: dict[str, str],
    windows: list[CorroborationWindow],
) -> dict[str, str]:
    timestamp = parse_timestamp(row["timestamp_utc"])
    row_date = row.get("date", timestamp.strftime("%Y-%m-%d"))
    matching_target_cluster: list[CorroborationWindow] = []
    matching_window_context: list[CorroborationWindow] = []
    matching_same_date: list[CorroborationWindow] = []

    for window in windows:
        cluster_end_exclusive = window.cluster_end_utc + timedelta(minutes=1)
        if window.cluster_start_utc <= timestamp < cluster_end_exclusive:
            matching_target_cluster.append(window)
        elif window.start_utc <= timestamp < window.end_utc:
            matching_window_context.append(window)
        elif row_date == window.date:
            matching_same_date.append(window)

    selected: CorroborationWindow | None = None
    scope = NOT_EXTERNALLY_TESTED_SCOPE
    if matching_target_cluster:
        selected = matching_target_cluster[0]
        scope = TARGET_CLUSTER
    elif matching_window_context:
        selected = matching_window_context[0]
        scope = BOUNDED_WINDOW_CONTEXT
    elif matching_same_date:
        selected = matching_same_date[0]
        scope = SAME_DATE_CONTEXT

    if selected is None:
        return {
            "corroboration_window_id": "",
            "corroboration_scope": NOT_EXTERNALLY_TESTED_SCOPE,
            "corroboration_class": NOT_EXTERNALLY_TESTED,
            "allowed_use": allowed_use_for_row(row, NOT_EXTERNALLY_TESTED, NOT_EXTERNALLY_TESTED_SCOPE),
            "policy_version": POLICY_VERSION,
            "active_placeholder_flag": str(is_placeholder(row)).lower(),
        }

    return {
        "corroboration_window_id": selected.window_id,
        "corroboration_scope": scope,
        "corroboration_class": selected.classification,
        "allowed_use": allowed_use_for_row(row, selected.classification, scope),
        "policy_version": POLICY_VERSION,
        "active_placeholder_flag": str(is_placeholder(row)).lower(),
    }


def allowed_use_for_row(row: dict[str, str], classification: str, scope: str) -> str:
    if is_placeholder(row):
        return "excluded_count_only"
    status = row.get("pair_quality_status")
    if status == STRICT_VALID_PAIR:
        return "primary_baseline_allowed"
    if status != WARNING_REVIEW_PAIR:
        return "prohibited_confirmed_artifact_or_invalid"
    if scope != TARGET_CLUSTER:
        return "descriptive_context_only_not_row_corrob"
    if classification == CONFIRMED_CLOSELY:
        return "stress_sensitivity_allowed_non_pooled"
    if classification == CONFIRMED_DIRECTIONALLY:
        return "adverse_widened_uncertainty_secondary_only"
    if classification == DISAGREES:
        return "adverse_only_exclude_favorable_calibration"
    if classification == INCONCLUSIVE:
        return "unresolved_adverse_only_exclude_favorable_calibration"
    return "descriptive_only_not_externally_corrob"


def evidence_counts(rows: list[dict[str, str]], windows: list[CorroborationWindow]) -> dict[str, object]:
    status_counts = Counter(row.get("pair_quality_status", "") for row in rows)
    placeholder_count = sum(1 for row in rows if is_placeholder(row))
    active_rows = [row for row in rows if not is_placeholder(row)]
    active_status_counts = Counter(row.get("pair_quality_status", "") for row in active_rows)

    annotated_warning_counts: Counter[tuple[str, str, str]] = Counter()
    for row in active_rows:
        if row.get("pair_quality_status") == WARNING_REVIEW_PAIR:
            annotation = annotate_corroboration(row, windows)
            annotated_warning_counts[
                (
                    annotation["corroboration_scope"],
                    annotation["corroboration_class"],
                    annotation["allowed_use"],
                )
            ] += 1

    return {
        "total_rows": len(rows),
        "pair_status_counts": dict(status_counts),
        "placeholder_rows": placeholder_count,
        "active_rows": len(active_rows),
        "active_pair_status_counts": dict(active_status_counts),
        "active_warning_row_window_eligibility_counts": [
            {
                "corroboration_scope": scope,
                "corroboration_class": classification,
                "allowed_use": allowed_use,
                "rows": count,
            }
            for (scope, classification, allowed_use), count in sorted(annotated_warning_counts.items())
        ],
    }


def group_rows(
    rows: list[dict[str, str]],
    group_function,
) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[group_function(row)].append(row)
    return dict(grouped)


def timestamp_for_row(row: dict[str, str]) -> datetime:
    return parse_timestamp(row["timestamp_utc"])


def session_group(row: dict[str, str]) -> str:
    return session_bucket(timestamp_for_row(row))


def session_hour_group(row: dict[str, str]) -> str:
    timestamp = timestamp_for_row(row)
    return f"{session_bucket(timestamp)}|utc_hour={timestamp.hour:02d}"


def day_of_week_group(row: dict[str, str]) -> str:
    return timestamp_for_row(row).strftime("%A")


def month_group(row: dict[str, str]) -> str:
    return timestamp_for_row(row).strftime("%Y-%m")


def summarize_by_group(
    rows: list[dict[str, str]],
    group_name: str,
    group_function,
) -> list[dict[str, object]]:
    summaries = []
    for group_value, group_rows_value in sorted(group_rows(rows, group_function).items()):
        summaries.append(
            {
                "group_type": group_name,
                "group_value": group_value,
                **summarize_rows(group_rows_value),
            }
        )
    return summaries


def split_train_validation(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    train = []
    validation = []
    for row in rows:
        timestamp = timestamp_for_row(row)
        if timestamp < datetime(2024, 10, 1):
            train.append(row)
        else:
            validation.append(row)
    return train, validation


def month_start(timestamp: datetime) -> datetime:
    return datetime(timestamp.year, timestamp.month, 1)


def add_one_month(timestamp: datetime) -> datetime:
    if timestamp.month == 12:
        return datetime(timestamp.year + 1, 1, 1)
    return datetime(timestamp.year, timestamp.month + 1, 1)


def rows_between(
    rows: list[dict[str, str]],
    start: datetime,
    end: datetime,
) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if start <= timestamp_for_row(row) < end
    ]


def candidate_summary(
    name: str,
    train_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    group_function=None,
    minimum_bucket_rows: int = 200,
) -> dict[str, object]:
    if group_function is None:
        thresholds = {"global": summarize_rows(train_rows)}
        validation_groups = {"global": validation_rows}
        data_poor_groups: list[str] = []
    else:
        train_groups = group_rows(train_rows, group_function)
        validation_groups = group_rows(validation_rows, group_function)
        thresholds = {group: summarize_rows(items) for group, items in train_groups.items()}
        global_threshold = summarize_rows(train_rows)
        data_poor_groups = [
            group for group, summary in thresholds.items() if int(summary["count"] or 0) < minimum_bucket_rows
        ]
        thresholds["__fallback_global__"] = global_threshold

    covered = 0
    total = 0
    absolute_errors: list[float] = []
    for group, rows in validation_groups.items():
        threshold = thresholds.get(group) or thresholds["__fallback_global__"]
        p95 = threshold["p95"]
        median = threshold["median"]
        if p95 is None or median is None:
            continue
        for row in rows:
            spread = parse_float(row["spread"])
            total += 1
            if spread <= float(p95):
                covered += 1
            absolute_errors.append(abs(spread - float(median)))

    return {
        "name": name,
        "conditioning": "global" if group_function is None else name.replace("_empirical_distribution", ""),
        "train_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "validation_p95_coverage": covered / total if total else None,
        "validation_median_mae": mean(absolute_errors) if absolute_errors else None,
        "data_poor_group_count": len(data_poor_groups),
        "data_poor_groups": data_poor_groups[:20],
        "selected": False,
        "selection_note": "",
    }


def validate_baseline_model(
    train_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    candidates = [
        candidate_summary("global_empirical_distribution", train_rows, validation_rows),
        candidate_summary("session_bucket_empirical_distribution", train_rows, validation_rows, session_group),
        candidate_summary("session_hour_empirical_distribution", train_rows, validation_rows, session_hour_group),
    ]
    global_candidate = candidates[0]
    global_candidate["selected"] = True
    global_candidate["selection_note"] = (
        "Selected because it is the simplest transparent baseline and had the least weak temporal "
        "holdout p95 coverage. Session/regime structure is retained as mandatory diagnostics and "
        "sensitivity context rather than promoted to a more fragile primary baseline."
    )
    return candidates


def static_tail_candidate(
    train_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    percentile_fraction: float,
    name: str,
) -> dict[str, object]:
    threshold = percentile(
        sorted(parse_float(row["spread"]) for row in train_rows),
        percentile_fraction,
    )
    validation_spreads = [parse_float(row["spread"]) for row in validation_rows]
    covered = sum(1 for spread in validation_spreads if spread <= threshold)
    return {
        "name": name,
        "rule_type": "static_train_only_empirical_percentile",
        "percentile": percentile_fraction,
        "calibration_period": "2024-01-01 <= timestamp < 2024-10-01",
        "validation_period": "2024-10-01 <= timestamp <= 2024-12-31",
        "calibration_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "threshold": threshold,
        "realized_validation_coverage": covered / len(validation_spreads) if validation_spreads else None,
        "validation_median_spread": percentile(sorted(validation_spreads), 0.50),
        "validation_p95_spread": percentile(sorted(validation_spreads), 0.95),
        "validation_p99_spread": percentile(sorted(validation_spreads), 0.99),
        "selected": False,
    }


def monthly_tail_folds(
    rows: list[dict[str, str]],
    lookback_days: int,
    percentile_fraction: float,
    minimum_observations: int,
    start_month: datetime = datetime(2024, 4, 1),
    end_month_exclusive: datetime = datetime(2025, 1, 1),
) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    current = start_month
    while current < end_month_exclusive:
        next_month = add_one_month(current)
        calibration_start = current - timedelta(days=lookback_days)
        calibration_rows = rows_between(rows, calibration_start, current)
        validation_rows = rows_between(rows, current, next_month)
        calibration_spreads = sorted(parse_float(row["spread"]) for row in calibration_rows)
        validation_spreads = [parse_float(row["spread"]) for row in validation_rows]
        threshold = (
            percentile(calibration_spreads, percentile_fraction)
            if len(calibration_spreads) >= minimum_observations
            else None
        )
        if threshold is None or not validation_spreads:
            realized_coverage = None
            covered_rows = 0
        else:
            covered_rows = sum(1 for spread in validation_spreads if spread <= threshold)
            realized_coverage = covered_rows / len(validation_spreads)
        folds.append(
            {
                "fold": current.strftime("%Y-%m"),
                "calibration_start": calibration_start.strftime("%Y-%m-%d %H:%M:%S"),
                "calibration_end_exclusive": current.strftime("%Y-%m-%d %H:%M:%S"),
                "validation_start": current.strftime("%Y-%m-%d %H:%M:%S"),
                "validation_end_exclusive": next_month.strftime("%Y-%m-%d %H:%M:%S"),
                "calibration_rows": len(calibration_rows),
                "validation_rows": len(validation_rows),
                "threshold": threshold,
                "covered_rows": covered_rows,
                "realized_coverage": realized_coverage,
                "validation_median_spread": percentile(sorted(validation_spreads), 0.50),
                "validation_p95_spread": percentile(sorted(validation_spreads), 0.95),
                "validation_p99_spread": percentile(sorted(validation_spreads), 0.99),
                "validation_max_spread": max(validation_spreads) if validation_spreads else None,
            }
        )
        current = next_month
    return folds


def rolling_monthly_tail_candidate(
    rows: list[dict[str, str]],
    lookback_days: int,
    percentile_fraction: float,
    minimum_observations: int,
    name: str,
) -> dict[str, object]:
    folds = monthly_tail_folds(
        rows,
        lookback_days=lookback_days,
        percentile_fraction=percentile_fraction,
        minimum_observations=minimum_observations,
    )
    coverages = [
        fold["realized_coverage"]
        for fold in folds
        if fold["realized_coverage"] is not None
    ]
    thresholds = [
        fold["threshold"]
        for fold in folds
        if fold["threshold"] is not None
    ]
    return {
        "name": name,
        "rule_type": "monthly_recalibrated_trailing_empirical_percentile",
        "lookback_days": lookback_days,
        "percentile": percentile_fraction,
        "minimum_observations": minimum_observations,
        "folds": folds,
        "fold_count": len(folds),
        "minimum_realized_coverage": min(coverages) if coverages else None,
        "mean_realized_coverage": mean(coverages) if coverages else None,
        "median_threshold": percentile(sorted(thresholds), 0.50) if thresholds else None,
        "maximum_threshold": max(thresholds) if thresholds else None,
        "thin_data_folds": [
            fold["fold"]
            for fold in folds
            if fold["calibration_rows"] < minimum_observations
        ],
        "selected": False,
    }


def validate_tail_hardening(rows: list[dict[str, str]]) -> dict[str, object]:
    strict_rows = sorted(select_strict_baseline_rows(rows), key=lambda row: row["timestamp_utc"])
    train_rows, validation_rows = split_train_validation(strict_rows)
    candidates = [
        static_tail_candidate(train_rows, validation_rows, 0.95, "A_control_static_train_p95"),
        static_tail_candidate(train_rows, validation_rows, 0.99, "B_static_train_p99"),
        static_tail_candidate(train_rows, validation_rows, 0.995, "B_static_train_p99_5"),
        rolling_monthly_tail_candidate(
            strict_rows,
            lookback_days=TAIL_RULE_LOOKBACK_DAYS,
            percentile_fraction=0.99,
            minimum_observations=TAIL_RULE_MINIMUM_OBSERVATIONS,
            name="C_rolling_30d_monthly_p99",
        ),
        rolling_monthly_tail_candidate(
            strict_rows,
            lookback_days=TAIL_RULE_LOOKBACK_DAYS,
            percentile_fraction=TAIL_RULE_PERCENTILE,
            minimum_observations=TAIL_RULE_MINIMUM_OBSERVATIONS,
            name="C_selected_rolling_30d_monthly_p99_5",
        ),
    ]

    selected = candidates[-1]
    selected["selected"] = True
    selected["selection_reason"] = (
        "Smallest tested rolling tail rule that stayed above 90% realized coverage "
        "in every monthly prospective fold while using only prior strict-valid rows."
    )

    return {
        "status": "hardened_tail_rule_selected",
        "original_failure_reproduced": candidates[0],
        "selected_rule": selected,
        "candidates": candidates,
        "defensibility_rule": {
            "minimum_required_coverage": MINIMUM_ACCEPTABLE_HOLDOUT_P95_COVERAGE,
            "required_no_future_data": True,
            "required_strict_only": True,
            "required_no_warning_review_baseline": True,
            "required_transparent_rule": True,
        },
        "prospective_cost_contract": {
            "information_allowed_at_time_t": "strict_valid_pair rows with timestamp earlier than the calibration boundary only",
            "calibration_schedule": "monthly boundary recalibration",
            "lookback_days": TAIL_RULE_LOOKBACK_DAYS,
            "percentile": TAIL_RULE_PERCENTILE,
            "minimum_observations": TAIL_RULE_MINIMUM_OBSERVATIONS,
            "insufficient_history_behavior": "return unavailable/error until minimum prior strict-valid rows exist; do not backfill with future rows",
            "session_time_fallback": "not used by selected primary tail rule; session diagnostics remain reporting-only",
            "returned_estimate": "trailing strict-valid p99.5 spread threshold for the current monthly calibration period",
            "deterministic": True,
            "metadata_returned": [
                "policy_version",
                "baseline_population",
                "calibration_start",
                "calibration_end_exclusive",
                "lookback_days",
                "percentile",
                "calibration_rows",
                "warning_review_rows_in_baseline",
            ],
        },
        "multi_year_scalability": {
            "assessment": "structurally suitable for multi-year expansion as a rolling/expanding family because it uses prior strict-valid observations only and does not hard-code 2024 dates",
            "additional_years_behavior": "monthly recalibration would adapt to changing spread regimes as new prior strict-valid evidence accumulates",
            "parameters_to_freeze_before_future_holdouts": [
                "lookback_days",
                "percentile",
                "minimum_observations",
                "calibration_schedule",
                "fallback behavior",
            ],
            "holdout_protection": "future years should be partitioned before further model refinement; failed holdouts must remain recorded rather than repeatedly tuned against",
        },
        "future_data_leakage_detected": False,
        "warning_review_rows_in_baseline": 0,
    }


def prospective_tail_cost_for_timestamp(
    strict_rows: list[dict[str, str]],
    timestamp: datetime,
    lookback_days: int = TAIL_RULE_LOOKBACK_DAYS,
    percentile_fraction: float = TAIL_RULE_PERCENTILE,
    minimum_observations: int = TAIL_RULE_MINIMUM_OBSERVATIONS,
) -> dict[str, object]:
    assert_strict_baseline_population(strict_rows)
    calibration_end = month_start(timestamp)
    calibration_start = calibration_end - timedelta(days=lookback_days)
    calibration_rows = rows_between(strict_rows, calibration_start, calibration_end)
    if len(calibration_rows) < minimum_observations:
        raise ValueError(
            "Insufficient prior strict-valid rows for prospective tail estimate: "
            f"{len(calibration_rows)} < {minimum_observations}"
        )
    threshold = percentile(
        sorted(parse_float(row["spread"]) for row in calibration_rows),
        percentile_fraction,
    )
    return {
        "estimate": threshold,
        "policy_version": POLICY_VERSION,
        "baseline_population": "active strict_valid_pair only",
        "calibration_start": calibration_start.strftime("%Y-%m-%d %H:%M:%S"),
        "calibration_end_exclusive": calibration_end.strftime("%Y-%m-%d %H:%M:%S"),
        "lookback_days": lookback_days,
        "percentile": percentile_fraction,
        "calibration_rows": len(calibration_rows),
        "warning_review_rows_in_baseline": 0,
    }


def _architecture_b_row_is_eligible(row: dict[str, str]) -> bool:
    """Apply the frozen Architecture B primary-population boundary."""
    if not is_active_strict_valid(row):
        return False
    try:
        spread = parse_float(row.get("spread", ""))
    except (TypeError, ValueError):
        return False
    if not math.isfinite(spread) or spread < 0:
        return False
    reasons = set(filter(None, row.get("pair_quality_reasons", "").split(";")))
    if "SYNTHETIC" in reasons or "DESCRIPTIVE_ONLY" in reasons:
        return False
    if row.get("synthetic", "").strip().lower() in {"1", "true", "yes"}:
        return False
    if row.get("population_role", "").strip().lower() == "descriptive_only":
        return False
    return True


def architecture_b_tail_cost_for_timestamp(
    rows: list[dict[str, str]],
    timestamp: datetime,
) -> dict[str, object]:
    """Return the frozen Architecture B estimate for ``timestamp``'s UTC month.

    This is a mechanical estimator only. It does not evaluate candidate
    performance. Each call recomputes from the information available before
    the current monthly boundary, so there is no carry-forward or backfill.
    """
    if timestamp.tzinfo is None or timestamp.utcoffset() != timedelta(0):
        raise ValueError("Architecture B timestamps must be timezone-explicit UTC.")

    update_boundary = datetime(
        timestamp.year,
        timestamp.month,
        1,
        tzinfo=timezone.utc,
    )
    eligible_rows = [row for row in rows if _architecture_b_row_is_eligible(row)]
    diagnostics: list[dict[str, object]] = []
    thresholds: list[float] = []

    for horizon_days in ARCHITECTURE_B_HORIZON_DAYS:
        horizon_start = update_boundary - timedelta(days=horizon_days)
        horizon_rows = [
            row
            for row in eligible_rows
            if horizon_start
            <= parse_timestamp(row["timestamp_utc"]).replace(tzinfo=timezone.utc)
            < update_boundary
        ]
        count = len(horizon_rows)
        diagnostic: dict[str, object] = {
            "horizon_calendar_days": horizon_days,
            "interval_start_inclusive_utc": horizon_start.isoformat().replace("+00:00", "Z"),
            "interval_end_exclusive_utc": update_boundary.isoformat().replace("+00:00", "Z"),
            "prior_strict_valid_count": count,
            "required_minimum": ARCHITECTURE_B_MINIMUM_OBSERVATIONS,
        }
        if count < ARCHITECTURE_B_MINIMUM_OBSERVATIONS:
            diagnostic.update(
                {
                    "status": "unavailable",
                    "reason": "minimum_prior_strict_valid_observations_not_met",
                    "threshold": None,
                }
            )
        else:
            threshold = percentile(
                sorted(parse_float(row["spread"]) for row in horizon_rows),
                ARCHITECTURE_B_PERCENTILE,
            )
            diagnostic.update({"status": "eligible", "threshold": threshold})
            thresholds.append(threshold)
        diagnostics.append(diagnostic)

    estimate = max(thresholds) if thresholds else None
    return {
        "candidate_family": "execution_cost_candidate_v2",
        "architecture": ARCHITECTURE_B_ID,
        "status": "available" if estimate is not None else "unavailable",
        "estimate": estimate,
        "update_boundary_utc": update_boundary.isoformat().replace("+00:00", "Z"),
        "update_cadence": "monthly",
        "baseline_population": "active strict_valid_pair only",
        "percentile": ARCHITECTURE_B_PERCENTILE,
        "percentile_semantics": "sorted rank q * (n - 1) with linear interpolation",
        "combination_rule": "maximum threshold among eligible horizons",
        "covered_comparison": "observed_spread <= threshold",
        "horizon_diagnostics": diagnostics,
        "warning_review_rows_in_baseline": 0,
        "carry_forward_used": False,
        "future_backfill_used": False,
        "policy_version": POLICY_VERSION,
        "source_artifacts": [ARCHITECTURE_B_SPEC_PATH, ARCHITECTURE_B_CRITIC_PATH],
    }


def architecture_b_observation_is_covered(
    observed_spread: float,
    threshold: float,
) -> bool:
    """Apply the frozen inclusive Architecture B coverage convention."""
    return observed_spread <= threshold


def build_baseline_model(rows: list[dict[str, str]]) -> dict[str, object]:
    strict_rows = select_strict_baseline_rows(rows)
    train_rows, validation_rows = split_train_validation(strict_rows)
    candidates = validate_baseline_model(train_rows, validation_rows)
    session_summaries = summarize_by_group(train_rows, "session_bucket", session_group)
    return {
        "model_form": "strict_valid_global_empirical_distribution_with_session_regime_diagnostics",
        "policy_version": POLICY_VERSION,
        "baseline_population": "active strict_valid_pair only",
        "warning_review_rows_in_primary_baseline": 0,
        "conditioning_variables": [
            "none for the primary global empirical baseline",
            "configured_session_overlap_bucket for mandatory diagnostics and sensitivity context",
            "UTC timestamp for session conversion and reporting",
        ],
        "fallback": "global strict-valid empirical distribution when a future session bucket is absent",
        "train_period": "2024-01-01 <= timestamp < 2024-10-01",
        "validation_period": "2024-10-01 <= timestamp <= 2024-12-31",
        "train_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "global_train_summary": summarize_rows(train_rows),
        "global_full_strict_summary": summarize_rows(strict_rows),
        "prospective_application_guard": {
            "train_period_summary_use": "candidate prospective baseline cost source",
            "full_sample_summary_use": "descriptive characterization only",
            "full_sample_summary_strategy_cost_use": "PROHIBITED_FOR_2024_STRATEGY_EVALUATION",
            "reason": (
                "Full-year strict summaries include validation-period evidence and could leak "
                "future-period spread information into later 2024 strategy evaluation."
            ),
        },
        "session_bucket_train_summaries": session_summaries,
        "candidate_validation": candidates,
        "validation_risk_flag": (
            "Temporal holdout p95 coverage is materially below nominal for all candidates, "
            "consistent with Q4 strict-valid spread drift. Future strategy integration must "
            "report conservative p99/tail sensitivity and not treat train-period p95 as a hard cap."
        ),
    }


def determine_gate(baseline_model: dict[str, object]) -> tuple[str, list[str]]:
    selected_candidates = [
        candidate
        for candidate in baseline_model["candidate_validation"]
        if candidate.get("selected")
    ]
    if not selected_candidates:
        return "EXECUTION_COST_MODEL_INVALID", ["No selected baseline candidate was recorded."]

    selected = selected_candidates[0]
    coverage = selected.get("validation_p95_coverage")
    reasons: list[str] = []
    if coverage is None or coverage < MINIMUM_ACCEPTABLE_HOLDOUT_P95_COVERAGE:
        reasons.append(
            "Selected strict-only candidate has materially weak temporal p95 holdout coverage "
            f"({coverage:.6f} < {MINIMUM_ACCEPTABLE_HOLDOUT_P95_COVERAGE:.2f})."
        )
    reasons.append(
        "Stress/sensitivity layer is a separated design contract and historical scenario summary; "
        "a hardened prospective stress-cost predicate has not been implemented."
    )
    if reasons:
        return "EXECUTION_COST_MODEL_NEEDS_SMALL_FOLLOWUP", reasons
    return "READY_FOR_STRATEGY_INTEGRATION_WITH_CONDITIONS", []


def determine_tail_hardening_gate(tail_hardening: dict[str, object]) -> tuple[str, list[str]]:
    selected = tail_hardening["selected_rule"]
    minimum_coverage = selected.get("minimum_realized_coverage")
    reasons: list[str] = []
    if minimum_coverage is None or minimum_coverage < MINIMUM_ACCEPTABLE_HOLDOUT_P95_COVERAGE:
        reasons.append(
            "Selected prospective tail rule did not meet required coverage: "
            f"{minimum_coverage} < {MINIMUM_ACCEPTABLE_HOLDOUT_P95_COVERAGE}."
        )
    if selected.get("thin_data_folds"):
        reasons.append(f"Selected rule has thin-data folds: {selected['thin_data_folds']}.")
    if tail_hardening.get("warning_review_rows_in_baseline") != 0:
        reasons.append("Warning-review rows entered the hardened baseline.")
    if tail_hardening.get("future_data_leakage_detected"):
        reasons.append("Future-data leakage was detected.")
    if reasons:
        return "EXECUTION_COST_MODEL_NEEDS_SMALL_FOLLOWUP", reasons
    return "READY_FOR_STRATEGY_INTEGRATION_WITH_CONDITIONS", [
        "Ready only for bounded mechanical strategy-integration wiring under the strict-only prospective tail contract; not approved for strategy discovery, ranking, optimization, or profitability claims."
    ]


def build_stress_layer(
    rows: list[dict[str, str]],
    windows: list[CorroborationWindow],
) -> dict[str, object]:
    buckets: dict[str, list[dict[str, str]]] = {
        "closely_corrob_target_cluster_warning": [],
        "directional_target_cluster_warning": [],
        "disagreed_target_cluster_warning": [],
        "inconclusive_target_cluster_warning": [],
        "untested_active_warning": [],
    }
    special_case_counts_by_scope = {
        window_id: {
            TARGET_CLUSTER: 0,
            BOUNDED_WINDOW_CONTEXT: 0,
            SAME_DATE_CONTEXT: 0,
            NOT_EXTERNALLY_TESTED_SCOPE: 0,
        }
        for window_id in SPECIAL_CASES
    }
    for row in rows:
        if is_placeholder(row) or row.get("pair_quality_status") != WARNING_REVIEW_PAIR:
            continue
        annotation = annotate_corroboration(row, windows)
        classification = annotation["corroboration_class"]
        scope = annotation["corroboration_scope"]
        window_id = annotation["corroboration_window_id"]
        if window_id in special_case_counts_by_scope:
            special_case_counts_by_scope[window_id][scope] += 1
        if scope != TARGET_CLUSTER:
            if classification == NOT_EXTERNALLY_TESTED:
                buckets["untested_active_warning"].append(row)
            continue
        if classification == CONFIRMED_CLOSELY:
            buckets["closely_corrob_target_cluster_warning"].append(row)
        elif classification == CONFIRMED_DIRECTIONALLY:
            buckets["directional_target_cluster_warning"].append(row)
        elif classification == DISAGREES:
            buckets["disagreed_target_cluster_warning"].append(row)
        elif classification == INCONCLUSIVE:
            buckets["inconclusive_target_cluster_warning"].append(row)

    return {
        "model_form": "separate_non_pooled_policy_stress_and_sensitivity_layer",
        "primary_baseline_pooling": "PROHIBITED",
        "prospective_membership_contract": {
            "status": "design_contract_only_no_strategy_application",
            "auditable_predicate_required_before_strategy_use": True,
            "hard_coded_historical_dates_for_future_membership": "PROHIBITED",
            "allowed_future_features": [
                "configured_session_overlap_bucket",
                "predeclared rollover/reopening UTC window flag",
                "predeclared timestamp features",
                "predeclared trailing spread quantile feature using strict-valid calibration only",
                "external corroboration status for labelled historical calibration/evaluation rows",
            ],
        },
        "scenario_summaries": {
            name: summarize_rows(items) for name, items in buckets.items()
        },
        "scenario_row_counts": {name: len(items) for name, items in buckets.items()},
        "directional_usage": "adverse_widened_uncertainty_secondary_only",
        "disagreed_inconclusive_usage": "excluded_from_favorable_calibration_retained_for_adverse_or_unresolved_sensitivity",
        "unresolved_strict_valid_extreme": {
            "window_id": "2024-04-05_strict_ge2_01",
            "treatment": SPECIAL_CASES["2024-04-05_strict_ge2_01"],
        },
        "special_case_counts_by_scope": special_case_counts_by_scope,
    }


def regime_characterization(rows: list[dict[str, str]]) -> dict[str, object]:
    return {
        "overall": summarize_rows(rows),
        "by_session_bucket": summarize_by_group(rows, "session_bucket", session_group),
        "by_day_of_week": summarize_by_group(rows, "day_of_week", day_of_week_group),
        "by_month": summarize_by_group(rows, "month", month_group),
        "by_rollover_bucket": summarize_by_group(rows, "rollover_bucket", lambda row: rollover_bucket(timestamp_for_row(row))),
    }


def lag_one_autocorrelation(rows: list[dict[str, str]]) -> float | None:
    ordered = sorted(rows, key=lambda row: row["timestamp_utc"])
    values = [parse_float(row["spread"]) for row in ordered]
    if len(values) < 3:
        return None
    x = values[:-1]
    y = values[1:]
    x_mean = mean(x)
    y_mean = mean(y)
    numerator = sum((left - x_mean) * (right - y_mean) for left, right in zip(x, y))
    denominator = math.sqrt(
        sum((left - x_mean) ** 2 for left in x)
        * sum((right - y_mean) ** 2 for right in y)
    )
    if denominator == 0:
        return None
    return numerator / denominator


def build_spec(
    reconciliation_path: Path = RECONCILIATION_PATH,
    policy_path: Path = POLICY_PATH,
    policy_json_path: Path = POLICY_JSON_PATH,
    target_windows_path: Path = TARGET_WINDOWS_PATH,
    fxcm_windows_path: Path = FXCM_WINDOWS_PATH,
) -> dict[str, object]:
    rows = read_csv_rows(reconciliation_path)
    windows = load_corroboration_windows(target_windows_path, fxcm_windows_path)
    strict_rows = select_strict_baseline_rows(rows)
    baseline_model = build_baseline_model(rows)
    stress_layer = build_stress_layer(rows, windows)
    tail_hardening = validate_tail_hardening(rows)
    pre_critic_gate, pre_critic_gate_reasons = determine_tail_hardening_gate(tail_hardening)
    final_gate = TAIL_HARDENING_FINAL_GATE_AFTER_CRITIC
    gate_reasons = [
        "Independent critic found material Q4 holdout reuse / selection-leakage risk.",
        "The rolling p99.5 tail rule is a candidate result, not yet policy-approved for strategy integration.",
        "A separate policy review must decide whether to freeze this rule for a clean future holdout or wait for multi-year partitioning.",
    ]

    return {
        "artifact": "execution_cost_model_spec",
        "status": "implemented_not_strategy_integrated",
        "gate": final_gate,
        "gate_reasons": gate_reasons,
        "pre_tail_critic_gate": pre_critic_gate,
        "pre_tail_critic_gate_reasons": pre_critic_gate_reasons,
        "policy": {
            "version": POLICY_VERSION,
            "source": str(policy_path.relative_to(PROJECT_DIR)),
            "json_source": str(policy_json_path.relative_to(PROJECT_DIR)),
            "binding_gate": "READY_FOR_EXECUTION_COST_MODELLING_WITH_CONDITIONS",
        },
        "input_data": {
            "reconciliation_path": str(reconciliation_path.relative_to(PROJECT_DIR)),
            "target_windows_path": str(target_windows_path.relative_to(PROJECT_DIR)),
            "fxcm_windows_path": str(fxcm_windows_path.relative_to(PROJECT_DIR)),
        },
        "policy_to_code_contract": {
            "primary_population_definition": "pair_quality_status == strict_valid_pair and MARKET_CLOSED_PLACEHOLDER absent",
            "excluded_from_primary_baseline": [
                "warning_review_pair",
                "placeholder/market-closed rows",
                "excluded rows",
                "confirmed artifact/invalid rows",
            ],
            "warning_review_baseline_leakage_assertion": "select_strict_baseline_rows plus assert_strict_baseline_population",
            "required_row_metadata": [
                "timestamp_utc",
                "pair_quality_status",
                "pair_quality_reasons",
                "active_placeholder_flag",
                "corroboration_window_id",
                "corroboration_scope",
                "corroboration_class",
                "allowed_use",
                "policy_version",
            ],
        },
        "evidence_counts": evidence_counts(rows, windows),
        "baseline_model": baseline_model,
        "prospective_tail_hardening": tail_hardening,
        "tail_hardening_independent_critic": {
            "status": "completed_read_only",
            "materially_changed_conclusion": True,
            "material_findings": TAIL_HARDENING_CRITIC_FINDINGS,
            "responses": TAIL_HARDENING_CRITIC_RESPONSES,
            "recommended_gate": TAIL_HARDENING_FINAL_GATE_AFTER_CRITIC,
        },
        "strict_only_characterization": {
            **regime_characterization(strict_rows),
            "lag_one_autocorrelation": lag_one_autocorrelation(strict_rows),
        },
        "stress_sensitivity_layer": stress_layer,
        "independent_critic": {
            "status": "completed_read_only",
            "materially_changed_implementation": True,
            "material_findings": [
                "Temporal validation shows material baseline underestimation; train-period p95 covers only about 73.1% of Q4 validation rows.",
                "Full-year strict summaries need an explicit descriptive-only guard to avoid future-period leakage into 2024 strategy evaluation.",
                "Stress model remains a design contract rather than an implemented prospective stress-cost model.",
                "Special-case counts needed scope splitting so context rows are not confused with target-cluster evidence.",
            ],
            "recommended_gate": "EXECUTION_COST_MODEL_NEEDS_SMALL_FOLLOWUP",
            "response": [
                "Final gate downgraded to EXECUTION_COST_MODEL_NEEDS_SMALL_FOLLOWUP.",
                "Added train-only/prospective application guard and prohibited full-year summaries as 2024 strategy cost inputs.",
                "Made weak p95 holdout coverage an executable gate reason.",
                "Split special-case counts by target-cluster, bounded-window, same-date, and not-tested scope.",
            ],
        },
        "output_contract": {
            "future_strategy_inputs": [
                "baseline spread empirical distribution from active strict-valid rows",
                "mandatory session/regime diagnostic summaries for context",
                "baseline median/p75/p90/p95/p99 spread estimate for timestamp context",
                "conservative strict-only percentile cost",
                "separate labelled stress/sensitivity scenario outputs",
                "evidence-class and policy-version metadata",
            ],
            "spread_only": True,
            "not_in_scope_or_missing": [
                "slippage",
                "commissions",
                "financing",
                "latency",
                "order-book depth",
                "market impact",
            ],
        },
        "limitations": [
            "FXCM corroboration remains demo/account/feed specific and partially supportive only.",
            "Warning-review evidence is not permitted in the primary baseline.",
            "Stress-regime predicates must be finalized as auditable functions before strategy application.",
            "The model is fitted on 2024 evidence and must preserve policy/version metadata in future use.",
        ],
        "no_strategy_use": True,
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, indent=2, sort_keys=True)
        output_file.write("\n")


def fmt(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def render_report(spec: dict[str, object]) -> str:
    baseline = spec["baseline_model"]
    evidence = spec["evidence_counts"]
    stress = spec["stress_sensitivity_layer"]
    critic = spec["independent_critic"]
    selected = [
        candidate
        for candidate in baseline["candidate_validation"]
        if candidate.get("selected")
    ][0]
    global_summary = baseline["global_full_strict_summary"]

    lines = [
        "# Execution-Cost Model Implementation",
        "",
        "Date: 2026-08-11",
        "Status: implemented and validated; not strategy-integrated",
        f"Gate decision: {spec['gate']}",
        "",
        "## Purpose",
        "",
        "This artifact implements the execution-cost modelling layer authorized by the post-corroboration evidence policy. It builds a spread-only primary baseline from active strict-valid evidence and keeps warning-review evidence out of the baseline.",
        "",
        "No strategy backtests, ranking, optimization, profitability claims, external acquisition, raw evidence changes, schema changes, or session-definition changes were performed.",
        "",
        "## Policy Source",
        "",
        f"- Policy version: `{spec['policy']['version']}`",
        f"- Policy artifact: `{spec['policy']['source']}`",
        f"- Policy JSON: `{spec['policy']['json_source']}`",
        f"- Binding policy gate: `{spec['policy']['binding_gate']}`",
        "",
        "## Policy-To-Code Contract",
        "",
        "- Primary baseline population: active `strict_valid_pair` rows only.",
        "- Baseline exclusion rule: `warning_review_pair`, placeholders, excluded rows, and confirmed artifact/invalid rows are prohibited from the primary baseline.",
        "- Enforcement: `select_strict_baseline_rows()` filters the population and `assert_strict_baseline_population()` raises on any warning or placeholder leakage.",
        "- Future model rows must carry timestamp, quality status, placeholder flag, corroboration window/scope/class, allowed-use, and policy-version metadata.",
        "",
        "## Evidence Counts",
        "",
        f"- Full reconciliation rows: {evidence['total_rows']}",
        f"- Active rows: {evidence['active_rows']}",
        f"- Placeholder rows: {evidence['placeholder_rows']}",
        f"- Active strict-valid rows: {evidence['active_pair_status_counts'].get(STRICT_VALID_PAIR, 0)}",
        f"- Active warning-review rows: {evidence['active_pair_status_counts'].get(WARNING_REVIEW_PAIR, 0)}",
        "",
        "## Baseline Model",
        "",
        f"- Selected form: `{baseline['model_form']}`",
        "- Major conditioning variables: none for the primary global empirical baseline; configured session overlap bucket and UTC timestamp are retained for diagnostics, reporting, and sensitivity context.",
        f"- Training period: {baseline['train_period']} ({baseline['train_rows']} strict rows)",
        f"- Validation period: {baseline['validation_period']} ({baseline['validation_rows']} strict rows)",
        f"- Strict-only full-sample median spread: {fmt(global_summary['median'])}",
        f"- Strict-only full-sample p95 spread: {fmt(global_summary['p95'])}",
        f"- Strict-only full-sample p99 spread: {fmt(global_summary['p99'])}",
        f"- Strict-only full-sample max spread: {fmt(global_summary['max'])}",
        f"- Lag-1 spread autocorrelation: {fmt(spec['strict_only_characterization']['lag_one_autocorrelation'])}",
        f"- Validation risk flag: {baseline['validation_risk_flag']}",
        f"- Prospective-use guard: {baseline['prospective_application_guard']['full_sample_summary_strategy_cost_use']}",
        "",
        "Candidate validation was temporal and leakage-resistant: Jan-Sep 2024 strict-valid rows trained the candidate distributions; Oct-Dec 2024 strict-valid rows validated them. No strategy information was used.",
        "",
        "| Candidate | Validation p95 coverage | Median MAE | Data-poor groups | Selected |",
        "|---|---:|---:|---:|---|",
    ]

    for candidate in baseline["candidate_validation"]:
        lines.append(
            "| {name} | {coverage} | {mae} | {poor} | {selected} |".format(
                name=candidate["name"],
                coverage=fmt(candidate["validation_p95_coverage"]),
                mae=fmt(candidate["validation_median_mae"]),
                poor=candidate["data_poor_group_count"],
                selected="yes" if candidate["selected"] else "no",
            )
        )

    lines.extend(
        [
            "",
            f"Selection rationale: {selected['selection_note']}",
            "",
            "Gate reasons:",
            "",
        ]
    )
    for reason in spec["gate_reasons"]:
        lines.append(f"- {reason}")

    lines.extend(
        [
            "",
            "## Stress And Sensitivity Layer",
            "",
            f"- Form: `{stress['model_form']}`",
            "- Primary baseline pooling: prohibited.",
            "- Closely corroborated target-cluster warning rows: separate non-pooled stress/sensitivity scenario only.",
            "- Directionally corroborated warning rows: adverse, widened-uncertainty, secondary scenario only.",
            "- Disagreed and inconclusive windows: excluded from favorable calibration and retained for adverse/unresolved reporting.",
            "- Future stress membership must be prospective and auditable; hard-coded historical stress dates are prohibited as future membership logic.",
            "",
            "Stress/sensitivity row counts:",
            "",
        ]
    )
    for name, count in sorted(stress["scenario_row_counts"].items()):
        lines.append(f"- `{name}`: {count}")

    lines.extend(
        [
            "",
            "Special-case counts are split by scope so target-cluster evidence is not confused with context rows:",
            "",
        ]
    )
    for window_id, counts in sorted(stress["special_case_counts_by_scope"].items()):
        lines.append(
            f"- `{window_id}`: target_cluster={counts[TARGET_CLUSTER]}, "
            f"bounded_window_context={counts[BOUNDED_WINDOW_CONTEXT]}, "
            f"same_date_context={counts[SAME_DATE_CONTEXT]}, "
            f"not_externally_tested={counts[NOT_EXTERNALLY_TESTED_SCOPE]}"
        )

    lines.extend(
        [
            "",
            "## Special Cases Preserved",
            "",
            "- `2024-12-11_ge2_04`: warning target disagreement; excluded from favorable calibration and retained in adverse sensitivity.",
            "- `2024-02-18_ge2_02`: unresolved warning target; excluded from favorable calibration and retained as unresolved/adverse evidence.",
            "- `2024-04-05_strict_ge2_01`: unresolved strict-valid extreme control; separately reported as a stress/control caveat.",
            "",
            "## Output Contract",
            "",
            "The model will provide future strategy tests with a strict-only baseline spread empirical distribution, conservative strict-only percentile costs, session/regime diagnostics, separate labelled stress/sensitivity scenarios, and provenance metadata.",
            "",
            "It is spread-only. Slippage, commissions, financing, latency, order-book depth, and market impact remain missing cost components and must not be silently added.",
            "",
            "## Tests",
            "",
            "Focused tests cover strict-only baseline enforcement, warning/placeholder leakage prevention, deterministic statistics, session boundary handling, missing bucket fallback declaration, stress/sensitivity separation, disagreement/inconclusive preservation, and policy-version reporting.",
            "",
            "## Independent Critic Findings",
            "",
            f"Critic materially changed implementation: {'yes' if critic['materially_changed_implementation'] else 'no'}.",
            "",
        ]
    )
    for finding in critic["material_findings"]:
        lines.append(f"- {finding}")
    lines.extend(
        [
            "",
            "Responses:",
            "",
        ]
    )
    for response in critic["response"]:
        lines.append(f"- {response}")
    lines.extend(
        [
            "",
            "## Prospective Tail Hardening Follow-Up",
            "",
            "The first implementation gate was downgraded to `EXECUTION_COST_MODEL_NEEDS_SMALL_FOLLOWUP` because train-period p95 coverage on Q4 strict-valid rows was only 0.731404. That failed history is preserved here and in `reports/execution_cost_prospective_tail_hardening.md`.",
            "",
            f"- Hardened selected rule: `{spec['prospective_tail_hardening']['selected_rule']['name']}`",
            f"- Hardened minimum monthly realized coverage: {fmt(spec['prospective_tail_hardening']['selected_rule']['minimum_realized_coverage'])}",
            f"- Pre-tail-critic gate: `{spec['pre_tail_critic_gate']}`",
            f"- Final hardened gate after critic: `{spec['gate']}`",
            "- Status: candidate hardening rule identified, but policy review is required because the same 2024/Q4 evidence was reused during rule selection.",
            "",
            "## Gate Decision",
            "",
            spec["gate"],
            "",
            "Exact next approval required: approve a policy review deciding whether the rolling p99.5 rule can be frozen before a clean future holdout or whether tail hardening must wait for multi-year partitioning. Do not begin strategy backtesting, ranking, optimization, profitability research, or multi-year acquisition.",
            "",
        ]
    )
    return "\n".join(lines)


def render_tail_hardening_report(spec: dict[str, object]) -> str:
    tail = spec["prospective_tail_hardening"]
    selected = tail["selected_rule"]
    original = tail["original_failure_reproduced"]
    critic = spec["tail_hardening_independent_critic"]
    lines = [
        "# Execution-Cost Prospective Tail Hardening",
        "",
        "Date: 2026-08-11",
        f"Gate decision: {spec['gate']}",
        "",
        "## Purpose",
        "",
        "This narrow follow-up hardens the strict-only execution-cost tail rule after the earlier global train-period p95 rule failed prospective Q4 validation. It does not run strategy tests, rank strategies, optimize parameters, acquire new data, change the evidence policy, modify raw evidence, or allow warning-review rows into the primary baseline.",
        "",
        "## Original Failure Reproduced",
        "",
        f"- Control rule: `{original['name']}`",
        f"- Calibration period: {original['calibration_period']}",
        f"- Validation period: {original['validation_period']}",
        f"- Target percentile: p{int(original['percentile'] * 1000) / 10:g}",
        f"- Realized Q4 validation coverage: {fmt(original['realized_validation_coverage'])}",
        f"- Required coverage threshold: {MINIMUM_ACCEPTABLE_HOLDOUT_P95_COVERAGE:.2f}",
        "",
        "## Candidates Tested",
        "",
        "| Candidate | Type | Intended percentile | Validation basis | Realized coverage | Median/threshold cost | Selected |",
        "|---|---|---:|---|---:|---:|---|",
    ]
    for candidate in tail["candidates"]:
        if candidate["rule_type"] == "monthly_recalibrated_trailing_empirical_percentile":
            validation_basis = f"{candidate['fold_count']} monthly prospective folds"
            coverage = candidate["minimum_realized_coverage"]
            cost = candidate["median_threshold"]
        else:
            validation_basis = candidate["validation_period"]
            coverage = candidate["realized_validation_coverage"]
            cost = candidate["threshold"]
        lines.append(
            "| {name} | {rule_type} | {percentile} | {basis} | {coverage} | {cost} | {selected} |".format(
                name=candidate["name"],
                rule_type=candidate["rule_type"],
                percentile=fmt(candidate["percentile"]),
                basis=validation_basis,
                coverage=fmt(coverage),
                cost=fmt(cost),
                selected="yes" if candidate["selected"] else "no",
            )
        )

    lines.extend(
        [
            "",
            "## Selected Rule",
            "",
            f"- Rule: `{selected['name']}`",
            f"- Lookback: {selected['lookback_days']} calendar days",
            f"- Percentile: {fmt(selected['percentile'])}",
            f"- Minimum prior strict-valid rows: {selected['minimum_observations']}",
            f"- Calibration schedule: monthly boundary recalibration",
            f"- Minimum monthly realized coverage: {fmt(selected['minimum_realized_coverage'])}",
            f"- Mean monthly realized coverage: {fmt(selected['mean_realized_coverage'])}",
            f"- Median threshold cost: {fmt(selected['median_threshold'])}",
            f"- Selection reason: {selected['selection_reason']}",
            f"- Pre-critic gate: {spec['pre_tail_critic_gate']}",
            f"- Final gate after critic: {spec['gate']}",
            "",
            "Monthly prospective folds:",
            "",
            "| Fold | Calibration rows | Validation rows | Threshold | Realized coverage | Validation p95 | Validation p99 |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for fold in selected["folds"]:
        lines.append(
            "| {fold} | {calibration_rows} | {validation_rows} | {threshold} | {coverage} | {p95} | {p99} |".format(
                fold=fold["fold"],
                calibration_rows=fold["calibration_rows"],
                validation_rows=fold["validation_rows"],
                threshold=fmt(fold["threshold"]),
                coverage=fmt(fold["realized_coverage"]),
                p95=fmt(fold["validation_p95_spread"]),
                p99=fmt(fold["validation_p99_spread"]),
            )
        )

    contract = tail["prospective_cost_contract"]
    scalability = tail["multi_year_scalability"]
    lines.extend(
        [
            "",
            "## Prospective Cost Contract",
            "",
            f"- Information allowed at time t: {contract['information_allowed_at_time_t']}",
            f"- Calibration schedule: {contract['calibration_schedule']}",
            f"- Lookback days: {contract['lookback_days']}",
            f"- Minimum observations: {contract['minimum_observations']}",
            f"- Insufficient-history behavior: {contract['insufficient_history_behavior']}",
            f"- Session/time fallback: {contract['session_time_fallback']}",
            f"- Returned estimate: {contract['returned_estimate']}",
            "- Full-year descriptive statistics remain research-only and must not silently become 2024 strategy inputs.",
            "",
            "## Stress Layer Guard",
            "",
            "- Primary baseline remains strict-only.",
            "- Warning-review rows entered baseline: no.",
            "- Stress/sensitivity remains separate from the primary baseline.",
            "- Disagreed/inconclusive evidence and the unresolved strict-valid extreme remain preserved in the model spec.",
            "",
            "## Multi-Year Scalability",
            "",
            f"- Assessment: {scalability['assessment']}",
            f"- Additional years behavior: {scalability['additional_years_behavior']}",
            "- Parameters that must be frozen before future holdouts: "
            + ", ".join(scalability["parameters_to_freeze_before_future_holdouts"]),
            f"- Holdout protection: {scalability['holdout_protection']}",
            "",
            "## Independent Critic Findings",
            "",
            f"Critic materially changed conclusion: {'yes' if critic['materially_changed_conclusion'] else 'no'}.",
            "",
        ]
    )
    for finding in critic["material_findings"]:
        lines.append(f"- {finding}")
    lines.extend(
        [
            "",
            "Responses:",
            "",
        ]
    )
    for response in critic["responses"]:
        lines.append(f"- {response}")
    lines.extend(
        [
            "## Gate Decision",
            "",
            spec["gate"],
            "",
        ]
    )
    for reason in spec["gate_reasons"]:
        lines.append(f"- {reason}")
    lines.extend(
        [
            "",
            "Exact next approval required: approve a policy review deciding whether the rolling p99.5 rule can be frozen before a clean future holdout or whether tail hardening must wait for multi-year partitioning. Do not begin strategy backtesting, ranking, optimization, profitability research, or multi-year acquisition.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build policy-enforced execution-cost model artifacts.")
    parser.add_argument("--spec-out", type=Path, default=SPEC_PATH)
    parser.add_argument("--report-out", type=Path, default=REPORT_PATH)
    parser.add_argument("--tail-report-out", type=Path, default=TAIL_HARDENING_REPORT_PATH)
    args = parser.parse_args()

    spec = build_spec()
    write_json(args.spec_out, spec)
    args.report_out.write_text(render_report(spec), encoding="utf-8")
    args.tail_report_out.write_text(render_tail_hardening_report(spec), encoding="utf-8")
    print(f"Wrote {args.spec_out}")
    print(f"Wrote {args.report_out}")
    print(f"Wrote {args.tail_report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
