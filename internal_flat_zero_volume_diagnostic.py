"""Create a diagnostic report for internal flat zero-volume runs.

Usage:
    python internal_flat_zero_volume_diagnostic.py MANIFEST_CSV LINKED_CSV
    python internal_flat_zero_volume_diagnostic.py MANIFEST_CSV LINKED_CSV --data-dir data_raw

The report reads existing manifest, linked observation, and raw CSV files. It
does not download data, regenerate other reports, or change filtering policy.
"""

from __future__ import annotations

import csv
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from candle_filters import remove_edge_inactive_placeholders
from data_quality import (
    EXPECTED_COLUMNS,
    INTERNAL_FLAT_ZERO_VOLUME,
    format_timestamp,
    parse_data_row,
    split_csv_rows,
)
from session_tools import SessionWindow, get_session_windows


PROJECT_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = PROJECT_DIR / "data_raw"
REPORTS_DIR = PROJECT_DIR / "reports"

DIAGNOSTIC_SCHEMA_VERSION = "1"
EXPECTED_SESSION_NAMES = ["Tokyo", "London", "New York"]
SESSION_COUNT_COLUMNS = {
    "Tokyo": "tokyo_overlap_rows",
    "London": "london_overlap_rows",
    "New York": "new_york_overlap_rows",
}

MANIFEST_REQUIRED_COLUMNS = [
    "date",
    "weekday",
    "source_filename",
    "file_status",
    "quality_status",
    "quality_reasons",
    "total_row_count",
    "active_row_count",
    "leading_inactive_row_count",
    "trailing_inactive_row_count",
    "internal_inactive_row_count",
]

LINKED_REQUIRED_COLUMNS = [
    "date",
    "weekday",
    "quality_tier",
    "session_status",
    "daily_range",
    "tokyo_range",
    "london_range",
    "new_york_range",
    "tokyo_active_candle_count",
    "london_active_candle_count",
    "new_york_active_candle_count",
]

DIAGNOSTIC_COLUMNS = [
    "diagnostic_schema_version",
    "date",
    "weekday",
    "source_filename",
    "manifest_file_status",
    "manifest_quality_status",
    "manifest_quality_reasons",
    "total_row_count",
    "active_row_count",
    "leading_inactive_row_count",
    "trailing_inactive_row_count",
    "internal_inactive_row_count",
    "run_number",
    "run_start_utc",
    "run_end_utc",
    "run_row_count",
    "tokyo_overlap_rows",
    "london_overlap_rows",
    "new_york_overlap_rows",
    "outside_configured_session_rows",
    "linked_quality_tier",
    "linked_session_status",
    "daily_range",
    "tokyo_range",
    "london_range",
    "new_york_range",
    "tokyo_active_candle_count",
    "london_active_candle_count",
    "new_york_active_candle_count",
]


@dataclass(frozen=True)
class DiagnosticArguments:
    """Command-line arguments for one diagnostic run."""

    manifest_path: Path
    linked_report_path: Path
    data_dir: Path


@dataclass(frozen=True)
class DiagnosticSummary:
    """Summary printed after creating a diagnostic report."""

    manifest_rows_read: int
    warning_dates: int
    internal_flat_runs: int
    output_path: Path


@dataclass
class RawDiagnosticRow:
    """One raw CSV row reduced to the fields needed for this diagnostic."""

    timestamp_text: str
    timestamp: datetime | None
    is_flat_zero_volume: bool


@dataclass
class InternalFlatRun:
    """One contiguous internal flat zero-volume run."""

    rows: list[RawDiagnosticRow]

    @property
    def row_count(self) -> int:
        """Return the number of raw rows in the run."""
        return len(self.rows)

    @property
    def start_timestamp(self) -> datetime:
        """Return the first timestamp, failing clearly when it is unavailable."""
        timestamp = self.rows[0].timestamp
        if timestamp is None:
            raise ValueError("Internal flat zero-volume run has a blank start timestamp.")
        return timestamp

    @property
    def end_timestamp(self) -> datetime:
        """Return the final timestamp, failing clearly when it is unavailable."""
        timestamp = self.rows[-1].timestamp
        if timestamp is None:
            raise ValueError("Internal flat zero-volume run has a blank end timestamp.")
        return timestamp


