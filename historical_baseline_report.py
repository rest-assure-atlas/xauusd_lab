"""
Create a descriptive historical baseline from one linked observation report.

Usage:
    python historical_baseline_report.py reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

import linked_observation_report as linked_report
from source_contracts import SourceContractError, validate_quote_side


PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"

BASELINE_SCHEMA_VERSION = "1"
DECIMAL_PLACES = Decimal("0.001")

BASELINE_COLUMNS = [
    "baseline_schema_version",
    "source_report",
    "provider",
    "instrument",
    "quote_side",
    "timeframe",
    "metric_section",
    "metric_name",
    "observation_group",
    "reason_code",
    "field_name",
    "count",
    "min",
    "median",
    "mean",
    "max",
    "notes",
]

COVERAGE_FIELDS = [
    "quality_tier",
    "linkage_status",
    "session_status",
    "manifest_file_status",
    "manifest_quality_status",
    "manifest_quality_reasons",
    "linkage_reasons",
]

RANGE_FIELDS = [
    "daily_range",
    "tokyo_range",
    "london_range",
    "new_york_range",
]

REQUIRED_LINKED_COLUMNS = [
    "linked_schema_version",
    "date",
    "weekday",
    "provider",
    "instrument",
    "quote_side",
    "timeframe",
    "source_filename",
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
    *RANGE_FIELDS,
]

REQUIRED_NONBLANK_FIELDS = [
    "linked_schema_version",
    "date",
    "weekday",
    "provider",
    "instrument",
    "quote_side",
    "timeframe",
    "source_filename",
    "manifest_schema_version",
    "validation_rule_version",
    "active_filter_rule_identity",
    "session_definition_checksum",
    "software_revision",
    "session_status",
    "manifest_file_status",
    "manifest_quality_status",
    "linkage_status",
    "quality_tier",
]

QUALITY_TIER_ORDER = [
    linked_report.STRICT_VALID,
    linked_report.WARNING_REVIEW,
    linked_report.CALENDAR_ONLY,
    linked_report.EXCLUDED_UNUSABLE,
]

VALUE_ORDER = {
    "quality_tier": QUALITY_TIER_ORDER,
    "linkage_status": [
        linked_report.LINKED,
        linked_report.CALENDAR_ONLY,
        linked_report.CONTRADICTION,
        linked_report.SOURCE_CHANGED,
        linked_report.SOURCE_UNAVAILABLE,
    ],
    "session_status": [
        "complete",
        "missing_file",
        "no_active_candles",
        "failed",
    ],
    "manifest_file_status": [
        "processed",
        "missing_file",
        "empty_file",
        "parse_failed",
        "no_active_candles",
    ],
    "manifest_quality_status": [
        "valid",
        "warning",
        "invalid",
        "not_assessed",
    ],
}


@dataclass(frozen=True)
class BaselineArguments:
    """Command-line arguments for one historical baseline report."""

    linked_report_path: Path


@dataclass(frozen=True)
class BaselineSummary:
    """Summary printed after creating a historical baseline report."""

    source_report: Path
    rows_read: int
    strict_valid_observations: int
    warning_review_observations: int
    calendar_only_observations: int
    excluded_unusable_observations: int
    output_path: Path


def parse_arguments(arguments: list[str]) -> BaselineArguments:
    """Read the linked observation report path from the command line."""
    if len(arguments) != 1:
        raise ValueError("Please provide exactly one linked observation report CSV path.")

    linked_report_path = Path(arguments[0])

    if not linked_report_path.exists():
        raise ValueError(f"Linked observation report does not exist: {linked_report_path}")

    if not linked_report_path.is_file():
        raise ValueError(f"Linked observation report path is not a file: {linked_report_path}")

    return BaselineArguments(linked_report_path=linked_report_path)


def build_baseline_report_path(linked_report_path: Path) -> Path:
    """Build the deterministic output path for one baseline report."""
    return REPORTS_DIR / f"historical_baseline_{linked_report_path.stem}.csv"


def read_linked_rows(linked_report_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read an existing linked observation report without regenerating anything."""
    with linked_report_path.open("r", newline="", encoding="utf-8") as report_file:
        reader = csv.DictReader(report_file)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not fieldnames:
        raise ValueError("Input linked report has no header row.")

    if not rows:
        raise ValueError("Input linked report contains no data rows.")

    return fieldnames, rows


