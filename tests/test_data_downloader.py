import unittest
from datetime import date

import data_downloader


class DataDownloaderCliTest(unittest.TestCase):
    def tearDown(self):
        data_downloader.PRICE_SIDE = "BID"

    def test_command_line_dates_default_to_bid(self):
        start_day, end_day, source = data_downloader.get_download_dates(["2024-02-14", "2024-02-15"])

        self.assertEqual(start_day, date(2024, 2, 14))
        self.assertEqual(end_day, date(2024, 2, 15))
        self.assertEqual(source, "command line")
        self.assertEqual(data_downloader.PRICE_SIDE, "BID")
        self.assertEqual(
            data_downloader.build_output_path(start_day).name,
            "XAUUSD_2024-02-14_1min_BID_UTC.csv",
        )

    def test_quote_side_space_form_sets_ask_and_leaves_dates(self):
        start_day, end_day, source = data_downloader.get_download_dates(
            ["--quote-side", "ASK", "2024-02-14", "2024-02-15"]
        )

        self.assertEqual(start_day, date(2024, 2, 14))
        self.assertEqual(end_day, date(2024, 2, 15))
        self.assertEqual(source, "command line")
        self.assertEqual(data_downloader.PRICE_SIDE, "ASK")
        self.assertEqual(
            data_downloader.build_output_path(start_day).name,
            "XAUUSD_2024-02-14_1min_ASK_UTC.csv",
        )

    def test_quote_side_equals_form_sets_ask_and_leaves_dates(self):
        start_day, end_day, _ = data_downloader.get_download_dates(
            ["--quote-side=ASK", "2024-02-14", "2024-02-15"]
        )

        self.assertEqual(start_day, date(2024, 2, 14))
        self.assertEqual(end_day, date(2024, 2, 15))
        self.assertEqual(data_downloader.PRICE_SIDE, "ASK")

    def test_unknown_duplicate_missing_and_invalid_quote_side_errors_are_clear(self):
        cases = (
            (["--price-side", "ASK", "2024-02-14"], "Unknown option: --price-side"),
            (["--quote-side", "ASK", "--quote-side=BID", "2024-02-14"], "only once"),
            (["--quote-side"], "BID or ASK"),
            (["--quote-side", "--price-side", "2024-02-14"], "BID or ASK"),
            (["--quote-side", "MID", "2024-02-14"], "quote_side must be one of: BID, ASK"),
            (["--quote-side=", "2024-02-14"], "quote_side must be one of: BID, ASK"),
        )

        for arguments, message in cases:
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(ValueError, message):
                    data_downloader.get_download_dates(arguments)


if __name__ == "__main__":
    unittest.main()
