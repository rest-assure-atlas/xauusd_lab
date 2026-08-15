"""Describe close-price BID/ASK spreads from the three-day reconciliation pilot."""

from __future__ import annotations

import csv
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from session_tools import get_session_windows


PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"
INPUT_PATH = REPORTS_DIR / "bid_ask_reconciliation_2024-01-09_to_2024-01-11.csv"
SUMMARY_PATH = REPORTS_DIR / "spread_characterization_2024-01-09_to_2024-01-11_summary.csv"
WIDE_OBSERVATIONS_PATH = REPORTS_DIR / "spread_characterization_2024-01-09_to_2024-01-11_wide_observations.csv"

EXPECTED_DATES = {"2024-01-09", "2024-01-10", "2024-01-11"}
EXPECTED_ROWS = 4320
EXPECTED_PROVIDER = "Dukascopy"
EXPECTED_INSTRUMENT = "XAUUSD"
EXPECTED_TIMEFRAME = "1min"
EXPECTED_PAIR_STATUS = "warning_review_pair"
PLACEHOLDER_REASON = "MARKET_CLOSED_PLACEHOLDER"
EXTREME_REASON = "EXTREME_SPREAD"
NEGATIVE_REASON = "NEGATIVE_SPREAD"
ZERO_REASON = "ZERO_SPREAD"

SUMMARY_COLUMNS = [
    "sample_start",
    "sample_end",
    "sample_days",
    "interpretation_scope",
    "session_window_type",
    "session_window_exclusive",
    "population", "group_type", "group_value", "count", "placeholder_count",
    "min_spread", "p05_spread", "p25_spread", "median_spread", "mean_spread",
    "p75_spread", "p95_spread", "p99_spread", "max_spread", "stddev_spread",
    "min_spread_bid_bps", "p05_spread_bid_bps", "p25_spread_bid_bps",
    "median_spread_bid_bps", "mean_spread_bid_bps", "p75_spread_bid_bps",
    "p95_spread_bid_bps", "p99_spread_bid_bps", "max_spread_bid_bps",
    "stddev_spread_bid_bps",
]

METADATA_FIELDS = {
    "sample_start": "2024-01-09",
    "sample_end": "2024-01-11",
    "sample_days": "3",
    "interpretation_scope": "descriptive_pilot_not_execution_realism",
}
SESSION_WINDOW_TYPE = "overlapping_research_window"
SESSION_WINDOW_EXCLUSIVE = "false"


@dataclass(frozen=True)
class CharacterizationResult:
    input_path: Path
    summary_path: Path
    wide_observations_path: Path
    rows: int
    placeholder_rows: int
    pair_status_counts: dict[str, int]
    negative_spreads: int
    zero_spreads: int
    extreme_spreads: int
    provenance_identities: set[tuple[str, str, str]]


@dataclass(frozen=True)
class CharacterizationExpectations:
    start_day: date
    end_day: date
    expected_pair_status: str = EXPECTED_PAIR_STATUS

    @property
    def expected_dates(self) -> set[str]:
        return {f"{day:%Y-%m-%d}" for day in each_day(self.start_day, self.end_day)}

    @property
    def expected_rows(self) -> int:
        return len(self.expected_dates) * 1440

    @property
    def metadata_fields(self) -> dict[str, str]:
        return {
            "sample_start": f"{self.start_day:%Y-%m-%d}",
            "sample_end": f"{self.end_day:%Y-%m-%d}",
            "sample_days": str(len(self.expected_dates)),
            "interpretation_scope": "descriptive_pilot_not_execution_realism",
        }


def parse_decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid decimal value: {value!r}") from error


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


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


def is_placeholder(row: dict[str, str]) -> bool:
    return PLACEHOLDER_REASON in row.get("pair_quality_reasons", "").split(";")


def validate_input(rows: list[dict[str, str]], expectations: CharacterizationExpectations | None = None) -> None:
    if expectations is None:
        expectations = CharacterizationExpectations(date(2024, 1, 9), date(2024, 1, 11))
    expected_rows = expectations.expected_rows
    expected_dates = expectations.expected_dates
    pair_status_counts = Counter(row.get("pair_quality_status", "") for row in rows)
    if pair_status_counts and set(pair_status_counts) != {expectations.expected_pair_status}:
        raise ValueError(f"Unexpected pair-quality population: {dict(pair_status_counts)}")
    for row in rows:
        reasons = row.get("pair_quality_reasons", "").split(";")
        if NEGATIVE_REASON in reasons or ZERO_REASON in reasons or EXTREME_REASON in reasons:
            raise ValueError("Reconciliation anomaly reason found where none was expected.")
    if len(rows) != expected_rows:
        raise ValueError(f"Expected {expected_rows} paired rows, found {len(rows)}.")
    dates = {row.get("date", "") for row in rows}
    if dates != expected_dates:
        raise ValueError(f"Expected dates {sorted(expected_dates)}, found {sorted(dates)}.")
    timestamps = [row.get("timestamp_utc", "") for row in rows]
    if len(set(timestamps)) != expected_rows:
        raise ValueError("Expected unique exact-pair timestamps in the reconciliation artifact.")
    if pair_status_counts != {expectations.expected_pair_status: expected_rows}:
        raise ValueError(f"Unexpected pair-quality population: {dict(pair_status_counts)}")
    identities = {(row.get("provider", ""), row.get("instrument", ""), row.get("timeframe", "")) for row in rows}
    if identities != {(EXPECTED_PROVIDER, EXPECTED_INSTRUMENT, EXPECTED_TIMEFRAME)}:
        raise ValueError(f"Unexpected provenance identity population: {sorted(identities)}")


