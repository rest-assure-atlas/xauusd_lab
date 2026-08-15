"""Operational partition locks for bounded multi-year XAUUSD research.

This module implements policy checks only. It does not acquire data, inspect
future-holdout distributions, run execution-cost validation, or run strategies.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"
PARTITION_PLAN_PATH = REPORTS_DIR / "multi_year_research_partition_plan.json"
PARTITION_LOCK_PATH = REPORTS_DIR / "multi_year_partition_lock.json"
ACCESS_LOG_SCHEMA_PATH = REPORTS_DIR / "holdout_access_log_schema.json"
ACCESS_LOG_PATH = REPORTS_DIR / "holdout_access_log.csv"
IMPLEMENTATION_REPORT_PATH = REPORTS_DIR / "multi_year_partition_lock_implementation.md"

LOCK_VERSION = "multi_year_partition_lock:v1:2026-08-11"

ALLOWED = "ALLOWED"
TECHNICAL_METADATA_ONLY = "TECHNICAL_METADATA_ONLY"
REQUIRES_RELEASE_APPROVAL = "REQUIRES_RELEASE_APPROVAL"
PROHIBITED_PRE_RELEASE = "PROHIBITED_PRE_RELEASE"

CONSUMED_DEVELOPMENT = "CONSUMED_DEVELOPMENT"
EXPANSION_SHAKEDOWN = "EXPANSION_SHAKEDOWN"
EXECUTION_COST_CLEAN_VALIDATION = "EXECUTION_COST_CLEAN_VALIDATION"
FUTURE_STRATEGY_DEVELOPMENT = "FUTURE_STRATEGY_DEVELOPMENT"
FUTURE_WALK_FORWARD_VALIDATION = "FUTURE_WALK_FORWARD_VALIDATION"
FINAL_UNTOUCHED_HOLDOUT = "FINAL_UNTOUCHED_HOLDOUT"

FINAL_HOLDOUT_YEARS = ["2023", "2025"]
FALLBACK_FINAL_HOLDOUT_YEARS = ["2023", "2022", "2021"]

FINAL_HOLDOUT_ALLOWED_PRE_RELEASE_OPERATIONS = [
    "annual_requested_day_count",
    "annual_file_existence_status",
    "checksum_presence_status",
    "source_identity_status",
    "terminal_completion_status",
    "coarse_schema_validity_status",
]

FINAL_HOLDOUT_PROHIBITED_PRE_RELEASE_OPERATIONS = [
    "spread_summary",
    "spread_summaries",
    "quality_distribution",
    "quality_distributions",
    "per_day_row_count",
    "per_day_row_counts",
    "per_month_row_count",
    "per_month_row_counts",
    "descriptive_statistic",
    "descriptive_statistics",
    "chart",
    "charts",
    "anomaly_list",
    "anomaly_lists",
    "strategy_output",
    "strategy_outputs",
    "execution_cost_output",
    "execution_cost_outputs",
    "exploratory_inspection",
]

ACCESS_LOG_COLUMNS = [
    "access_id",
    "timestamp_utc",
    "requester",
    "mission_id",
    "partition_id",
    "year_or_range",
    "artifact_path",
    "requested_operation",
    "fields_or_operations_inspected",
    "distributional_content_inspected",
    "access_class",
    "decision",
    "approved_gate_or_work_order",
    "approval_reference",
    "reason",
    "artifacts_touched",
    "partition_clean_before_access",
    "partition_clean_after_access",
    "consumption_status_after_access",
    "holdout_status_before",
    "holdout_status_after",
    "holdout_status_consumed_or_changed",
]

OPERATION_ALIASES = {
    "row_count_annual": "annual_requested_day_count",
    "annual_row_count": "annual_requested_day_count",
    "file_exists": "annual_file_existence_status",
    "file_existence": "annual_file_existence_status",
    "checksum_status": "checksum_presence_status",
    "schema_report": "coarse_schema_validity_status",
    "schema_validity": "coarse_schema_validity_status",
    "quality_summary": "quality_distributions",
    "quality_distribution_summary": "quality_distributions",
    "spread_stats": "descriptive_statistics",
    "spread_statistics": "spread_summaries",
    "row_count_daily": "per_day_row_counts",
    "daily_row_count": "per_day_row_counts",
    "row_count_monthly": "per_month_row_counts",
    "monthly_row_count": "per_month_row_counts",
    "plot": "charts",
    "plots": "charts",
    "anomalies": "anomaly_lists",
    "strategy_result": "strategy_outputs",
    "backtest_output": "strategy_outputs",
    "execution_cost_result": "execution_cost_outputs",
}


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def frozen_execution_cost_candidate() -> dict[str, Any]:
    candidate = {
        "candidate_version": "execution_cost_tail_rule_v1_candidate",
        "label": "2024_developed_candidate_not_cleanly_validated",
        "lookback": "rolling_30_calendar_day",
        "lookback_days": 30,
        "recalibration_cadence": "monthly_boundary",
        "population": "active strict_valid_pair only",
        "percentile": 0.995,
        "minimum_prior_strict_valid_observations": 1000,
        "calibration_information_set": "prospective_only_rows_before_monthly_boundary",
        "warning_review_baseline_use": "PROHIBITED",
        "placeholder_use": "PROHIBITED",
        "insufficient_history_behavior": "return_unavailable_or_error_no_future_backfill",
        "policy_version": "post_corroboration_execution_cost_evidence_policy:2026-08-10",
    }
    candidate["reproducibility_id"] = canonical_hash(candidate)
    return candidate


def build_partition_lock(plan: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "2010": {
            "partition_id": "A2",
            "role": EXPANSION_SHAKEDOWN,
            "holdout_status": "not_strategy_holdout",
            "approved_use": "availability_provenance_pipeline_scale_check_only",
        },
        "2011": {
            "partition_id": "B",
            "role": EXECUTION_COST_CLEAN_VALIDATION,
            "holdout_status": "reserved_until_execution_cost_validation_release",
            "approved_use": "clean_validation_only_after_release",
        },
        "2012": {
            "partition_id": "B",
            "role": EXECUTION_COST_CLEAN_VALIDATION,
            "holdout_status": "reserved_until_execution_cost_validation_release",
            "approved_use": "clean_validation_only_after_release",
        },
        "2013": {
            "partition_id": "B",
            "role": EXECUTION_COST_CLEAN_VALIDATION,
            "holdout_status": "reserved_until_execution_cost_validation_release",
            "approved_use": "clean_validation_only_after_release",
        },
        "2014": {
            "partition_id": "B",
            "role": EXECUTION_COST_CLEAN_VALIDATION,
            "holdout_status": "reserved_until_execution_cost_validation_release",
            "approved_use": "clean_validation_only_after_release",
        },
        "2015": {
            "partition_id": "C",
            "role": FUTURE_STRATEGY_DEVELOPMENT,
            "holdout_status": "reserved_until_strategy_development_approval",
            "approved_use": "future_strategy_development_only_after_protocol_gate",
        },
        "2016": {
            "partition_id": "C",
            "role": FUTURE_STRATEGY_DEVELOPMENT,
            "holdout_status": "reserved_until_strategy_development_approval",
            "approved_use": "future_strategy_development_only_after_protocol_gate",
        },
        "2017": {
            "partition_id": "C",
            "role": FUTURE_STRATEGY_DEVELOPMENT,
            "holdout_status": "reserved_until_strategy_development_approval",
            "approved_use": "future_strategy_development_only_after_protocol_gate",
        },
        "2018": {
            "partition_id": "C",
            "role": FUTURE_STRATEGY_DEVELOPMENT,
            "holdout_status": "reserved_until_strategy_development_approval",
            "approved_use": "future_strategy_development_only_after_protocol_gate",
        },
        "2019": {
            "partition_id": "C",
            "role": FUTURE_STRATEGY_DEVELOPMENT,
            "holdout_status": "reserved_until_strategy_development_approval",
            "approved_use": "future_strategy_development_only_after_protocol_gate",
        },
        "2020": {
            "partition_id": "D",
            "role": FUTURE_WALK_FORWARD_VALIDATION,
            "holdout_status": "reserved_until_strategy_validation_approval",
            "approved_use": "future_walk_forward_validation_only_after_protocol_gate",
        },
        "2021": {
            "partition_id": "D",
            "role": FUTURE_WALK_FORWARD_VALIDATION,
            "holdout_status": "reserved_until_strategy_validation_approval",
            "approved_use": "future_walk_forward_validation_only_after_protocol_gate",
        },
        "2022": {
            "partition_id": "D",
            "role": FUTURE_WALK_FORWARD_VALIDATION,
            "holdout_status": "reserved_until_strategy_validation_approval",
            "approved_use": "future_walk_forward_validation_only_after_protocol_gate",
        },
        "2023": {
            "partition_id": "E",
            "role": FINAL_UNTOUCHED_HOLDOUT,
            "holdout_status": "untouched_until_final_release",
            "approved_use": "final_evaluation_only_after_explicit_release_gate",
        },
        "2024": {
            "partition_id": "A",
            "role": CONSUMED_DEVELOPMENT,
            "holdout_status": "consumed",
            "approved_use": "already_used_pipeline_corrob_execution_cost_development_tail_hardening",
            "never_pristine_holdout": True,
        },
        "2025": {
            "partition_id": "E",
            "role": FINAL_UNTOUCHED_HOLDOUT,
            "holdout_status": "untouched_until_final_release",
            "approved_use": "final_evaluation_only_after_explicit_release_gate",
        },
    }
    return {
        "artifact": "multi_year_partition_lock",
        "lock_version": LOCK_VERSION,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_partition_plan": "reports/multi_year_research_partition_plan.json",
        "source_plan_final_gate": plan.get("final_gate"),
        "mission_scope": "implementation_preparation_only_no_acquisition_no_validation_no_strategy_research",
        "partition_manifest": manifest,
        "fallback_rules": {
            "final_holdout_fallback_years_order": FALLBACK_FINAL_HOLDOUT_YEARS,
            "fallback_requires_recorded_substitution_reason": True,
            "fallback_must_not_be_used_silently": True,
        },
        "access_policy": {
            "classes": [
                ALLOWED,
                TECHNICAL_METADATA_ONLY,
                REQUIRES_RELEASE_APPROVAL,
                PROHIBITED_PRE_RELEASE,
            ],
            "final_holdout_allowed_pre_release_operations": FINAL_HOLDOUT_ALLOWED_PRE_RELEASE_OPERATIONS,
            "final_holdout_prohibited_pre_release_operations": FINAL_HOLDOUT_PROHIBITED_PRE_RELEASE_OPERATIONS,
            "final_holdout_release_required_for": [
                "execution_cost_outputs",
                "strategy_outputs",
                "descriptive_statistics",
                "charts",
                "exploratory_inspection",
            ],
            "non_final_reserved_distributional_access_requires_purpose_release": True,
        },
        "release_policy": {
            "automatic_release": "PROHIBITED",
            "explicit_human_approval_required": True,
            "release_event_required_fields": [
                "timestamp_utc",
                "year",
                "approval_reference",
                "release_purpose",
                "policy_model_or_strategy_version",
                "holdout_status_before",
                "holdout_status_after",
            ],
            "released_holdout_status": "released_for_approved_purpose_and_consumed_for_that_purpose",
            "release_events": [],
        },
        "frozen_execution_cost_candidate": frozen_execution_cost_candidate(),
        "strategy_protocol_placeholder": {
            "serious_strategy_discovery_status": "BLOCKED",
            "required_gate": "separate_strategy_research_protocol_gate",
            "allowed_before_gate": "mechanical_plumbing_or_test_fixture_only_after_separate_approval",
            "prohibited_before_gate": [
                "strategy_discovery",
                "strategy_backtesting",
                "strategy_ranking",
                "parameter_optimization",
                "profitability_claims",
            ],
        },
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_partition_lock(path: Path = PARTITION_LOCK_PATH) -> dict[str, Any]:
    return load_json(path)


def get_year_record(lock: dict[str, Any], year: int | str) -> dict[str, Any]:
    key = str(year)
    try:
        return lock["partition_manifest"][key]
    except KeyError as exc:
        raise ValueError(f"Year {key} is not in the approved partition manifest.") from exc


def classify_access(
    lock: dict[str, Any],
    year: int | str,
    requested_operation: str,
    *,
    approval_reference: str = "",
    release_approved: bool = False,
) -> dict[str, Any]:
    year_record = get_year_record(lock, year)
    operation = normalize_operation(requested_operation)
    role = year_record["role"]
    released = year_record.get("holdout_status", "").startswith("released_for_approved_purpose")

    if role == CONSUMED_DEVELOPMENT:
        if operation in {"treat_as_pristine_holdout", "final_holdout_release"}:
            return _decision(year_record, operation, PROHIBITED_PRE_RELEASE, False, "2024 is consumed development evidence.")
        return _decision(year_record, operation, ALLOWED, True, "Consumed development partition; not pristine holdout evidence.")

    if role == FINAL_UNTOUCHED_HOLDOUT and not released:
        if operation in FINAL_HOLDOUT_ALLOWED_PRE_RELEASE_OPERATIONS:
            return _decision(year_record, operation, TECHNICAL_METADATA_ONLY, True, "Permitted coarse technical metadata only.")
        if operation == "final_holdout_release":
            approved = bool(release_approved and approval_reference)
            return _decision(
                year_record,
                operation,
                REQUIRES_RELEASE_APPROVAL,
                approved,
                "Explicit human release approval required.",
            )
        return _decision(
            year_record,
            operation,
            PROHIBITED_PRE_RELEASE,
            False,
            "Final untouched holdout is locked before explicit release.",
        )

    if role in {
        EXECUTION_COST_CLEAN_VALIDATION,
        FUTURE_STRATEGY_DEVELOPMENT,
        FUTURE_WALK_FORWARD_VALIDATION,
    }:
        if operation in FINAL_HOLDOUT_ALLOWED_PRE_RELEASE_OPERATIONS:
            return _decision(year_record, operation, TECHNICAL_METADATA_ONLY, True, "Reserved partition technical metadata only.")
        if operation in FINAL_HOLDOUT_PROHIBITED_PRE_RELEASE_OPERATIONS:
            return _decision(
                year_record,
                operation,
                REQUIRES_RELEASE_APPROVAL,
                False,
                "Reserved partition requires purpose-specific release before distributional access.",
            )
        return _decision(year_record, operation, REQUIRES_RELEASE_APPROVAL, False, "Reserved partition requires approved purpose release.")

    return _decision(year_record, operation, ALLOWED, True, "Operation allowed by current partition role.")


def normalize_operation(operation: str) -> str:
    normalized = operation.strip().lower().replace("-", "_").replace(" ", "_")
    return OPERATION_ALIASES.get(normalized, normalized)


def _decision(
    year_record: dict[str, Any],
    operation: str,
    access_class: str,
    approved: bool,
    reason: str,
) -> dict[str, Any]:
    return {
        "partition_id": year_record["partition_id"],
        "role": year_record["role"],
        "requested_operation": operation,
        "access_class": access_class,
        "decision": "approved" if approved else "rejected",
        "approved": approved,
        "reason": reason,
        "holdout_status_before": year_record["holdout_status"],
        "holdout_status_after": year_record["holdout_status"],
        "holdout_status_consumed_or_changed": "no",
    }


def release_final_holdout(
    lock: dict[str, Any],
    year: int | str,
    *,
    approval_reference: str,
    release_purpose: str,
    policy_model_or_strategy_version: str,
    access_log_path: Path | None = None,
    requester: str = "",
    mission_id: str = "",
    access_id: str = "",
    artifact_path: str = "",
    timestamp_utc: str | None = None,
) -> dict[str, Any]:
    if not approval_reference:
        raise ValueError("Final holdout release requires an explicit approval reference.")
    if not release_purpose:
        raise ValueError("Final holdout release requires a release purpose.")
    if not policy_model_or_strategy_version:
        raise ValueError("Final holdout release requires a policy/model/strategy version.")

    updated = deepcopy(lock)
    year_key = str(year)
    year_record = get_year_record(updated, year_key)
    if year_record["role"] != FINAL_UNTOUCHED_HOLDOUT:
        raise ValueError(f"Year {year_key} is not a final untouched holdout.")

    before = year_record["holdout_status"]
    after = "released_for_approved_purpose_and_consumed_for_that_purpose"
    year_record["holdout_status"] = after
    year_record["release_purpose"] = release_purpose
    year_record["released_policy_model_or_strategy_version"] = policy_model_or_strategy_version
    timestamp = timestamp_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    event = {
        "timestamp_utc": timestamp,
        "year": year_key,
        "partition_id": year_record["partition_id"],
        "approval_reference": approval_reference,
        "release_purpose": release_purpose,
        "policy_model_or_strategy_version": policy_model_or_strategy_version,
        "holdout_status_before": before,
        "holdout_status_after": after,
    }
    updated["release_policy"]["release_events"].append(event)
    if access_log_path is not None:
        if not requester or not mission_id or not access_id:
            raise ValueError("Access-log release recording requires requester, mission_id, and access_id.")
        append_access_log(
            access_log_path,
            {
                "access_id": access_id,
                "timestamp_utc": timestamp,
                "requester": requester,
                "mission_id": mission_id,
                "partition_id": year_record["partition_id"],
                "year_or_range": year_key,
                "artifact_path": artifact_path,
                "requested_operation": "final_holdout_release",
                "fields_or_operations_inspected": "release_metadata_only",
                "distributional_content_inspected": "no",
                "access_class": REQUIRES_RELEASE_APPROVAL,
                "decision": "approved",
                "approved_gate_or_work_order": approval_reference,
                "approval_reference": approval_reference,
                "reason": release_purpose,
                "artifacts_touched": artifact_path,
                "partition_clean_before_access": "yes",
                "partition_clean_after_access": "no",
                "consumption_status_after_access": "released_for_approved_purpose",
                "holdout_status_before": before,
                "holdout_status_after": after,
                "holdout_status_consumed_or_changed": "yes",
            },
        )
    return updated


def ensure_access_log(path: Path = ACCESS_LOG_PATH) -> None:
    if path.exists() and path.stat().st_size > 0:
        with path.open("r", newline="", encoding="utf-8") as handle:
            header = next(csv.reader(handle), [])
        if header == ACCESS_LOG_COLUMNS:
            return
        existing_rows = list(csv.DictReader(path.open("r", newline="", encoding="utf-8")))
        if existing_rows:
            raise ValueError(f"Refusing to rewrite non-empty access log with incompatible header: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerow(ACCESS_LOG_COLUMNS)


def append_access_log(path: Path, event: dict[str, Any]) -> None:
    ensure_access_log(path)
    row = {column: str(event.get(column, "")) for column in ACCESS_LOG_COLUMNS}
    with path.open("a", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=ACCESS_LOG_COLUMNS).writerow(row)


def access_event_from_decision(
    *,
    access_id: str,
    timestamp_utc: str,
    requester: str,
    mission_id: str,
    year_or_range: str,
    decision: dict[str, Any],
    approval_reference: str = "",
    approved_gate_or_work_order: str = "",
    fields_or_operations_inspected: str = "",
    distributional_content_inspected: str = "no",
    partition_clean_before_access: str = "",
    partition_clean_after_access: str = "",
    consumption_status_after_access: str = "",
    artifact_path: str = "",
    artifacts_touched: str = "",
) -> dict[str, Any]:
    return {
        "access_id": access_id,
        "timestamp_utc": timestamp_utc,
        "requester": requester,
        "mission_id": mission_id,
        "partition_id": decision["partition_id"],
        "year_or_range": year_or_range,
        "artifact_path": artifact_path or artifacts_touched,
        "requested_operation": decision["requested_operation"],
        "fields_or_operations_inspected": fields_or_operations_inspected or decision["requested_operation"],
        "distributional_content_inspected": distributional_content_inspected,
        "access_class": decision["access_class"],
        "decision": decision["decision"],
        "approved_gate_or_work_order": approved_gate_or_work_order or approval_reference,
        "approval_reference": approval_reference,
        "reason": decision["reason"],
        "artifacts_touched": artifacts_touched,
        "partition_clean_before_access": partition_clean_before_access,
        "partition_clean_after_access": partition_clean_after_access,
        "consumption_status_after_access": consumption_status_after_access,
        "holdout_status_before": decision["holdout_status_before"],
        "holdout_status_after": decision["holdout_status_after"],
        "holdout_status_consumed_or_changed": decision["holdout_status_consumed_or_changed"],
    }


def write_access_log_schema(path: Path = ACCESS_LOG_SCHEMA_PATH) -> None:
    schema = {
        "artifact": "holdout_access_log_schema",
        "date": "2026-08-11",
        "status": "operational_for_partition_lock_v1",
        "csv_path": "reports/holdout_access_log.csv",
        "columns": ACCESS_LOG_COLUMNS,
        "required_fields": ACCESS_LOG_COLUMNS,
        "approved_minimum_fields_preserved": [
            "fields_or_operations_inspected",
            "distributional_content_inspected",
            "approved_gate_or_work_order",
            "partition_clean_before_access",
            "partition_clean_after_access",
            "consumption_status_after_access",
        ],
        "allowed_access_classes": [
            ALLOWED,
            TECHNICAL_METADATA_ONLY,
            REQUIRES_RELEASE_APPROVAL,
            PROHIBITED_PRE_RELEASE,
        ],
        "allowed_decisions": ["approved", "rejected"],
        "final_holdout_pre_release_distributional_access": "PROHIBITED",
        "final_holdout_pre_release_allowed_operations": FINAL_HOLDOUT_ALLOWED_PRE_RELEASE_OPERATIONS,
        "final_holdout_pre_release_prohibited_operations": FINAL_HOLDOUT_PROHIBITED_PRE_RELEASE_OPERATIONS,
        "fake_historical_entries_populated": False,
    }
    path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(lock: dict[str, Any], path: Path = IMPLEMENTATION_REPORT_PATH) -> None:
    candidate = lock["frozen_execution_cost_candidate"]
    report = f"""# Multi-Year Partition Lock Implementation

