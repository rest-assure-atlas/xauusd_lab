"""Load linked observation reports through a small quality-aware contract.

This module is an internal access layer over existing linked-observation CSV
reports. It does not generate reports, read raw data, or calculate research
fields.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Iterator

import linked_observation_report as linked_report


CONTRACT_NAME = "research_observation_contract_v1"
SUPPORTED_LINKED_SCHEMA_VERSION = linked_report.LINKED_SCHEMA_VERSION

IDENTITY_FIELDS = ("date", "provider", "instrument", "quote_side", "timeframe")
COMPATIBILITY_FIELDS = (
    "linked_schema_version",
    "provider",
    "instrument",
    "quote_side",
    "timeframe",
    "manifest_schema_version",
    "validation_rule_version",
    "active_filter_rule_identity",
    "session_definition_checksum",
)
QUALITY_TIERS = (
    linked_report.STRICT_VALID,
    linked_report.WARNING_REVIEW,
    linked_report.CALENDAR_ONLY,
    linked_report.EXCLUDED_UNUSABLE,
)
REQUIRED_COLUMNS = tuple(linked_report.LINKED_COLUMNS)


class ResearchObservationContractError(ValueError):
    """Raised when a linked report violates the research observation contract."""


@dataclass(frozen=True)
class ResearchObservation:
    """One loaded proposed research observation unit from a linked report."""

    source_report_path: Path
    row: dict[str, str]

    @property
    def identity(self) -> tuple[str, str, str, str, str]:
        """Return the logical identity fields preserved as CSV strings."""
        return tuple(self.row[field] for field in IDENTITY_FIELDS)

    @property
    def quality_tier(self) -> str:
        """Return the observation-level quality tier."""
        return self.row["quality_tier"]

    @property
    def software_revision(self) -> str:
        """Return the source linked report software revision for this row."""
        return self.row["software_revision"]

    def value_or_none(self, field_name: str) -> str | None:
        """Return a field value, exposing blank CSV values as unavailable."""
        value = self.row[field_name]
        if value == "":
            return None
        return value


@dataclass(frozen=True)
class ResearchObservationCollection:
    """A validated collection of linked-report observations."""

    observations: tuple[ResearchObservation, ...]
    source_report_paths: tuple[Path, ...]
    contract_metadata: dict[str, str]

    def __iter__(self) -> Iterator[ResearchObservation]:
        return iter(self.observations)

    def __len__(self) -> int:
        return len(self.observations)

    def _observations_for_tier(self, quality_tier: str) -> tuple[ResearchObservation, ...]:
        return tuple(
            observation
            for observation in self.observations
            if observation.quality_tier == quality_tier
        )

    def strict_valid_observations(self) -> tuple[ResearchObservation, ...]:
        return self._observations_for_tier(linked_report.STRICT_VALID)

    def warning_review_observations(self) -> tuple[ResearchObservation, ...]:
        return self._observations_for_tier(linked_report.WARNING_REVIEW)

    def calendar_only_observations(self) -> tuple[ResearchObservation, ...]:
        return self._observations_for_tier(linked_report.CALENDAR_ONLY)

    def excluded_unusable_observations(self) -> tuple[ResearchObservation, ...]:
        return self._observations_for_tier(linked_report.EXCLUDED_UNUSABLE)

    def coverage_observations(self) -> tuple[ResearchObservation, ...]:
        return tuple(
            observation
            for observation in self.observations
            if observation.quality_tier
            in {linked_report.CALENDAR_ONLY, linked_report.EXCLUDED_UNUSABLE}
        )

    def population_counts(self) -> dict[str, int]:
        counts = Counter(observation.quality_tier for observation in self.observations)
        return {quality_tier: counts[quality_tier] for quality_tier in QUALITY_TIERS}


def load_linked_report(path: str | Path) -> ResearchObservationCollection:
    """Load one linked-observation report CSV."""
    return load_linked_reports([path])


def load_linked_reports(paths: Iterable[str | Path]) -> ResearchObservationCollection:
    """Load compatible linked-observation report CSVs."""
    report_paths = tuple(Path(path) for path in paths)
    if not report_paths:
        raise ResearchObservationContractError("Please provide at least one linked report path.")

    observations: list[ResearchObservation] = []
    contract_metadata: dict[str, str] | None = None
    identities: dict[tuple[str, str, str, str, str], Path] = {}

    for report_path in report_paths:
        report_rows = _read_linked_report_rows(report_path)
        for row_number, row in report_rows:
            parsed_date = _validate_row(report_path, row_number, row)
            if contract_metadata is None:
                contract_metadata = {
                    field: row[field] for field in COMPATIBILITY_FIELDS
                }
            else:
                _validate_contract_compatibility(
                    report_path,
                    row_number,
                    row,
                    contract_metadata,
                )

            observation = ResearchObservation(
                source_report_path=report_path,
                row=row,
            )
            identity = observation.identity
            if identity in identities:
                raise ResearchObservationContractError(
                    f"Duplicate proposed research observation unit {identity} in "
                    f"{report_path}; first seen in {identities[identity]}."
                )
            identities[identity] = report_path
            observations.append(observation)

    sorted_observations = tuple(
        sorted(
            observations,
            key=lambda observation: (
                date.fromisoformat(observation.row["date"]),
                observation.row["provider"],
                observation.row["instrument"],
                observation.row["quote_side"],
                observation.row["timeframe"],
            ),
        )
    )

    return ResearchObservationCollection(
        observations=sorted_observations,
        source_report_paths=report_paths,
        contract_metadata=contract_metadata or {},
    )


def _read_linked_report_rows(report_path: Path) -> list[tuple[int, dict[str, str]]]:
    if not report_path.exists():
        raise ResearchObservationContractError(f"Linked report does not exist: {report_path}")

    if not report_path.is_file():
        raise ResearchObservationContractError(
            f"Linked report path is not a file: {report_path}"
        )

    try:
        with report_path.open("r", newline="", encoding="utf-8") as report_file:
            reader = csv.DictReader(report_file)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ResearchObservationContractError(
                    f"Input linked report has no usable header row: {report_path}"
                )

            missing_columns = [
                column for column in REQUIRED_COLUMNS if column not in fieldnames
            ]
            if missing_columns:
                raise ResearchObservationContractError(
                    f"Input linked report {report_path} is missing required columns: "
                    + ", ".join(missing_columns)
                )

            rows: list[tuple[int, dict[str, str]]] = []
            for row_number, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise ResearchObservationContractError(
                        f"Malformed CSV row in {report_path} at row {row_number}."
                    )
                rows.append((row_number, dict(row)))
    except OSError as error:
        raise ResearchObservationContractError(
            f"Could not read linked report {report_path}: {error}"
        ) from error
    except csv.Error as error:
        raise ResearchObservationContractError(
            f"Malformed CSV in linked report {report_path}: {error}"
        ) from error

    if not rows:
        raise ResearchObservationContractError(
            f"Input linked report contains no data rows: {report_path}"
        )

    return rows


def _validate_row(report_path: Path, row_number: int, row: dict[str, str]) -> date:
    for field in (*IDENTITY_FIELDS, *COMPATIBILITY_FIELDS, "quality_tier"):
        if row[field] == "":
            raise ResearchObservationContractError(
                f"Blank required field {field} in {report_path} at row {row_number}."
            )

    if row["linked_schema_version"] != SUPPORTED_LINKED_SCHEMA_VERSION:
        raise ResearchObservationContractError(
            f"Unsupported linked_schema_version in {report_path} at row {row_number}: "
            f"{row['linked_schema_version']}"
        )

    try:
        parsed_date = date.fromisoformat(row["date"])
    except ValueError as error:
        raise ResearchObservationContractError(
            f"Invalid date in {report_path} at row {row_number}: {row['date']}"
        ) from error

    if row["quality_tier"] not in QUALITY_TIERS:
        raise ResearchObservationContractError(
            f"Unknown quality_tier in {report_path} at row {row_number}: "
            f"{row['quality_tier']}"
        )

    return parsed_date


def _validate_contract_compatibility(
    report_path: Path,
    row_number: int,
    row: dict[str, str],
    expected_metadata: dict[str, str],
) -> None:
    for field in COMPATIBILITY_FIELDS:
        if row[field] != expected_metadata[field]:
            raise ResearchObservationContractError(
                f"Incompatible {field} in {report_path} at row {row_number}: "
                f"expected {expected_metadata[field]}, found {row[field]}"
            )
