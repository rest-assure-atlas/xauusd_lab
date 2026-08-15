import unittest

import multiyear_acquisition_phase1 as phase1


class MultiYearAcquisitionPhase1Test(unittest.TestCase):
    def test_target_roles_are_limited_to_approved_phase1_years(self):
        self.assertEqual(phase1.ROLE_BY_YEAR[2010], "EXPANSION_SHAKEDOWN")
        self.assertEqual(phase1.ROLE_BY_YEAR[2011], "EXECUTION_COST_CLEAN_VALIDATION")
        self.assertEqual(phase1.ROLE_BY_YEAR[2014], "EXECUTION_COST_CLEAN_VALIDATION")
        self.assertNotIn(2023, phase1.ROLE_BY_YEAR)
        self.assertNotIn(2025, phase1.ROLE_BY_YEAR)

    def test_final_holdout_year_ranges_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Final holdout"):
            phase1.year_range(2023)
        with self.assertRaisesRegex(ValueError, "Final holdout"):
            phase1.year_range(2025)

    def test_out_of_scope_year_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside phase 1"):
            phase1.year_range(2015)

    def test_year_integrity_requires_no_missing_sides_or_negative_spreads(self):
        validation = {
            "calendar_dates_expected": 365,
            "calendar_dates_in_reconciliation": 365,
            "raw_bid_files": 365,
            "raw_ask_files": 365,
            "bid_manifest_processed": 365,
            "ask_manifest_processed": 365,
            "bid_missing_files": 0,
            "ask_missing_files": 0,
            "reconciliation": {
                "missing_bid_rows": 0,
                "missing_ask_rows": 0,
                "duplicate_bid_timestamps": 0,
                "duplicate_ask_timestamps": 0,
                "negative_spreads": 0,
            },
        }
        self.assertTrue(phase1.year_integrity_passes(validation))
        validation["reconciliation"]["negative_spreads"] = 1
        self.assertFalse(phase1.year_integrity_passes(validation))


if __name__ == "__main__":
    unittest.main()
