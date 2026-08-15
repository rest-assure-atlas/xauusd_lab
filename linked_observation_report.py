"""Create an orchestrated provenance-linked daily/session observation report.

Usage:
    python linked_observation_report.py 2024-01-01 2024-01-31
    python linked_observation_report.py 2024-01-01 2024-01-31 --data-dir data_raw
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import data_manifest
import session_report
from candle_filters import ACTIVE_FILTER_RULE_IDENTITY
from data_quality import (
    INSTRUMENT,
    PROVIDER,
    QUOTE_SIDE,
    READ_ERROR,
    TIMEFRAME,
    assess_raw_csv_bytes,
    file_provenance_fields,
    missing_file_assessment,
    parse_failed_assessment,
)
from session_tools import SessionDefinition, load_session_definitions
from source_contracts import (
    DEFAULT_SOURCE_CONTRACT,
    SourceContract,
    build_report_filename,
)


PROJECT_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = PROJECT_DIR / "data_raw"
REPORTS_DIR = PROJECT_DIR / "reports"

LINKED_SCHEMA_VERSION = "1"

LINKED = "linked"
CALENDAR_ONLY = "calendar_only"
CONTRADICTION = "contradiction"
SOURCE_CHANGED = "source_changed"
SOURCE_UNAVAILABLE = "source_unavailable"

STRICT_VALID = "strict_valid"
WARNING_REVIEW = "warning_review"
EXCLUDED_UNUSABLE = "excluded_unusable"

DATE_COVERAGE_MISMATCH = "DATE_COVERAGE_MISMATCH"
DUPLICATE_DATE = "DUPLICATE_DATE"
PROVIDER_MISMATCH = "PROVIDER_MISMATCH"
INSTRUMENT_MISMATCH = "INSTRUMENT_MISMATCH"
QUOTE_SIDE_MISMATCH = "QUOTE_SIDE_MISMATCH"
TIMEFRAME_MISMATCH = "TIMEFRAME_MISMATCH"
SOURCE_FILENAME_MISMATCH = "SOURCE_FILENAME_MISMATCH"
SOURCE_SIZE_MISMATCH = "SOURCE_SIZE_MISMATCH"
SOURCE_CHECKSUM_MISMATCH = "SOURCE_CHECKSUM_MISMATCH"
SOURCE_CHECKSUM_UNAVAILABLE = "SOURCE_CHECKSUM_UNAVAILABLE"
SOURCE_IDENTITY_CHANGED = "SOURCE_IDENTITY_CHANGED"
ROW_COUNT_MISMATCH = "ROW_COUNT_MISMATCH"
ACTIVE_COUNT_MISMATCH = "ACTIVE_COUNT_MISMATCH"
STATUS_DISAGREEMENT = "STATUS_DISAGREEMENT"
SESSION_VALUES_WITH_MANIFEST_FAILURE = "SESSION_VALUES_WITH_MANIFEST_FAILURE"
MANIFEST_PROCESSED_SESSION_FAILED = "MANIFEST_PROCESSED_SESSION_FAILED"

LINKAGE_REASON_ORDER = [
    DATE_COVERAGE_MISMATCH,
    DUPLICATE_DATE,
    PROVIDER_MISMATCH,
    INSTRUMENT_MISMATCH,
    QUOTE_SIDE_MISMATCH,
    TIMEFRAME_MISMATCH,
    SOURCE_FILENAME_MISMATCH,
    SOURCE_SIZE_MISMATCH,
    SOURCE_CHECKSUM_MISMATCH,
    SOURCE_CHECKSUM_UNAVAILABLE,
    SOURCE_IDENTITY_CHANGED,
    ROW_COUNT_MISMATCH,
    ACTIVE_COUNT_MISMATCH,
    STATUS_DISAGREEMENT,
    SESSION_VALUES_WITH_MANIFEST_FAILURE,
    MANIFEST_PROCESSED_SESSION_FAILED,
]

EXPECTED_SESSION_NAMES = ["Tokyo", "London", "New York"]
EXPECTED_SESSION_PREFIXES = ["tokyo", "london", "new_york"]
EXPECTED_SESSION_REPORT_BASE_COLUMNS = [
    "date",
    "weekday",
    "status",
    "daily_open",
    "daily_high",
    "daily_low",
    "daily_close",
    "daily_range",
    "time_of_daily_high_utc",
    "time_of_daily_low_utc",
    "total_csv_rows",
    "active_candle_count",
    "inactive_placeholder_count",
]
EXPECTED_SESSION_STAT_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "range",
    "time_of_high_utc",
    "time_of_low_utc",
    "active_candle_count",
]

SESSION_COUNT_COLUMNS = {
    "total_csv_rows": "session_total_csv_rows",
    "active_candle_count": "session_active_candle_count",
    "inactive_placeholder_count": "session_inactive_placeholder_count",
}
DAILY_CALCULATION_COLUMNS = [
    "daily_open",
    "daily_high",
    "daily_low",
    "daily_close",
    "daily_range",
    "time_of_daily_high_utc",
    "time_of_daily_low_utc",
]


def expected_session_report_columns() -> list[str]:
    """Return the v0.10 session-report columns this linker accepts."""
    columns = list(EXPECTED_SESSION_REPORT_BASE_COLUMNS)

    for prefix in EXPECTED_SESSION_PREFIXES:
        for column in EXPECTED_SESSION_STAT_COLUMNS:
            columns.append(f"{prefix}_{column}")

    return columns


def session_calculation_columns() -> list[str]:
    """Return calculation columns copied from the session-report row."""
    columns = list(DAILY_CALCULATION_COLUMNS)

    for prefix in EXPECTED_SESSION_PREFIXES:
        for column in EXPECTED_SESSION_STAT_COLUMNS:
            columns.append(f"{prefix}_{column}")

    return columns


LINKED_COLUMNS = [
    "linked_schema_version",
    "date",
    "weekday",
    "provider",
    "instrument",
    "quote_side",
    "timeframe",
    "source_filename",
    "source_file_size_bytes",
    "source_checksum_algorithm",
    "source_checksum",
    "manifest_schema_version",
    "validation_rule_version",
    "active_filter_rule_identity",
    "session_definition_checksum",
    "software_revision",
    "session_status",
    "manifest_file_status",
    "manifest_quality_status",
    "manifest_quality_reasons",
    "linkage_status",
    "linkage_reasons",
    "quality_tier",
    "manifest_total_row_count",
    "manifest_active_row_count",
    "session_total_csv_rows",
    "session_active_candle_count",
    "session_inactive_placeholder_count",
    *session_calculation_columns(),
]


@dataclass(frozen=True)
class SourceIdentity:
    """Source identity established from the raw bytes used in one row."""

    filename: str
    file_size_bytes: str
    checksum_algorithm: str
    checksum: str


@dataclass
class LinkedReportArguments:
    """Command-line arguments for one linked report run."""

    start_day: date
    end_day: date
    data_dir: Path


@dataclass
class LinkedReportSummary:
    """Counts printed after a linked report run finishes."""

    requested_dates: int
    strict_valid_observations: int
    warning_review_observations: int
    excluded_unusable_observations: int
    calendar_only_observations: int
    output_path: Path


def parse_day(day_text: str) -> date:
    """Convert text like '2024-01-31' into a Python date."""
    try:
        return datetime.strptime(day_text, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError("Please enter dates in YYYY-MM-DD format.") from error


def parse_arguments(arguments: list[str]) -> LinkedReportArguments:
    """Read the inclusive date range and optional data directory."""
    if len(arguments) not in (2, 4):
        raise ValueError("Please enter a start date and end date.")

    start_day = parse_day(arguments[0])
    end_day = parse_day(arguments[1])

    if end_day < start_day:
        raise ValueError("The end date cannot be earlier than the start date.")

    data_dir = DATA_RAW_DIR

    if len(arguments) == 4:
        if arguments[2] != "--data-dir":
            raise ValueError("The only optional linked-report flag is --data-dir.")

        data_dir = Path(arguments[3])

    if not data_dir.exists():
        raise ValueError(f"Data directory does not exist: {data_dir}")

    if not data_dir.is_dir():
        raise ValueError(f"Data directory is not a folder: {data_dir}")

    return LinkedReportArguments(
        start_day=start_day,
        end_day=end_day,
        data_dir=data_dir,
    )


def each_day(start_day: date, end_day: date):
    """Yield every date from start_day to end_day, including both dates."""
    current_day = start_day

    while current_day <= end_day:
        yield current_day
        current_day += timedelta(days=1)


def build_linked_report_path(
    start_day: date,
    end_day: date,
    source_contract: SourceContract = DEFAULT_SOURCE_CONTRACT,
    *,
    legacy_side_omitted: bool = True,
) -> Path:
    """Build the deterministic output path for a linked report date range."""
    filename = build_report_filename(
        "linked_observation_report",
        start_day,
        end_day,
        source_contract,
        legacy_side_omitted=legacy_side_omitted,
    )
    return REPORTS_DIR / filename


def read_source_bytes(source_path: Path) -> bytes:
    """Read raw bytes through a patchable boundary for provenance tests."""
    return source_path.read_bytes()


def source_identity_from_bytes(source_filename: str, raw_bytes: bytes) -> SourceIdentity:
    """Create source identity fields from the exact bytes used by this run."""
    provenance = file_provenance_fields(raw_bytes)
    return SourceIdentity(
        filename=source_filename,
        file_size_bytes=provenance["source_file_size_bytes"],
        checksum_algorithm=provenance["source_checksum_algorithm"],
        checksum=provenance["source_checksum"],
    )


def build_manifest_row_from_assessment(
    day: date,
    assessment_fields: dict[str, str],
    source_contract: SourceContract = DEFAULT_SOURCE_CONTRACT,
) -> dict[str, str]:
    """Combine manifest base metadata with already-created assessment fields."""
    row = data_manifest.base_manifest_row(day, source_contract)
    row.update(assessment_fields)
    return row


def build_session_missing_row(
    day: date,
    session_columns: list[str],
) -> session_report.DailyReportResult:
    """Create the existing session-report missing-file status row."""
    return session_report.DailyReportResult(
        row=session_report.empty_report_row(day, session_columns, "missing_file"),
        completed=False,
        missing_file=True,
        failed=False,
    )


def build_session_failed_row(
    day: date,
    session_columns: list[str],
) -> session_report.DailyReportResult:
    """Create the existing session-report failed status row."""
    return session_report.DailyReportResult(
        row=session_report.empty_report_row(day, session_columns, "failed"),
        completed=False,
        missing_file=False,
        failed=True,
    )


def normalize_session_definitions(
    definitions: list[SessionDefinition],
) -> list[dict[str, str]]:
    """Create a stable serializable form of the current session definitions."""
    normalized = []

    for definition in definitions:
        normalized.append(
            {
                "name": definition.name,
                "timezone": definition.timezone_name,
                "local_start": definition.local_start.strftime("%H:%M"),
                "local_end": definition.local_end.strftime("%H:%M"),
                "color": definition.color,
            }
        )

    return normalized


def calculate_session_definition_checksum(
    definitions: list[SessionDefinition] | None = None,
) -> str:
    """Return a deterministic checksum for the configured session definitions."""
    if definitions is None:
        definitions = load_session_definitions()

    payload = json.dumps(
        normalize_session_definitions(definitions),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def get_software_revision() -> str:
    """Return the current Git commit, marking uncommitted code state honestly."""
    try:
        revision_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_DIR,
            check=True,
            capture_output=True,
            text=True,
        )

        status_result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=normal"],
            cwd=PROJECT_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"

    revision = revision_result.stdout.strip()

    if not revision:
        return "unknown"

    if status_result.stdout.strip():
        return f"{revision}-dirty"

    return revision


def validate_session_configuration(sample_day: date) -> list[str]:
    """Validate the deferred session schema assumptions for this milestone."""
    definitions = load_session_definitions()
    names = [definition.name for definition in definitions]
    prefixes = [session_report.session_prefix(name) for name in names]

    if len(set(names)) != len(names):
        raise ValueError("Session definitions contain duplicate session names.")

    if len(set(prefixes)) != len(prefixes):
        raise ValueError("Session definitions contain duplicate or colliding prefixes.")

    if names != EXPECTED_SESSION_NAMES:
        raise ValueError(
            "Linked observations currently require Tokyo, London, and New York "
            "session definitions in that order."
        )

    generated_columns = []

    for prefix in prefixes:
        for column in EXPECTED_SESSION_STAT_COLUMNS:
            generated_columns.append(f"{prefix}_{column}")

    if len(set(generated_columns)) != len(generated_columns):
        raise ValueError("Generated session columns contain duplicates.")

    if set(generated_columns) & set(EXPECTED_SESSION_REPORT_BASE_COLUMNS):
        raise ValueError("Generated session columns collide with base report columns.")

    if session_report.BASE_COLUMNS != EXPECTED_SESSION_REPORT_BASE_COLUMNS:
        raise ValueError("Session report base column contract has changed.")

    if session_report.SESSION_STAT_COLUMNS != EXPECTED_SESSION_STAT_COLUMNS:
        raise ValueError("Session report statistic column contract has changed.")

    session_columns = session_report.build_report_columns(sample_day)

    if session_columns != expected_session_report_columns():
        raise ValueError("Session report generated column contract has changed.")

    return session_columns


def ordered_linkage_reasons(reasons: set[str]) -> str:
    """Format linkage reason codes in deterministic order."""
    return ";".join(reason for reason in LINKAGE_REASON_ORDER if reason in reasons)


def has_calculated_session_values(session_row: dict[str, str]) -> bool:
    """Return True when a session row contains non-count calculation values."""
    return any(session_row.get(column, "") for column in session_calculation_columns())


def add_source_contract_reasons(
    reasons: set[str],
    manifest_row: dict[str, str],
    expected_filename: str,
    source_contract: SourceContract = DEFAULT_SOURCE_CONTRACT,
) -> None:
    """Compare manifest source-contract fields with the linked expectation."""
    if manifest_row.get("provider") != source_contract.provider:
        reasons.add(PROVIDER_MISMATCH)

    if manifest_row.get("instrument") != source_contract.instrument:
        reasons.add(INSTRUMENT_MISMATCH)

    if manifest_row.get("quote_side") != source_contract.quote_side:
        reasons.add(QUOTE_SIDE_MISMATCH)

    if manifest_row.get("timeframe") != source_contract.timeframe:
        reasons.add(TIMEFRAME_MISMATCH)

    if manifest_row.get("source_filename") != expected_filename:
        reasons.add(SOURCE_FILENAME_MISMATCH)


def add_source_identity_reasons(
    reasons: set[str],
    manifest_row: dict[str, str],
    source_identity: SourceIdentity | None,
    source_read_failed: bool,
    source_changed: bool,
) -> None:
    """Compare manifest provenance with the bytes used by this run."""
    manifest_file_status = manifest_row.get("file_status", "")

    if source_changed:
        reasons.add(SOURCE_IDENTITY_CHANGED)

    if source_read_failed:
        reasons.add(SOURCE_CHECKSUM_UNAVAILABLE)
        return

    if source_identity is None:
        if manifest_file_status != "missing_file":
            reasons.add(SOURCE_CHECKSUM_UNAVAILABLE)
        return

    if manifest_row.get("source_file_size_bytes") != source_identity.file_size_bytes:
        reasons.add(SOURCE_SIZE_MISMATCH)

    if (
        manifest_row.get("source_checksum_algorithm")
        != source_identity.checksum_algorithm
        or manifest_row.get("source_checksum") != source_identity.checksum
    ):
        reasons.add(SOURCE_CHECKSUM_MISMATCH)


def add_status_and_count_reasons(
    reasons: set[str],
    manifest_row: dict[str, str],
    session_row: dict[str, str],
) -> None:
    """Reconcile directly comparable statuses and counts."""
    session_status = session_row.get("status", "")
    manifest_file_status = manifest_row.get("file_status", "")

    if (
        session_status == "complete"
        and manifest_file_status in {"missing_file", "empty_file", "parse_failed"}
        and has_calculated_session_values(session_row)
    ):
        reasons.add(SESSION_VALUES_WITH_MANIFEST_FAILURE)

    if manifest_file_status == "processed" and session_status == "failed":
        reasons.add(MANIFEST_PROCESSED_SESSION_FAILED)

    if session_status == "missing_file" and manifest_file_status != "missing_file":
        reasons.add(STATUS_DISAGREEMENT)

    if manifest_file_status == "missing_file" and session_status != "missing_file":
        reasons.add(STATUS_DISAGREEMENT)

    if session_status == "no_active_candles" and manifest_file_status != "no_active_candles":
        reasons.add(STATUS_DISAGREEMENT)

    if manifest_file_status == "no_active_candles" and session_status != "no_active_candles":
        reasons.add(STATUS_DISAGREEMENT)

    manifest_total = manifest_row.get("total_row_count", "")
    session_total = session_row.get("total_csv_rows", "")

    if manifest_total and session_total and manifest_total != session_total:
        reasons.add(ROW_COUNT_MISMATCH)

    manifest_active = manifest_row.get("active_row_count", "")
    session_active = session_row.get("active_candle_count", "")

    if manifest_active and session_active and manifest_active != session_active:
        reasons.add(ACTIVE_COUNT_MISMATCH)


def collect_linkage_reasons(
    day: date,
    expected_filename: str,
    manifest_row: dict[str, str],
    session_row: dict[str, str],
    source_identity: SourceIdentity | None,
    source_read_failed: bool,
    source_changed: bool,
    source_contract: SourceContract = DEFAULT_SOURCE_CONTRACT,
) -> set[str]:
    """Collect deterministic linkage and reconciliation reason codes."""
    reasons: set[str] = set()
    expected_date = f"{day:%Y-%m-%d}"
    expected_weekday = day.strftime("%A")

    if (
        manifest_row.get("date") != expected_date
        or session_row.get("date") != expected_date
        or manifest_row.get("weekday") != expected_weekday
        or session_row.get("weekday") != expected_weekday
    ):
        reasons.add(DATE_COVERAGE_MISMATCH)

    add_source_contract_reasons(
        reasons,
        manifest_row,
        expected_filename,
        source_contract,
    )
    add_source_identity_reasons(
        reasons,
        manifest_row,
        source_identity,
        source_read_failed,
        source_changed,
    )
    add_status_and_count_reasons(reasons, manifest_row, session_row)

    return reasons


def determine_linkage_status(
    reasons: set[str],
    session_status: str,
    manifest_file_status: str,
) -> str:
    """Classify linkage and reconciliation status independently of quality."""
    if SOURCE_IDENTITY_CHANGED in reasons:
        return SOURCE_CHANGED

    if SOURCE_CHECKSUM_UNAVAILABLE in reasons:
        return SOURCE_UNAVAILABLE

    if reasons:
        return CONTRADICTION

    if (
        session_status == "missing_file"
        and manifest_file_status == "missing_file"
    ):
        return CALENDAR_ONLY

    if (
        session_status == "no_active_candles"
        and manifest_file_status == "no_active_candles"
    ):
        return CALENDAR_ONLY

    return LINKED


def classify_quality_tier(
    linkage_status: str,
    session_status: str,
    manifest_file_status: str,
    manifest_quality_status: str,
) -> str:
    """Classify default research usability without changing source statuses."""
    if linkage_status in {CONTRADICTION, SOURCE_CHANGED, SOURCE_UNAVAILABLE}:
        return EXCLUDED_UNUSABLE

    if (
        session_status == "complete"
        and manifest_file_status == "processed"
        and manifest_quality_status == "valid"
    ):
        return STRICT_VALID

    if (
        session_status == "complete"
        and manifest_file_status == "processed"
        and manifest_quality_status == "warning"
    ):
        return WARNING_REVIEW

    if (
        session_status in {"missing_file", "no_active_candles"}
        or manifest_file_status in {"missing_file", "no_active_candles"}
        or manifest_quality_status == "not_assessed"
    ):
        return CALENDAR_ONLY

    return EXCLUDED_UNUSABLE


def build_linked_row(
    day: date,
    manifest_row: dict[str, str],
    session_row: dict[str, str],
    source_identity: SourceIdentity | None,
    source_read_failed: bool,
    source_changed: bool,
    session_definition_checksum: str,
    software_revision: str,
    source_contract: SourceContract = DEFAULT_SOURCE_CONTRACT,
) -> dict[str, str]:
    """Build one linked report row from same-run manifest and session rows."""
    expected_filename = data_manifest.build_source_filename(day, source_contract)
    reasons = collect_linkage_reasons(
        day,
        expected_filename,
        manifest_row,
        session_row,
        source_identity,
        source_read_failed,
        source_changed,
        source_contract,
    )
    session_status = session_row.get("status", "")
    manifest_file_status = manifest_row.get("file_status", "")
    manifest_quality_status = manifest_row.get("quality_status", "")
    linkage_status = determine_linkage_status(
        reasons,
        session_status,
        manifest_file_status,
    )
    quality_tier = classify_quality_tier(
        linkage_status,
        session_status,
        manifest_file_status,
        manifest_quality_status,
    )
    row = {column: "" for column in LINKED_COLUMNS}

    row["linked_schema_version"] = LINKED_SCHEMA_VERSION
    row["date"] = f"{day:%Y-%m-%d}"
    row["weekday"] = day.strftime("%A")
    row["provider"] = manifest_row.get("provider", "")
    row["instrument"] = manifest_row.get("instrument", "")
    row["quote_side"] = manifest_row.get("quote_side", "")
    row["timeframe"] = manifest_row.get("timeframe", "")
    row["source_filename"] = manifest_row.get("source_filename", "")
    row["source_file_size_bytes"] = manifest_row.get("source_file_size_bytes", "")
    row["source_checksum_algorithm"] = manifest_row.get("source_checksum_algorithm", "")
    row["source_checksum"] = manifest_row.get("source_checksum", "")
    row["manifest_schema_version"] = manifest_row.get("manifest_schema_version", "")
    row["validation_rule_version"] = manifest_row.get("validation_rule_version", "")
    row["active_filter_rule_identity"] = ACTIVE_FILTER_RULE_IDENTITY
    row["session_definition_checksum"] = session_definition_checksum
    row["software_revision"] = software_revision
    row["session_status"] = session_status
    row["manifest_file_status"] = manifest_file_status
    row["manifest_quality_status"] = manifest_quality_status
    row["manifest_quality_reasons"] = manifest_row.get("quality_reasons", "")
    row["linkage_status"] = linkage_status
    row["linkage_reasons"] = ordered_linkage_reasons(reasons)
    row["quality_tier"] = quality_tier
    row["manifest_total_row_count"] = manifest_row.get("total_row_count", "")
    row["manifest_active_row_count"] = manifest_row.get("active_row_count", "")

    for source_column, linked_column in SESSION_COUNT_COLUMNS.items():
        row[linked_column] = session_row.get(source_column, "")

    for column in session_calculation_columns():
        row[column] = session_row.get(column, "")

    return row


def process_linked_day(
    day: date,
    data_dir: Path,
    session_columns: list[str],
    session_definition_checksum: str,
    software_revision: str,
    source_contract: SourceContract = DEFAULT_SOURCE_CONTRACT,
) -> dict[str, str]:
    """Process one requested date through both existing producers from one source."""
    source_path = data_manifest.build_source_path(data_dir, day, source_contract)

    if not source_path.exists():
        manifest_row = build_manifest_row_from_assessment(
            day,
            missing_file_assessment().fields,
            source_contract,
        )
        session_result = build_session_missing_row(day, session_columns)
        source_changed = source_path.exists()
        return build_linked_row(
            day,
            manifest_row,
            session_result.row,
            source_identity=None,
            source_read_failed=False,
            source_changed=source_changed,
            session_definition_checksum=session_definition_checksum,
            software_revision=software_revision,
            source_contract=source_contract,
        )

    try:
        raw_bytes = read_source_bytes(source_path)
    except OSError:
        manifest_row = build_manifest_row_from_assessment(
            day,
            parse_failed_assessment(None, READ_ERROR).fields,
            source_contract,
        )
        session_result = build_session_failed_row(day, session_columns)
        return build_linked_row(
            day,
            manifest_row,
            session_result.row,
            source_identity=None,
            source_read_failed=True,
            source_changed=False,
            session_definition_checksum=session_definition_checksum,
            software_revision=software_revision,
            source_contract=source_contract,
        )

    expected_filename = data_manifest.build_source_filename(day, source_contract)
    source_identity = source_identity_from_bytes(expected_filename, raw_bytes)
    manifest_row = build_manifest_row_from_assessment(
        day,
        assess_raw_csv_bytes(raw_bytes, day).fields,
        source_contract,
    )
    session_result = session_report.process_raw_bytes_for_day(
        day,
        session_columns,
        raw_bytes,
    )

    try:
        after_bytes = read_source_bytes(source_path)
    except OSError:
        source_changed = True
    else:
        after_identity = source_identity_from_bytes(expected_filename, after_bytes)
        source_changed = after_identity != source_identity

    return build_linked_row(
        day,
        manifest_row,
        session_result.row,
        source_identity=source_identity,
        source_read_failed=False,
        source_changed=source_changed,
        session_definition_checksum=session_definition_checksum,
        software_revision=software_revision,
        source_contract=source_contract,
    )


def validate_linked_rows_cover_requested_dates(
    rows: list[dict[str, str]],
    requested_days: list[date],
) -> None:
    """Reject dropped, duplicate, reordered, or extra linked dates."""
    expected_dates = [f"{day:%Y-%m-%d}" for day in requested_days]
    actual_dates = [row.get("date", "") for row in rows]

    if len(actual_dates) != len(expected_dates):
        raise ValueError("Linked report date coverage does not match requested dates.")

    duplicate_dates = {
        linked_date
        for linked_date, count in Counter(actual_dates).items()
        if count > 1
    }

    if duplicate_dates:
        raise ValueError(
            "Linked report contains duplicate date rows: "
            + ", ".join(sorted(duplicate_dates))
        )

    if actual_dates != expected_dates:
        raise ValueError("Linked report date coverage does not match requested dates.")


def write_linked_report(rows: list[dict[str, str]], output_path: Path) -> None:
    """Write linked rows atomically with the stable column order."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            "w",
            newline="",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as report_file:
            temporary_path = Path(report_file.name)
            writer = csv.DictWriter(report_file, fieldnames=LINKED_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
            report_file.flush()

        os.replace(temporary_path, output_path)
    except Exception as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass

        raise OSError(
            f"Failed to write linked report atomically: {output_path}: {error}"
        ) from error


def summarize_linked_report(
    rows: list[dict[str, str]],
    output_path: Path,
) -> LinkedReportSummary:
    """Count quality tiers for terminal reporting."""
    tier_counts = Counter(row["quality_tier"] for row in rows)

    return LinkedReportSummary(
        requested_dates=len(rows),
        strict_valid_observations=tier_counts[STRICT_VALID],
        warning_review_observations=tier_counts[WARNING_REVIEW],
        excluded_unusable_observations=tier_counts[EXCLUDED_UNUSABLE],
        calendar_only_observations=tier_counts[CALENDAR_ONLY],
        output_path=output_path,
    )


def create_linked_observation_report(
    start_day: date,
    end_day: date,
    data_dir: Path = DATA_RAW_DIR,
    source_contract: SourceContract = DEFAULT_SOURCE_CONTRACT,
    *,
    legacy_side_omitted: bool = True,
) -> LinkedReportSummary:
    """Create the linked daily/session observation report for a date range."""
    output_path = build_linked_report_path(
        start_day,
        end_day,
        source_contract,
        legacy_side_omitted=legacy_side_omitted,
    )
    requested_days = list(each_day(start_day, end_day))
    session_columns = validate_session_configuration(start_day)
    session_definition_checksum = calculate_session_definition_checksum()
    software_revision = get_software_revision()

    rows = [
        process_linked_day(
            day,
            data_dir,
            session_columns,
            session_definition_checksum,
            software_revision,
            source_contract,
        )
        for day in requested_days
    ]
    validate_linked_rows_cover_requested_dates(rows, requested_days)

    write_linked_report(rows, output_path)
    return summarize_linked_report(rows, output_path)


def print_summary(summary: LinkedReportSummary) -> None:
    """Print a concise linked-report completion summary."""
    print("Linked observation report complete.")
    print(f"Requested dates: {summary.requested_dates}")
    print(f"Strict-valid observations: {summary.strict_valid_observations}")
    print(f"Warning-review observations: {summary.warning_review_observations}")
    print(f"Excluded/unusable observations: {summary.excluded_unusable_observations}")
    print(f"Calendar-only observations: {summary.calendar_only_observations}")
    print(f"Output path: {summary.output_path}")


def print_usage() -> None:
    """Print the correct command format."""
    print(
        "Usage: python linked_observation_report.py "
        "YYYY-MM-DD YYYY-MM-DD [--data-dir DATA_DIR]"
    )
    print("Example: python linked_observation_report.py 2024-01-01 2024-01-31")
    print(
        "Example: python linked_observation_report.py "
        "2024-01-01 2024-01-31 --data-dir data_raw"
    )


def main() -> int:
    """Run the linked observation report tool from the command line."""
    try:
        linked_arguments = parse_arguments(sys.argv[1:])
        summary = create_linked_observation_report(
            linked_arguments.start_day,
            linked_arguments.end_day,
            linked_arguments.data_dir,
        )
    except ValueError as error:
        print(f"Input error: {error}")
        print()
        print_usage()
        return 1
    except OSError as error:
        print(f"File error: {error}")
        return 1

    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
