import csv
import dataclasses
import unittest
from datetime import date, time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import data_manifest
import session_report
from fixture_helpers import make_active_rows, write_csv
from source_contracts import (
    ASK,
    BID,
    DEFAULT_SOURCE_CONTRACT,
    SourceContract,
    SourceContractError,
    build_raw_csv_filename,
    build_report_filename,
    source_contract_for_side,
    validate_quote_side,
)


class SourceContractsTest(unittest.TestCase):
    def test_bid_legacy_manifest_and_session_report_paths_are_unchanged(self):
        start_day = date(2024, 1, 1)
        end_day = date(2024, 1, 31)

        self.assertEqual(
            data_manifest.build_source_filename(date(2024, 1, 26)),
            "XAUUSD_2024-01-26_1min_BID_UTC.csv",
        )
        self.assertEqual(
            data_manifest.build_manifest_path(start_day, end_day).name,
            "data_manifest_2024-01-01_to_2024-01-31.csv",
        )
        self.assertEqual(
            session_report.build_csv_path(date(2024, 1, 26)).name,
            "XAUUSD_2024-01-26_1min_BID_UTC.csv",
        )
        self.assertEqual(
            session_report.build_report_path(start_day, end_day).name,
            "session_report_2024-01-01_to_2024-01-31.csv",
        )

    def test_valid_bid_side_is_accepted(self):
        self.assertEqual(validate_quote_side(BID), BID)
        self.assertEqual(source_contract_for_side(BID).quote_side, BID)

    def test_valid_ask_side_is_accepted(self):
        self.assertEqual(validate_quote_side(ASK), ASK)
        self.assertEqual(source_contract_for_side(ASK).quote_side, ASK)

    def test_invalid_quote_side_is_rejected(self):
        for quote_side in ("", "bid", "Ask", "MID", " BID"):
            with self.subTest(quote_side=quote_side):
                with self.assertRaises(SourceContractError):
                    validate_quote_side(quote_side)

    def test_ask_is_rejected_under_legacy_side_omitted_naming(self):
        ask_contract = source_contract_for_side(ASK)

        with self.assertRaisesRegex(SourceContractError, "BID-only"):
            build_report_filename(
                "data_manifest",
                date(2024, 1, 1),
                date(2024, 1, 31),
                ask_contract,
            )

        with self.assertRaisesRegex(SourceContractError, "BID-only"):
            data_manifest.build_manifest_path(
                date(2024, 1, 1),
                date(2024, 1, 31),
                ask_contract,
            )

    def test_side_aware_bid_filename_and_paths_can_include_side(self):
        bid_contract = source_contract_for_side(BID)

        self.assertEqual(
            build_raw_csv_filename(date(2024, 1, 26), bid_contract),
            "XAUUSD_2024-01-26_1min_BID_UTC.csv",
        )
        self.assertEqual(
            data_manifest.build_manifest_path(
                date(2024, 1, 1),
                date(2024, 1, 31),
                bid_contract,
                legacy_side_omitted=False,
            ).name,
            "data_manifest_BID_2024-01-01_to_2024-01-31.csv",
        )
        self.assertEqual(
            session_report.build_report_path(
                date(2024, 1, 1),
                date(2024, 1, 31),
                bid_contract,
                legacy_side_omitted=False,
            ).name,
            "session_report_BID_2024-01-01_to_2024-01-31.csv",
        )

    def test_side_aware_ask_filename_and_paths_include_side(self):
        ask_contract = source_contract_for_side(ASK)

        self.assertEqual(
            build_raw_csv_filename(date(2024, 1, 26), ask_contract),
            "XAUUSD_2024-01-26_1min_ASK_UTC.csv",
        )
        self.assertEqual(
            data_manifest.build_source_filename(date(2024, 1, 26), ask_contract),
            "XAUUSD_2024-01-26_1min_ASK_UTC.csv",
        )
        self.assertEqual(
            data_manifest.build_manifest_path(
                date(2024, 1, 1),
                date(2024, 1, 31),
                ask_contract,
                legacy_side_omitted=False,
            ).name,
            "data_manifest_ASK_2024-01-01_to_2024-01-31.csv",
        )
        self.assertEqual(
            session_report.build_csv_path(date(2024, 1, 26), ask_contract).name,
            "XAUUSD_2024-01-26_1min_ASK_UTC.csv",
        )
        self.assertEqual(
            session_report.build_report_path(
                date(2024, 1, 1),
                date(2024, 1, 31),
                ask_contract,
                legacy_side_omitted=False,
            ).name,
            "session_report_ASK_2024-01-01_to_2024-01-31.csv",
        )


    def test_create_ask_manifest_uses_side_specific_output_and_row_identity(self):
        ask_contract = source_contract_for_side(ASK)
        day = date(2024, 1, 26)

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            ask_path = data_dir / build_raw_csv_filename(day, ask_contract)
            write_csv(ask_path, make_active_rows(day, time(0, 0), time(0, 2)))

            with patch("data_manifest.REPORTS_DIR", reports_dir):
                summary = data_manifest.create_data_manifest(
                    day,
                    day,
                    data_dir,
                    ask_contract,
                    legacy_side_omitted=False,
                )

            with summary.output_path.open("r", newline="", encoding="utf-8") as manifest_file:
                rows = list(csv.DictReader(manifest_file))

        self.assertEqual(summary.output_path.name, "data_manifest_ASK_2024-01-26_to_2024-01-26.csv")
        self.assertEqual(summary.processed_files, 1)
        self.assertEqual(rows[0]["quote_side"], ASK)
        self.assertEqual(rows[0]["source_filename"], "XAUUSD_2024-01-26_1min_ASK_UTC.csv")
        self.assertEqual(rows[0]["file_status"], "processed")

    def test_create_session_report_can_use_ask_side_specific_paths(self):
        ask_contract = source_contract_for_side(ASK)
        day = date(2024, 1, 26)

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            ask_path = data_dir / build_raw_csv_filename(day, ask_contract)
            write_csv(ask_path, make_active_rows(day, time(0, 0), time(0, 2)))

            with (
                patch("session_report.DATA_RAW_DIR", data_dir),
                patch("session_report.REPORTS_DIR", reports_dir),
            ):
                summary = session_report.create_session_report(
                    day,
                    day,
                    ask_contract,
                    legacy_side_omitted=False,
                )

            with summary.output_path.open("r", newline="", encoding="utf-8") as report_file:
                rows = list(csv.DictReader(report_file))

        self.assertEqual(summary.output_path.name, "session_report_ASK_2024-01-26_to_2024-01-26.csv")
        self.assertEqual(summary.completed_dates, 1)
        self.assertEqual(rows[0]["status"], "complete")
        self.assertEqual(rows[0]["total_csv_rows"], "2")

    def test_create_session_report_rejects_ask_legacy_side_omitted_naming(self):
        with self.assertRaisesRegex(SourceContractError, "BID-only"):
            session_report.create_session_report(
                date(2024, 1, 1),
                date(2024, 1, 1),
                source_contract_for_side(ASK),
            )

    def test_source_contract_is_immutable(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            DEFAULT_SOURCE_CONTRACT.quote_side = ASK

    def test_source_contract_side_identity_is_recorded_in_manifest_rows(self):
        ask_contract = SourceContract(quote_side=ASK)
        row = data_manifest.base_manifest_row(date(2024, 1, 26), ask_contract)

        self.assertEqual(row["provider"], "Dukascopy")
        self.assertEqual(row["instrument"], "XAUUSD")
        self.assertEqual(row["quote_side"], ASK)
        self.assertEqual(row["timeframe"], "1min")
        self.assertEqual(row["source_filename"], "XAUUSD_2024-01-26_1min_ASK_UTC.csv")


if __name__ == "__main__":
    unittest.main()
