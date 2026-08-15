import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import spread_characterization as spread


class SpreadCharacterizationTest(unittest.TestCase):
    def row(self, timestamp="2024-01-09 00:00:00", spread_value="0.100", bid_close="2000.000", reasons="BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW"):
        ask_close = f"{float(bid_close) + float(spread_value):.3f}"
        return {
            "date": timestamp[:10],
            "timestamp_utc": timestamp,
            "provider": "Dukascopy",
            "instrument": "XAUUSD",
            "timeframe": "1min",
            "bid_close": bid_close,
            "ask_close": ask_close,
            "spread": spread_value,
            "pair_quality_status": "warning_review_pair",
            "pair_quality_reasons": reasons,
        }

    def write_rows(self, path: Path, rows):
        fieldnames = [
            "date", "timestamp_utc", "provider", "instrument", "timeframe",
            "bid_close", "ask_close", "spread", "pair_quality_status", "pair_quality_reasons",
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def test_percentile_uses_linear_interpolation(self):
        values = [spread.parse_decimal(value) for value in ["1", "2", "3", "4"]]
        self.assertEqual(spread.percentile(values, spread.Decimal("0.50")), spread.Decimal("2.5"))

    def test_placeholder_detection_uses_pair_reason(self):
        row = self.row(reasons="BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW;MARKET_CLOSED_PLACEHOLDER")
        self.assertTrue(spread.is_placeholder(row))

    def test_summary_keeps_warning_review_and_secondary_placeholder_split(self):
        rows = [
            self.row(timestamp="2024-01-09 00:00:00", spread_value="0.100"),
            self.row(timestamp="2024-01-09 00:01:00", spread_value="0.300", reasons="BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW;MARKET_CLOSED_PLACEHOLDER"),
        ]
        with TemporaryDirectory() as temp_root:
            output_path = Path(temp_root) / "summary.csv"
            spread.write_summary(rows, output_path)
            with output_path.open(newline="", encoding="utf-8") as f:
                summary_rows = list(csv.DictReader(f))
        overall = [row for row in summary_rows if row["population"] == "all_warning_review_pairs" and row["group_type"] == "overall"][0]
        diagnostic = [row for row in summary_rows if row["population"] == "non_placeholder_diagnostic" and row["group_type"] == "overall"][0]
        self.assertEqual(overall["count"], "2")
        self.assertEqual(overall["placeholder_count"], "1")
        self.assertEqual(overall["mean_spread"], "0.200000")
        self.assertEqual(diagnostic["count"], "1")
        self.assertEqual(diagnostic["mean_spread"], "0.100000")

    def test_validate_input_rejects_silent_strict_valid_upgrade(self):
        rows = [self.row(timestamp=f"2024-01-09 00:{minute:02d}:00") for minute in range(2)]
        original_expected_rows = spread.EXPECTED_ROWS
        original_expected_dates = spread.EXPECTED_DATES
        try:
            spread.EXPECTED_ROWS = 2
            spread.EXPECTED_DATES = {"2024-01-09"}
            rows[0]["pair_quality_status"] = "strict_valid_pair"
            with self.assertRaisesRegex(ValueError, "pair-quality"):
                spread.validate_input(rows)
        finally:
            spread.EXPECTED_ROWS = original_expected_rows
            spread.EXPECTED_DATES = original_expected_dates

    def test_validate_input_rejects_spread_anomaly_reasons(self):
        rows = [self.row(timestamp=f"2024-01-09 00:{minute:02d}:00") for minute in range(2)]
        original_expected_rows = spread.EXPECTED_ROWS
        original_expected_dates = spread.EXPECTED_DATES
        try:
            spread.EXPECTED_ROWS = 2
            spread.EXPECTED_DATES = {"2024-01-09"}
            rows[1]["pair_quality_reasons"] += ";ZERO_SPREAD"
            with self.assertRaisesRegex(ValueError, "anomaly"):
                spread.validate_input(rows)
        finally:
            spread.EXPECTED_ROWS = original_expected_rows
            spread.EXPECTED_DATES = original_expected_dates


if __name__ == "__main__":
    unittest.main()