def parse_day(day_text: str) -> date:
    """Convert text like '2024-01-31' into a Python date."""
    try:
        return datetime.strptime(day_text, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError(f"Date must use YYYY-MM-DD format: {day_text}") from error


def parse_arguments(arguments: list[str]) -> DiagnosticArguments:
    """Read manifest path, linked report path, and optional data directory."""
    if len(arguments) not in (2, 4):
        raise ValueError("Please provide a manifest CSV and linked observation CSV.")

    manifest_path = Path(arguments[0])
    linked_report_path = Path(arguments[1])
    data_dir = DATA_RAW_DIR

    if len(arguments) == 4:
        if arguments[2] != "--data-dir":
            raise ValueError("The only optional diagnostic flag is --data-dir.")
        data_dir = Path(arguments[3])

    if not manifest_path.exists():
        raise ValueError(f"Manifest CSV does not exist: {manifest_path}")
    if not manifest_path.is_file():
        raise ValueError(f"Manifest path is not a file: {manifest_path}")

    if not linked_report_path.exists():
        raise ValueError(f"Linked observation report does not exist: {linked_report_path}")
    if not linked_report_path.is_file():
        raise ValueError(f"Linked observation report path is not a file: {linked_report_path}")

    if not data_dir.exists():
        raise ValueError(f"Data directory does not exist: {data_dir}")
    if not data_dir.is_dir():
        raise ValueError(f"Data directory is not a folder: {data_dir}")

    return DiagnosticArguments(
        manifest_path=manifest_path,
        linked_report_path=linked_report_path,
        data_dir=data_dir,
    )


def read_required_csv_rows(
    csv_path: Path,
    required_columns: list[str],
    report_label: str,
) -> tuple[list[str], list[dict[str, str]]]:
    """Read one CSV and validate the columns this diagnostic needs."""
    with csv_path.open("r", newline="", encoding="utf-8") as report_file:
        reader = csv.DictReader(report_file)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not fieldnames:
        raise ValueError(f"Input {report_label} has no header row.")

    missing_columns = [
        column for column in required_columns if column not in fieldnames
    ]
    if missing_columns:
        raise ValueError(
            f"Input {report_label} is missing required columns: "
            + ", ".join(missing_columns)
        )

    if not rows:
        raise ValueError(f"Input {report_label} contains no data rows.")

    return fieldnames, rows


def date_values(rows: list[dict[str, str]], report_label: str) -> list[str]:
    """Return ordered date values, rejecting blanks, duplicates, and bad text."""
    values = []
    seen = set()
    duplicates = []

    for row in rows:
        date_text = row.get("date", "")
        if not date_text:
            raise ValueError(f"Input {report_label} contains a blank date.")
        parse_day(date_text)

        if date_text in seen:
            duplicates.append(date_text)
        seen.add(date_text)
        values.append(date_text)

    if duplicates:
        raise ValueError(
            f"Input {report_label} contains duplicate dates: "
            + ", ".join(sorted(set(duplicates)))
        )

    return values


def validate_compatible_date_coverage(
    manifest_rows: list[dict[str, str]],
    linked_rows: list[dict[str, str]],
) -> None:
    """Reject inputs that do not cover the same dates in the same order."""
    manifest_dates = date_values(manifest_rows, "manifest")
    linked_dates = date_values(linked_rows, "linked report")

    if manifest_dates != linked_dates:
        raise ValueError(
            "Manifest and linked report date coverage does not match."
        )

    for manifest_row, linked_row in zip(manifest_rows, linked_rows):
        if manifest_row.get("weekday", "") != linked_row.get("weekday", ""):
            raise ValueError(
                "Manifest and linked report weekday coverage does not match."
            )


def split_reason_codes(reason_text: str) -> list[str]:
    """Split manifest reason text into deterministic machine-readable codes."""
    return [reason for reason in reason_text.split(";") if reason]


def row_has_internal_flat_warning(row: dict[str, str]) -> bool:
    """Return True when the manifest row contains the diagnostic reason code."""
    return INTERNAL_FLAT_ZERO_VOLUME in split_reason_codes(
        row.get("quality_reasons", "")
    )


def read_raw_diagnostic_rows(raw_path: Path) -> list[RawDiagnosticRow]:
    """Read one raw CSV and mark flat zero-volume rows using current rules."""
    raw_bytes = raw_path.read_bytes()
    csv_parts = split_csv_rows(raw_bytes)

    if csv_parts is None:
        raise ValueError(f"Raw CSV could not be decoded as expected UTF-8 CSV: {raw_path}")

    header, raw_rows = csv_parts
    if header != EXPECTED_COLUMNS:
        raise ValueError(f"Raw CSV has an unexpected header: {raw_path}")

    diagnostic_rows = []
    for row_number, raw_row in enumerate(raw_rows, start=2):
        if len(raw_row) != len(EXPECTED_COLUMNS):
            raise ValueError(
                f"Raw CSV row {row_number} has an unexpected column count: {raw_path}"
            )

        parsed_row = parse_data_row(raw_row)
        diagnostic_rows.append(
            RawDiagnosticRow(
                timestamp_text=raw_row[0],
                timestamp=parsed_row.timestamp,
                is_flat_zero_volume=parsed_row.is_flat_zero_volume,
            )
        )

    return diagnostic_rows


def detect_internal_flat_runs(
    raw_rows: list[RawDiagnosticRow],
) -> list[InternalFlatRun]:
    """Return contiguous flat zero-volume runs after edge placeholders are removed."""
    active_result = remove_edge_inactive_placeholders(
        raw_rows,
        lambda row: row.is_flat_zero_volume,
    )
    runs = []
    current_run = []

    for row in active_result.active_rows:
        if row.is_flat_zero_volume:
            if row.timestamp is None:
                raise ValueError(
                    "Internal flat zero-volume row has an invalid timestamp: "
                    f"{row.timestamp_text}"
                )
            current_run.append(row)
            continue

        if current_run:
            runs.append(InternalFlatRun(rows=current_run))
            current_run = []

    if current_run:
        runs.append(InternalFlatRun(rows=current_run))

    return runs


def load_expected_session_windows(day: date) -> dict[str, SessionWindow]:
    """Load the configured sessions this deterministic schema reports."""
    windows = {window.name: window for window in get_session_windows(day)}
    missing_names = [
        session_name
        for session_name in EXPECTED_SESSION_NAMES
        if session_name not in windows
    ]

    if missing_names:
        raise ValueError(
            "Diagnostic requires configured sessions: "
            + ", ".join(EXPECTED_SESSION_NAMES)
        )

    return windows


def count_session_overlaps(
    run: InternalFlatRun,
    session_windows: dict[str, SessionWindow],
) -> dict[str, int]:
    """Count run rows that fall inside each configured session window."""
    counts = {session_name: 0 for session_name in EXPECTED_SESSION_NAMES}
    outside_count = 0

    for row in run.rows:
        if row.timestamp is None:
            raise ValueError(
                "Internal flat zero-volume row has an invalid timestamp: "
                f"{row.timestamp_text}"
            )

        matched_any_session = False
        for session_name in EXPECTED_SESSION_NAMES:
            window = session_windows[session_name]
            if window.start_utc <= row.timestamp < window.end_utc:
                counts[session_name] += 1
                matched_any_session = True

        if not matched_any_session:
            outside_count += 1

    counts["outside_configured_session_rows"] = outside_count
    return counts


def parse_count(value_text: str, field_name: str, day_text: str) -> int:
    """Parse one manifest count field."""
    try:
        return int(value_text)
    except ValueError as error:
        raise ValueError(
            f"Manifest {field_name} is not an integer for {day_text}: {value_text}"
        ) from error


def build_diagnostic_row(
    manifest_row: dict[str, str],
    linked_row: dict[str, str],
    run: InternalFlatRun,
    run_number: int,
    overlap_counts: dict[str, int],
) -> dict[str, str]:
    """Build one deterministic output row for one internal run."""
    row = {column: "" for column in DIAGNOSTIC_COLUMNS}
    row["diagnostic_schema_version"] = DIAGNOSTIC_SCHEMA_VERSION
    row["date"] = manifest_row["date"]
    row["weekday"] = manifest_row["weekday"]
    row["source_filename"] = manifest_row["source_filename"]
    row["manifest_file_status"] = manifest_row["file_status"]
    row["manifest_quality_status"] = manifest_row["quality_status"]
    row["manifest_quality_reasons"] = manifest_row["quality_reasons"]
    row["total_row_count"] = manifest_row["total_row_count"]
    row["active_row_count"] = manifest_row["active_row_count"]
    row["leading_inactive_row_count"] = manifest_row["leading_inactive_row_count"]
    row["trailing_inactive_row_count"] = manifest_row["trailing_inactive_row_count"]
    row["internal_inactive_row_count"] = manifest_row["internal_inactive_row_count"]
    row["run_number"] = str(run_number)
    row["run_start_utc"] = format_timestamp(run.start_timestamp)
    row["run_end_utc"] = format_timestamp(run.end_timestamp)
    row["run_row_count"] = str(run.row_count)

    for session_name, output_column in SESSION_COUNT_COLUMNS.items():
        row[output_column] = str(overlap_counts[session_name])
    row["outside_configured_session_rows"] = str(
        overlap_counts["outside_configured_session_rows"]
    )

    row["linked_quality_tier"] = linked_row["quality_tier"]
    row["linked_session_status"] = linked_row["session_status"]
    row["daily_range"] = linked_row["daily_range"]
    row["tokyo_range"] = linked_row["tokyo_range"]
    row["london_range"] = linked_row["london_range"]
    row["new_york_range"] = linked_row["new_york_range"]
    row["tokyo_active_candle_count"] = linked_row["tokyo_active_candle_count"]
    row["london_active_candle_count"] = linked_row["london_active_candle_count"]
    row["new_york_active_candle_count"] = linked_row["new_york_active_candle_count"]
    return row


def build_diagnostic_rows(
    manifest_rows: list[dict[str, str]],
    linked_rows_by_date: dict[str, dict[str, str]],
    data_dir: Path,
) -> list[dict[str, str]]:
    """Build one output row per detected internal flat zero-volume run."""
    diagnostic_rows = []

    for manifest_row in manifest_rows:
        if not row_has_internal_flat_warning(manifest_row):
            continue

        day_text = manifest_row["date"]
        day = parse_day(day_text)
        raw_path = data_dir / manifest_row["source_filename"]

        if not raw_path.exists():
            raise FileNotFoundError(
                f"Raw CSV for warning date is missing: {raw_path}"
            )

        raw_rows = read_raw_diagnostic_rows(raw_path)
        runs = detect_internal_flat_runs(raw_rows)
        detected_count = sum(run.row_count for run in runs)
        manifest_count = parse_count(
            manifest_row["internal_inactive_row_count"],
            "internal_inactive_row_count",
            day_text,
        )

        if detected_count != manifest_count:
            raise ValueError(
                "Manifest internal_inactive_row_count does not match detected "
                f"run rows for {day_text}: manifest {manifest_count}, "
                f"detected {detected_count}"
            )

        session_windows = load_expected_session_windows(day)
        linked_row = linked_rows_by_date[day_text]

        for run_number, run in enumerate(runs, start=1):
            overlap_counts = count_session_overlaps(run, session_windows)
            diagnostic_rows.append(
                build_diagnostic_row(
                    manifest_row,
                    linked_row,
                    run,
                    run_number,
                    overlap_counts,
                )
            )

    return diagnostic_rows


def build_diagnostic_report_path(
    manifest_rows: list[dict[str, str]],
) -> Path:
    """Build the deterministic output path from input date coverage."""
    first_day = parse_day(manifest_rows[0]["date"])
    last_day = parse_day(manifest_rows[-1]["date"])
    filename = (
        f"internal_flat_zero_volume_diagnostic_{first_day:%Y-%m-%d}"
        f"_to_{last_day:%Y-%m-%d}.csv"
    )
    return REPORTS_DIR / filename


def write_diagnostic_report(
    rows: list[dict[str, str]],
    output_path: Path,
) -> None:
    """Write diagnostic rows atomically with the stable column order."""
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
            writer = csv.DictWriter(report_file, fieldnames=DIAGNOSTIC_COLUMNS)
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
            f"Failed to write diagnostic report atomically: {output_path}: {error}"
        ) from error