Date: 2026-08-11
Status: partition-lock/access-log preparation complete
Preserved prior gate: READY_FOR_PARTITION_LOCK_AND_ACCESS_LOG_PREPARATION_ONLY
Implementation readiness result: READY_FOR_BOUNDED_MULTIYEAR_ACQUISITION pending separate explicit acquisition approval

## Scope

This implementation only operationalizes the approved multi-year partition plan.
It did not acquire market data, inspect future-holdout distributions, run
execution-cost validation on new years, run strategy research, alter raw
evidence, or change the approved partition roles.

## Partition Manifest

- 2024: `CONSUMED_DEVELOPMENT`
- 2010: `EXPANSION_SHAKEDOWN`
- 2011-2014: `EXECUTION_COST_CLEAN_VALIDATION`
- 2015-2019: `FUTURE_STRATEGY_DEVELOPMENT`
- 2020-2022: `FUTURE_WALK_FORWARD_VALIDATION`
- 2023: `FINAL_UNTOUCHED_HOLDOUT`
- 2025: `FINAL_UNTOUCHED_HOLDOUT`

Fallback final holdout order is preserved as: 2023, 2022, 2021. Fallback use
requires a recorded substitution reason and must not occur silently.

## Access Policy

The helper module `partition_lock.py` classifies access requests as
`ALLOWED`, `TECHNICAL_METADATA_ONLY`, `REQUIRES_RELEASE_APPROVAL`, or
`PROHIBITED_PRE_RELEASE`.