def validate_linked_report_rows(
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> None:
    """Validate the linked-report fields required by the baseline."""
    missing_columns = [
        column for column in REQUIRED_LINKED_COLUMNS if column not in fieldnames
    ]

    if missing_columns:
        raise ValueError(
            "Input linked report is missing required columns: "
            + ", ".join(missing_columns)
        )

    seen_dates: set[str] = set()
    expected_source_identity: dict[str, str] | None = None

    for row_number, row in enumerate(rows, start=2):
        if row["linked_schema_version"] != linked_report.LINKED_SCHEMA_VERSION:
            raise ValueError(
                "Unsupported linked_schema_version on row "
                f"{row_number}: {row['linked_schema_version']}"
            )

        date_text = row["date"]
        if date_text in seen_dates:
            raise ValueError(f"Duplicate date in linked report: {date_text}")
        seen_dates.add(date_text)

        blank_fields = [
            field for field in REQUIRED_NONBLANK_FIELDS if row.get(field, "") == ""
        ]
        if blank_fields:
            raise ValueError(
                f"Unexpected blank required field on row {row_number}: "
                + ", ".join(blank_fields)
            )

        try:
            validate_quote_side(row["quote_side"])
        except SourceContractError as error:
            raise ValueError(
                f"Unsupported quote_side on row {row_number}: {row['quote_side']}"
            ) from error

        row_source_identity = {
            field: row[field]
            for field in ("provider", "instrument", "quote_side", "timeframe")
        }
        if expected_source_identity is None:
            expected_source_identity = row_source_identity
        elif row_source_identity != expected_source_identity:
            mismatched_fields = [
                field
                for field, expected_value in expected_source_identity.items()
                if row_source_identity[field] != expected_value
            ]
            raise ValueError(
                "Input linked report mixes source identity on row "
                f"{row_number}: " + ", ".join(mismatched_fields)
            )


def source_identity_from_rows(linked_rows: list[dict[str, str]]) -> dict[str, str]:
    """Return the already-validated source identity for one linked report."""
    first_row = linked_rows[0]
    return {
        field: first_row[field]
        for field in ("provider", "instrument", "quote_side", "timeframe")
    }


def blank_metric_row(source_report: str, source_identity: dict[str, str]) -> dict[str, str]:
    """Return an empty baseline metric row with stable common fields."""
    return {
        "baseline_schema_version": BASELINE_SCHEMA_VERSION,
        "source_report": source_report,
        "provider": source_identity["provider"],
        "instrument": source_identity["instrument"],
        "quote_side": source_identity["quote_side"],
        "timeframe": source_identity["timeframe"],
        "metric_section": "",
        "metric_name": "",
        "observation_group": "",
        "reason_code": "",
        "field_name": "",
        "count": "",
        "min": "",
        "median": "",
        "mean": "",
        "max": "",
        "notes": "",
    }


def label_blank(value: str) -> str:
    """Use a readable deterministic label for blank coverage values."""
    if value == "":
        return "blank"

    return value


def ordered_values(field_name: str, counts: Counter[str]) -> list[str]:
    """Return coverage values in a stable, human-friendly order."""
    configured_order = VALUE_ORDER.get(field_name, [])
    configured_values = [value for value in configured_order if value in counts]
    remaining_values = [
        value for value in counts if value not in configured_order
    ]
    remaining_values.sort(key=lambda value: (value != "", value))
    return configured_values + remaining_values


def split_reason_codes(reason_text: str) -> list[str]:
    """Split semicolon-separated linked or manifest reason codes."""
    return [reason for reason in reason_text.split(";") if reason]


def add_coverage_rows(
    baseline_rows: list[dict[str, str]],
    source_report: str,
    source_identity: dict[str, str],
    linked_rows: list[dict[str, str]],
) -> None:
    """Append deterministic coverage count rows."""
    for field_name in COVERAGE_FIELDS:
        counts = Counter(row[field_name] for row in linked_rows)

        for value in ordered_values(field_name, counts):
            baseline_row = blank_metric_row(source_report, source_identity)
            baseline_row["metric_section"] = "coverage"
            baseline_row["metric_name"] = f"row_count_by_{field_name}"
            baseline_row["observation_group"] = label_blank(value)
            baseline_row["field_name"] = field_name
            baseline_row["count"] = str(counts[value])
            baseline_rows.append(baseline_row)

    for field_name in ("manifest_quality_reasons", "linkage_reasons"):
        reason_counts: Counter[str] = Counter()
        for row in linked_rows:
            reason_counts.update(split_reason_codes(row[field_name]))

        for reason_code in sorted(reason_counts):
            baseline_row = blank_metric_row(source_report, source_identity)
            baseline_row["metric_section"] = "coverage"
            baseline_row["metric_name"] = f"row_count_by_{field_name}_reason_code"
            baseline_row["observation_group"] = "all"
            baseline_row["reason_code"] = reason_code
            baseline_row["field_name"] = field_name
            baseline_row["count"] = str(reason_counts[reason_code])
            baseline_row["notes"] = "reason codes are split on semicolons"
            baseline_rows.append(baseline_row)


def parse_decimal_value(row: dict[str, str], field_name: str) -> Decimal | None:
    """Parse one range value, treating blank text as unavailable."""
    value_text = row[field_name]
    if value_text == "":
        return None

    try:
        return Decimal(value_text)
    except InvalidOperation as error:
        date_text = row.get("date", "unknown date")
        raise ValueError(
            f"Non-numeric value in {field_name} on {date_text}: {value_text}"
        ) from error


def numeric_values(
    rows: list[dict[str, str]],
    field_name: str,
) -> list[Decimal]:
    """Return parsed numeric values for one range field."""
    values: list[Decimal] = []

    for row in rows:
        value = parse_decimal_value(row, field_name)
        if value is not None:
            values.append(value)

    return values


def format_decimal(value: Decimal) -> str:
    """Format descriptive range metrics to the report's three-decimal style."""
    return f"{value.quantize(DECIMAL_PLACES, rounding=ROUND_HALF_UP):.3f}"


def median_decimal(values: list[Decimal]) -> Decimal:
    """Calculate a deterministic median for already-sorted Decimal values."""
    midpoint = len(values) // 2

    if len(values) % 2:
        return values[midpoint]

    return (values[midpoint - 1] + values[midpoint]) / Decimal("2")


def add_range_summary_row(
    baseline_rows: list[dict[str, str]],
    source_report: str,
    source_identity: dict[str, str],
    metric_name: str,
    observation_group: str,
    reason_code: str,
    field_name: str,
    values: list[Decimal],
    notes: str,
) -> None:
    """Append one numeric range summary row."""
    baseline_row = blank_metric_row(source_report, source_identity)
    baseline_row["metric_section"] = "range_summary"
    baseline_row["metric_name"] = metric_name
    baseline_row["observation_group"] = observation_group
    baseline_row["reason_code"] = reason_code
    baseline_row["field_name"] = field_name
    baseline_row["count"] = str(len(values))
    baseline_row["notes"] = notes

    if values:
        sorted_values = sorted(values)
        baseline_row["min"] = format_decimal(sorted_values[0])
        baseline_row["median"] = format_decimal(median_decimal(sorted_values))
        baseline_row["mean"] = format_decimal(sum(sorted_values) / len(sorted_values))
        baseline_row["max"] = format_decimal(sorted_values[-1])

    baseline_rows.append(baseline_row)


def add_range_summary_rows(
    baseline_rows: list[dict[str, str]],
    source_report: str,
    source_identity: dict[str, str],
    linked_rows: list[dict[str, str]],
) -> None:
    """Append strict and warning-review range summaries."""
    strict_rows = [
        row for row in linked_rows if row["quality_tier"] == linked_report.STRICT_VALID
    ]
    warning_rows = [
        row for row in linked_rows if row["quality_tier"] == linked_report.WARNING_REVIEW
    ]

    for field_name in RANGE_FIELDS:
        add_range_summary_row(
            baseline_rows,
            source_report,
            source_identity,
            "range_summary",
            linked_report.STRICT_VALID,
            "",
            field_name,
            numeric_values(strict_rows, field_name),
            "headline baseline uses strict-valid observations only",
        )
        add_range_summary_row(
            baseline_rows,
            source_report,
            source_identity,
            "range_summary",
            linked_report.WARNING_REVIEW,
            "",
            field_name,
            numeric_values(warning_rows, field_name),
            "warning-review observations are reported separately",
        )

        reason_codes = sorted(
            {
                reason_code
                for row in warning_rows
                for reason_code in split_reason_codes(row["manifest_quality_reasons"])
            }
        )
        for reason_code in reason_codes:
            reason_rows = [
                row
                for row in warning_rows
                if reason_code in split_reason_codes(row["manifest_quality_reasons"])
            ]
            add_range_summary_row(
                baseline_rows,
                source_report,
                source_identity,
                "range_summary_by_warning_reason",
                linked_report.WARNING_REVIEW,
                reason_code,
                field_name,
                numeric_values(reason_rows, field_name),
                "warning reason is retained; no warning is classified as harmless",
            )


def rows_for_observation_group(
    linked_rows: list[dict[str, str]],
    observation_group: str,
) -> list[dict[str, str]]:
    """Return rows for one availability observation group."""
    if observation_group == "all":
        return linked_rows

    return [row for row in linked_rows if row["quality_tier"] == observation_group]


def add_availability_rows(
    baseline_rows: list[dict[str, str]],
    source_report: str,
    source_identity: dict[str, str],
    linked_rows: list[dict[str, str]],
) -> None:
    """Append numeric value and blank availability counts."""
    for observation_group in ["all", *QUALITY_TIER_ORDER]:
        group_rows = rows_for_observation_group(linked_rows, observation_group)

        for field_name in RANGE_FIELDS:
            usable_count = len(numeric_values(group_rows, field_name))
            blank_count = sum(1 for row in group_rows if row[field_name] == "")

            for metric_name, count in (
                ("usable_numeric_value_count", usable_count),
                ("blank_value_count", blank_count),
            ):
                baseline_row = blank_metric_row(source_report, source_identity)
                baseline_row["metric_section"] = "availability"
                baseline_row["metric_name"] = metric_name
                baseline_row["observation_group"] = observation_group
                baseline_row["field_name"] = field_name
                baseline_row["count"] = str(count)
                baseline_row["notes"] = "blank range values are unavailable, not zero"
                baseline_rows.append(baseline_row)


def build_baseline_rows(
    linked_rows: list[dict[str, str]],
    source_report: str,
) -> list[dict[str, str]]:
    """Build all baseline metric rows from already-validated linked rows."""
    source_identity = source_identity_from_rows(linked_rows)
    baseline_rows: list[dict[str, str]] = []
    add_coverage_rows(baseline_rows, source_report, source_identity, linked_rows)
    add_availability_rows(baseline_rows, source_report, source_identity, linked_rows)
    add_range_summary_rows(baseline_rows, source_report, source_identity, linked_rows)
    return baseline_rows


def write_baseline_report(rows: list[dict[str, str]], output_path: Path) -> None:
    """Write the deterministic baseline CSV report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as report_file:
        writer = csv.DictWriter(report_file, fieldnames=BASELINE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def summarize_baseline_report(
    linked_report_path: Path,
    linked_rows: list[dict[str, str]],
    output_path: Path,
) -> BaselineSummary:
    """Build the terminal summary for one baseline report."""
    tier_counts = Counter(row["quality_tier"] for row in linked_rows)

    return BaselineSummary(
        source_report=linked_report_path,
        rows_read=len(linked_rows),
        strict_valid_observations=tier_counts[linked_report.STRICT_VALID],
        warning_review_observations=tier_counts[linked_report.WARNING_REVIEW],
        calendar_only_observations=tier_counts[linked_report.CALENDAR_ONLY],
        excluded_unusable_observations=tier_counts[linked_report.EXCLUDED_UNUSABLE],
        output_path=output_path,
    )


def create_historical_baseline_report(
    linked_report_path: Path,
) -> BaselineSummary:
    """Create a descriptive baseline from one existing linked report CSV."""
    fieldnames, linked_rows = read_linked_rows(linked_report_path)
    validate_linked_report_rows(fieldnames, linked_rows)

    source_report = linked_report_path.name
    baseline_rows = build_baseline_rows(linked_rows, source_report)
    output_path = build_baseline_report_path(linked_report_path)
    write_baseline_report(baseline_rows, output_path)

    return summarize_baseline_report(linked_report_path, linked_rows, output_path)


def print_summary(summary: BaselineSummary) -> None:
    """Print a concise descriptive baseline summary."""
    print("Historical baseline report complete.")
    print(f"Source report: {summary.source_report}")
    print(f"Linked rows read: {summary.rows_read}")
    print(f"Strict-valid observations: {summary.strict_valid_observations}")
    print(f"Warning-review observations: {summary.warning_review_observations}")
    print(f"Calendar-only observations: {summary.calendar_only_observations}")
    print(f"Excluded/unusable observations: {summary.excluded_unusable_observations}")
    print("Headline numeric baseline: strict_valid observations only.")
    print("Warning-review numeric summaries are reported separately.")
    print(f"Output path: {summary.output_path}")


def print_usage() -> None:
    """Print the correct command format."""
    print("Usage: python historical_baseline_report.py LINKED_OBSERVATION_REPORT_CSV")
    print(
        "Example: python historical_baseline_report.py "
        "reports/linked_observation_report_2024-01-01_to_2024-01-31.csv"
    )


def main(arguments: list[str] | None = None) -> int:
    """Run the historical baseline report tool from the command line."""
    if arguments is None:
        arguments = sys.argv[1:]

    try:
        baseline_arguments = parse_arguments(arguments)
        summary = create_historical_baseline_report(
            baseline_arguments.linked_report_path
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
