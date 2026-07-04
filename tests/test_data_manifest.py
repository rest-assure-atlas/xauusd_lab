import csv
import unittest
from datetime import date, time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import data_manifest
from fixture_helpers import (
    make_active_rows,
    make_placeholder_rows,
    production_csv_path,
    write_daily_csv,
)


class DataManifestTest(unittest.TestCase):
    def read_manifest_rows(self, manifest_path: Path):
        with manifest_path.open("r", newline="", encoding="utf-8") as manifest_file:
            return list(csv.DictReader(manifest_file))

    def test_source_filename_uses_exact_production_contract(self):
        self.assertEqual(
            data_manifest.build_source_filename(date(2024, 1, 26)),
            "XAUUSD_2024-01-26_1min_BID_UTC.csv",
        )

    def test_manifest_columns_have_stable_order(self):
        expected_columns = [
            "manifest_schema_version",
            "validation_rule_version",
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

        self.assertEqual(data_manifest.MANIFEST_COLUMNS, expected_columns)

    def test_missing_file_row_keeps_expected_filename_and_blank_provenance(self):
        day = date(2024, 1, 15)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            data_dir.mkdir()
            row = data_manifest.build_manifest_row(data_dir, day)

        self.assertEqual(row["source_filename"], "XAUUSD_2024-01-15_1min_BID_UTC.csv")
        self.assertEqual(row["file_status"], "missing_file")
        self.assertEqual(row["quality_status"], "not_assessed")
        self.assertEqual(row["source_file_size_bytes"], "")
        self.assertEqual(row["source_checksum_algorithm"], "")
        self.assertEqual(row["source_checksum"], "")

    def test_manifest_summary_counts_reconcile_to_requested_dates(self):
        start_day = date(2024, 1, 1)
        end_day = date(2024, 1, 6)

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            write_daily_csv(
                data_dir,
                date(2024, 1, 1),
                make_active_rows(date(2024, 1, 1), time(0, 0), time(0, 0)),
            )

            warning_rows = make_active_rows(date(2024, 1, 2), time(0, 0), time(0, 0))
            warning_rows.pop(720)
            write_daily_csv(data_dir, date(2024, 1, 2), warning_rows)

            production_csv_path(data_dir, date(2024, 1, 4)).write_bytes(b"")

            production_csv_path(data_dir, date(2024, 1, 5)).write_text(
                "wrong,open,high,low,close,volume\n",
                encoding="utf-8",
            )

            write_daily_csv(
                data_dir,
                date(2024, 1, 6),
                make_placeholder_rows(date(2024, 1, 6), time(0, 0), time(0, 2)),
            )

            with patch("data_manifest.REPORTS_DIR", reports_dir):
                summary = data_manifest.create_data_manifest(
                    start_day,
                    end_day,
                    data_dir,
                )

            rows = self.read_manifest_rows(summary.output_path)

        statuses_by_date = {row["date"]: row["file_status"] for row in rows}
        qualities_by_date = {row["date"]: row["quality_status"] for row in rows}
        file_status_total = (
            summary.processed_files
            + summary.missing_files
            + summary.empty_files
            + summary.parse_failures
            + summary.no_active_candle_files
        )
        quality_status_total = (
            summary.valid_dates
            + summary.warning_dates
            + summary.invalid_dates
            + summary.not_assessed_dates
        )

        self.assertEqual(summary.requested_dates, 6)
        self.assertEqual(summary.processed_files, 2)
        self.assertEqual(summary.missing_files, 1)
        self.assertEqual(summary.empty_files, 1)
        self.assertEqual(summary.parse_failures, 1)
        self.assertEqual(summary.no_active_candle_files, 1)
        self.assertEqual(summary.valid_dates, 1)
        self.assertEqual(summary.warning_dates, 1)
        self.assertEqual(summary.invalid_dates, 2)
        self.assertEqual(summary.not_assessed_dates, 2)
        self.assertEqual(file_status_total, summary.requested_dates)
        self.assertEqual(quality_status_total, summary.requested_dates)
        self.assertEqual(
            statuses_by_date,
            {
                "2024-01-01": "processed",
                "2024-01-02": "processed",
                "2024-01-03": "missing_file",
                "2024-01-04": "empty_file",
                "2024-01-05": "parse_failed",
                "2024-01-06": "no_active_candles",
            },
        )
        self.assertEqual(qualities_by_date["2024-01-01"], "valid")
        self.assertEqual(qualities_by_date["2024-01-02"], "warning")
        self.assertEqual(qualities_by_date["2024-01-03"], "not_assessed")
        self.assertEqual(qualities_by_date["2024-01-04"], "invalid")
        self.assertEqual(qualities_by_date["2024-01-05"], "invalid")
        self.assertEqual(qualities_by_date["2024-01-06"], "not_assessed")

    def test_manifest_output_is_date_sorted_and_deterministic(self):
        start_day = date(2024, 1, 1)
        end_day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            write_daily_csv(
                data_dir,
                start_day,
                make_active_rows(start_day, time(0, 0), time(0, 2)),
            )

            with patch("data_manifest.REPORTS_DIR", reports_dir):
                first_summary = data_manifest.create_data_manifest(
                    start_day,
                    end_day,
                    data_dir,
                )
                first_bytes = first_summary.output_path.read_bytes()

                second_summary = data_manifest.create_data_manifest(
                    start_day,
                    end_day,
                    data_dir,
                )
                second_bytes = second_summary.output_path.read_bytes()

            rows = self.read_manifest_rows(second_summary.output_path)

        self.assertEqual(first_summary.output_path, second_summary.output_path)
        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual([row["date"] for row in rows], ["2024-01-01", "2024-01-02"])

    def test_existing_empty_data_directory_produces_missing_rows(self):
        start_day = date(2024, 1, 1)
        end_day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            with patch("data_manifest.REPORTS_DIR", reports_dir):
                summary = data_manifest.create_data_manifest(
                    start_day,
                    end_day,
                    data_dir,
                )

            rows = self.read_manifest_rows(summary.output_path)

        self.assertEqual(summary.requested_dates, 2)
        self.assertEqual(summary.missing_files, 2)
        self.assertEqual(summary.not_assessed_dates, 2)
        self.assertEqual([row["file_status"] for row in rows], ["missing_file", "missing_file"])

    def test_parse_arguments_rejects_invalid_date_input(self):
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            data_manifest.parse_arguments(["not-a-date", "2024-01-02"])

    def test_parse_arguments_rejects_reversed_range(self):
        with self.assertRaisesRegex(ValueError, "earlier"):
            data_manifest.parse_arguments(["2024-01-02", "2024-01-01"])

    def test_parse_arguments_rejects_missing_data_directory(self):
        with TemporaryDirectory() as temp_root:
            missing_dir = Path(temp_root) / "missing"

            with self.assertRaisesRegex(ValueError, "does not exist"):
                data_manifest.parse_arguments(
                    [
                        "2024-01-01",
                        "2024-01-02",
                        "--data-dir",
                        str(missing_dir),
                    ]
                )

    def test_main_returns_nonzero_for_invalid_date(self):
        with (
            patch.object(
                data_manifest.sys,
                "argv",
                ["data_manifest.py", "bad-date", "2024-01-02"],
            ),
            patch("builtins.print") as mock_print,
        ):
            exit_code = data_manifest.main()

        self.assertEqual(exit_code, 1)
        self.assertIn("Input error:", mock_print.call_args_list[0].args[0])


if __name__ == "__main__":
    unittest.main()
