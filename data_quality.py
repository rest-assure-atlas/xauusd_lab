"""Validate raw Dukascopy XAU/USD one-minute BID CSV files.

This module reads raw CSV files without modifying them and returns deterministic
manifest fields describing file provenance, structural validation, and cautious
research-suitability status.
"""

from __future__ import annotations

import csv
import hashlib
import io
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from candle_filters import is_flat_zero_volume_candle, remove_edge_inactive_placeholders


MANIFEST_SCHEMA_VERSION = "1"
VALIDATION_RULE_VERSION = "raw_data_quality_v1"

PROVIDER = "Dukascopy"
INSTRUMENT = "XAUUSD"
QUOTE_SIDE = "BID"
TIMEFRAME = "1min"

EXPECTED_COLUMNS = ["timestamp_utc", "open", "high", "low", "close", "volume"]
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

MISSING_FILE = "MISSING_FILE"
EMPTY_FILE = "EMPTY_FILE"
READ_ERROR = "READ_ERROR"
HEADER_MISMATCH = "HEADER_MISMATCH"
ROW_SHAPE_MISMATCH = "ROW_SHAPE_MISMATCH"
INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
TIMESTAMP_OFF_MINUTE = "TIMESTAMP_OFF_MINUTE"
TIMESTAMP_DATE_MISMATCH = "TIMESTAMP_DATE_MISMATCH"
INVALID_NUMERIC = "INVALID_NUMERIC"
OHLC_INCONSISTENT = "OHLC_INCONSISTENT"
NEGATIVE_VOLUME = "NEGATIVE_VOLUME"
DUPLICATE_TIMESTAMP = "DUPLICATE_TIMESTAMP"
OUT_OF_ORDER_TIMESTAMP = "OUT_OF_ORDER_TIMESTAMP"
MISSING_MINUTES = "MISSING_MINUTES"
PARTIAL_DAY_COVERAGE = "PARTIAL_DAY_COVERAGE"
INTERNAL_FLAT_ZERO_VOLUME = "INTERNAL_FLAT_ZERO_VOLUME"
NO_ACTIVE_CANDLES = "NO_ACTIVE_CANDLES"

REASON_ORDER = [
    MISSING_FILE,
    EMPTY_FILE,
    READ_ERROR,
    HEADER_MISMATCH,
    ROW_SHAPE_MISMATCH,
    INVALID_TIMESTAMP,
    TIMESTAMP_OFF_MINUTE,
    TIMESTAMP_DATE_MISMATCH,
    INVALID_NUMERIC,
    OHLC_INCONSISTENT,
    NEGATIVE_VOLUME,
    DUPLICATE_TIMESTAMP,
    OUT_OF_ORDER_TIMESTAMP,
    MISSING_MINUTES,
    PARTIAL_DAY_COVERAGE,
    INTERNAL_FLAT_ZERO_VOLUME,
    NO_ACTIVE_CANDLES,
]

INVALID_REASON_CODES = {
    READ_ERROR,
    HEADER_MISMATCH,
    ROW_SHAPE_MISMATCH,
    INVALID_TIMESTAMP,
    TIMESTAMP_OFF_MINUTE,
    TIMESTAMP_DATE_MISMATCH,
    INVALID_NUMERIC,
    OHLC_INCONSISTENT,
    NEGATIVE_VOLUME,
    DUPLICATE_TIMESTAMP,
    OUT_OF_ORDER_TIMESTAMP,
}

WARNING_REASON_CODES = {
    MISSING_MINUTES,
    PARTIAL_DAY_COVERAGE,
    INTERNAL_FLAT_ZERO_VOLUME,
}

ASSESSMENT_COLUMNS = [
    "source_file_size_bytes",
    "source_checksum_algorithm",
    "source_checksum",
    "file_status",
    "quality_status",
    "quality_reasons",
    "total_row_count",
    "active_row_count",
    "leading_inactive_row_count",
    "trailing_inactive_row_count",
    "internal_inactive_row_count",
    "first_timestamp_utc",
    "last_timestamp_utc",
    "first_active_timestamp_utc",
    "last_active_timestamp_utc",
    "duplicate_timestamp_count",
    "out_of_order_timestamp_count",
    "missing_minute_count",
    "internal_gap_count",
    "maximum_internal_gap_minutes",
    "leading_day_gap_minutes",
    "trailing_day_gap_minutes",
    "invalid_timestamp_count",
    "off_minute_timestamp_count",
    "wrong_date_timestamp_count",
    "invalid_numeric_row_count",
    "ohlc_consistency_failure_count",
    "negative_volume_count",
]


