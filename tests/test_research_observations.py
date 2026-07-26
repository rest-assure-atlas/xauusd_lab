import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import linked_observation_report as linked_report
import research_observations


class ResearchObservationsTests(unittest.TestCase):
    def linked_row(self, day_text, quality_tier=linked_report.STRICT_VALID, **overrides):
        row = {column: "" for column in linked_report.LINKED_COLUMNS}
        row.update(
            {
                "linked_schema_version": linked_report.LINKED_SCHEMA_VERSION,
                "date": day_text,
                "weekday": "Monday",
                "provider": "Dukascopy",
                "instrument": "XAUUSD",
                "quote_side": "BID",
                "timeframe": "1min",
                "source_filename": f"XAUUSD_{day_text}_1min_BID_UTC.csv",
                "source_file_size_bytes": "100",
                "source_checksum_algorithm": "sha256",
                "source_checksum": f"checksum-{day_text}",
                "manifest_schema_version": "1",
                "validation_rule_version": "raw_data_quality_v1",
                "active_filter_rule_identity": "edge_flat_zero_volume_v1",
                "session_definition_checksum": "session-checksum",
                "software_revision": "revision-a",
                "session_status": "complete",
                "manifest_file_status": "processed",
                "manifest_quality_status": "valid",
                "manifest_quality_reasons": "",
                "linkage_status": "linked",
                "linkage_reasons": "",
                "quality_tier": quality_tier,
                "manifest_total_row_count": "1440",
                "manifest_active_row_count": "1440",
                "session_total_csv_rows": "1440",
                "session_active_candle_count": "1440",
                "session_inactive_placeholder_count": "0",
                "daily_open": "2000.000",
                "daily_high": "2010.000",
                "daily_low": "1990.000",
                "daily_close": "2005.000",
                "daily_range": "20.000",
                "time_of_daily_high_utc": "12:00:00",
                "time_of_daily_low_utc": "08:00:00",
            }
        )

        if quality_tier == linked_report.WARNING_REVIEW:
            row["manifest_quality_status"] = "warning"
            row["manifest_quality_reasons"] = "INTERNAL_FLAT_ZERO_VOLUME"
        elif quality_tier == linked_report.CALENDAR_ONLY:
            row["session_status"] = "no_active_candles"
            row["manifest_file_status"] = "no_active_candles"
            row["manifest_quality_status"] = "not_assessed"
            row["manifest_quality_reasons"] = "NO_ACTIVE_CANDLES"
            row["linkage_status"] = linked_report.CALENDAR_ONLY
            for column in linked_report.LINKED_COLUMNS:
                if (
                    column.startswith("daily_")
                    or column.startswith("tokyo_")
                    or column.startswith("london_")
                    or column.startswith("new_york_")
                    or column.startswith("time_of_daily_")
                ):
                    row[column] = ""
        elif quality_tier == linked_report.EXCLUDED_UNUSABLE:
            row["session_status"] = "failed"
            row["manifest_quality_status"] = "invalid"
            row["manifest_quality_reasons"] = "PARSE_FAILED"
            row["linkage_status"] = linked_report.CONTRADICTION

        row.update(overrides)
        return row

    def write_report(self, path: Path, rows, fieldnames=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(fieldnames or linked_report.LINKED_COLUMNS)
        with path.open("w", newline="", encoding="utf-8") as report_file:
            writer = csv.DictWriter(
                report_file,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows)

    def test_valid_single_linked_report_loads_in_chronological_order(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            self.write_report(
                report_path,
                [
                    self.linked_row("2024-01-03"),
                    self.linked_row("2024-01-01"),
                    self.linked_row("2024-01-02"),
                ],
            )

            collection = research_observations.load_linked_report(report_path)

        self.assertEqual(len(collection), 3)
        self.assertEqual([row.row["date"] for row in collection], [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
        ])

    def test_original_row_fields_and_source_report_path_are_preserved(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            fieldnames = [*linked_report.LINKED_COLUMNS, "extra_calculation"]
            row = self.linked_row("2024-01-01", extra_calculation="kept")
            self.write_report(report_path, [row], fieldnames=fieldnames)

            collection = research_observations.load_linked_report(report_path)

        observation = tuple(collection)[0]
        self.assertEqual(observation.source_report_path, report_path)
        self.assertEqual(observation.row["extra_calculation"], "kept")
        self.assertEqual(observation.row["daily_range"], "20.000")

    def test_quality_selectors_return_only_their_named_tiers(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            rows = [
                self.linked_row("2024-01-01", linked_report.STRICT_VALID),
                self.linked_row("2024-01-02", linked_report.WARNING_REVIEW),
                self.linked_row("2024-01-03", linked_report.CALENDAR_ONLY),
                self.linked_row("2024-01-04", linked_report.EXCLUDED_UNUSABLE),
            ]
            self.write_report(report_path, rows)

            collection = research_observations.load_linked_report(report_path)

        self.assertEqual(
            [row.quality_tier for row in collection.strict_valid_observations()],
            [linked_report.STRICT_VALID],
        )
        self.assertEqual(
            [row.quality_tier for row in collection.warning_review_observations()],
            [linked_report.WARNING_REVIEW],
        )
        self.assertEqual(
            [row.quality_tier for row in collection.coverage_observations()],
            [linked_report.CALENDAR_ONLY, linked_report.EXCLUDED_UNUSABLE],
        )

    def test_population_counts_keep_all_quality_tiers_separate(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            rows = [
                self.linked_row("2024-01-01", linked_report.STRICT_VALID),
                self.linked_row("2024-01-02", linked_report.WARNING_REVIEW),
                self.linked_row("2024-01-03", linked_report.WARNING_REVIEW),
                self.linked_row("2024-01-04", linked_report.CALENDAR_ONLY),
            ]
            self.write_report(report_path, rows)

            collection = research_observations.load_linked_report(report_path)

        self.assertEqual(
            collection.population_counts(),
            {
                linked_report.STRICT_VALID: 1,
                linked_report.WARNING_REVIEW: 2,
                linked_report.CALENDAR_ONLY: 1,
                linked_report.EXCLUDED_UNUSABLE: 0,
            },
        )

    def test_blank_calculation_field_is_unavailable_not_zero(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            row = self.linked_row("2024-01-01", linked_report.CALENDAR_ONLY)
            self.write_report(report_path, [row])

            observation = tuple(
                research_observations.load_linked_report(report_path)
            )[0]

        self.assertEqual(observation.row["daily_range"], "")
        self.assertIsNone(observation.value_or_none("daily_range"))
        self.assertNotEqual(observation.value_or_none("daily_range"), "0")

    def test_strict_valid_or_warning_review_row_with_blank_session_fields_is_accepted(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            rows = [
                self.linked_row("2024-01-01", linked_report.STRICT_VALID),
                self.linked_row("2024-01-02", linked_report.WARNING_REVIEW),
            ]
            self.write_report(report_path, rows)

            collection = research_observations.load_linked_report(report_path)

        self.assertEqual(len(collection.strict_valid_observations()), 1)
        self.assertEqual(len(collection.warning_review_observations()), 1)
        self.assertEqual(tuple(collection)[0].row["tokyo_range"], "")
        self.assertEqual(tuple(collection)[1].row["tokyo_range"], "")

    def test_calendar_only_blank_calculations_are_accepted(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            self.write_report(
                report_path,
                [self.linked_row("2024-01-01", linked_report.CALENDAR_ONLY)],
            )

            collection = research_observations.load_linked_report(report_path)

        self.assertEqual(len(collection.calendar_only_observations()), 1)

    def test_compatible_multiple_reports_load_in_chronological_order(self):
        with TemporaryDirectory() as temp_root:
            first_path = Path(temp_root) / "first.csv"
            second_path = Path(temp_root) / "second.csv"
            self.write_report(second_path, [self.linked_row("2024-02-01")])
            self.write_report(first_path, [self.linked_row("2024-01-01")])

            collection = research_observations.load_linked_reports(
                [second_path, first_path]
            )

        self.assertEqual([row.row["date"] for row in collection], [
            "2024-01-01",
            "2024-02-01",
        ])

    def test_compatible_reports_with_different_software_revisions_are_accepted(self):
        with TemporaryDirectory() as temp_root:
            first_path = Path(temp_root) / "first.csv"
            second_path = Path(temp_root) / "second.csv"
            self.write_report(
                first_path,
                [self.linked_row("2024-01-01", software_revision="revision-a")],
            )
            self.write_report(
                second_path,
                [self.linked_row("2024-02-01", software_revision="revision-b")],
            )

            collection = research_observations.load_linked_reports(
                [first_path, second_path]
            )

        self.assertEqual(
            [row.software_revision for row in collection],
            ["revision-a", "revision-b"],
        )

    def test_missing_input_file_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            missing_path = Path(temp_root) / "missing.csv"

            with self.assertRaisesRegex(
                research_observations.ResearchObservationContractError,
                "does not exist",
            ):
                research_observations.load_linked_report(missing_path)

    def test_empty_report_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            self.write_report(report_path, [])

            with self.assertRaisesRegex(
                research_observations.ResearchObservationContractError,
                "contains no data rows",
            ):
                research_observations.load_linked_report(report_path)

    def test_missing_required_column_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            fieldnames = [
                column
                for column in linked_report.LINKED_COLUMNS
                if column != "quality_tier"
            ]
            row = self.linked_row("2024-01-01")
            self.write_report(report_path, [row], fieldnames=fieldnames)

            with self.assertRaisesRegex(
                research_observations.ResearchObservationContractError,
                "missing required columns: quality_tier",
            ):
                research_observations.load_linked_report(report_path)

    def test_unsupported_linked_schema_version_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            row = self.linked_row("2024-01-01", linked_schema_version="2")
            self.write_report(report_path, [row])

            with self.assertRaisesRegex(
                research_observations.ResearchObservationContractError,
                "Unsupported linked_schema_version",
            ):
                research_observations.load_linked_report(report_path)

    def test_unknown_quality_tier_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            row = self.linked_row("2024-01-01", quality_tier="mystery")
            self.write_report(report_path, [row])

            with self.assertRaisesRegex(
                research_observations.ResearchObservationContractError,
                "Unknown quality_tier",
            ):
                research_observations.load_linked_report(report_path)

    def test_blank_required_identity_or_contract_field_is_rejected(self):
        required_fields = [
            "date",
            "provider",
            "instrument",
            "quote_side",
            "timeframe",
            "linked_schema_version",
            "manifest_schema_version",
            "validation_rule_version",
            "active_filter_rule_identity",
            "session_definition_checksum",
            "quality_tier",
        ]
        for field in required_fields:
            with self.subTest(field=field):
                with TemporaryDirectory() as temp_root:
                    report_path = Path(temp_root) / "linked.csv"
                    row = self.linked_row("2024-01-01")
                    row[field] = ""
                    self.write_report(report_path, [row])

                    with self.assertRaisesRegex(
                        research_observations.ResearchObservationContractError,
                        f"Blank required field {field}",
                    ):
                        research_observations.load_linked_report(report_path)

    def test_invalid_date_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            row = self.linked_row("not-a-date")
            self.write_report(report_path, [row])

            with self.assertRaisesRegex(
                research_observations.ResearchObservationContractError,
                "Invalid date",
            ):
                research_observations.load_linked_report(report_path)

    def test_duplicate_identity_within_one_report_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            self.write_report(
                report_path,
                [self.linked_row("2024-01-01"), self.linked_row("2024-01-01")],
            )

            with self.assertRaisesRegex(
                research_observations.ResearchObservationContractError,
                "Duplicate proposed research observation unit",
            ):
                research_observations.load_linked_report(report_path)

    def test_duplicate_identity_across_reports_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            first_path = Path(temp_root) / "first.csv"
            second_path = Path(temp_root) / "second.csv"
            self.write_report(first_path, [self.linked_row("2024-01-01")])
            self.write_report(second_path, [self.linked_row("2024-01-01")])

            with self.assertRaisesRegex(
                research_observations.ResearchObservationContractError,
                "Duplicate proposed research observation unit",
            ):
                research_observations.load_linked_reports([first_path, second_path])

    def test_incompatible_contract_dimensions_are_rejected(self):
        incompatible_values = {
            "provider": "Other",
            "instrument": "EURUSD",
            "quote_side": "ASK",
            "timeframe": "5min",
            "manifest_schema_version": "2",
            "validation_rule_version": "other_rule",
            "active_filter_rule_identity": "other_filter",
            "session_definition_checksum": "other-session-checksum",
        }
        for field, value in incompatible_values.items():
            with self.subTest(field=field):
                with TemporaryDirectory() as temp_root:
                    first_path = Path(temp_root) / "first.csv"
                    second_path = Path(temp_root) / "second.csv"
                    self.write_report(first_path, [self.linked_row("2024-01-01")])
                    self.write_report(
                        second_path,
                        [self.linked_row("2024-02-01", **{field: value})],
                    )

                    with self.assertRaisesRegex(
                        research_observations.ResearchObservationContractError,
                        f"Incompatible {field}",
                    ):
                        research_observations.load_linked_reports(
                            [first_path, second_path]
                        )


if __name__ == "__main__":
    unittest.main()
