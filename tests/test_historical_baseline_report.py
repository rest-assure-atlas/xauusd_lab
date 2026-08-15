import contextlib
import csv
import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import historical_baseline_report as baseline
import linked_observation_report as linked_report


class HistoricalBaselineReportTest(unittest.TestCase):
    def linked_row(
        self,
        day_text="2024-01-02",
        quality_tier=linked_report.STRICT_VALID,
        daily_range="10.000",
        tokyo_range="2.000",
        london_range="3.000",
        new_york_range="4.000",
        manifest_quality_reasons="",
        linkage_reasons="",
        quote_side="BID",
    ):
        row = {column: "" for column in linked_report.LINKED_COLUMNS}
        row["linked_schema_version"] = linked_report.LINKED_SCHEMA_VERSION
        row["date"] = day_text
        row["weekday"] = "Tuesday"
        row["provider"] = "Dukascopy"
        row["instrument"] = "XAUUSD"
        row["quote_side"] = quote_side
        row["timeframe"] = "1min"
        row["source_filename"] = f"XAUUSD_{day_text}_1min_{quote_side}_UTC.csv"
        row["source_file_size_bytes"] = "100"
        row["source_checksum_algorithm"] = "sha256"
        row["source_checksum"] = "a" * 64
        row["manifest_schema_version"] = "1"
        row["validation_rule_version"] = "raw_data_quality_v1"
        row["active_filter_rule_identity"] = "edge_flat_zero_volume_v1"
        row["session_definition_checksum"] = "b" * 64
        row["software_revision"] = "testrev"
        row["session_status"] = "complete"
        row["manifest_file_status"] = "processed"
        row["manifest_quality_status"] = "valid"
        row["manifest_quality_reasons"] = manifest_quality_reasons
        row["linkage_status"] = linked_report.LINKED
        row["linkage_reasons"] = linkage_reasons
        row["quality_tier"] = quality_tier
        row["manifest_total_row_count"] = "1440"
        row["manifest_active_row_count"] = "1440"
        row["session_total_csv_rows"] = "1440"
        row["session_active_candle_count"] = "1440"
        row["session_inactive_placeholder_count"] = "0"
        row["daily_range"] = daily_range
        row["tokyo_range"] = tokyo_range
        row["london_range"] = london_range
        row["new_york_range"] = new_york_range

        if quality_tier == linked_report.WARNING_REVIEW:
            row["manifest_quality_status"] = "warning"
            if not row["manifest_quality_reasons"]:
                row["manifest_quality_reasons"] = "INTERNAL_FLAT_ZERO_VOLUME"

        if quality_tier == linked_report.CALENDAR_ONLY:
            row["session_status"] = "no_active_candles"
            row["manifest_file_status"] = "no_active_candles"
            row["manifest_quality_status"] = "not_assessed"
            row["manifest_quality_reasons"] = "NO_ACTIVE_CANDLES"
            row["linkage_status"] = linked_report.CALENDAR_ONLY
            row["daily_range"] = daily_range
            row["tokyo_range"] = tokyo_range
            row["london_range"] = london_range
            row["new_york_range"] = new_york_range

        if quality_tier == linked_report.EXCLUDED_UNUSABLE:
            row["manifest_quality_status"] = "invalid"
            row["manifest_quality_reasons"] = "INVALID_TIMESTAMP"
            row["linkage_status"] = linked_report.CONTRADICTION
            if not row["linkage_reasons"]:
                row["linkage_reasons"] = linked_report.SOURCE_CHECKSUM_MISMATCH

        return row

    def write_linked_report(self, report_path: Path, rows, fieldnames=None):
        if fieldnames is None:
            fieldnames = linked_report.LINKED_COLUMNS

        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", newline="", encoding="utf-8") as report_file:
            writer = csv.DictWriter(report_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row[field] for field in fieldnames})

    def read_baseline_rows(self, report_path: Path):
        with report_path.open("r", newline="", encoding="utf-8") as report_file:
            reader = csv.DictReader(report_file)
            return reader.fieldnames, list(reader)

    def create_baseline(self, linked_path: Path, reports_dir: Path):
        with patch("historical_baseline_report.REPORTS_DIR", reports_dir):
            summary = baseline.create_historical_baseline_report(linked_path)

        _, rows = self.read_baseline_rows(summary.output_path)
        return summary, rows

    def find_metric(
        self,
        rows,
        metric_section,
        metric_name,
        observation_group,
        field_name,
        reason_code="",
    ):
        matches = [
            row
            for row in rows
            if row["metric_section"] == metric_section
            and row["metric_name"] == metric_name
            and row["observation_group"] == observation_group
            and row["field_name"] == field_name
            and row["reason_code"] == reason_code
        ]
        self.assertEqual(matches, matches[:1])
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_cli_reads_linked_report_path_directly(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked_observation_report_sample.csv"
            reports_dir = temp_root_path / "reports"
            self.write_linked_report(linked_path, [self.linked_row()])

            with (
                patch("historical_baseline_report.REPORTS_DIR", reports_dir),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                exit_code = baseline.main([str(linked_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(
                (reports_dir / "historical_baseline_linked_observation_report_sample.csv").exists()
            )

    def test_required_schema_validation_rejects_missing_columns(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            fieldnames = [
                column
                for column in linked_report.LINKED_COLUMNS
                if column != "daily_range"
            ]
            self.write_linked_report(linked_path, [self.linked_row()], fieldnames)

            with self.assertRaisesRegex(ValueError, "missing required columns: daily_range"):
                baseline.create_historical_baseline_report(linked_path)

    def test_unsupported_linked_schema_version_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            linked_path = Path(temp_root) / "linked.csv"
            row = self.linked_row()
            row["linked_schema_version"] = "2"
            self.write_linked_report(linked_path, [row])

            with self.assertRaisesRegex(ValueError, "Unsupported linked_schema_version"):
                baseline.create_historical_baseline_report(linked_path)

    def test_duplicate_dates_are_rejected(self):
        with TemporaryDirectory() as temp_root:
            linked_path = Path(temp_root) / "linked.csv"
            rows = [self.linked_row("2024-01-02"), self.linked_row("2024-01-02")]
            self.write_linked_report(linked_path, rows)

            with self.assertRaisesRegex(ValueError, "Duplicate date"):
                baseline.create_historical_baseline_report(linked_path)

    def test_explicit_ask_linked_report_is_accepted_and_named_by_source_report(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = (
                temp_root_path
                / "linked_observation_report_ASK_2024-01-02_to_2024-01-02.csv"
            )
            reports_dir = temp_root_path / "reports"
            self.write_linked_report(
                linked_path,
                [self.linked_row("2024-01-02", quote_side="ASK")],
            )

            summary, baseline_rows = self.create_baseline(linked_path, reports_dir)

        self.assertEqual(
            summary.output_path.name,
            "historical_baseline_linked_observation_report_ASK_2024-01-02_to_2024-01-02.csv",
        )
        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "coverage",
                "row_count_by_quality_tier",
                linked_report.STRICT_VALID,
                "quality_tier",
            )["count"],
            "1",
        )

    def test_mixed_quote_side_rows_are_rejected_before_population_pooling(self):
        with TemporaryDirectory() as temp_root:
            linked_path = Path(temp_root) / "linked.csv"
            rows = [
                self.linked_row("2024-01-02", quote_side="BID"),
                self.linked_row("2024-01-03", quote_side="ASK"),
            ]
            self.write_linked_report(linked_path, rows)

            with self.assertRaisesRegex(ValueError, "mixes source identity.*quote_side"):
                baseline.create_historical_baseline_report(linked_path)

    def test_provider_instrument_timeframe_mismatch_is_rejected(self):
        mismatch_cases = {
            "provider": "OtherProvider",
            "instrument": "EURUSD",
            "timeframe": "5min",
        }
        for field, replacement in mismatch_cases.items():
            with self.subTest(field=field):
                with TemporaryDirectory() as temp_root:
                    linked_path = Path(temp_root) / "linked.csv"
                    second_row = self.linked_row("2024-01-03")
                    second_row[field] = replacement
                    self.write_linked_report(
                        linked_path,
                        [self.linked_row("2024-01-02"), second_row],
                    )

                    with self.assertRaisesRegex(ValueError, f"mixes source identity.*{field}"):
                        baseline.create_historical_baseline_report(linked_path)

    def test_unknown_quote_side_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            linked_path = Path(temp_root) / "linked.csv"
            self.write_linked_report(
                linked_path,
                [self.linked_row("2024-01-02", quote_side="MID")],
            )

            with self.assertRaisesRegex(ValueError, "Unsupported quote_side"):
                baseline.create_historical_baseline_report(linked_path)

    def test_blank_required_identity_or_status_field_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            linked_path = Path(temp_root) / "linked.csv"
            row = self.linked_row()
            row["provider"] = ""
            self.write_linked_report(linked_path, [row])

            with self.assertRaisesRegex(ValueError, "Unexpected blank required field"):
                baseline.create_historical_baseline_report(linked_path)

    def test_coverage_counts_by_quality_tier_and_statuses_are_written(self):
        rows = [
            self.linked_row("2024-01-02"),
            self.linked_row("2024-01-03", linked_report.WARNING_REVIEW),
            self.linked_row(
                "2024-01-04",
                linked_report.CALENDAR_ONLY,
                daily_range="",
                tokyo_range="",
                london_range="",
                new_york_range="",
            ),
            self.linked_row("2024-01-05", linked_report.EXCLUDED_UNUSABLE),
        ]

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            self.write_linked_report(linked_path, rows)
            _, baseline_rows = self.create_baseline(
                linked_path,
                temp_root_path / "reports",
            )

        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "coverage",
                "row_count_by_quality_tier",
                linked_report.STRICT_VALID,
                "quality_tier",
            )["count"],
            "1",
        )
        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "coverage",
                "row_count_by_linkage_status",
                linked_report.LINKED,
                "linkage_status",
            )["count"],
            "2",
        )
        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "coverage",
                "row_count_by_session_status",
                "no_active_candles",
                "session_status",
            )["count"],
            "1",
        )
        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "coverage",
                "row_count_by_manifest_quality_status",
                "invalid",
                "manifest_quality_status",
            )["count"],
            "1",
        )
        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "coverage",
                "row_count_by_manifest_quality_reasons",
                "INTERNAL_FLAT_ZERO_VOLUME",
                "manifest_quality_reasons",
            )["count"],
            "1",
        )
        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "coverage",
                "row_count_by_linkage_reasons",
                linked_report.SOURCE_CHECKSUM_MISMATCH,
                "linkage_reasons",
            )["count"],
            "1",
        )
        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "coverage",
                "row_count_by_manifest_quality_reasons_reason_code",
                "all",
                "manifest_quality_reasons",
                "INVALID_TIMESTAMP",
            )["count"],
            "1",
        )

    def test_daily_range_strict_valid_summary_is_written(self):
        rows = [
            self.linked_row("2024-01-02", daily_range="10.000"),
            self.linked_row("2024-01-03", daily_range="20.000"),
        ]

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            self.write_linked_report(linked_path, rows)
            _, baseline_rows = self.create_baseline(
                linked_path,
                temp_root_path / "reports",
            )

        metric = self.find_metric(
            baseline_rows,
            "range_summary",
            "range_summary",
            linked_report.STRICT_VALID,
            "daily_range",
        )
        self.assertEqual(metric["count"], "2")
        self.assertEqual(metric["min"], "10.000")
        self.assertEqual(metric["median"], "15.000")
        self.assertEqual(metric["mean"], "15.000")
        self.assertEqual(metric["max"], "20.000")

    def test_daily_range_warning_review_summary_is_separate(self):
        rows = [
            self.linked_row("2024-01-02", daily_range="10.000"),
            self.linked_row("2024-01-03", linked_report.WARNING_REVIEW, daily_range="30.000"),
            self.linked_row("2024-01-04", linked_report.WARNING_REVIEW, daily_range="50.000"),
        ]

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            self.write_linked_report(linked_path, rows)
            _, baseline_rows = self.create_baseline(
                linked_path,
                temp_root_path / "reports",
            )

        strict_metric = self.find_metric(
            baseline_rows,
            "range_summary",
            "range_summary",
            linked_report.STRICT_VALID,
            "daily_range",
        )
        warning_metric = self.find_metric(
            baseline_rows,
            "range_summary",
            "range_summary",
            linked_report.WARNING_REVIEW,
            "daily_range",
        )
        self.assertEqual(strict_metric["mean"], "10.000")
        self.assertEqual(warning_metric["count"], "2")
        self.assertEqual(warning_metric["mean"], "40.000")

    def test_warning_rows_are_summarized_by_reason_code(self):
        rows = [
            self.linked_row(
                "2024-01-02",
                linked_report.WARNING_REVIEW,
                daily_range="12.000",
                manifest_quality_reasons="INTERNAL_FLAT_ZERO_VOLUME",
            ),
            self.linked_row(
                "2024-01-03",
                linked_report.WARNING_REVIEW,
                daily_range="30.000",
                manifest_quality_reasons="PARTIAL_DAY_COVERAGE",
            ),
        ]

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            self.write_linked_report(linked_path, rows)
            _, baseline_rows = self.create_baseline(
                linked_path,
                temp_root_path / "reports",
            )

        flat_metric = self.find_metric(
            baseline_rows,
            "range_summary",
            "range_summary_by_warning_reason",
            linked_report.WARNING_REVIEW,
            "daily_range",
            "INTERNAL_FLAT_ZERO_VOLUME",
        )
        partial_metric = self.find_metric(
            baseline_rows,
            "range_summary",
            "range_summary_by_warning_reason",
            linked_report.WARNING_REVIEW,
            "daily_range",
            "PARTIAL_DAY_COVERAGE",
        )
        self.assertEqual(flat_metric["mean"], "12.000")
        self.assertEqual(partial_metric["mean"], "30.000")

    def test_calendar_only_rows_are_excluded_from_numeric_metrics(self):
        rows = [
            self.linked_row("2024-01-02", daily_range="10.000"),
            self.linked_row(
                "2024-01-03",
                linked_report.CALENDAR_ONLY,
                daily_range="999.000",
                tokyo_range="999.000",
                london_range="999.000",
                new_york_range="999.000",
            ),
        ]

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            self.write_linked_report(linked_path, rows)
            _, baseline_rows = self.create_baseline(
                linked_path,
                temp_root_path / "reports",
            )

        metric = self.find_metric(
            baseline_rows,
            "range_summary",
            "range_summary",
            linked_report.STRICT_VALID,
            "daily_range",
        )
        self.assertEqual(metric["count"], "1")
        self.assertEqual(metric["max"], "10.000")

    def test_excluded_unusable_rows_are_excluded_from_numeric_metrics(self):
        rows = [
            self.linked_row("2024-01-02", daily_range="10.000"),
            self.linked_row(
                "2024-01-03",
                linked_report.EXCLUDED_UNUSABLE,
                daily_range="999.000",
            ),
        ]

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            self.write_linked_report(linked_path, rows)
            _, baseline_rows = self.create_baseline(
                linked_path,
                temp_root_path / "reports",
            )

        metric = self.find_metric(
            baseline_rows,
            "range_summary",
            "range_summary",
            linked_report.STRICT_VALID,
            "daily_range",
        )
        self.assertEqual(metric["count"], "1")
        self.assertEqual(metric["max"], "10.000")

    def test_blank_session_ranges_are_unavailable_not_zero(self):
        rows = [
            self.linked_row("2024-01-02", tokyo_range=""),
            self.linked_row("2024-01-03", tokyo_range="5.000"),
        ]

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            self.write_linked_report(linked_path, rows)
            _, baseline_rows = self.create_baseline(
                linked_path,
                temp_root_path / "reports",
            )

        range_metric = self.find_metric(
            baseline_rows,
            "range_summary",
            "range_summary",
            linked_report.STRICT_VALID,
            "tokyo_range",
        )
        blank_metric = self.find_metric(
            baseline_rows,
            "availability",
            "blank_value_count",
            linked_report.STRICT_VALID,
            "tokyo_range",
        )
        usable_metric = self.find_metric(
            baseline_rows,
            "availability",
            "usable_numeric_value_count",
            linked_report.STRICT_VALID,
            "tokyo_range",
        )
        self.assertEqual(range_metric["count"], "1")
        self.assertEqual(range_metric["min"], "5.000")
        self.assertEqual(blank_metric["count"], "1")
        self.assertEqual(usable_metric["count"], "1")

    def test_session_range_summaries_cover_tokyo_london_new_york(self):
        rows = [
            self.linked_row(
                "2024-01-02",
                tokyo_range="1.000",
                london_range="2.000",
                new_york_range="6.000",
            ),
            self.linked_row(
                "2024-01-03",
                tokyo_range="3.000",
                london_range="4.000",
                new_york_range="8.000",
            ),
        ]

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            self.write_linked_report(linked_path, rows)
            _, baseline_rows = self.create_baseline(
                linked_path,
                temp_root_path / "reports",
            )

        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "range_summary",
                "range_summary",
                linked_report.STRICT_VALID,
                "tokyo_range",
            )["median"],
            "2.000",
        )
        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "range_summary",
                "range_summary",
                linked_report.STRICT_VALID,
                "london_range",
            )["median"],
            "3.000",
        )
        self.assertEqual(
            self.find_metric(
                baseline_rows,
                "range_summary",
                "range_summary",
                linked_report.STRICT_VALID,
                "new_york_range",
            )["median"],
            "7.000",
        )

    def test_output_path_is_deterministic_from_input_report_name(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = (
                temp_root_path
                / "inputs"
                / "linked_observation_report_2024-01-01_to_2024-01-31.csv"
            )
            reports_dir = temp_root_path / "reports"
            self.write_linked_report(linked_path, [self.linked_row()])

            summary, _ = self.create_baseline(linked_path, reports_dir)

        self.assertEqual(
            summary.output_path,
            reports_dir
            / "historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv",
        )

    def test_baseline_rows_preserve_source_identity(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "renamed_linked.csv"
            self.write_linked_report(
                linked_path,
                [self.linked_row("2024-01-02", quote_side="ASK")],
            )
            _, baseline_rows = self.create_baseline(
                linked_path,
                temp_root_path / "reports",
            )

        for row in baseline_rows:
            self.assertEqual(row["provider"], "Dukascopy")
            self.assertEqual(row["instrument"], "XAUUSD")
            self.assertEqual(row["quote_side"], "ASK")
            self.assertEqual(row["timeframe"], "1min")

    def test_baseline_columns_have_stable_order(self):
        self.assertEqual(
            baseline.BASELINE_COLUMNS,
            [
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
            ],
        )

    def test_console_summary_includes_coverage_and_strict_warning_separation(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            linked_path = temp_root_path / "linked.csv"
            reports_dir = temp_root_path / "reports"
            self.write_linked_report(
                linked_path,
                [
                    self.linked_row("2024-01-02"),
                    self.linked_row("2024-01-03", linked_report.WARNING_REVIEW),
                ],
            )

            output = io.StringIO()
            with (
                patch("historical_baseline_report.REPORTS_DIR", reports_dir),
                contextlib.redirect_stdout(output),
            ):
                exit_code = baseline.main([str(linked_path)])

        self.assertEqual(exit_code, 0)
        console_text = output.getvalue()
        self.assertIn("Strict-valid observations: 1", console_text)
        self.assertIn("Warning-review observations: 1", console_text)
        self.assertIn("Headline numeric baseline: strict_valid observations only.", console_text)
        self.assertIn("Warning-review numeric summaries are reported separately.", console_text)


if __name__ == "__main__":
    unittest.main()