@dataclass
class ParsedRow:
    """One processable CSV row with parsed validation details."""

    timestamp: datetime | None
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: float | None
    numeric_valid: bool
    is_flat_zero_volume: bool


@dataclass
class QualityAssessment:
    """Manifest fields produced from one raw file check."""

    fields: dict[str, str]


def blank_assessment_fields() -> dict[str, str]:
    """Create an empty field dictionary using the stable assessment columns."""
    return {column: "" for column in ASSESSMENT_COLUMNS}


def ordered_reasons(reasons: set[str]) -> str:
    """Format reason codes in a deterministic machine-readable order."""
    return ";".join(reason for reason in REASON_ORDER if reason in reasons)


def file_provenance_fields(raw_bytes: bytes) -> dict[str, str]:
    """Return deterministic size and checksum fields for readable bytes."""
    return {
        "source_file_size_bytes": str(len(raw_bytes)),
        "source_checksum_algorithm": "sha256",
        "source_checksum": hashlib.sha256(raw_bytes).hexdigest(),
    }


def missing_file_assessment() -> QualityAssessment:
    """Return manifest fields for an absent expected raw file."""
    fields = blank_assessment_fields()
    fields["file_status"] = "missing_file"
    fields["quality_status"] = "not_assessed"
    fields["quality_reasons"] = MISSING_FILE
    return QualityAssessment(fields=fields)


def empty_file_assessment(raw_bytes: bytes) -> QualityAssessment:
    """Return manifest fields for a zero-byte or header-only file."""
    fields = blank_assessment_fields()
    fields.update(file_provenance_fields(raw_bytes))
    fields["file_status"] = "empty_file"
    fields["quality_status"] = "invalid"
    fields["quality_reasons"] = EMPTY_FILE
    fields["total_row_count"] = "0"
    return QualityAssessment(fields=fields)


def parse_failed_assessment(
    raw_bytes: bytes | None,
    reason_code: str,
) -> QualityAssessment:
    """Return manifest fields for a file that cannot be structurally assessed."""
    fields = blank_assessment_fields()

    if raw_bytes is not None:
        fields.update(file_provenance_fields(raw_bytes))

    fields["file_status"] = "parse_failed"
    fields["quality_status"] = "invalid"
    fields["quality_reasons"] = reason_code
    return QualityAssessment(fields=fields)


def parse_timestamp(timestamp_text: str) -> datetime | None:
    """Parse only the exact source timestamp format."""
    try:
        parsed_timestamp = datetime.strptime(timestamp_text, TIMESTAMP_FORMAT)
    except ValueError:
        return None

    if parsed_timestamp.strftime(TIMESTAMP_FORMAT) != timestamp_text:
        return None

    return parsed_timestamp


def format_timestamp(timestamp: datetime) -> str:
    """Format a timestamp deterministically for the manifest."""
    return timestamp.strftime(TIMESTAMP_FORMAT)


def parse_number(value: str) -> float | None:
    """Parse one numeric CSV value, rejecting NaN and infinity."""
    try:
        number = float(value)
    except ValueError:
        return None

    if not math.isfinite(number):
        return None

    return number


def row_has_ohlc_failure(
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
) -> bool:
    """Return True when OHLC values violate candle consistency."""
    return (
        high_price < open_price
        or high_price < close_price
        or low_price > open_price
        or low_price > close_price
        or high_price < low_price
    )


def parse_data_row(row: list[str]) -> ParsedRow:
    """Convert one structurally valid CSV row into parsed validation values."""
    timestamp = parse_timestamp(row[0])
    open_price = parse_number(row[1])
    high_price = parse_number(row[2])
    low_price = parse_number(row[3])
    close_price = parse_number(row[4])
    volume = parse_number(row[5])

    numbers = [open_price, high_price, low_price, close_price, volume]
    numeric_valid = all(number is not None for number in numbers)
    is_flat_zero_volume = False

    if numeric_valid:
        is_flat_zero_volume = is_flat_zero_volume_candle(
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
        )

    return ParsedRow(
        timestamp=timestamp,
        open=open_price,
        high=high_price,
        low=low_price,
        close=close_price,
        volume=volume,
        numeric_valid=numeric_valid,
        is_flat_zero_volume=is_flat_zero_volume,
    )


def split_csv_rows(raw_bytes: bytes) -> tuple[list[str], list[list[str]]] | None:
    """Decode bytes and return a CSV header plus data rows."""
    try:
        csv_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return None

    try:
        csv_rows = list(csv.reader(io.StringIO(csv_text)))
    except csv.Error:
        return None

    if not csv_rows:
        return [], []

    return csv_rows[0], csv_rows[1:]