def percentile(sorted_values: list[Decimal], fraction: Decimal) -> Decimal | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = fraction * Decimal(len(sorted_values) - 1)
    lower = int(position.to_integral_value(rounding="ROUND_FLOOR"))
    upper = int(position.to_integral_value(rounding="ROUND_CEILING"))
    if lower == upper:
        return sorted_values[lower]
    weight = position - Decimal(lower)
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * weight


def stddev(values: list[Decimal]) -> Decimal | None:
    if len(values) < 2:
        return None
    floats = [float(value) for value in values]
    mean = sum(floats) / len(floats)
    return Decimal(str(math.sqrt(sum((value - mean) ** 2 for value in floats) / (len(floats) - 1))))


def format_decimal(value: Decimal | None) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def summarize(population: str, group_type: str, group_value: str, rows: list[dict[str, str]], metadata_fields: dict[str, str] | None = None) -> dict[str, str]:
    if metadata_fields is None:
        metadata_fields = METADATA_FIELDS
    spreads = sorted(parse_decimal(row["spread"]) for row in rows)
    bps = sorted((parse_decimal(row["spread"]) / parse_decimal(row["bid_close"])) * Decimal("10000") for row in rows)
    count = len(rows)
    return {
        **metadata_fields,
        "session_window_type": SESSION_WINDOW_TYPE if group_type == "session" else "",
        "session_window_exclusive": SESSION_WINDOW_EXCLUSIVE if group_type == "session" else "",
        "population": population,
        "group_type": group_type,
        "group_value": group_value,
        "count": str(count),
        "placeholder_count": str(sum(1 for row in rows if is_placeholder(row))),
        "min_spread": format_decimal(spreads[0] if spreads else None),
        "p05_spread": format_decimal(percentile(spreads, Decimal("0.05"))),
        "p25_spread": format_decimal(percentile(spreads, Decimal("0.25"))),
        "median_spread": format_decimal(percentile(spreads, Decimal("0.50"))),
        "mean_spread": format_decimal(sum(spreads) / Decimal(count) if count else None),
        "p75_spread": format_decimal(percentile(spreads, Decimal("0.75"))),
        "p95_spread": format_decimal(percentile(spreads, Decimal("0.95"))),
        "p99_spread": format_decimal(percentile(spreads, Decimal("0.99"))),
        "max_spread": format_decimal(spreads[-1] if spreads else None),
        "stddev_spread": format_decimal(stddev(spreads)),
        "min_spread_bid_bps": format_decimal(bps[0] if bps else None),
        "p05_spread_bid_bps": format_decimal(percentile(bps, Decimal("0.05"))),
        "p25_spread_bid_bps": format_decimal(percentile(bps, Decimal("0.25"))),
        "median_spread_bid_bps": format_decimal(percentile(bps, Decimal("0.50"))),
        "mean_spread_bid_bps": format_decimal(sum(bps) / Decimal(count) if count else None),
        "p75_spread_bid_bps": format_decimal(percentile(bps, Decimal("0.75"))),
        "p95_spread_bid_bps": format_decimal(percentile(bps, Decimal("0.95"))),
        "p99_spread_bid_bps": format_decimal(percentile(bps, Decimal("0.99"))),
        "max_spread_bid_bps": format_decimal(bps[-1] if bps else None),
        "stddev_spread_bid_bps": format_decimal(stddev(bps)),
    }


def group_by_day(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["date"]].append(row)
    return dict(grouped)


def group_by_hour(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["timestamp_utc"][11:13]].append(row)
    return dict(grouped)


