"""Create a side-aware BID/ASK reconciliation artifact for XAU/USD CSV files."""

from __future__ import annotations

import csv
import hashlib
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

import data_manifest
import data_quality
from candle_filters import is_flat_zero_volume_candle
from source_contracts import ASK, BID, INSTRUMENT, PROVIDER, TIMEFRAME, SourceContract


PROJECT_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = PROJECT_DIR / "data_raw"
REPORTS_DIR = PROJECT_DIR / "reports"
PAIR_SCHEMA_VERSION = "1"
PAIR_VALIDATION_RULE_VERSION = "bid_ask_reconciliation_v1"
EXTREME_SPREAD_THRESHOLD = Decimal("10")

STRICT_VALID_PAIR = "strict_valid_pair"
WARNING_REVIEW_PAIR = "warning_review_pair"
MISSING_BID = "missing_bid"
MISSING_ASK = "missing_ask"
TIMESTAMP_MISMATCH = "timestamp_mismatch"
INVALID_SPREAD = "invalid_spread"
EXCLUDED = "excluded"

REASON_ORDER = [
    "MISSING_BID", "MISSING_ASK", "BID_DUPLICATE_TIMESTAMP", "ASK_DUPLICATE_TIMESTAMP",
    "BID_INVALID_TIMESTAMP", "ASK_INVALID_TIMESTAMP", "TIMESTAMP_MISMATCH",
    "BID_SOURCE_IDENTITY_MISMATCH", "ASK_SOURCE_IDENTITY_MISMATCH", "PROVIDER_MISMATCH",
    "INSTRUMENT_MISMATCH", "TIMEFRAME_MISMATCH", "BID_QUOTE_SIDE_MISMATCH",
    "ASK_QUOTE_SIDE_MISMATCH", "BID_SIDE_WARNING_REVIEW", "ASK_SIDE_WARNING_REVIEW",
    "BID_SIDE_EXCLUDED_UNUSABLE", "ASK_SIDE_EXCLUDED_UNUSABLE", "BID_SIDE_CALENDAR_ONLY",
    "ASK_SIDE_CALENDAR_ONLY", "QUALITY_TIER_MISMATCH", "NEGATIVE_SPREAD", "ZERO_SPREAD",
    "EXTREME_SPREAD", "MARKET_CLOSED_PLACEHOLDER", "INVALID_NUMERIC",
]

PAIR_COLUMNS = [
    "pair_schema_version", "validation_rule_version", "date", "timestamp_utc", "provider",
    "instrument", "timeframe", "bid_source_filename", "bid_source_checksum_algorithm",
    "bid_source_checksum", "bid_manifest_quality_status", "bid_manifest_quality_reasons",
    "bid_quality_tier", "ask_source_filename", "ask_source_checksum_algorithm", "ask_source_checksum",
    "ask_manifest_quality_status", "ask_manifest_quality_reasons", "ask_quality_tier",
    "bid_open", "bid_high", "bid_low", "bid_close", "bid_volume", "ask_open", "ask_high",
    "ask_low", "ask_close", "ask_volume", "spread", "pair_quality_status", "pair_quality_reasons",
]


@dataclass(frozen=True)
class ReconciliationSummary:
    start_day: date
    end_day: date
    output_path: Path
    total_bid_rows: int
    total_ask_rows: int
    exact_timestamp_matches: int
    missing_bid_rows: int
    missing_ask_rows: int
    duplicate_bid_timestamps: int
    duplicate_ask_timestamps: int
    negative_spreads: int
    zero_spreads: int
    extreme_spreads: int
    warning_review_pairs: int
    excluded_or_invalid_rows: int
    pair_status_counts: dict[str, int]