def create_internal_flat_zero_volume_diagnostic(
    manifest_path: Path,
    linked_report_path: Path,
    data_dir: Path = DATA_RAW_DIR,
) -> DiagnosticSummary:
    """Create the internal flat zero-volume diagnostic from existing files."""
    _manifest_columns, manifest_rows = read_required_csv_rows(
        manifest_path,
        MANIFEST_REQUIRED_COLUMNS,
        "manifest",
    )
    _linked_columns, linked_rows = read_required_csv_rows(
        linked_report_path,
        LINKED_REQUIRED_COLUMNS,
        "linked report",
    )
    validate_compatible_date_coverage(manifest_rows, linked_rows)

    linked_rows_by_date = {row["date"]: row for row in linked_rows}
    diagnostic_rows = build_diagnostic_rows(
        manifest_rows,
        linked_rows_by_date,
        data_dir,
    )
    output_path = build_diagnostic_report_path(manifest_rows)
    write_diagnostic_report(diagnostic_rows, output_path)

    return DiagnosticSummary(
        manifest_rows_read=len(manifest_rows),
        warning_dates=sum(1 for row in manifest_rows if row_has_internal_flat_warning(row)),
        internal_flat_runs=len(diagnostic_rows),
        output_path=output_path,
    )


def print_summary(summary: DiagnosticSummary) -> None:
    """Print a concise diagnostic completion summary."""
    print("Internal flat zero-volume diagnostic complete.")
    print(f"Manifest rows read: {summary.manifest_rows_read}")
    print(f"Warning dates: {summary.warning_dates}")
    print(f"Internal flat runs: {summary.internal_flat_runs}")
    print(f"Output path: {summary.output_path}")


def print_usage() -> None:
    """Print the correct command format."""
    print(
        "Usage: python internal_flat_zero_volume_diagnostic.py "
        "MANIFEST_CSV LINKED_OBSERVATION_REPORT_CSV [--data-dir DATA_DIR]"
    )
    print(
        "Example: python internal_flat_zero_volume_diagnostic.py "
        "reports/data_manifest_2024-01-01_to_2024-01-31.csv "
        "reports/linked_observation_report_2024-01-01_to_2024-01-31.csv "
        "--data-dir data_raw"
    )


def main(arguments: list[str] | None = None) -> int:
    """Run the diagnostic tool from the command line."""
    if arguments is None:
        arguments = sys.argv[1:]

    try:
        diagnostic_arguments = parse_arguments(arguments)
        summary = create_internal_flat_zero_volume_diagnostic(
            diagnostic_arguments.manifest_path,
            diagnostic_arguments.linked_report_path,
            diagnostic_arguments.data_dir,
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
