import csv
import tempfile
import unittest
from pathlib import Path

import partition_lock


class PartitionLockTest(unittest.TestCase):
    def lock(self):
        return partition_lock.build_partition_lock(
            {
                "final_gate": "READY_FOR_PARTITION_LOCK_AND_ACCESS_LOG_PREPARATION_ONLY",
            }
        )

    def test_partition_roles_load_correctly(self):
        lock = self.lock()
        self.assertEqual(lock["partition_manifest"]["2024"]["role"], partition_lock.CONSUMED_DEVELOPMENT)
        self.assertEqual(lock["partition_manifest"]["2010"]["role"], partition_lock.EXPANSION_SHAKEDOWN)
        self.assertEqual(lock["partition_manifest"]["2011"]["role"], partition_lock.EXECUTION_COST_CLEAN_VALIDATION)
        self.assertEqual(lock["partition_manifest"]["2014"]["role"], partition_lock.EXECUTION_COST_CLEAN_VALIDATION)
        self.assertEqual(lock["partition_manifest"]["2015"]["role"], partition_lock.FUTURE_STRATEGY_DEVELOPMENT)
        self.assertEqual(lock["partition_manifest"]["2019"]["role"], partition_lock.FUTURE_STRATEGY_DEVELOPMENT)
        self.assertEqual(lock["partition_manifest"]["2020"]["role"], partition_lock.FUTURE_WALK_FORWARD_VALIDATION)
        self.assertEqual(lock["partition_manifest"]["2022"]["role"], partition_lock.FUTURE_WALK_FORWARD_VALIDATION)
        self.assertEqual(lock["partition_manifest"]["2023"]["role"], partition_lock.FINAL_UNTOUCHED_HOLDOUT)
        self.assertEqual(lock["partition_manifest"]["2025"]["role"], partition_lock.FINAL_UNTOUCHED_HOLDOUT)
        self.assertEqual(
            lock["fallback_rules"]["final_holdout_fallback_years_order"],
            ["2023", "2022", "2021"],
        )

    def test_final_holdout_rejects_prohibited_pre_release_operations(self):
        decision = partition_lock.classify_access(self.lock(), 2023, "spread_summary")
        self.assertFalse(decision["approved"])
        self.assertEqual(decision["access_class"], partition_lock.PROHIBITED_PRE_RELEASE)

    def test_final_holdout_allows_technical_metadata_only(self):
        decision = partition_lock.classify_access(self.lock(), 2025, "checksum_presence_status")
        self.assertTrue(decision["approved"])
        self.assertEqual(decision["access_class"], partition_lock.TECHNICAL_METADATA_ONLY)

    def test_access_attempts_can_be_logged(self):
        lock = self.lock()
        decision = partition_lock.classify_access(lock, 2023, "spread_summary")
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "holdout_access_log.csv"
            event = partition_lock.access_event_from_decision(
                access_id="test_access_001",
                timestamp_utc="2026-08-11T00:00:00Z",
                requester="unittest",
                mission_id="partition_lock_test",
                year_or_range="2023",
                decision=decision,
                approved_gate_or_work_order="unit_test_gate",
                distributional_content_inspected="yes",
                artifacts_touched="reports/example.csv",
            )
            partition_lock.append_access_log(log_path, event)
            with log_path.open("r", newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["requested_operation"], "spread_summary")
        self.assertEqual(rows[0]["decision"], "rejected")
        self.assertEqual(rows[0]["distributional_content_inspected"], "yes")
        self.assertEqual(rows[0]["approved_gate_or_work_order"], "unit_test_gate")

    def test_release_requires_explicit_approval_state(self):
        decision = partition_lock.classify_access(self.lock(), 2023, "final_holdout_release")
        self.assertFalse(decision["approved"])
        self.assertEqual(decision["access_class"], partition_lock.REQUIRES_RELEASE_APPROVAL)
        with self.assertRaisesRegex(ValueError, "approval reference"):
            partition_lock.release_final_holdout(
                self.lock(),
                2023,
                approval_reference="",
                release_purpose="final evaluation",
                policy_model_or_strategy_version="strategy_protocol_v1",
            )

    def test_released_holdout_status_change_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "holdout_access_log.csv"
            released = partition_lock.release_final_holdout(
                self.lock(),
                2023,
                approval_reference="human_approval_2026_08_11",
                release_purpose="final evaluation",
                policy_model_or_strategy_version="strategy_protocol_v1",
                access_log_path=log_path,
                requester="unittest",
                mission_id="release_test",
                access_id="release_001",
                artifact_path="reports/multi_year_partition_lock.json",
                timestamp_utc="2026-08-11T00:00:00Z",
            )
            with log_path.open("r", newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(
            released["partition_manifest"]["2023"]["holdout_status"],
            "released_for_approved_purpose_and_consumed_for_that_purpose",
        )
        self.assertEqual(len(released["release_policy"]["release_events"]), 1)
        self.assertEqual(
            released["release_policy"]["release_events"][0]["holdout_status_before"],
            "untouched_until_final_release",
        )
        self.assertEqual(rows[0]["requested_operation"], "final_holdout_release")
        self.assertEqual(rows[0]["holdout_status_consumed_or_changed"], "yes")
        self.assertEqual(rows[0]["distributional_content_inspected"], "no")

    def test_frozen_execution_cost_candidate_is_unchanged(self):
        candidate = self.lock()["frozen_execution_cost_candidate"]
        self.assertEqual(candidate["candidate_version"], "execution_cost_tail_rule_v1_candidate")
        self.assertEqual(candidate["lookback_days"], 30)
        self.assertEqual(candidate["recalibration_cadence"], "monthly_boundary")
        self.assertEqual(candidate["population"], "active strict_valid_pair only")
        self.assertEqual(candidate["percentile"], 0.995)
        self.assertEqual(candidate["minimum_prior_strict_valid_observations"], 1000)
        self.assertEqual(candidate["warning_review_baseline_use"], "PROHIBITED")
        expected = candidate["reproducibility_id"]
        without_hash = dict(candidate)
        without_hash.pop("reproducibility_id")
        self.assertEqual(expected, partition_lock.canonical_hash(without_hash))

    def test_2024_is_never_pristine_holdout(self):
        decision = partition_lock.classify_access(self.lock(), 2024, "treat_as_pristine_holdout")
        self.assertFalse(decision["approved"])
        self.assertEqual(decision["access_class"], partition_lock.PROHIBITED_PRE_RELEASE)

    def test_strategy_discovery_remains_blocked(self):
        lock = self.lock()
        self.assertEqual(
            lock["strategy_protocol_placeholder"]["serious_strategy_discovery_status"],
            "BLOCKED",
        )
        decision = partition_lock.classify_access(lock, 2015, "strategy_outputs")
        self.assertFalse(decision["approved"])
        self.assertEqual(decision["access_class"], partition_lock.REQUIRES_RELEASE_APPROVAL)

    def test_operation_aliases_are_normalized(self):
        allowed = partition_lock.classify_access(self.lock(), 2023, "schema_report")
        rejected = partition_lock.classify_access(self.lock(), 2023, "quality_summary")
        self.assertTrue(allowed["approved"])
        self.assertEqual(allowed["requested_operation"], "coarse_schema_validity_status")
        self.assertFalse(rejected["approved"])
        self.assertEqual(rejected["requested_operation"], "quality_distributions")


if __name__ == "__main__":
    unittest.main()