Final untouched holdouts remain locked before release. Pre-release access allows
only the coarse technical metadata already approved by policy:

- annual requested-day count
- annual file-existence status
- checksum presence/status
- source identity status
- terminal completion status
- coarse schema-validity status

Pre-release final-holdout access rejects spread summaries, quality
distributions, per-day/per-month row counts, descriptive statistics, charts,
anomaly lists, strategy outputs, execution-cost outputs, and exploratory
inspection.

## Access Log

`reports/holdout_access_log.csv` now has the operational v1 header. No fake
historical entries were added. The helper can append access attempts with
timestamp, requester, mission ID, partition/year, artifact path, requested
operation, fields/operations inspected, distributional-content flag, access
class, approval/rejection, approved gate/work order, approval reference, reason,
artifacts touched, partition clean before/after, consumption status after
access, and holdout status before/after.

## Release Rule

Final holdouts cannot be released automatically. A release requires an explicit
human approval reference, purpose, and policy/model/strategy version. Release
events are recorded in the lock artifact and, when an access-log path is
provided, durably appended to the CSV log with no distributional inspection.
The release marks the holdout consumed for that approved purpose.

## Frozen Execution-Cost Candidate

Candidate: `{candidate["candidate_version"]}`

- rolling 30-calendar-day lookback
- monthly recalibration
- active `strict_valid_pair` only
- p99.5
- minimum 1,000 prior strict-valid observations
- prospective-only information set
- no warning-review baseline use
- reproducibility identifier: `{candidate["reproducibility_id"]}`

