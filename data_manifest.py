"""Create a data quality and provenance manifest for raw XAU/USD CSV files.

Usage:
    python data_manifest.py 2024-01-01 2024-01-31
    python data_manifest.py 2024-01-01 2024-01-31 --data-dir data_raw
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from data_quality import (
    ASSESSMENT_COLUMNS,
    INSTRUMENT,
    MANIFEST_SCHEMA_VERSION,
    PROVIDER,
    QUOTE_SIDE,
    TIMEFRAME,
    VALIDATION_RULE_VERSION,
    assess_raw_csv_file,
    missing_file_assessment,
)


PROJECT_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = PROJECT_DIR / "data_raw"
REPORTS_DIR = PROJECT_DIR / "reports"

MANIFEST_COLUMNS = [
    "manifest_schema_version",
    "validation_rule_version",
    "date",
    "weekday",
    "provider",
    "instrument",
    "quote_side",
    "timeframe",
    "source_filename",
    *ASSESSMENT_COLUMNS,
]


@dataclass
class ManifestArguments:
    """Command-line arguments for one manifest run."""

    start_day: date
    end_day: date
    data_dir: Path


@dataclass
class ManifestSummary:
    """Counts printed after a manifest run finishes."""

    requested_dates: int
    processed_files: int
    missing_files: int
    empty_files: int
    parse_failures: int
    no_active_candle_files: int
    valid_dates: int
    warning_dates: int
    invalid_dates: int
    not_assessed_dates: int
    output_path: Path


def parse_day(day_text: str) -> date:
    """Convert text like '2024-01-31' into a Python date."""
    try:
        return datetime.strptime(day_text, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError("Please enter dates in YYYY-MM-DD format.") from error


def parse_arguments(arguments: list[str]) -> ManifestArguments:
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
            raise ValueError("The only optional manifest flag is --data-dir.")

        data_dir = Path(arguments[3])

    if not data_dir.exists():
        raise ValueError(f"Data directory does not exist: {data_dir}")

    if not data_dir.is_dir():
        raise ValueError(f"Data directory is not a folder: {data_dir}")

    return ManifestArguments(
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


def build_source_filename(day: date) -> str:
    """Build the expected raw CSV basename for one requested day."""
    return f"XAUUSD_{day:%Y-%m-%d}_1min_BID_UTC.csv"


def build_source_path(data_dir: Path, day: date) -> Path:
    """Build the expected raw CSV path for one requested day."""
    return data_dir / build_source_filename(day)


def build_manifest_path(start_day: date, end_day: date) -> Path:
    """Build the deterministic output path for a manifest date range."""
    filename = f"data_manifest_{start_day:%Y-%m-%d}_to_{end_day:%Y-%m-%d}.csv"
    return REPORTS_DIR / filename


def base_manifest_row(day: date) -> dict[str, str]:
    """Create one manifest row with stable source metadata filled in."""
    row = {column: "" for column in MANIFEST_COLUMNS}
    row["manifest_schema_version"] = MANIFEST_SCHEMA_VERSION
    row["validation_rule_version"] = VALIDATION_RULE_VERSION
    row["date"] = f"{day:%Y-%m-%d}"
    row["weekday"] = day.strftime("%A")
    row["provider"] = PROVIDER
    row["instrument"] = INSTRUMENT
    row["quote_side"] = QUOTE_SIDE
    row["timeframe"] = TIMEFRAME
    row["source_filename"] = build_source_filename(day)
    return row


def build_manifest_row(data_dir: Path, day: date) -> dict[str, str]:
    """Build one manifest row for a requested calendar date."""
    row = base_manifest_row(day)
    source_path = build_source_path(data_dir, day)

    if source_path.exists():
        assessment = assess_raw_csv_file(source_path, day)
    else:
        assessment = missing_file_assessment()

    row.update(assessment.fields)
    return row


def write_manifest(rows: list[dict[str, str]], output_path: Path) -> None:
    """Write manifest rows with the stable column order."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as manifest_file:
        writer = csv.DictWriter(manifest_file, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def summarize_manifest(rows: list[dict[str, str]], output_path: Path) -> ManifestSummary:
    """Count file and quality statuses for terminal reporting."""
    file_status_counts = Counter(row["file_status"] for row in rows)
    quality_status_counts = Counter(row["quality_status"] for row in rows)

    return ManifestSummary(
        requested_dates=len(rows),
        processed_files=file_status_counts["processed"],
        missing_files=file_status_counts["missing_file"],
        empty_files=file_status_counts["empty_file"],
        parse_failures=file_status_counts["parse_failed"],
        no_active_candle_files=file_status_counts["no_active_candles"],
        valid_dates=quality_status_counts["valid"],
        warning_dates=quality_status_counts["warning"],
        invalid_dates=quality_status_counts["invalid"],
        not_assessed_dates=quality_status_counts["not_assessed"],
        output_path=output_path,
    )


def create_data_manifest(
    start_day: date,
    end_day: date,
    data_dir: Path = DATA_RAW_DIR,
) -> ManifestSummary:
    """Create a full data quality manifest for an inclusive date range."""
    days = list(each_day(start_day, end_day))
    rows = [build_manifest_row(data_dir, day) for day in days]
    output_path = build_manifest_path(start_day, end_day)
    write_manifest(rows, output_path)
    return summarize_manifest(rows, output_path)


def print_summary(summary: ManifestSummary) -> None:
    """Print the required manifest completion summary."""
    print("Data manifest complete.")
    print(f"Requested dates: {summary.requested_dates}")
    print(f"Processed files: {summary.processed_files}")
    print(f"Missing files: {summary.missing_files}")
    print(f"Empty files: {summary.empty_files}")
    print(f"Parse failures: {summary.parse_failures}")
    print(f"No-active-candle files: {summary.no_active_candle_files}")
    print(f"Valid dates: {summary.valid_dates}")
    print(f"Warning dates: {summary.warning_dates}")
    print(f"Invalid dates: {summary.invalid_dates}")
    print(f"Not-assessed dates: {summary.not_assessed_dates}")
    print(f"Output path: {summary.output_path}")


def print_usage() -> None:
    """Print the correct command format."""
    print("Usage: python data_manifest.py YYYY-MM-DD YYYY-MM-DD [--data-dir DATA_DIR]")
    print("Example: python data_manifest.py 2024-01-01 2024-01-31")
    print("Example: python data_manifest.py 2024-01-01 2024-01-31 --data-dir data_raw")


def main() -> int:
    """Run the manifest tool from the command line."""
    try:
        manifest_arguments = parse_arguments(sys.argv[1:])
        summary = create_data_manifest(
            manifest_arguments.start_day,
            manifest_arguments.end_day,
            manifest_arguments.data_dir,
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
