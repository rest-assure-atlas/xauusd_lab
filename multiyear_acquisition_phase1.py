"""Bounded 2010-2014 BID/ASK acquisition orchestration.

This module wraps the existing Dukascopy downloader, provenance, quality, and
reconciliation tools. It intentionally does not run execution-cost validation or
strategy research.
"""

from __future__ import annotations

import csv
import json
import time
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import bid_ask_reconciliation
import data_downloader
import data_manifest
import linked_observation_report
from source_contracts import ASK, BID, SourceContract


PROJECT_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = PROJECT_DIR / "data_raw"
REPORTS_DIR = PROJECT_DIR / "reports"
PARTITION_LOCK_PATH = REPORTS_DIR / "multi_year_partition_lock.json"
PARTITION_PLAN_PATH = REPORTS_DIR / "multi_year_research_partition_plan.json"
CHECKPOINT_PATH = REPORTS_DIR / "multiyear_acquisition_phase1_checkpoint.json"
SUMMARY_PATH = REPORTS_DIR / "multiyear_acquisition_phase1_2010_2014_summary.json"
REPORT_PATH = REPORTS_DIR / "multiyear_acquisition_phase1_2010_2014.md"

MISSION_ID = "MULTI_YEAR_ACQUISITION_PHASE1_2010_2014"
TARGET_YEARS = [2010, 2011, 2012, 2013, 2014]
FINAL_HOLDOUT_YEARS = {2023, 2025}
MAX_SIDE_PASSES = 3
ROLE_BY_YEAR = {
    2010: "EXPANSION_SHAKEDOWN",
    2011: "EXECUTION_COST_CLEAN_VALIDATION",
    2012: "EXECUTION_COST_CLEAN_VALIDATION",
    2013: "EXECUTION_COST_CLEAN_VALIDATION",
    2014: "EXECUTION_COST_CLEAN_VALIDATION",
}


@dataclass(frozen=True)
class YearRange:
    year: int
    start_day: date
    end_day: date


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(path)


def year_range(year: int) -> YearRange:
    if year in FINAL_HOLDOUT_YEARS:
        raise ValueError(f"Final holdout year {year} is outside this mission.")
    if year not in TARGET_YEARS:
        raise ValueError(f"Year {year} is outside phase 1 scope.")
    return YearRange(year=year, start_day=date(year, 1, 1), end_day=date(year, 12, 31))


def load_checkpoint() -> dict[str, Any]:
    if CHECKPOINT_PATH.exists():
        return read_json(CHECKPOINT_PATH)
    return {
        "artifact": "multiyear_acquisition_phase1_checkpoint",
        "mission_id": MISSION_ID,
        "created_utc": utc_now(),
        "updated_utc": utc_now(),
        "current_year": 2010,
        "completed_years": [],
        "years": {},
        "exact_next_operation": "acquire_2010_bid",
        "last_successful_checkpoint": "",
    }


def save_checkpoint(checkpoint: dict[str, Any], next_operation: str) -> None:
    checkpoint["updated_utc"] = utc_now()
    checkpoint["exact_next_operation"] = next_operation
    checkpoint["last_successful_checkpoint"] = next_operation
    write_json(CHECKPOINT_PATH, checkpoint)


def enforce_partition_policy() -> None:
    lock = read_json(PARTITION_LOCK_PATH)
    plan = read_json(PARTITION_PLAN_PATH)
    manifest = lock.get("partition_manifest", {})
    for year, role in ROLE_BY_YEAR.items():
        actual = manifest.get(str(year), {}).get("role")
        if actual != role:
            raise RuntimeError(f"Partition role mismatch for {year}: {actual!r} != {role!r}")
    for year in FINAL_HOLDOUT_YEARS:
        actual = manifest.get(str(year), {}).get("role")
        if actual != "FINAL_UNTOUCHED_HOLDOUT":
            raise RuntimeError(f"Final holdout role mismatch for {year}: {actual!r}")
    if plan.get("execution_cost_candidate_freeze_decision") != "FROZEN_WITH_SMALL_PREDECLARED_CLARIFICATIONS":
        raise RuntimeError("Frozen execution-cost candidate policy was not found.")