The candidate was recorded exactly as a frozen candidate for future clean
multi-year validation. It was not retuned.

## Strategy Protocol Placeholder

Serious strategy discovery remains `BLOCKED` until a separate
strategy-research protocol gate exists. This implementation does not design,
test, rank, or optimize strategies.

## Independent Critic Outcome

The read-only critic found material issues in the first implementation:
gate wording could be read as acquisition permission, the access log omitted
approved leakage-control fields, final-holdout releases were not durably
access-logged by the helper, and operation labels needed basic normalization.
The implementation was tightened before final reporting.

## Final Gate

`READY_FOR_BOUNDED_MULTIYEAR_ACQUISITION`

This gate permits only a later, separately approved bounded acquisition mission.
It does not itself authorize acquisition.
"""
    path.write_text(report, encoding="utf-8")


def write_artifacts() -> dict[str, Any]:
    plan = load_json(PARTITION_PLAN_PATH)
    lock = build_partition_lock(plan)
    PARTITION_LOCK_PATH.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_access_log_schema()
    ensure_access_log()
    write_report(lock)
    return lock


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage XAUUSD multi-year partition locks.")
    parser.add_argument("--write-artifacts", action="store_true", help="Write lock JSON, access-log schema/header, and report.")
    args = parser.parse_args()
    if args.write_artifacts:
        write_artifacts()
    else:
        parser.error("No action requested.")


if __name__ == "__main__":
    main()
