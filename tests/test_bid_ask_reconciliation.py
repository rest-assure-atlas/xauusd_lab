import csv
import hashlib
import unittest
from datetime import date, time
from pathlib import Path
from tempfile import TemporaryDirectory

import bid_ask_reconciliation as recon
from fixture_helpers import make_active_rows, make_placeholder_rows, write_csv
from source_contracts import ASK, BID, SourceContract, build_raw_csv_filename


class BidAskReconciliationTest(unittest.TestCase):
    def setUp(self):
        self.day = date(2024, 1, 9)

    def linked_row(self, side, quality_tier="strict_valid", provider="Dukascopy", instrument="XAUUSD", timeframe="1min"):
        filename = build_raw_csv_filename(self.day, SourceContract(provider=provider, instrument=instrument, quote_side=side, timeframe=timeframe))
        checksum = hashlib.sha256(filename.encode("utf-8")).hexdigest()
        return {
            "date": f"{self.day:%Y-%m-%d}",
            "provider": provider,
            "instrument": instrument,
            "quote_side": side,
            "timeframe": timeframe,
            "source_filename": filename,
            "source_file_size_bytes": "",
            "source_checksum_algorithm": "sha256",
            "source_checksum": "",
            "manifest_quality_status": "valid" if quality_tier == "strict_valid" else "warning",
            "manifest_quality_reasons": "" if quality_tier == "strict_valid" else "INTERNAL_FLAT_ZERO_VOLUME",
            "quality_tier": quality_tier,
        }

    def active_row(self, close="2000.100", timestamp="2024-01-09 00:00:00"):
        row = make_active_rows(self.day, time(0, 0), time(0, 1))[0]
        row["timestamp_utc"] = timestamp
        row["close"] = close
        row["high"] = max(row["open"], close)
        row["low"] = min(row["open"], close)
        return row

    def write_side(self, directory, side, rows):
        return write_csv(directory / build_raw_csv_filename(self.day, SourceContract(quote_side=side)), rows)

    def write_linked(self, path, rows):
        fieldnames = [
            "date", "provider", "instrument", "quote_side", "timeframe", "source_filename",
            "source_file_size_bytes", "source_checksum_algorithm", "source_checksum", "manifest_quality_status",
            "manifest_quality_reasons", "quality_tier",
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def run_reconciliation(self, bid_rows, ask_rows, bid_link=None, ask_link=None):
        with TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            data_dir = root / "data_raw"
            reports_dir = root / "reports"
            data_dir.mkdir()
            reports_dir.mkdir()
            self.write_side(data_dir, BID, bid_rows)
            self.write_side(data_dir, ASK, ask_rows)
            bid_link_path = reports_dir / "bid_linked.csv"
            ask_link_path = reports_dir / "ask_linked.csv"
            self.write_linked(bid_link_path, [bid_link or self.linked_row(BID)])
            self.write_linked(ask_link_path, [ask_link or self.linked_row(ASK)])
            output_path = reports_dir / "paired.csv"
            summary = recon.create_reconciliation(self.day, self.day, data_dir, bid_link_path, ask_link_path, output_path)
            with output_path.open(newline="", encoding="utf-8") as output_file:
                rows = list(csv.DictReader(output_file))
            return summary, rows

    def test_exact_bid_ask_pairing(self):
        summary, rows = self.run_reconciliation([self.active_row("2000.100")], [self.active_row("2000.150")])
        self.assertEqual(summary.exact_timestamp_matches, 1)
        self.assertEqual(rows[0]["spread"], "0.050")
        self.assertEqual(rows[0]["pair_quality_status"], recon.STRICT_VALID_PAIR)
        self.assertEqual(rows[0]["bid_source_filename"], "XAUUSD_2024-01-09_1min_BID_UTC.csv")
        self.assertEqual(rows[0]["ask_source_filename"], "XAUUSD_2024-01-09_1min_ASK_UTC.csv")

    def test_missing_ask_side_is_explicit(self):
        summary, rows = self.run_reconciliation([self.active_row()], [])
        self.assertEqual(summary.missing_ask_rows, 1)
        self.assertEqual(rows[0]["pair_quality_status"], recon.MISSING_ASK)
        self.assertIn("MISSING_ASK", rows[0]["pair_quality_reasons"])

    def test_missing_bid_side_is_explicit(self):
        summary, rows = self.run_reconciliation([], [self.active_row()])
        self.assertEqual(summary.missing_bid_rows, 1)
        self.assertEqual(rows[0]["pair_quality_status"], recon.MISSING_BID)

    def test_mismatched_timestamps_are_missing_side_rows(self):
        _, rows = self.run_reconciliation([self.active_row(timestamp="2024-01-09 00:00:00")], [self.active_row(timestamp="2024-01-09 00:01:00")])
        self.assertEqual([row["pair_quality_status"] for row in rows], [recon.MISSING_ASK, recon.MISSING_BID])

    def test_duplicate_bid_timestamp_blocks_valid_pairing(self):
        bid = [self.active_row("2000.100"), self.active_row("2000.110")]
        _, rows = self.run_reconciliation(bid, [self.active_row("2000.150")])
        self.assertEqual(rows[0]["pair_quality_status"], recon.TIMESTAMP_MISMATCH)
        self.assertIn("BID_DUPLICATE_TIMESTAMP", rows[0]["pair_quality_reasons"])

    def test_duplicate_ask_timestamp_blocks_valid_pairing(self):
        ask = [self.active_row("2000.150"), self.active_row("2000.160")]
        _, rows = self.run_reconciliation([self.active_row("2000.100")], ask)
        self.assertEqual(rows[0]["pair_quality_status"], recon.TIMESTAMP_MISMATCH)
        self.assertIn("ASK_DUPLICATE_TIMESTAMP", rows[0]["pair_quality_reasons"])

    def test_negative_spread_is_invalid(self):
        summary, rows = self.run_reconciliation([self.active_row("2000.200")], [self.active_row("2000.100")])
        self.assertEqual(summary.negative_spreads, 1)
        self.assertEqual(rows[0]["pair_quality_status"], recon.INVALID_SPREAD)

    def test_zero_spread_is_warning_review(self):
        summary, rows = self.run_reconciliation([self.active_row("2000.100")], [self.active_row("2000.100")])
        self.assertEqual(summary.zero_spreads, 1)
        self.assertEqual(rows[0]["pair_quality_status"], recon.WARNING_REVIEW_PAIR)
        self.assertIn("ZERO_SPREAD", rows[0]["pair_quality_reasons"])

    def test_extreme_spread_is_warning_review(self):
        summary, rows = self.run_reconciliation([self.active_row("2000.100")], [self.active_row("2011.100")])
        self.assertEqual(summary.extreme_spreads, 1)
        self.assertEqual(rows[0]["pair_quality_status"], recon.WARNING_REVIEW_PAIR)
        self.assertIn("EXTREME_SPREAD", rows[0]["pair_quality_reasons"])

    def test_quality_tier_mismatch_prevents_strict_valid_pair(self):
        ask_link = self.linked_row(ASK, quality_tier="warning_review")
        _, rows = self.run_reconciliation([self.active_row("2000.100")], [self.active_row("2000.150")], ask_link=ask_link)
        self.assertEqual(rows[0]["pair_quality_status"], recon.WARNING_REVIEW_PAIR)
        self.assertIn("QUALITY_TIER_MISMATCH", rows[0]["pair_quality_reasons"])
        self.assertIn("ASK_SIDE_WARNING_REVIEW", rows[0]["pair_quality_reasons"])

    def test_provider_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "provider"):
            self.run_reconciliation([self.active_row()], [self.active_row("2000.150")], bid_link=self.linked_row(BID, provider="Other"))

    def test_instrument_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "instrument"):
            self.run_reconciliation([self.active_row()], [self.active_row("2000.150")], bid_link=self.linked_row(BID, instrument="EURUSD"))

    def test_timeframe_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "timeframe"):
            self.run_reconciliation([self.active_row()], [self.active_row("2000.150")], bid_link=self.linked_row(BID, timeframe="5min"))

    def test_incompatible_quote_side_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            path = Path(temp_root) / "linked.csv"
            self.write_linked(path, [self.linked_row(ASK)])
            with self.assertRaisesRegex(ValueError, "quote_side"):
                recon.load_linked_rows(path, BID)

    def test_placeholder_pair_is_warning_review(self):
        placeholder = make_placeholder_rows(self.day, time(0, 0), time(0, 1), 2000.0)[0]
        _, rows = self.run_reconciliation([placeholder], [placeholder])
        self.assertEqual(rows[0]["pair_quality_status"], recon.WARNING_REVIEW_PAIR)
        self.assertIn("MARKET_CLOSED_PLACEHOLDER", rows[0]["pair_quality_reasons"])

    def test_legacy_bid_evidence_remains_untouched(self):
        with TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            data_dir = root / "data_raw"
            reports_dir = root / "reports"
            data_dir.mkdir()
            reports_dir.mkdir()
            bid_path = self.write_side(data_dir, BID, [self.active_row("2000.100")])
            before = bid_path.read_bytes()
            ask_path = self.write_side(data_dir, ASK, [self.active_row("2000.150")])
            ask_before = ask_path.read_bytes()
            bid_link_path = reports_dir / "bid_linked.csv"
            ask_link_path = reports_dir / "ask_linked.csv"
            self.write_linked(bid_link_path, [self.linked_row(BID)])
            self.write_linked(ask_link_path, [self.linked_row(ASK)])
            recon.create_reconciliation(self.day, self.day, data_dir, bid_link_path, ask_link_path, reports_dir / "paired.csv")
            self.assertEqual(bid_path.read_bytes(), before)
            self.assertEqual(ask_path.read_bytes(), ask_before)

    def test_raw_checksum_drift_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            data_dir = root / "data_raw"
            reports_dir = root / "reports"
            data_dir.mkdir()
            reports_dir.mkdir()
            bid_path = self.write_side(data_dir, BID, [self.active_row("2000.100")])
            ask_path = self.write_side(data_dir, ASK, [self.active_row("2000.150")])
            bid_link = self.linked_row(BID)
            ask_link = self.linked_row(ASK)
            for link, path in ((bid_link, bid_path), (ask_link, ask_path)):
                raw = path.read_bytes()
                link["source_file_size_bytes"] = str(len(raw))
                link["source_checksum"] = hashlib.sha256(raw).hexdigest()
            bid_path.write_text(bid_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            bid_link_path = reports_dir / "bid_linked.csv"
            ask_link_path = reports_dir / "ask_linked.csv"
            self.write_linked(bid_link_path, [bid_link])
            self.write_linked(ask_link_path, [ask_link])
            with self.assertRaisesRegex(ValueError, "checksum changed|size changed"):
                recon.create_reconciliation(self.day, self.day, data_dir, bid_link_path, ask_link_path, reports_dir / "paired.csv")

    def test_invalid_timestamp_is_timestamp_mismatch(self):
        _, rows = self.run_reconciliation([self.active_row(timestamp="not-a-timestamp")], [self.active_row("2000.150")])
        invalid_rows = [row for row in rows if "BID_INVALID_TIMESTAMP" in row["pair_quality_reasons"]]
        self.assertEqual(len(invalid_rows), 1)
        self.assertEqual(invalid_rows[0]["pair_quality_status"], recon.TIMESTAMP_MISMATCH)


if __name__ == "__main__":
    unittest.main()