def set_downloader_side(side: str) -> None:
    data_downloader.SYMBOL = "XAUUSD"
    data_downloader.PRICE_SIDE = side
    data_downloader.TIMEFRAME = "min_1"


def acquire_side(
    range_: YearRange,
    side: str,
    checkpoint: dict[str, Any],
    year_record: dict[str, Any],
) -> dict[str, Any]:
    set_downloader_side(side)
    started = time.monotonic()
    all_days = list(data_downloader.each_day(range_.start_day, range_.end_day))
    attempted = successful_downloads = skipped_existing = failed_attempts = 0
    retry_passes = 0
    for pass_number in range(1, MAX_SIDE_PASSES + 1):
        retry_passes = pass_number - 1
        days_to_process = [
            day for day in all_days if not data_downloader.build_output_path(day).exists()
        ]
        if not days_to_process:
            break
        for index, day in enumerate(days_to_process, start=1):
            output_path = data_downloader.build_output_path(day)
            existed = output_path.exists()
            attempted += 1
            ok = data_downloader.download_one_day(day)
            if ok and not existed:
                successful_downloads += 1
            elif ok and existed:
                skipped_existing += 1
            else:
                failed_attempts += 1
            completed_files = sum(1 for completed_day in all_days if data_downloader.build_output_path(completed_day).exists())
            if index % 25 == 0 or day == days_to_process[-1] or not ok:
                missing_days = [
                    f"{missing_day:%Y-%m-%d}"
                    for missing_day in all_days
                    if not data_downloader.build_output_path(missing_day).exists()
                ]
                year_record["acquisition_progress"] = {
                    "side": side,
                    "pass_number": pass_number,
                    "retry_passes": retry_passes,
                    "last_attempted_day": f"{day:%Y-%m-%d}",
                    "attempted_days": attempted,
                    "completed_files": completed_files,
                    "successful_downloads": successful_downloads,
                    "skipped_existing_days": skipped_existing,
                    "failed_attempts": failed_attempts,
                    "remaining_missing_days": missing_days,
                }
                save_checkpoint(checkpoint, f"acquire_{range_.year}_{side.lower()}_through_{day:%Y-%m-%d}")
    completed_files = sum(1 for day in all_days if data_downloader.build_output_path(day).exists())
    missing_days = [
        f"{day:%Y-%m-%d}"
        for day in all_days
        if not data_downloader.build_output_path(day).exists()
    ]
    skipped_existing = completed_files - successful_downloads
    year_record["acquisition_progress"] = {
        "side": side,
        "retry_passes": retry_passes,
        "attempted_days": attempted,
        "completed_files": completed_files,
        "successful_downloads": successful_downloads,
        "skipped_existing_days": skipped_existing,
        "failed_attempts": failed_attempts,
        "remaining_missing_days": missing_days,
    }
    save_checkpoint(checkpoint, f"acquire_{range_.year}_{side.lower()}_complete")
    return {
        "side": side,
        "successful_or_skipped_days": completed_files,
        "skipped_existing_days": skipped_existing,
        "successful_downloads": successful_downloads,
        "failed_days": len(missing_days),
        "failed_attempts": failed_attempts,
        "retry_count": retry_passes,
        "remaining_missing_days": missing_days,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def create_side_artifacts(range_: YearRange, side: str) -> dict[str, Any]:
    contract = SourceContract(quote_side=side)
    legacy = side == BID
    manifest_summary = data_manifest.create_data_manifest(
        range_.start_day,
        range_.end_day,
        DATA_RAW_DIR,
        contract,
        legacy_side_omitted=legacy,
    )
    linked_summary = linked_observation_report.create_linked_observation_report(
        range_.start_day,
        range_.end_day,
        DATA_RAW_DIR,
        contract,
        legacy_side_omitted=legacy,
    )
    return {
        "manifest_path": str(manifest_summary.output_path.relative_to(PROJECT_DIR)),
        "linked_path": str(linked_summary.output_path.relative_to(PROJECT_DIR)),
        "manifest": {
            "requested_dates": manifest_summary.requested_dates,
            "processed_files": manifest_summary.processed_files,
            "missing_files": manifest_summary.missing_files,
            "empty_files": manifest_summary.empty_files,
            "parse_failures": manifest_summary.parse_failures,
            "no_active_candle_files": manifest_summary.no_active_candle_files,
            "valid_dates": manifest_summary.valid_dates,
            "warning_dates": manifest_summary.warning_dates,
            "invalid_dates": manifest_summary.invalid_dates,
            "not_assessed_dates": manifest_summary.not_assessed_dates,
        },
        "linked": {
            "requested_dates": linked_summary.requested_dates,
            "strict_valid_observations": linked_summary.strict_valid_observations,
            "warning_review_observations": linked_summary.warning_review_observations,
            "excluded_unusable_observations": linked_summary.excluded_unusable_observations,
            "calendar_only_observations": linked_summary.calendar_only_observations,
        },
    }


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def directory_size_for_year(year: int) -> int:
    total = 0
    for side in (BID, ASK):
        pattern = f"XAUUSD_{year}-*_1min_{side}_UTC.csv"
        total += sum(path.stat().st_size for path in DATA_RAW_DIR.glob(pattern))
    return total


def report_size(paths: list[str]) -> int:
    total = 0
    for path_text in paths:
        path = PROJECT_DIR / path_text
        if path.exists():
            total += path.stat().st_size
    return total


def analyze_reconciliation(path: Path) -> dict[str, Any]:
    status_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    dates: set[str] = set()
    timestamp_keys: set[tuple[str, str]] = set()
    duplicate_timestamp_rows = 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            status_counts[row.get("pair_quality_status", "")] += 1
            dates.add(row.get("date", ""))
            key = (row.get("date", ""), row.get("timestamp_utc", ""))
            if key in timestamp_keys:
                duplicate_timestamp_rows += 1
            timestamp_keys.add(key)
            for reason in row.get("pair_quality_reasons", "").split(";"):
                if reason:
                    reason_counts[reason] += 1
    return {
        "rows": sum(status_counts.values()),
        "date_count": len(dates),
        "pair_status_counts": dict(status_counts),
        "reason_counts": dict(reason_counts),
        "duplicate_output_timestamp_rows": duplicate_timestamp_rows,
    }


def validate_year(range_: YearRange, side_artifacts: dict[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    bid_linked = PROJECT_DIR / side_artifacts[BID]["linked_path"]
    ask_linked = PROJECT_DIR / side_artifacts[ASK]["linked_path"]
    reconciliation_summary = bid_ask_reconciliation.create_reconciliation(
        range_.start_day,
        range_.end_day,
        DATA_RAW_DIR,
        bid_linked,
        ask_linked,
    )
    reconciliation_path = reconciliation_summary.output_path
    reconciliation_analysis = analyze_reconciliation(reconciliation_path)
    expected_dates = (range_.end_day - range_.start_day).days + 1
    validation = {
        "calendar_dates_expected": expected_dates,
        "calendar_dates_in_reconciliation": reconciliation_analysis["date_count"],
        "raw_bid_files": len(list(DATA_RAW_DIR.glob(f"XAUUSD_{range_.year}-*_1min_BID_UTC.csv"))),
        "raw_ask_files": len(list(DATA_RAW_DIR.glob(f"XAUUSD_{range_.year}-*_1min_ASK_UTC.csv"))),
        "bid_manifest_processed": side_artifacts[BID]["manifest"]["processed_files"],
        "ask_manifest_processed": side_artifacts[ASK]["manifest"]["processed_files"],
        "bid_not_assessed_dates": side_artifacts[BID]["manifest"]["not_assessed_dates"],
        "ask_not_assessed_dates": side_artifacts[ASK]["manifest"]["not_assessed_dates"],
        "bid_missing_files": side_artifacts[BID]["manifest"]["missing_files"],
        "ask_missing_files": side_artifacts[ASK]["manifest"]["missing_files"],
        "reconciliation_path": str(reconciliation_path.relative_to(PROJECT_DIR)),
        "reconciliation": {
            "total_bid_rows": reconciliation_summary.total_bid_rows,
            "total_ask_rows": reconciliation_summary.total_ask_rows,
            "exact_timestamp_matches": reconciliation_summary.exact_timestamp_matches,
            "missing_bid_rows": reconciliation_summary.missing_bid_rows,
            "missing_ask_rows": reconciliation_summary.missing_ask_rows,
            "duplicate_bid_timestamps": reconciliation_summary.duplicate_bid_timestamps,
            "duplicate_ask_timestamps": reconciliation_summary.duplicate_ask_timestamps,
            "negative_spreads": reconciliation_summary.negative_spreads,
            "zero_spreads": reconciliation_summary.zero_spreads,
            "extreme_spreads": reconciliation_summary.extreme_spreads,
            "warning_review_pairs": reconciliation_summary.warning_review_pairs,
            "excluded_or_invalid_rows": reconciliation_summary.excluded_or_invalid_rows,
            "pair_status_counts": reconciliation_summary.pair_status_counts,
            "reason_counts": reconciliation_analysis["reason_counts"],
            "duplicate_output_timestamp_rows": reconciliation_analysis["duplicate_output_timestamp_rows"],
        },
        "validation_duration_seconds": round(time.monotonic() - started, 3),
    }
    validation["status"] = "pass" if year_integrity_passes(validation) else "followup_required"
    return validation


def year_integrity_passes(validation: dict[str, Any]) -> bool:
    expected = validation["calendar_dates_expected"]
    if validation["raw_bid_files"] != expected or validation["raw_ask_files"] != expected:
        return False
    bid_assessed_or_calendar = validation["bid_manifest_processed"] + side_artifacts_count(validation, "bid")
    ask_assessed_or_calendar = validation["ask_manifest_processed"] + side_artifacts_count(validation, "ask")
    if bid_assessed_or_calendar != expected or ask_assessed_or_calendar != expected:
        return False
    if validation["bid_missing_files"] or validation["ask_missing_files"]:
        return False
    reconciliation = validation["reconciliation"]
    if reconciliation["missing_bid_rows"] or reconciliation["missing_ask_rows"]:
        return False
    if reconciliation["duplicate_bid_timestamps"] or reconciliation["duplicate_ask_timestamps"]:
        return False
    if reconciliation["negative_spreads"]:
        return False
    if validation["calendar_dates_in_reconciliation"] != expected:
        return False
    return True


def side_artifacts_count(validation: dict[str, Any], side_prefix: str) -> int:
    """Count calendar-only/no-active files already accounted for by manifest."""
    return validation.get(f"{side_prefix}_not_assessed_dates", 0)


def process_year(year: int, checkpoint: dict[str, Any]) -> dict[str, Any]:
    range_ = year_range(year)
    year_record = checkpoint.setdefault("years", {}).setdefault(str(year), {"year": year, "role": ROLE_BY_YEAR[year]})
    year_record["started_utc"] = year_record.get("started_utc") or utc_now()
    checkpoint["current_year"] = year
    save_checkpoint(checkpoint, f"acquire_{year}_bid")

    acquisition: dict[str, Any] = year_record.setdefault("acquisition", {})
    if acquisition.get(BID, {}).get("failed_days") is None or acquisition.get(BID, {}).get("failed_days"):
        acquisition[BID] = acquire_side(range_, BID, checkpoint, year_record)
        save_checkpoint(checkpoint, f"acquire_{year}_ask")
    if acquisition.get(ASK, {}).get("failed_days") is None or acquisition.get(ASK, {}).get("failed_days"):
        acquisition[ASK] = acquire_side(range_, ASK, checkpoint, year_record)
        save_checkpoint(checkpoint, f"build_{year}_provenance")
    if acquisition[BID]["failed_days"] or acquisition[ASK]["failed_days"]:
        year_record["gate"] = "source_availability_block"
        save_checkpoint(checkpoint, f"stop_after_{year}_source_availability_block")
        return year_record

    side_artifacts = year_record.setdefault("side_artifacts", {})
    for side in (BID, ASK):
        if side not in side_artifacts:
            side_artifacts[side] = create_side_artifacts(range_, side)
            save_checkpoint(checkpoint, f"build_{year}_{side.lower()}_provenance")

    if "validation" not in year_record:
        year_record["validation"] = validate_year(range_, side_artifacts)
        artifact_paths = [
            side_artifacts[BID]["manifest_path"],
            side_artifacts[BID]["linked_path"],
            side_artifacts[ASK]["manifest_path"],
            side_artifacts[ASK]["linked_path"],
            year_record["validation"]["reconciliation_path"],
        ]
        year_record["artifact_paths"] = artifact_paths
        year_record["storage"] = {
            "raw_size_bytes": directory_size_for_year(year),
            "processed_report_size_bytes": report_size(artifact_paths),
            "acquisition_duration_seconds": round(
                acquisition[BID]["duration_seconds"] + acquisition[ASK]["duration_seconds"],
                3,
            ),
            "validation_duration_seconds": year_record["validation"]["validation_duration_seconds"],
        }
        year_record["completed_utc"] = utc_now()
        year_record["gate"] = "pass" if year_record["validation"]["status"] == "pass" else "data_integrity_followup"
        save_checkpoint(checkpoint, f"completed_{year}")

    if year_record["gate"] == "pass" and year not in checkpoint["completed_years"]:
        checkpoint["completed_years"].append(year)
        save_checkpoint(checkpoint, f"completed_{year}")
    return year_record


def annual_summary_from_checkpoint(checkpoint: dict[str, Any]) -> dict[str, Any]:
    years = checkpoint.get("years", {})
    completed_years = checkpoint.get("completed_years", [])
    return {
        "artifact": "multiyear_acquisition_phase1_2010_2014_summary",
        "created_utc": utc_now(),
        "mission_id": MISSION_ID,
        "completed_years": completed_years,
        "years": years,
        "execution_cost_candidate_validation_run": False,
        "strategy_research_run": False,
        "final_holdouts_accessed": False,
    }


def write_markdown_report(summary: dict[str, Any], gate: str, critic_notes: dict[str, Any] | None = None) -> None:
    years = summary["years"]
    lines = [
        "# Multi-Year Acquisition Phase 1: 2010-2014",
        "",
        f"- Mission: `{MISSION_ID}`",
        f"- Final gate: `{gate}`",
        "- Execution-cost candidate validation run: no",
        "- Strategy research run: no",
        "- Final holdouts accessed: no",
        "",
        "## Annual Evidence",
        "",
    ]
    for year in TARGET_YEARS:
        record = years.get(str(year), {})
        validation = record.get("validation", {})
        reconciliation = validation.get("reconciliation", {})
        storage = record.get("storage", {})
        acquisition = record.get("acquisition", {})
        bid_acquisition = acquisition.get(BID, {})
        ask_acquisition = acquisition.get(ASK, {})
        bid_files = validation.get("raw_bid_files", bid_acquisition.get("successful_or_skipped_days", ""))
        ask_files = validation.get("raw_ask_files", ask_acquisition.get("successful_or_skipped_days", ""))
        lines.extend(
            [
                f"### {year} - {ROLE_BY_YEAR[year]}",
                "",
                f"- Gate: `{record.get('gate', 'not_completed')}`",
                f"- BID files: {bid_files}",
                f"- ASK files: {ask_files}",
                f"- Exact timestamp matches: {reconciliation.get('exact_timestamp_matches', '')}",
                f"- Missing BID rows: {reconciliation.get('missing_bid_rows', '')}",
                f"- Missing ASK rows: {reconciliation.get('missing_ask_rows', '')}",
                f"- Duplicate BID timestamps: {reconciliation.get('duplicate_bid_timestamps', '')}",
                f"- Duplicate ASK timestamps: {reconciliation.get('duplicate_ask_timestamps', '')}",
                f"- Negative spreads: {reconciliation.get('negative_spreads', '')}",
                f"- Zero spreads: {reconciliation.get('zero_spreads', '')}",
                f"- Warning-review pairs: {reconciliation.get('warning_review_pairs', '')}",
                f"- Pair quality counts: `{json.dumps(reconciliation.get('pair_status_counts', {}), sort_keys=True)}`",
                f"- Raw size bytes: {storage.get('raw_size_bytes', '')}",
                f"- Processed report size bytes: {storage.get('processed_report_size_bytes', '')}",
                f"- Acquisition duration seconds: {storage.get('acquisition_duration_seconds', '')}",
                f"- Validation duration seconds: {storage.get('validation_duration_seconds', '')}",
                "",
            ]
        )
    if critic_notes:
        lines.extend(["## Independent Review", ""])
        for key, value in critic_notes.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def determine_gate(checkpoint: dict[str, Any]) -> str:
    years = checkpoint.get("years", {})
    if "2010" not in years:
        return "MULTIYEAR_ACQUISITION_NEEDS_SMALL_FOLLOWUP"
    if years["2010"].get("gate") == "source_availability_block":
        return "MULTIYEAR_SOURCE_AVAILABILITY_BLOCK"
    if years["2010"].get("gate") != "pass":
        return "MULTIYEAR_ACQUISITION_DATA_INTEGRITY_BLOCK"
    if set(checkpoint.get("completed_years", [])) != set(TARGET_YEARS):
        return "MULTIYEAR_ACQUISITION_NEEDS_SMALL_FOLLOWUP"
    if any(years[str(year)].get("gate") != "pass" for year in TARGET_YEARS):
        return "MULTIYEAR_ACQUISITION_DATA_INTEGRITY_BLOCK"
    return "READY_FOR_CLEAN_EXECUTION_COST_VALIDATION_2011_2014"


def main() -> int:
    enforce_partition_policy()
    checkpoint = load_checkpoint()
    for year in TARGET_YEARS:
        if year in checkpoint.get("completed_years", []):
            continue
        record = process_year(year, checkpoint)
        if year == 2010 and record.get("gate") != "pass":
            break
        if record.get("gate") != "pass":
            break
    gate = determine_gate(checkpoint)
    summary = annual_summary_from_checkpoint(checkpoint)
    write_json(SUMMARY_PATH, summary)
    write_markdown_report(summary, gate)
    save_checkpoint(checkpoint, f"final_gate_{gate}")
    print(json.dumps({"gate": gate, "summary_path": str(SUMMARY_PATH), "report_path": str(REPORT_PATH)}, indent=2))
    return 0 if gate in {
        "READY_FOR_CLEAN_EXECUTION_COST_VALIDATION_2011_2014",
        "MULTIYEAR_ACQUISITION_NEEDS_SMALL_FOLLOWUP",
        "MULTIYEAR_ACQUISITION_DATA_INTEGRITY_BLOCK",
        "MULTIYEAR_SOURCE_AVAILABILITY_BLOCK",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