def parse_day(day_text: str) -> date:
    try:
        return datetime.strptime(day_text, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError("Please enter dates in YYYY-MM-DD format.") from error


def each_day(start_day: date, end_day: date):
    current_day = start_day
    while current_day <= end_day:
        yield current_day
        current_day += timedelta(days=1)


def build_output_path(start_day: date, end_day: date) -> Path:
    return REPORTS_DIR / f"bid_ask_reconciliation_{start_day:%Y-%m-%d}_to_{end_day:%Y-%m-%d}.csv"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def load_linked_rows(path: Path, expected_side: str) -> dict[str, dict[str, str]]:
    rows = read_csv_rows(path)
    by_day: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        if row.get("quote_side") != expected_side:
            raise ValueError(f"{path} row {row_number} has quote_side={row.get('quote_side')!r}; expected {expected_side}.")
        if row.get("date") in by_day:
            raise ValueError(f"{path} has duplicate linked date {row.get('date')}.")
        by_day[row["date"]] = row
    return by_day


def require_source_identity(day_text: str, side: str, linked_row: dict[str, str]) -> None:
    expected_filename = data_manifest.build_source_filename(parse_day(day_text), SourceContract(quote_side=side))
    checks = {
        "provider": PROVIDER,
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        "quote_side": side,
        "source_filename": expected_filename,
    }
    mismatches = [field for field, expected in checks.items() if linked_row.get(field) != expected]
    if mismatches:
        raise ValueError(f"{side} linked provenance for {day_text} has incompatible identity: {', '.join(mismatches)}")


def parse_decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def validate_raw_provenance(path: Path, linked_row: dict[str, str]) -> None:
    raw_bytes = path.read_bytes()
    expected_size = linked_row.get("source_file_size_bytes", "")
    if expected_size and str(len(raw_bytes)) != expected_size:
        raise ValueError(f"Raw file size changed after linked provenance was generated: {path}")
    if linked_row.get("source_checksum_algorithm") != "sha256":
        raise ValueError(f"Unsupported checksum algorithm in linked provenance: {path}")
    expected_checksum = linked_row.get("source_checksum", "")
    actual_checksum = hashlib.sha256(raw_bytes).hexdigest()
    if expected_checksum and actual_checksum != expected_checksum:
        raise ValueError(f"Raw file checksum changed after linked provenance was generated: {path}")


def timestamp_is_valid(timestamp_text: str, expected_day: date) -> bool:
    timestamp = data_quality.parse_timestamp(timestamp_text)
    if timestamp is None:
        return False
    return (
        timestamp.date() == expected_day
        and timestamp.second == 0
        and timestamp.microsecond == 0
    )


def index_raw_rows(path: Path, expected_day: date, side: str) -> tuple[dict[str, dict[str, str]], Counter[str], int]:
    rows = read_csv_rows(path)
    counts: Counter[str] = Counter()
    indexed: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        timestamp_text = row.get("timestamp_utc", "")
        if timestamp_is_valid(timestamp_text, expected_day):
            key = timestamp_text
        else:
            key = f"__INVALID_{side}_{row_number}"
            row = dict(row)
            row["_timestamp_invalid"] = "1"
            row["_timestamp_original"] = timestamp_text
        counts[key] += 1
        indexed[key] = row
    return indexed, counts, len(rows)


def ordered_reasons(reasons: set[str]) -> str:
    return ";".join(reason for reason in REASON_ORDER if reason in reasons)


def side_tier_reasons(prefix: str, quality_tier: str) -> set[str]:
    if quality_tier == "strict_valid":
        return set()
    if quality_tier == "warning_review":
        return {f"{prefix}_SIDE_WARNING_REVIEW"}
    if quality_tier == "calendar_only":
        return {f"{prefix}_SIDE_CALENDAR_ONLY"}
    return {f"{prefix}_SIDE_EXCLUDED_UNUSABLE"}


def is_placeholder(row: dict[str, str]) -> bool:
    values = [parse_decimal(row.get(column, "")) for column in ("open", "high", "low", "close", "volume")]
    if any(value is None for value in values):
        return False
    return is_flat_zero_volume_candle(*(float(value) for value in values))


def classify_pair(bid_row, ask_row, bid_count, ask_count, bid_linked, ask_linked):
    reasons: set[str] = set()
    spread: Decimal | None = None
    if bid_row is None:
        reasons.add("MISSING_BID")
    if ask_row is None:
        reasons.add("MISSING_ASK")
    if bid_count > 1:
        reasons.add("BID_DUPLICATE_TIMESTAMP")
    if ask_count > 1:
        reasons.add("ASK_DUPLICATE_TIMESTAMP")
    if bid_row is not None and bid_row.get("_timestamp_invalid"):
        reasons.add("BID_INVALID_TIMESTAMP")
    if ask_row is not None and ask_row.get("_timestamp_invalid"):
        reasons.add("ASK_INVALID_TIMESTAMP")
    if bid_row is not None:
        reasons.update(side_tier_reasons("BID", bid_linked.get("quality_tier", "")))
    if ask_row is not None:
        reasons.update(side_tier_reasons("ASK", ask_linked.get("quality_tier", "")))
    if bid_row is not None and ask_row is not None and bid_linked.get("quality_tier") != ask_linked.get("quality_tier"):
        reasons.add("QUALITY_TIER_MISMATCH")
    if bid_row is not None and ask_row is not None:
        bid_close = parse_decimal(bid_row.get("close", ""))
        ask_close = parse_decimal(ask_row.get("close", ""))
        if bid_close is None or ask_close is None:
            reasons.add("INVALID_NUMERIC")
        else:
            spread = ask_close - bid_close
            if spread < 0:
                reasons.add("NEGATIVE_SPREAD")
            elif spread == 0:
                reasons.add("ZERO_SPREAD")
            elif spread > EXTREME_SPREAD_THRESHOLD:
                reasons.add("EXTREME_SPREAD")
        if is_placeholder(bid_row) or is_placeholder(ask_row):
            reasons.add("MARKET_CLOSED_PLACEHOLDER")
    if (
        "BID_DUPLICATE_TIMESTAMP" in reasons
        or "ASK_DUPLICATE_TIMESTAMP" in reasons
        or "BID_INVALID_TIMESTAMP" in reasons
        or "ASK_INVALID_TIMESTAMP" in reasons
    ):
        reasons.add("TIMESTAMP_MISMATCH")
        return TIMESTAMP_MISMATCH, reasons, spread
    if "MISSING_BID" in reasons:
        return MISSING_BID, reasons, spread
    if "MISSING_ASK" in reasons:
        return MISSING_ASK, reasons, spread
    if "NEGATIVE_SPREAD" in reasons or "INVALID_NUMERIC" in reasons:
        return INVALID_SPREAD, reasons, spread
    if any(reason.endswith("EXCLUDED_UNUSABLE") or reason.endswith("CALENDAR_ONLY") for reason in reasons):
        return EXCLUDED, reasons, spread
    if reasons:
        return WARNING_REVIEW_PAIR, reasons, spread
    return STRICT_VALID_PAIR, reasons, spread


def build_pair_row(day_text, timestamp, bid_row, ask_row, bid_count, ask_count, bid_linked, ask_linked):
    status, reasons, spread = classify_pair(bid_row, ask_row, bid_count, ask_count, bid_linked, ask_linked)
    row = {column: "" for column in PAIR_COLUMNS}
    output_timestamp = timestamp
    if bid_row is not None and bid_row.get("_timestamp_original") is not None:
        output_timestamp = bid_row.get("_timestamp_original", "")
    if ask_row is not None and ask_row.get("_timestamp_original") is not None:
        output_timestamp = ask_row.get("_timestamp_original", "")
    row.update({
        "pair_schema_version": PAIR_SCHEMA_VERSION,
        "validation_rule_version": PAIR_VALIDATION_RULE_VERSION,
        "date": day_text,
        "timestamp_utc": output_timestamp,
        "provider": PROVIDER,
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        "bid_source_filename": bid_linked.get("source_filename", ""),
        "bid_source_checksum_algorithm": bid_linked.get("source_checksum_algorithm", ""),
        "bid_source_checksum": bid_linked.get("source_checksum", ""),
        "bid_manifest_quality_status": bid_linked.get("manifest_quality_status", ""),
        "bid_manifest_quality_reasons": bid_linked.get("manifest_quality_reasons", ""),
        "bid_quality_tier": bid_linked.get("quality_tier", ""),
        "ask_source_filename": ask_linked.get("source_filename", ""),
        "ask_source_checksum_algorithm": ask_linked.get("source_checksum_algorithm", ""),
        "ask_source_checksum": ask_linked.get("source_checksum", ""),
        "ask_manifest_quality_status": ask_linked.get("manifest_quality_status", ""),
        "ask_manifest_quality_reasons": ask_linked.get("manifest_quality_reasons", ""),
        "ask_quality_tier": ask_linked.get("quality_tier", ""),
        "spread": "" if spread is None else format(spread, "f"),
        "pair_quality_status": status,
        "pair_quality_reasons": ordered_reasons(reasons),
    })
    for prefix, source_row in (("bid", bid_row), ("ask", ask_row)):
        if source_row is None:
            continue
        for column in ("open", "high", "low", "close", "volume"):
            row[f"{prefix}_{column}"] = source_row.get(column, "")
    return row


def reconcile_day(day: date, data_dir: Path, bid_linked, ask_linked):
    day_text = f"{day:%Y-%m-%d}"
    require_source_identity(day_text, BID, bid_linked)
    require_source_identity(day_text, ASK, ask_linked)
    bid_path = data_dir / bid_linked["source_filename"]
    ask_path = data_dir / ask_linked["source_filename"]
    validate_raw_provenance(bid_path, bid_linked)
    validate_raw_provenance(ask_path, ask_linked)
    bid_rows, bid_counts, total_bid = index_raw_rows(bid_path, day, BID)
    ask_rows, ask_counts, total_ask = index_raw_rows(ask_path, day, ASK)
    timestamps = sorted(set(bid_counts) | set(ask_counts))
    rows = [build_pair_row(day_text, ts, bid_rows.get(ts), ask_rows.get(ts), bid_counts[ts], ask_counts[ts], bid_linked, ask_linked) for ts in timestamps]
    duplicate_bid = sum(count - 1 for count in bid_counts.values() if count > 1)
    duplicate_ask = sum(count - 1 for count in ask_counts.values() if count > 1)
    return rows, total_bid, total_ask, duplicate_bid, duplicate_ask


def create_reconciliation(start_day: date, end_day: date, data_dir: Path = DATA_RAW_DIR, bid_linked_path: Path | None = None, ask_linked_path: Path | None = None, output_path: Path | None = None) -> ReconciliationSummary:
    if end_day < start_day:
        raise ValueError("The end date cannot be earlier than the start date.")
    bid_linked_path = bid_linked_path or REPORTS_DIR / "linked_observation_report_2024-01-01_to_2024-01-31.csv"
    ask_linked_path = ask_linked_path or REPORTS_DIR / "linked_observation_report_ASK_2024-01-09_to_2024-01-11.csv"
    output_path = output_path or build_output_path(start_day, end_day)
    bid_by_day = load_linked_rows(bid_linked_path, BID)
    ask_by_day = load_linked_rows(ask_linked_path, ASK)
    all_rows: list[dict[str, str]] = []
    total_bid_rows = total_ask_rows = duplicate_bid = duplicate_ask = 0
    for day in each_day(start_day, end_day):
        day_text = f"{day:%Y-%m-%d}"
        if day_text not in bid_by_day or day_text not in ask_by_day:
            raise ValueError(f"Missing side-specific linked provenance for {day_text}.")
        rows, bid_count, ask_count, bid_dupes, ask_dupes = reconcile_day(day, data_dir, bid_by_day[day_text], ask_by_day[day_text])
        all_rows.extend(rows)
        total_bid_rows += bid_count
        total_ask_rows += ask_count
        duplicate_bid += bid_dupes
        duplicate_ask += ask_dupes
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=PAIR_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)
    status_counts = Counter(row["pair_quality_status"] for row in all_rows)
    reason_sets = [set(row["pair_quality_reasons"].split(";")) for row in all_rows]
    return ReconciliationSummary(
        start_day=start_day,
        end_day=end_day,
        output_path=output_path,
        total_bid_rows=total_bid_rows,
        total_ask_rows=total_ask_rows,
        exact_timestamp_matches=sum(1 for row in all_rows if row["bid_close"] and row["ask_close"]),
        missing_bid_rows=status_counts[MISSING_BID],
        missing_ask_rows=status_counts[MISSING_ASK],
        duplicate_bid_timestamps=duplicate_bid,
        duplicate_ask_timestamps=duplicate_ask,
        negative_spreads=sum("NEGATIVE_SPREAD" in reasons for reasons in reason_sets),
        zero_spreads=sum("ZERO_SPREAD" in reasons for reasons in reason_sets),
        extreme_spreads=sum("EXTREME_SPREAD" in reasons for reasons in reason_sets),
        warning_review_pairs=status_counts[WARNING_REVIEW_PAIR],
        excluded_or_invalid_rows=status_counts[INVALID_SPREAD] + status_counts[EXCLUDED],
        pair_status_counts=dict(status_counts),
    )


