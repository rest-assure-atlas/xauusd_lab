import csv
import hashlib
import unittest
from collections import Counter
from datetime import date, time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import chart
import explorer
import session_report
from fixture_helpers import (
    make_active_rows,
    make_friday_rows_active_until_22_utc,
    make_placeholder_only_day,
    production_csv_filename,
    write_daily_csv,
    write_invalid_daily_csv,
)


class SessionReportTest(unittest.TestCase):
    def make_raw_row(
        self,
        day,
        time_text,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
    ):
        return {
            "timestamp_utc": f"{day.isoformat()} {time_text}",
            "open": f"{open_price:.3f}",
            "high": f"{high_price:.3f}",
            "low": f"{low_price:.3f}",
            "close": f"{close_price:.3f}",
            "volume": str(volume),
        }

    def run_single_day_report_from_rows(self, day, rows):
        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            write_daily_csv(data_dir, day, rows)

            with (
                patch("session_report.DATA_RAW_DIR", data_dir),
                patch("session_report.REPORTS_DIR", reports_dir),
            ):
                summary = session_report.create_session_report(day, day)

            with summary.output_path.open("r", newline="", encoding="utf-8") as report_file:
                return next(csv.DictReader(report_file))

    def test_short_january_range_writes_one_row_per_date(self):
        start_day = date(2024, 1, 1)
        end_day = date(2024, 1, 3)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"

            for day in session_report.each_day(start_day, end_day):
                write_daily_csv(data_dir, day, make_active_rows(day, end_time=time(0, 5)))

            with (
                patch("session_report.DATA_RAW_DIR", data_dir),
                patch("session_report.REPORTS_DIR", reports_dir),
            ):
                summary = session_report.create_session_report(start_day, end_day)

            with summary.output_path.open("r", newline="", encoding="utf-8") as report_file:
                rows = list(csv.DictReader(report_file))

        self.assertEqual(summary.requested_dates, 3)
        self.assertEqual(len(rows), 3)
        self.assertEqual(summary.completed_dates, 3)
        self.assertEqual(summary.missing_files, 0)
        self.assertEqual(summary.no_active_candle_dates, 0)
        self.assertEqual(summary.failed_dates, 0)
        self.assertEqual([row["status"] for row in rows], ["complete", "complete", "complete"])

    def test_single_day_values_match_existing_calculations(self):
        day = date(2024, 1, 26)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            csv_path = write_daily_csv(
                data_dir,
                day,
                make_friday_rows_active_until_22_utc(day),
            )

            before_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()

            with (
                patch("session_report.DATA_RAW_DIR", data_dir),
                patch("session_report.REPORTS_DIR", reports_dir),
            ):
                summary = session_report.create_session_report(day, day)

            with summary.output_path.open("r", newline="", encoding="utf-8") as report_file:
                report_row = next(csv.DictReader(report_file))

            raw_rows = explorer.load_candles(csv_path)
            daily_statistics = explorer.calculate_daily_statistics(raw_rows)
            session_statistics = {
                statistics.session_name.lower().replace(" ", "_"): statistics
                for statistics in explorer.calculate_session_statistics_for_day(day, raw_rows)
            }
            after_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()

        self.assertEqual(report_row["daily_open"], f"{daily_statistics['open_price']:.3f}")
        self.assertEqual(report_row["daily_high"], f"{daily_statistics['high_price']:.3f}")
        self.assertEqual(report_row["daily_low"], f"{daily_statistics['low_price']:.3f}")
        self.assertEqual(report_row["daily_close"], f"{daily_statistics['close_price']:.3f}")
        self.assertEqual(report_row["daily_range"], f"{daily_statistics['daily_range']:.3f}")
        self.assertEqual(report_row["active_candle_count"], "1320")
        self.assertEqual(report_row["inactive_placeholder_count"], "120")

        tokyo_statistics = session_statistics["tokyo"]
        self.assertEqual(report_row["tokyo_open"], f"{tokyo_statistics.open:.3f}")
        self.assertEqual(report_row["tokyo_high"], f"{tokyo_statistics.high:.3f}")
        self.assertEqual(report_row["tokyo_low"], f"{tokyo_statistics.low:.3f}")
        self.assertEqual(report_row["tokyo_close"], f"{tokyo_statistics.close:.3f}")
        self.assertEqual(report_row["tokyo_range"], f"{tokyo_statistics.range_dollars:.3f}")
        self.assertEqual(report_row["tokyo_active_candle_count"], "540")

        self.assertEqual(before_hash, after_hash)

    def test_daily_high_tie_records_first_active_occurrence_after_edge_filtering(self):
        day = date(2024, 1, 2)
        active_rows = [
            self.make_raw_row(day, "00:01:00", 2000.0, 2002.0, 1999.0, 2001.0, 10),
            self.make_raw_row(day, "00:02:00", 2001.0, 2010.0, 2000.0, 2009.0, 12),
            self.make_raw_row(day, "00:03:00", 2009.0, 2009.5, 2005.0, 2006.0, 11),
            self.make_raw_row(day, "00:04:00", 2006.0, 2010.0, 2001.0, 2002.0, 13),
            self.make_raw_row(day, "00:05:00", 2002.0, 2004.0, 1998.0, 2003.0, 9),
        ]
        rows = [
            self.make_raw_row(day, "00:00:00", 2500.0, 2500.0, 2500.0, 2500.0, 0),
            *active_rows,
            self.make_raw_row(day, "00:06:00", 2600.0, 2600.0, 2600.0, 2600.0, 0),
        ]

        report_row = self.run_single_day_report_from_rows(day, rows)
        tied_high_times = [
            row["timestamp_utc"].split()[1]
            for row in active_rows
            if row["high"] == "2010.000"
        ]

        self.assertEqual(tied_high_times, ["00:02:00", "00:04:00"])
        self.assertEqual(report_row["active_candle_count"], "5")
        self.assertEqual(report_row["inactive_placeholder_count"], "2")
        self.assertEqual(report_row["daily_high"], "2010.000")
        self.assertEqual(report_row["time_of_daily_high_utc"], tied_high_times[0])

    def test_daily_low_tie_records_first_active_occurrence_after_edge_filtering(self):
        day = date(2024, 1, 3)
        active_rows = [
            self.make_raw_row(day, "00:01:00", 2000.0, 2004.0, 1998.0, 2002.0, 10),
            self.make_raw_row(day, "00:02:00", 2002.0, 2003.0, 1980.0, 1985.0, 12),
            self.make_raw_row(day, "00:03:00", 1985.0, 1995.0, 1984.0, 1992.0, 11),
            self.make_raw_row(day, "00:04:00", 1992.0, 2000.0, 1980.0, 1999.0, 13),
            self.make_raw_row(day, "00:05:00", 1999.0, 2001.0, 1995.0, 2000.0, 9),
        ]
        rows = [
            self.make_raw_row(day, "00:00:00", 1000.0, 1000.0, 1000.0, 1000.0, 0),
            *active_rows,
            self.make_raw_row(day, "00:06:00", 900.0, 900.0, 900.0, 900.0, 0),
        ]

        report_row = self.run_single_day_report_from_rows(day, rows)
        tied_low_times = [
            row["timestamp_utc"].split()[1]
            for row in active_rows
            if row["low"] == "1980.000"
        ]

        self.assertEqual(tied_low_times, ["00:02:00", "00:04:00"])
        self.assertEqual(report_row["active_candle_count"], "5")
        self.assertEqual(report_row["inactive_placeholder_count"], "2")
        self.assertEqual(report_row["daily_low"], "1980.000")
        self.assertEqual(report_row["time_of_daily_low_utc"], tied_low_times[0])

    def test_summary_counts_reconcile_to_requested_dates_with_all_statuses(self):
        start_day = date(2024, 1, 1)
        end_day = date(2024, 1, 5)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"

            write_daily_csv(data_dir, date(2024, 1, 1), make_active_rows(date(2024, 1, 1)))
            write_daily_csv(data_dir, date(2024, 1, 2), make_active_rows(date(2024, 1, 2)))
            write_daily_csv(
                data_dir,
                date(2024, 1, 3),
                make_placeholder_only_day(date(2024, 1, 3)),
            )
            write_invalid_daily_csv(data_dir, date(2024, 1, 4))
            # 2024-01-05 is intentionally absent to exercise missing_file.

            with (
                patch("session_report.DATA_RAW_DIR", data_dir),
                patch("session_report.REPORTS_DIR", reports_dir),
                patch("builtins.print"),
            ):
                summary = session_report.create_session_report(start_day, end_day)

            with summary.output_path.open("r", newline="", encoding="utf-8") as report_file:
                rows = list(csv.DictReader(report_file))

        statuses_by_date = {row["date"]: row["status"] for row in rows}
        status_counts = Counter(statuses_by_date.values())

        counted_dates = (
            summary.completed_dates
            + summary.missing_files
            + summary.no_active_candle_dates
            + summary.failed_dates
        )

        self.assertEqual(summary.requested_dates, 5)
        self.assertEqual(summary.completed_dates, 2)
        self.assertEqual(summary.no_active_candle_dates, 1)
        self.assertEqual(summary.failed_dates, 1)
        self.assertEqual(summary.missing_files, 1)
        self.assertEqual(len(rows), 5)
        self.assertEqual(
            statuses_by_date,
            {
                "2024-01-01": "complete",
                "2024-01-02": "complete",
                "2024-01-03": "no_active_candles",
                "2024-01-04": "failed",
                "2024-01-05": "missing_file",
            },
        )
        self.assertEqual(status_counts["complete"], 2)
        self.assertEqual(status_counts["no_active_candles"], 1)
        self.assertEqual(status_counts["failed"], 1)
        self.assertEqual(status_counts["missing_file"], 1)
        self.assertEqual(counted_dates, summary.requested_dates)

    def test_missing_file_produces_missing_file_status_row(self):
        day = date(2024, 1, 15)
        columns = session_report.build_report_columns(day)
        missing_path = session_report.PROJECT_DIR / "missing_test_file.csv"

        with patch("session_report.build_csv_path", return_value=missing_path):
            result = session_report.process_one_day(day, columns)

        self.assertEqual(result.row["date"], "2024-01-15")
        self.assertEqual(result.row["weekday"], "Monday")
        self.assertEqual(result.row["status"], "missing_file")
        self.assertFalse(result.completed)
        self.assertTrue(result.missing_file)
        self.assertFalse(result.failed)

    def test_report_columns_have_stable_order(self):
        columns = session_report.build_report_columns(date(2024, 1, 1))
        expected_columns = [
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
            "tokyo_open",
            "tokyo_high",
            "tokyo_low",
            "tokyo_close",
            "tokyo_range",
            "tokyo_time_of_high_utc",
            "tokyo_time_of_low_utc",
            "tokyo_active_candle_count",
            "london_open",
            "london_high",
            "london_low",
            "london_close",
            "london_range",
            "london_time_of_high_utc",
            "london_time_of_low_utc",
            "london_active_candle_count",
            "new_york_open",
            "new_york_high",
            "new_york_low",
            "new_york_close",
            "new_york_range",
            "new_york_time_of_high_utc",
            "new_york_time_of_low_utc",
            "new_york_active_candle_count",
        ]

        self.assertEqual(columns, expected_columns)

    def test_csv_path_builders_use_production_filename(self):
        day = date(2024, 1, 26)
        expected_filename = production_csv_filename(day)

        self.assertEqual(session_report.build_csv_path(day).name, expected_filename)
        self.assertEqual(explorer.build_csv_path(day).name, expected_filename)
        self.assertEqual(chart.build_csv_path(day).name, expected_filename)


if __name__ == "__main__":
    unittest.main()