def group_by_session(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_day = group_by_day(rows)
    for day_text, day_rows in by_day.items():
        day = datetime.strptime(day_text, "%Y-%m-%d").date()
        windows = get_session_windows(day)
        for row in day_rows:
            timestamp = datetime.strptime(row["timestamp_utc"], "%Y-%m-%d %H:%M:%S")
            for window in windows:
                if window.start_utc <= timestamp < window.end_utc:
                    grouped[window.name].append(row)
    return dict(grouped)


def write_summary(rows: list[dict[str, str]], path: Path, metadata_fields: dict[str, str] | None = None) -> None:
    if metadata_fields is None:
        metadata_fields = METADATA_FIELDS
    full_rows = list(rows)
    non_placeholder_rows = [row for row in rows if not is_placeholder(row)]
    summary_rows: list[dict[str, str]] = []
    for population, population_rows in (("all_warning_review_pairs", full_rows), ("non_placeholder_diagnostic", non_placeholder_rows)):
        summary_rows.append(summarize(population, "overall", "all", population_rows, metadata_fields))
        for day_text, group_rows in sorted(group_by_day(population_rows).items()):
            summary_rows.append(summarize(population, "day", day_text, group_rows, metadata_fields))
        for hour, group_rows in sorted(group_by_hour(population_rows).items()):
            summary_rows.append(summarize(population, "hour_utc", hour, group_rows, metadata_fields))
        for session_name, group_rows in sorted(group_by_session(population_rows).items()):
            summary_rows.append(summarize(population, "session", session_name, group_rows, metadata_fields))

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(summary_rows)


def write_wide_observations(rows: list[dict[str, str]], path: Path, metadata_fields: dict[str, str] | None = None) -> None:
    if metadata_fields is None:
        metadata_fields = METADATA_FIELDS
    populations = [
        ("all_warning_review_pairs", list(rows)),
        ("non_placeholder_diagnostic", [row for row in rows if not is_placeholder(row)]),
    ]
    columns = [
        "sample_start", "sample_end", "sample_days", "interpretation_scope", "population",
        "wide_threshold_source", "wide_threshold_spread", "timestamp_utc", "date", "provider",
        "instrument", "timeframe", "bid_close", "ask_close", "spread", "spread_bid_bps",
        "pair_quality_status", "pair_quality_reasons",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        for population, population_rows in populations:
            spreads = sorted(parse_decimal(row["spread"]) for row in population_rows)
            p99 = percentile(spreads, Decimal("0.99"))
            selected = [row for row in population_rows if parse_decimal(row["spread"]) >= p99]
            for row in selected:
                output_row = {column: row.get(column, "") for column in columns}
                output_row.update(metadata_fields)
                output_row["population"] = population
                output_row["wide_threshold_source"] = "population_p99_spread"
                output_row["wide_threshold_spread"] = format_decimal(p99)
                output_row["spread_bid_bps"] = format_decimal((parse_decimal(row["spread"]) / parse_decimal(row["bid_close"])) * Decimal("10000"))
                writer.writerow(output_row)


def characterize(input_path: Path = INPUT_PATH, summary_path: Path = SUMMARY_PATH, wide_path: Path = WIDE_OBSERVATIONS_PATH, expectations: CharacterizationExpectations | None = None) -> CharacterizationResult:
    rows = read_rows(input_path)
    validate_input(rows, expectations)
    metadata_fields = expectations.metadata_fields if expectations is not None else METADATA_FIELDS
    write_summary(rows, summary_path, metadata_fields)
    write_wide_observations(rows, wide_path, metadata_fields)
    return CharacterizationResult(
        input_path=input_path,
        summary_path=summary_path,
        wide_observations_path=wide_path,
        rows=len(rows),
        placeholder_rows=sum(1 for row in rows if is_placeholder(row)),
        pair_status_counts=dict(Counter(row["pair_quality_status"] for row in rows)),
        negative_spreads=sum(1 for row in rows if parse_decimal(row["spread"]) < 0),
        zero_spreads=sum(1 for row in rows if parse_decimal(row["spread"]) == 0),
        extreme_spreads=sum(1 for row in rows if EXTREME_REASON in row["pair_quality_reasons"].split(";")),
        provenance_identities={(row["provider"], row["instrument"], row["timeframe"]) for row in rows},
    )


def main() -> int:
    if len(sys.argv) not in (1, 4):
        print("Usage: python spread_characterization.py [YYYY-MM-DD YYYY-MM-DD RECONCILIATION_CSV]")
        return 1
    if len(sys.argv) == 4:
        start_day = parse_day(sys.argv[1])
        end_day = parse_day(sys.argv[2])
        if end_day < start_day:
            print("Error: end date cannot be earlier than start date")
            return 1
        input_path = Path(sys.argv[3])
        summary_path = REPORTS_DIR / f"spread_characterization_{start_day:%Y-%m-%d}_to_{end_day:%Y-%m-%d}_summary.csv"
        wide_path = REPORTS_DIR / f"spread_characterization_{start_day:%Y-%m-%d}_to_{end_day:%Y-%m-%d}_wide_observations.csv"
        result = characterize(input_path, summary_path, wide_path, CharacterizationExpectations(start_day, end_day))
    else:
        result = characterize()
    print(f"input={result.input_path}")
    print(f"summary={result.summary_path}")
    print(f"wide_observations={result.wide_observations_path}")
    print(f"rows={result.rows}")
    print(f"placeholder_rows={result.placeholder_rows}")
    print(f"pair_status_counts={result.pair_status_counts}")
    print(f"negative_spreads={result.negative_spreads}")
    print(f"zero_spreads={result.zero_spreads}")
    print(f"extreme_spreads={result.extreme_spreads}")
    print(f"provenance_identities={sorted(result.provenance_identities)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