def add_timestamp_metrics(
    fields: dict[str, str],
    parsed_rows: list[ParsedRow],
    requested_day: date,
    reasons: set[str],
) -> None:
    """Add timestamp validation counts and continuity metrics."""
    invalid_timestamp_count = 0
    off_minute_timestamp_count = 0
    wrong_date_timestamp_count = 0
    duplicate_timestamp_count = 0
    out_of_order_timestamp_count = 0

    parsed_timestamps = []
    seen_timestamps = set()
    previous_timestamp = None

    for row in parsed_rows:
        timestamp = row.timestamp

        if timestamp is None:
            invalid_timestamp_count += 1
            continue

        parsed_timestamps.append(timestamp)

        if timestamp.second != 0 or timestamp.microsecond != 0:
            off_minute_timestamp_count += 1

        if timestamp.date() != requested_day:
            wrong_date_timestamp_count += 1

        if timestamp in seen_timestamps:
            duplicate_timestamp_count += 1
        else:
            seen_timestamps.add(timestamp)

        if previous_timestamp is not None and timestamp < previous_timestamp:
            out_of_order_timestamp_count += 1

        previous_timestamp = timestamp

    if invalid_timestamp_count:
        reasons.add(INVALID_TIMESTAMP)
    if off_minute_timestamp_count:
        reasons.add(TIMESTAMP_OFF_MINUTE)
    if wrong_date_timestamp_count:
        reasons.add(TIMESTAMP_DATE_MISMATCH)
    if duplicate_timestamp_count:
        reasons.add(DUPLICATE_TIMESTAMP)
    if out_of_order_timestamp_count:
        reasons.add(OUT_OF_ORDER_TIMESTAMP)

    fields["invalid_timestamp_count"] = str(invalid_timestamp_count)
    fields["off_minute_timestamp_count"] = str(off_minute_timestamp_count)
    fields["wrong_date_timestamp_count"] = str(wrong_date_timestamp_count)
    fields["duplicate_timestamp_count"] = str(duplicate_timestamp_count)
    fields["out_of_order_timestamp_count"] = str(out_of_order_timestamp_count)

    if parsed_timestamps and invalid_timestamp_count == 0:
        fields["first_timestamp_utc"] = format_timestamp(min(parsed_timestamps))
        fields["last_timestamp_utc"] = format_timestamp(max(parsed_timestamps))

    continuity_is_reliable = (
        invalid_timestamp_count == 0
        and off_minute_timestamp_count == 0
        and wrong_date_timestamp_count == 0
    )

    if not continuity_is_reliable:
        return

    unique_timestamps = sorted(seen_timestamps)
    start_of_day = datetime.combine(requested_day, datetime.min.time())
    end_of_day = start_of_day + timedelta(hours=23, minutes=59)
    leading_day_gap_minutes = int(
        (unique_timestamps[0] - start_of_day).total_seconds() // 60
    )
    trailing_day_gap_minutes = int(
        (end_of_day - unique_timestamps[-1]).total_seconds() // 60
    )
    missing_minute_count = 0
    internal_gap_count = 0
    maximum_internal_gap_minutes = 0

    for previous_timestamp, current_timestamp in zip(
        unique_timestamps,
        unique_timestamps[1:],
    ):
        elapsed_minutes = int(
            (current_timestamp - previous_timestamp).total_seconds() // 60
        )
        missing_minutes = elapsed_minutes - 1

        if missing_minutes > 0:
            missing_minute_count += missing_minutes
            internal_gap_count += 1
            maximum_internal_gap_minutes = max(
                maximum_internal_gap_minutes,
                missing_minutes,
            )

    if missing_minute_count:
        reasons.add(MISSING_MINUTES)

    if leading_day_gap_minutes or trailing_day_gap_minutes:
        reasons.add(PARTIAL_DAY_COVERAGE)

    fields["missing_minute_count"] = str(missing_minute_count)
    fields["internal_gap_count"] = str(internal_gap_count)
    fields["maximum_internal_gap_minutes"] = str(maximum_internal_gap_minutes)
    fields["leading_day_gap_minutes"] = str(leading_day_gap_minutes)
    fields["trailing_day_gap_minutes"] = str(trailing_day_gap_minutes)


def add_numeric_metrics(
    fields: dict[str, str],
    parsed_rows: list[ParsedRow],
    reasons: set[str],
) -> None:
    """Add numeric, OHLC, and volume validation counts."""
    invalid_numeric_row_count = 0
    ohlc_consistency_failure_count = 0
    negative_volume_count = 0

    for row in parsed_rows:
        if not row.numeric_valid:
            invalid_numeric_row_count += 1
            continue

        if row_has_ohlc_failure(row.open, row.high, row.low, row.close):
            ohlc_consistency_failure_count += 1

        if row.volume < 0:
            negative_volume_count += 1

    if invalid_numeric_row_count:
        reasons.add(INVALID_NUMERIC)
    if ohlc_consistency_failure_count:
        reasons.add(OHLC_INCONSISTENT)
    if negative_volume_count:
        reasons.add(NEGATIVE_VOLUME)

    fields["invalid_numeric_row_count"] = str(invalid_numeric_row_count)
    fields["ohlc_consistency_failure_count"] = str(ohlc_consistency_failure_count)
    fields["negative_volume_count"] = str(negative_volume_count)