def print_summary(summary: ReconciliationSummary) -> None:
    print("BID/ASK reconciliation complete.")
    print(f"Date range: {summary.start_day:%Y-%m-%d} to {summary.end_day:%Y-%m-%d}")
    print(f"Total BID rows: {summary.total_bid_rows}")
    print(f"Total ASK rows: {summary.total_ask_rows}")
    print(f"Exact timestamp matches: {summary.exact_timestamp_matches}")
    print(f"Missing BID rows: {summary.missing_bid_rows}")
    print(f"Missing ASK rows: {summary.missing_ask_rows}")
    print(f"Duplicate BID timestamps: {summary.duplicate_bid_timestamps}")
    print(f"Duplicate ASK timestamps: {summary.duplicate_ask_timestamps}")
    print(f"Negative spreads: {summary.negative_spreads}")
    print(f"Zero spreads: {summary.zero_spreads}")
    print(f"Extreme spreads: {summary.extreme_spreads}")
    print(f"Warning-review pairs: {summary.warning_review_pairs}")
    print(f"Excluded/invalid rows: {summary.excluded_or_invalid_rows}")
    print(f"Output path: {summary.output_path}")


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 bid_ask_reconciliation.py YYYY-MM-DD YYYY-MM-DD")
        return 1
    try:
        summary = create_reconciliation(parse_day(sys.argv[1]), parse_day(sys.argv[2]))
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        return 1
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
