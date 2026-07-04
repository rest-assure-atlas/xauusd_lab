import hashlib
import unittest
from datetime import date, time
from pathlib import Path
from tempfile import TemporaryDirectory

import data_quality
from fixture_helpers import (
    CSV_HEADERS,
    make_active_rows,
    make_placeholder_rows,
    production_csv_path,
    write_daily_csv,
)


class DataQualityTest(unittest.TestCase):
    def setUp(self):
        self.day = date(2024, 1, 2)

    def assess_rows(self, rows):
        with TemporaryDirectory() as temp_root:
            csv_path = write_daily_csv(Path(temp_root), self.day, rows)
            return data_quality.assess_raw_csv_file(csv_path, self.day).fields

    def one_active_row(self, timestamp="2024-01-02 00:00:00"):
        row = make_active_rows(self.day, time(0, 0), time(0, 1))[0]
        row["timestamp_utc"] = timestamp
        return row

    def full_day_rows(self):
        return make_active_rows(self.day, time(0, 0), time(0, 0))

    def assert_timestamp_text_is_invalid(self, timestamp_text):
        fields = self.assess_rows([self.one_active_row(timestamp_text)])

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["invalid_timestamp_count"], "1")
        self.assertEqual(fields["off_minute_timestamp_count"], "0")
        self.assertIn(data_quality.INVALID_TIMESTAMP, fields["quality_reasons"])
        self.assertEqual(fields["first_timestamp_utc"], "")
        self.assertEqual(fields["last_timestamp_utc"], "")

    def test_valid_ordered_minute_data(self):
        fields = self.assess_rows(self.full_day_rows())

        self.assertEqual(fields["file_status"], "processed")
        self.assertEqual(fields["quality_status"], "valid")
        self.assertEqual(fields["quality_reasons"], "")
        self.assertEqual(fields["total_row_count"], "1440")
        self.assertEqual(fields["active_row_count"], "1440")
        self.assertEqual(fields["first_timestamp_utc"], "2024-01-02 00:00:00")
        self.assertEqual(fields["last_timestamp_utc"], "2024-01-02 23:59:00")
        self.assertEqual(fields["duplicate_timestamp_count"], "0")
        self.assertEqual(fields["out_of_order_timestamp_count"], "0")
        self.assertEqual(fields["missing_minute_count"], "0")
        self.assertEqual(fields["internal_gap_count"], "0")
        self.assertEqual(fields["maximum_internal_gap_minutes"], "0")
        self.assertEqual(fields["leading_day_gap_minutes"], "0")
        self.assertEqual(fields["trailing_day_gap_minutes"], "0")

    def test_exact_zero_padded_timestamp_text_is_accepted(self):
        fields = self.assess_rows([self.one_active_row("2024-01-02 00:00:00")])

        self.assertEqual(fields["invalid_timestamp_count"], "0")
        self.assertNotIn(data_quality.INVALID_TIMESTAMP, fields["quality_reasons"])
        self.assertEqual(fields["first_timestamp_utc"], "2024-01-02 00:00:00")
        self.assertEqual(fields["last_timestamp_utc"], "2024-01-02 00:00:00")

    def test_one_row_midday_file_is_partial_day_warning(self):
        row = self.one_active_row("2024-01-02 12:00:00")
        fields = self.assess_rows([row])

        self.assertEqual(fields["file_status"], "processed")
        self.assertEqual(fields["quality_status"], "warning")
        self.assertEqual(fields["leading_day_gap_minutes"], "720")
        self.assertEqual(fields["trailing_day_gap_minutes"], "719")
        self.assertEqual(fields["missing_minute_count"], "0")
        self.assertIn(data_quality.PARTIAL_DAY_COVERAGE, fields["quality_reasons"])

    def test_missing_start_of_day_range_is_warning(self):
        rows = make_active_rows(self.day, time(0, 5), time(0, 0))
        fields = self.assess_rows(rows)

        self.assertEqual(fields["quality_status"], "warning")
        self.assertEqual(fields["leading_day_gap_minutes"], "5")
        self.assertEqual(fields["trailing_day_gap_minutes"], "0")
        self.assertIn(data_quality.PARTIAL_DAY_COVERAGE, fields["quality_reasons"])

    def test_missing_end_of_day_range_is_warning(self):
        rows = make_active_rows(self.day, time(0, 0), time(22, 0))
        fields = self.assess_rows(rows)

        self.assertEqual(fields["quality_status"], "warning")
        self.assertEqual(fields["leading_day_gap_minutes"], "0")
        self.assertEqual(fields["trailing_day_gap_minutes"], "120")
        self.assertIn(data_quality.PARTIAL_DAY_COVERAGE, fields["quality_reasons"])

    def test_missing_file_assessment(self):
        fields = data_quality.missing_file_assessment().fields

        self.assertEqual(fields["file_status"], "missing_file")
        self.assertEqual(fields["quality_status"], "not_assessed")
        self.assertEqual(fields["quality_reasons"], data_quality.MISSING_FILE)
        self.assertEqual(fields["source_file_size_bytes"], "")
        self.assertEqual(fields["source_checksum"], "")

    def test_empty_file_is_invalid_with_checksum(self):
        with TemporaryDirectory() as temp_root:
            csv_path = production_csv_path(Path(temp_root), self.day)
            csv_path.write_bytes(b"")
            fields = data_quality.assess_raw_csv_file(csv_path, self.day).fields

        self.assertEqual(fields["file_status"], "empty_file")
        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["quality_reasons"], data_quality.EMPTY_FILE)
        self.assertEqual(fields["source_file_size_bytes"], "0")
        self.assertEqual(fields["source_checksum_algorithm"], "sha256")
        self.assertEqual(
            fields["source_checksum"],
            hashlib.sha256(b"").hexdigest(),
        )
        self.assertEqual(fields["total_row_count"], "0")

    def test_header_only_file_is_empty_file(self):
        fields = self.assess_rows([])

        self.assertEqual(fields["file_status"], "empty_file")
        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["total_row_count"], "0")

    def test_incorrect_header_is_parse_failed(self):
        with TemporaryDirectory() as temp_root:
            csv_path = production_csv_path(Path(temp_root), self.day)
            csv_path.write_text("wrong,open,high,low,close,volume\n", encoding="utf-8")
            fields = data_quality.assess_raw_csv_file(csv_path, self.day).fields

        self.assertEqual(fields["file_status"], "parse_failed")
        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["quality_reasons"], data_quality.HEADER_MISMATCH)

    def test_malformed_row_shape_is_parse_failed(self):
        with TemporaryDirectory() as temp_root:
            csv_path = production_csv_path(Path(temp_root), self.day)
            csv_path.write_text(
                ",".join(CSV_HEADERS) + "\n2024-01-02 00:00:00,2000.000\n",
                encoding="utf-8",
            )
            fields = data_quality.assess_raw_csv_file(csv_path, self.day).fields

        self.assertEqual(fields["file_status"], "parse_failed")
        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["quality_reasons"], data_quality.ROW_SHAPE_MISMATCH)

    def test_invalid_timestamp_is_counted_without_parse_failure(self):
        row = self.one_active_row("not-a-timestamp")
        fields = self.assess_rows([row])

        self.assertEqual(fields["file_status"], "processed")
        self.assertEqual(fields["quality_status"], "invalid")
        self.assertIn(data_quality.INVALID_TIMESTAMP, fields["quality_reasons"])
        self.assertEqual(fields["invalid_timestamp_count"], "1")
        self.assertEqual(fields["missing_minute_count"], "")
        self.assertEqual(fields["leading_day_gap_minutes"], "")
        self.assertEqual(fields["trailing_day_gap_minutes"], "")

    def test_non_zero_padded_month_timestamp_is_invalid(self):
        self.assert_timestamp_text_is_invalid("2024-1-02 00:00:00")

    def test_non_zero_padded_day_timestamp_is_invalid(self):
        self.assert_timestamp_text_is_invalid("2024-01-2 00:00:00")

    def test_non_zero_padded_hour_timestamp_is_invalid(self):
        self.assert_timestamp_text_is_invalid("2024-01-02 0:00:00")

    def test_non_zero_padded_minute_timestamp_is_invalid(self):
        self.assert_timestamp_text_is_invalid("2024-01-02 00:0:00")

    def test_non_zero_padded_second_timestamp_is_invalid(self):
        self.assert_timestamp_text_is_invalid("2024-01-02 00:00:0")

    def test_leading_whitespace_timestamp_is_invalid(self):
        self.assert_timestamp_text_is_invalid(" 2024-01-02 00:00:00")

    def test_trailing_whitespace_timestamp_is_invalid(self):
        self.assert_timestamp_text_is_invalid("2024-01-02 00:00:00 ")

    def test_fractional_zero_microsecond_timestamp_is_invalid(self):
        row = self.one_active_row("2024-01-02 00:00:00.000000")
        fields = self.assess_rows([row])

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["invalid_timestamp_count"], "1")
        self.assertEqual(fields["off_minute_timestamp_count"], "0")
        self.assertIn(data_quality.INVALID_TIMESTAMP, fields["quality_reasons"])

    def test_fractional_nonzero_microsecond_timestamp_is_invalid(self):
        row = self.one_active_row("2024-01-02 00:00:00.500000")
        fields = self.assess_rows([row])

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["invalid_timestamp_count"], "1")
        self.assertEqual(fields["off_minute_timestamp_count"], "0")
        self.assertIn(data_quality.INVALID_TIMESTAMP, fields["quality_reasons"])

    def test_off_minute_timestamp_is_counted(self):
        row = self.one_active_row("2024-01-02 00:00:30")
        fields = self.assess_rows([row])

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertIn(data_quality.TIMESTAMP_OFF_MINUTE, fields["quality_reasons"])
        self.assertEqual(fields["invalid_timestamp_count"], "0")
        self.assertEqual(fields["off_minute_timestamp_count"], "1")
        self.assertEqual(fields["missing_minute_count"], "")

    def test_wrong_date_timestamp_is_counted(self):
        row = self.one_active_row("2024-01-03 00:00:00")
        fields = self.assess_rows([row])

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertIn(data_quality.TIMESTAMP_DATE_MISMATCH, fields["quality_reasons"])
        self.assertEqual(fields["wrong_date_timestamp_count"], "1")
        self.assertEqual(fields["missing_minute_count"], "")

    def test_invalid_numeric_value_is_counted_without_parse_failure(self):
        row = self.one_active_row()
        row["open"] = "not-a-number"
        fields = self.assess_rows([row])

        self.assertEqual(fields["file_status"], "processed")
        self.assertEqual(fields["quality_status"], "invalid")
        self.assertIn(data_quality.INVALID_NUMERIC, fields["quality_reasons"])
        self.assertEqual(fields["invalid_numeric_row_count"], "1")
        self.assertEqual(fields["active_row_count"], "")

    def test_nan_and_infinite_numeric_values_are_invalid(self):
        first_row = self.one_active_row("2024-01-02 00:00:00")
        first_row["open"] = "NaN"
        second_row = self.one_active_row("2024-01-02 00:01:00")
        second_row["volume"] = "inf"
        fields = self.assess_rows([first_row, second_row])

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["invalid_numeric_row_count"], "2")
        self.assertIn(data_quality.INVALID_NUMERIC, fields["quality_reasons"])

    def test_invalid_ohlc_relationship_is_counted(self):
        row = self.one_active_row()
        row["high"] = "1990.000"
        fields = self.assess_rows([row])

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["ohlc_consistency_failure_count"], "1")
        self.assertIn(data_quality.OHLC_INCONSISTENT, fields["quality_reasons"])

    def test_negative_volume_is_counted(self):
        row = self.one_active_row()
        row["volume"] = "-1.00000000"
        fields = self.assess_rows([row])

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["negative_volume_count"], "1")
        self.assertIn(data_quality.NEGATIVE_VOLUME, fields["quality_reasons"])

    def test_duplicate_timestamp_is_counted(self):
        rows = make_active_rows(self.day, time(0, 0), time(0, 2))
        rows[1]["timestamp_utc"] = rows[0]["timestamp_utc"]
        fields = self.assess_rows(rows)

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["duplicate_timestamp_count"], "1")
        self.assertEqual(fields["out_of_order_timestamp_count"], "0")
        self.assertIn(data_quality.DUPLICATE_TIMESTAMP, fields["quality_reasons"])

    def test_out_of_order_timestamp_is_counted(self):
        rows = make_active_rows(self.day, time(0, 0), time(0, 2))
        rows = [rows[1], rows[0]]
        fields = self.assess_rows(rows)

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["out_of_order_timestamp_count"], "1")
        self.assertEqual(fields["duplicate_timestamp_count"], "0")
        self.assertIn(data_quality.OUT_OF_ORDER_TIMESTAMP, fields["quality_reasons"])

    def test_out_of_order_file_reports_chronological_first_and_last_timestamps(self):
        rows = make_active_rows(self.day, time(0, 0), time(0, 3))
        rows = [rows[2], rows[0], rows[1]]
        fields = self.assess_rows(rows)

        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["out_of_order_timestamp_count"], "1")
        self.assertEqual(fields["first_timestamp_utc"], "2024-01-02 00:00:00")
        self.assertEqual(fields["last_timestamp_utc"], "2024-01-02 00:02:00")
        self.assertEqual(fields["first_active_timestamp_utc"], "2024-01-02 00:00:00")
        self.assertEqual(fields["last_active_timestamp_utc"], "2024-01-02 00:02:00")
        self.assertLessEqual(
            fields["first_active_timestamp_utc"],
            fields["last_active_timestamp_utc"],
        )

    def test_one_missing_minute_is_warning(self):
        rows = self.full_day_rows()
        rows.pop(720)
        fields = self.assess_rows(rows)

        self.assertEqual(fields["quality_status"], "warning")
        self.assertEqual(fields["missing_minute_count"], "1")
        self.assertEqual(fields["internal_gap_count"], "1")
        self.assertEqual(fields["maximum_internal_gap_minutes"], "1")
        self.assertEqual(fields["leading_day_gap_minutes"], "0")
        self.assertEqual(fields["trailing_day_gap_minutes"], "0")
        self.assertEqual(fields["quality_reasons"], data_quality.MISSING_MINUTES)

    def test_multiple_internal_gaps_are_counted(self):
        rows = self.full_day_rows()

        for missing_index in (500, 11, 10):
            rows.pop(missing_index)

        fields = self.assess_rows(rows)

        self.assertEqual(fields["quality_status"], "warning")
        self.assertEqual(fields["missing_minute_count"], "3")
        self.assertEqual(fields["internal_gap_count"], "2")
        self.assertEqual(fields["maximum_internal_gap_minutes"], "2")
        self.assertEqual(fields["leading_day_gap_minutes"], "0")
        self.assertEqual(fields["trailing_day_gap_minutes"], "0")

    def test_leading_and_trailing_inactive_placeholders_are_counted(self):
        rows = (
            make_placeholder_rows(self.day, time(0, 0), time(0, 2))
            + make_active_rows(self.day, time(0, 2), time(23, 58))
            + make_placeholder_rows(self.day, time(23, 58), time(0, 0))
        )
        fields = self.assess_rows(rows)

        self.assertEqual(fields["file_status"], "processed")
        self.assertEqual(fields["quality_status"], "valid")
        self.assertEqual(fields["active_row_count"], "1436")
        self.assertEqual(fields["leading_inactive_row_count"], "2")
        self.assertEqual(fields["trailing_inactive_row_count"], "2")
        self.assertEqual(fields["first_active_timestamp_utc"], "2024-01-02 00:02:00")
        self.assertEqual(fields["last_active_timestamp_utc"], "2024-01-02 23:57:00")
        self.assertEqual(fields["leading_day_gap_minutes"], "0")
        self.assertEqual(fields["trailing_day_gap_minutes"], "0")
        self.assertNotIn(
            data_quality.PARTIAL_DAY_COVERAGE,
            fields["quality_reasons"],
        )

    def test_internal_flat_zero_volume_row_is_preserved_and_warned(self):
        rows = make_active_rows(self.day, time(0, 0), time(0, 3))
        rows[1] = make_placeholder_rows(self.day, time(0, 1), time(0, 2))[0]
        fields = self.assess_rows(rows)

        self.assertEqual(fields["file_status"], "processed")
        self.assertEqual(fields["quality_status"], "warning")
        self.assertEqual(fields["active_row_count"], "3")
        self.assertEqual(fields["internal_inactive_row_count"], "1")
        self.assertIn(
            data_quality.INTERNAL_FLAT_ZERO_VOLUME,
            fields["quality_reasons"],
        )

    def test_no_active_candle_file_is_not_assessed(self):
        rows = make_placeholder_rows(self.day, time(0, 0), time(0, 3))
        fields = self.assess_rows(rows)

        self.assertEqual(fields["file_status"], "no_active_candles")
        self.assertEqual(fields["quality_status"], "not_assessed")
        self.assertEqual(fields["active_row_count"], "0")
        self.assertEqual(fields["leading_inactive_row_count"], "3")
        self.assertIn(data_quality.NO_ACTIVE_CANDLES, fields["quality_reasons"])

    def test_source_sha256_is_deterministic(self):
        rows = make_active_rows(self.day, time(0, 0), time(0, 2))

        with TemporaryDirectory() as temp_root:
            csv_path = write_daily_csv(Path(temp_root), self.day, rows)
            expected_checksum = hashlib.sha256(csv_path.read_bytes()).hexdigest()

            first_fields = data_quality.assess_raw_csv_file(csv_path, self.day).fields
            second_fields = data_quality.assess_raw_csv_file(csv_path, self.day).fields

        self.assertEqual(first_fields["source_checksum_algorithm"], "sha256")
        self.assertEqual(first_fields["source_checksum"], expected_checksum)
        self.assertEqual(first_fields["source_checksum"], second_fields["source_checksum"])

    def test_assessment_does_not_modify_source_file_bytes(self):
        rows = make_active_rows(self.day, time(0, 0), time(0, 2))

        with TemporaryDirectory() as temp_root:
            csv_path = write_daily_csv(Path(temp_root), self.day, rows)
            before_bytes = csv_path.read_bytes()

            data_quality.assess_raw_csv_file(csv_path, self.day)

            after_bytes = csv_path.read_bytes()

        self.assertEqual(before_bytes, after_bytes)

    def test_decode_error_is_parse_failed_read_error(self):
        with TemporaryDirectory() as temp_root:
            csv_path = production_csv_path(Path(temp_root), self.day)
            csv_path.write_bytes(b"\xff\xfe\x00")
            fields = data_quality.assess_raw_csv_file(csv_path, self.day).fields

        self.assertEqual(fields["file_status"], "parse_failed")
        self.assertEqual(fields["quality_status"], "invalid")
        self.assertEqual(fields["quality_reasons"], data_quality.READ_ERROR)


if __name__ == "__main__":
    unittest.main()