def add_active_row_metrics(
    fields: dict[str, str],
    parsed_rows: list[ParsedRow],
    reasons: set[str],
) -> str:
    """Add inactive-edge and active-row metrics when numeric rows allow it."""
    if any(not row.numeric_valid for row in parsed_rows):
        return "processed"

    active_result = remove_edge_inactive_placeholders(
        parsed_rows,
        lambda row: row.is_flat_zero_volume,
    )
    internal_inactive_count = sum(
        1 for row in active_result.active_rows if row.is_flat_zero_volume
    )

    if internal_inactive_count:
        reasons.add(INTERNAL_FLAT_ZERO_VOLUME)

    fields["active_row_count"] = str(active_result.active_count)
    fields["leading_inactive_row_count"] = str(active_result.leading_inactive_count)
    fields["trailing_inactive_row_count"] = str(active_result.trailing_inactive_count)
    fields["internal_inactive_row_count"] = str(internal_inactive_count)

    active_timestamps = [row.timestamp for row in active_result.active_rows]

    if active_timestamps and all(timestamp is not None for timestamp in active_timestamps):
        fields["first_active_timestamp_utc"] = format_timestamp(min(active_timestamps))
        fields["last_active_timestamp_utc"] = format_timestamp(max(active_timestamps))

    if active_result.active_count == 0:
        reasons.add(NO_ACTIVE_CANDLES)
        return "no_active_candles"

    return "processed"


def classify_quality(file_status: str, reasons: set[str]) -> str:
    """Classify one processable file using conservative suitability rules."""
    if file_status == "missing_file":
        return "not_assessed"

    if file_status in {"empty_file", "parse_failed"}:
        return "invalid"

    if reasons & INVALID_REASON_CODES:
        return "invalid"

    if file_status == "no_active_candles":
        return "not_assessed"

    if reasons & WARNING_REASON_CODES:
        return "warning"

    return "valid"


def assess_processable_rows(
    raw_bytes: bytes,
    raw_rows: list[list[str]],
    requested_day: date,
) -> QualityAssessment:
    """Assess data rows after the file has passed header and row-shape checks."""
    fields = blank_assessment_fields()
    fields.update(file_provenance_fields(raw_bytes))
    fields["total_row_count"] = str(len(raw_rows))

    parsed_rows = [parse_data_row(row) for row in raw_rows]
    reasons: set[str] = set()

    add_timestamp_metrics(fields, parsed_rows, requested_day, reasons)
    add_numeric_metrics(fields, parsed_rows, reasons)

    file_status = add_active_row_metrics(fields, parsed_rows, reasons)
    quality_status = classify_quality(file_status, reasons)

    fields["file_status"] = file_status
    fields["quality_status"] = quality_status
    fields["quality_reasons"] = "" if quality_status == "valid" else ordered_reasons(reasons)

    return QualityAssessment(fields=fields)


def assess_raw_csv_file(file_path: Path, requested_day: date) -> QualityAssessment:
    """Assess one existing raw CSV file without writing to it."""
    try:
        raw_bytes = file_path.read_bytes()
    except OSError:
        return parse_failed_assessment(None, READ_ERROR)

    return assess_raw_csv_bytes(raw_bytes, requested_day)


def assess_raw_csv_bytes(raw_bytes: bytes, requested_day: date) -> QualityAssessment:
    """Assess raw CSV bytes without rereading or modifying the source file."""
    if len(raw_bytes) == 0:
        return empty_file_assessment(raw_bytes)

    csv_parts = split_csv_rows(raw_bytes)

    if csv_parts is None:
        return parse_failed_assessment(raw_bytes, READ_ERROR)

    header, raw_rows = csv_parts

    if header != EXPECTED_COLUMNS:
        return parse_failed_assessment(raw_bytes, HEADER_MISMATCH)

    if not raw_rows:
        return empty_file_assessment(raw_bytes)

    for row in raw_rows:
        if len(row) != len(EXPECTED_COLUMNS):
            return parse_failed_assessment(raw_bytes, ROW_SHAPE_MISMATCH)

    return assess_processable_rows(raw_bytes, raw_rows, requested_day)
