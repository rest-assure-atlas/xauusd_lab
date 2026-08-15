import unittest
from datetime import datetime, timedelta, timezone

import execution_cost_model as model


class ExecutionCostModelTest(unittest.TestCase):
    def row(
        self,
        timestamp="2024-01-25 23:22:00",
        spread="0.400",
        status=model.STRICT_VALID_PAIR,
        reasons="",
    ):
        return {
            "date": timestamp[:10],
            "timestamp_utc": timestamp,
            "spread": spread,
            "bid_close": "2000.000",
            "ask_close": f"{2000 + float(spread):.3f}",
            "pair_quality_status": status,
            "pair_quality_reasons": reasons,
        }

    def windows(self):
        return [
            model.CorroborationWindow(
                window_id="2024-01-25_ge2_01",
                kind="warning_ge2_target",
                classification=model.CONFIRMED_CLOSELY,
                date="2024-01-25",
                start_utc=datetime(2024, 1, 25, 22, 52),
                end_utc=datetime(2024, 1, 25, 23, 59),
                cluster_start_utc=datetime(2024, 1, 25, 23, 22),
                cluster_end_utc=datetime(2024, 1, 25, 23, 29),
            ),
            model.CorroborationWindow(
                window_id="2024-12-11_ge2_04",
                kind="warning_ge2_target",
                classification=model.DISAGREES,
                date="2024-12-11",
                start_utc=datetime(2024, 12, 11, 17, 30),
                end_utc=datetime(2024, 12, 11, 18, 31),
                cluster_start_utc=datetime(2024, 12, 11, 18, 0),
                cluster_end_utc=datetime(2024, 12, 11, 18, 0),
            ),
            model.CorroborationWindow(
                window_id="2024-02-18_ge2_02",
                kind="warning_ge2_target",
                classification=model.INCONCLUSIVE,
                date="2024-02-18",
                start_utc=datetime(2024, 2, 18, 22, 55),
                end_utc=datetime(2024, 2, 19, 0, 0),
                cluster_start_utc=datetime(2024, 2, 18, 23, 25),
                cluster_end_utc=datetime(2024, 2, 18, 23, 30),
            ),
        ]

    def architecture_b_rows(self, start, count, spread="1.0", step_minutes=1):
        return [
            self.row(
                timestamp=(start + timedelta(minutes=index * step_minutes)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                spread=str(spread),
            )
            for index in range(count)
        ]

    def test_strict_baseline_rejects_warning_leakage(self):
        warning = self.row(status=model.WARNING_REVIEW_PAIR)
        with self.assertRaisesRegex(ValueError, "non-strict"):
            model.assert_strict_baseline_population([warning])

    def test_strict_baseline_rejects_placeholder_leakage(self):
        placeholder = self.row(reasons=model.PLACEHOLDER_REASON)
        with self.assertRaisesRegex(ValueError, "placeholder"):
            model.assert_strict_baseline_population([placeholder])

    def test_select_strict_baseline_filters_warning_and_placeholders(self):
        rows = [
            self.row(timestamp="2024-01-25 23:20:00", status=model.STRICT_VALID_PAIR),
            self.row(timestamp="2024-01-25 23:21:00", status=model.WARNING_REVIEW_PAIR),
            self.row(timestamp="2024-01-25 23:22:00", reasons=model.PLACEHOLDER_REASON),
        ]
        selected = model.select_strict_baseline_rows(rows)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["timestamp_utc"], "2024-01-25 23:20:00")

    def test_percentile_is_deterministic_linear_interpolation(self):
        self.assertEqual(model.percentile([1.0, 2.0, 3.0, 4.0], 0.50), 2.5)

    def test_session_bucket_handles_overlap(self):
        bucket = model.session_bucket(datetime(2024, 1, 26, 13, 30))
        self.assertEqual(bucket, "London+New York")

    def test_close_warning_target_cluster_is_non_pooled_stress_only(self):
        row = self.row(status=model.WARNING_REVIEW_PAIR)
        annotation = model.annotate_corroboration(row, self.windows())
        self.assertEqual(annotation["corroboration_scope"], model.TARGET_CLUSTER)
        self.assertEqual(annotation["corroboration_class"], model.CONFIRMED_CLOSELY)
        self.assertEqual(annotation["allowed_use"], "stress_sensitivity_allowed_non_pooled")
        self.assertEqual(annotation["policy_version"], model.POLICY_VERSION)

    def test_window_context_does_not_become_row_level_confirmation(self):
        row = self.row(timestamp="2024-01-25 22:53:00", status=model.WARNING_REVIEW_PAIR)
        annotation = model.annotate_corroboration(row, self.windows())
        self.assertEqual(annotation["corroboration_scope"], model.BOUNDED_WINDOW_CONTEXT)
        self.assertEqual(annotation["allowed_use"], "descriptive_context_only_not_row_corrob")

    def test_untested_warning_rows_remain_uncorroborated(self):
        row = self.row(timestamp="2024-03-01 12:00:00", status=model.WARNING_REVIEW_PAIR)
        annotation = model.annotate_corroboration(row, self.windows())
        self.assertEqual(annotation["corroboration_scope"], model.NOT_EXTERNALLY_TESTED_SCOPE)
        self.assertEqual(annotation["corroboration_class"], model.NOT_EXTERNALLY_TESTED)

    def test_disagreed_and_inconclusive_cases_are_preserved(self):
        disagree = self.row(
            timestamp="2024-12-11 18:00:00",
            status=model.WARNING_REVIEW_PAIR,
        )
        inconclusive = self.row(
            timestamp="2024-02-18 23:25:00",
            status=model.WARNING_REVIEW_PAIR,
        )
        disagree_annotation = model.annotate_corroboration(disagree, self.windows())
        inconclusive_annotation = model.annotate_corroboration(inconclusive, self.windows())
        self.assertEqual(disagree_annotation["allowed_use"], "adverse_only_exclude_favorable_calibration")
        self.assertEqual(
            inconclusive_annotation["allowed_use"],
            "unresolved_adverse_only_exclude_favorable_calibration",
        )

    def test_stress_layer_keeps_warning_rows_out_of_baseline(self):
        rows = [
            self.row(timestamp="2024-01-25 23:22:00", spread="2.200", status=model.WARNING_REVIEW_PAIR),
            self.row(timestamp="2024-12-11 18:00:00", spread="2.040", status=model.WARNING_REVIEW_PAIR),
            self.row(timestamp="2024-02-18 23:25:00", spread="4.440", status=model.WARNING_REVIEW_PAIR),
        ]
        stress = model.build_stress_layer(rows, self.windows())
        self.assertEqual(stress["primary_baseline_pooling"], "PROHIBITED")
        self.assertEqual(stress["scenario_row_counts"]["closely_corrob_target_cluster_warning"], 1)
        self.assertEqual(stress["scenario_row_counts"]["disagreed_target_cluster_warning"], 1)
        self.assertEqual(stress["scenario_row_counts"]["inconclusive_target_cluster_warning"], 1)
        self.assertEqual(
            stress["special_case_counts_by_scope"]["2024-12-11_ge2_04"][model.TARGET_CLUSTER],
            1,
        )
        self.assertEqual(
            stress["special_case_counts_by_scope"]["2024-02-18_ge2_02"][model.TARGET_CLUSTER],
            1,
        )

    def test_build_baseline_model_reports_no_warning_baseline_rows(self):
        rows = []
        for index in range(12):
            month = 1 if index < 8 else 10
            rows.append(
                self.row(
                    timestamp=f"2024-{month:02d}-25 10:{index % 60:02d}:00",
                    spread=f"0.{index + 1:03d}",
                    status=model.STRICT_VALID_PAIR,
                )
            )
        rows.append(self.row(status=model.WARNING_REVIEW_PAIR))
        baseline = model.build_baseline_model(rows)
        self.assertEqual(baseline["warning_review_rows_in_primary_baseline"], 0)
        self.assertEqual(baseline["policy_version"], model.POLICY_VERSION)
        self.assertEqual(
            baseline["model_form"],
            "strict_valid_global_empirical_distribution_with_session_regime_diagnostics",
        )
        self.assertEqual(
            baseline["prospective_application_guard"]["full_sample_summary_strategy_cost_use"],
            "PROHIBITED_FOR_2024_STRATEGY_EVALUATION",
        )

    def test_weak_temporal_validation_downgrades_gate(self):
        baseline = {
            "candidate_validation": [
                {
                    "selected": True,
                    "validation_p95_coverage": 0.7314037340709276,
                }
            ]
        }
        gate, reasons = model.determine_gate(baseline)
        self.assertEqual(gate, "EXECUTION_COST_MODEL_NEEDS_SMALL_FOLLOWUP")
        self.assertTrue(any("p95 holdout coverage" in reason for reason in reasons))

    def test_prospective_tail_cost_uses_only_prior_month_boundary_rows(self):
        rows = []
        for day in range(1, 31):
            rows.append(
                self.row(
                    timestamp=f"2024-03-{day:02d} 12:00:00",
                    spread=f"0.{day:03d}",
                    status=model.STRICT_VALID_PAIR,
                )
            )
        rows.append(
            self.row(
                timestamp="2024-04-01 00:00:00",
                spread="9.999",
                status=model.STRICT_VALID_PAIR,
            )
        )
        estimate = model.prospective_tail_cost_for_timestamp(
            rows,
            datetime(2024, 4, 15, 12, 0),
            lookback_days=30,
            percentile_fraction=1.0,
            minimum_observations=10,
        )
        self.assertEqual(estimate["estimate"], 0.03)
        self.assertEqual(estimate["calibration_end_exclusive"], "2024-04-01 00:00:00")
        self.assertEqual(estimate["warning_review_rows_in_baseline"], 0)

    def test_prospective_tail_cost_rejects_insufficient_history(self):
        rows = [
            self.row(
                timestamp="2024-03-31 12:00:00",
                spread="0.400",
                status=model.STRICT_VALID_PAIR,
            )
        ]
        with self.assertRaisesRegex(ValueError, "Insufficient prior strict-valid"):
            model.prospective_tail_cost_for_timestamp(
                rows,
                datetime(2024, 4, 15, 12, 0),
                minimum_observations=2,
            )

    def test_architecture_b_requires_timezone_explicit_utc(self):
        with self.assertRaisesRegex(ValueError, "timezone-explicit UTC"):
            model.architecture_b_tail_cost_for_timestamp([], datetime(2024, 4, 15))

    def test_architecture_b_uses_frozen_horizons_and_maximum_eligible_threshold(self):
        boundary = datetime(2024, 4, 1, tzinfo=timezone.utc)
        rows = []
        rows.extend(self.architecture_b_rows(boundary.replace(tzinfo=None) - timedelta(days=300), 1000, "9.0"))
        rows.extend(self.architecture_b_rows(boundary.replace(tzinfo=None) - timedelta(days=60), 1000, "5.0"))
        rows.extend(self.architecture_b_rows(boundary.replace(tzinfo=None) - timedelta(days=20), 1000, "1.0"))

        result = model.architecture_b_tail_cost_for_timestamp(rows, boundary + timedelta(days=12))

        self.assertEqual(result["estimate"], 9.0)
        self.assertEqual(result["status"], "available")
        self.assertEqual(
            [item["horizon_calendar_days"] for item in result["horizon_diagnostics"]],
            [30, 90, 365],
        )
        self.assertTrue(all(item["status"] == "eligible" for item in result["horizon_diagnostics"]))

    def test_architecture_b_interval_is_left_closed_right_open_and_prior_only(self):
        boundary = datetime(2024, 4, 1, tzinfo=timezone.utc)
        start = boundary.replace(tzinfo=None) - timedelta(days=30)
        rows = [self.row(timestamp=start.strftime("%Y-%m-%d %H:%M:%S"), spread="2.0") for _ in range(1000)]
        rows.append(self.row(timestamp=(start - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"), spread="99.0"))
        rows.append(self.row(timestamp=boundary.strftime("%Y-%m-%d %H:%M:%S"), spread="99.0"))
        rows.append(self.row(timestamp=(boundary + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), spread="99.0"))

        result = model.architecture_b_tail_cost_for_timestamp(rows, boundary + timedelta(days=20))

        self.assertEqual(result["estimate"], 2.0)
        self.assertEqual(result["horizon_diagnostics"][0]["prior_strict_valid_count"], 1000)

    def test_architecture_b_eligibility_boundary_and_unavailable_horizons(self):
        boundary = datetime(2024, 4, 1, tzinfo=timezone.utc)
        rows = self.architecture_b_rows(boundary.replace(tzinfo=None) - timedelta(days=20), 999)
        unavailable = model.architecture_b_tail_cost_for_timestamp(rows, boundary + timedelta(days=1))
        self.assertEqual(unavailable["status"], "unavailable")
        self.assertIsNone(unavailable["estimate"])
        self.assertFalse(unavailable["carry_forward_used"])
        self.assertFalse(unavailable["future_backfill_used"])

        rows.append(self.row(timestamp="2024-03-31 23:59:00", spread="1.0"))
        available = model.architecture_b_tail_cost_for_timestamp(rows, boundary + timedelta(days=1))
        self.assertEqual(available["status"], "available")

    def test_architecture_b_filters_non_primary_and_synthetic_populations(self):
        boundary = datetime(2024, 4, 1, tzinfo=timezone.utc)
        rows = [self.row(timestamp="2024-03-15 12:00:00", spread="1.0") for _ in range(1000)]
        rows.extend(
            [
                self.row(timestamp="2024-03-20 12:00:00", spread="99.0", status=model.WARNING_REVIEW_PAIR),
                self.row(timestamp="2024-03-20 12:01:00", spread="99.0", status="excluded"),
                self.row(timestamp="2024-03-20 12:02:00", spread="99.0", status="calendar_only"),
                self.row(timestamp="2024-03-20 12:03:00", spread="99.0", reasons=model.PLACEHOLDER_REASON),
                self.row(timestamp="2024-03-20 12:04:00", spread="99.0", reasons="SYNTHETIC"),
            ]
        )
        descriptive = self.row(timestamp="2024-03-20 12:05:00", spread="99.0")
        descriptive["population_role"] = "descriptive_only"
        rows.append(descriptive)

        result = model.architecture_b_tail_cost_for_timestamp(rows, boundary + timedelta(days=3))

        self.assertEqual(result["estimate"], 1.0)
        self.assertEqual(result["horizon_diagnostics"][0]["prior_strict_valid_count"], 1000)
        self.assertEqual(result["warning_review_rows_in_baseline"], 0)

    def test_architecture_b_forbidden_spreads_do_not_satisfy_horizon_minimum(self):
        boundary = datetime(2024, 4, 1, tzinfo=timezone.utc)
        valid_rows = [self.row(timestamp="2024-03-15 12:00:00", spread="1.0") for _ in range(999)]

        for forbidden_spread in ("not-a-number", "nan", "inf", "-inf", "-0.001"):
            with self.subTest(spread=forbidden_spread):
                forbidden = self.row(timestamp="2024-03-16 12:00:00", spread="1.0")
                forbidden["spread"] = forbidden_spread

                result = model.architecture_b_tail_cost_for_timestamp(
                    valid_rows + [forbidden],
                    boundary + timedelta(days=3),
                )

                self.assertEqual(result["status"], "unavailable")
                self.assertIsNone(result["estimate"])
                self.assertTrue(
                    all(
                        item["prior_strict_valid_count"] == 999
                        and item["status"] == "unavailable"
                        and item["threshold"] is None
                        for item in result["horizon_diagnostics"]
                    )
                )

    def test_architecture_b_forbidden_spreads_never_affect_thresholds(self):
        boundary = datetime(2024, 4, 1, tzinfo=timezone.utc)
        valid_rows = [self.row(timestamp="2024-03-15 12:00:00", spread="1.0") for _ in range(1000)]
        forbidden_rows = []
        for spread in ("not-a-number", "nan", "inf", "-inf", "-999999"):
            row = self.row(timestamp="2024-03-16 12:00:00", spread="1.0")
            row["spread"] = spread
            forbidden_rows.append(row)

        result = model.architecture_b_tail_cost_for_timestamp(
            valid_rows + forbidden_rows,
            boundary + timedelta(days=3),
        )

        self.assertEqual(result["estimate"], 1.0)
        self.assertTrue(
            all(item["prior_strict_valid_count"] == 1000 for item in result["horizon_diagnostics"])
        )

    def test_architecture_b_preserves_numeric_zero_spread(self):
        boundary = datetime(2024, 4, 1, tzinfo=timezone.utc)
        rows = [self.row(timestamp="2024-03-15 12:00:00", spread="1.0") for _ in range(999)]
        rows.append(self.row(timestamp="2024-03-16 12:00:00", spread="0.0"))

        result = model.architecture_b_tail_cost_for_timestamp(rows, boundary + timedelta(days=3))

        self.assertEqual(result["status"], "available")
        self.assertTrue(
            all(item["prior_strict_valid_count"] == 1000 for item in result["horizon_diagnostics"])
        )

    def test_architecture_b_preserves_v1_quantile_precision_and_inclusive_coverage(self):
        boundary = datetime(2024, 4, 1, tzinfo=timezone.utc)
        values = [float(index) / 1000 for index in range(1000)]
        rows = [self.row(timestamp="2024-03-15 12:00:00", spread=repr(value)) for value in values]

        first = model.architecture_b_tail_cost_for_timestamp(rows, boundary + timedelta(days=2))
        second = model.architecture_b_tail_cost_for_timestamp(list(reversed(rows)), boundary + timedelta(days=20))
        expected = model.percentile(sorted(values), 0.995)

        self.assertEqual(first, second)
        self.assertEqual(first["estimate"], expected)
        self.assertTrue(model.architecture_b_observation_is_covered(expected, expected))
        self.assertFalse(model.architecture_b_observation_is_covered(expected + 1e-12, expected))

    def test_architecture_b_monthly_recalibration_has_no_carry_forward_or_future_backfill(self):
        march_rows = [self.row(timestamp="2024-03-15 12:00:00", spread="3.0") for _ in range(1000)]
        april_boundary = datetime(2024, 4, 1, tzinfo=timezone.utc)
        april = model.architecture_b_tail_cost_for_timestamp(march_rows, april_boundary + timedelta(days=5))
        same_month = model.architecture_b_tail_cost_for_timestamp(march_rows, april_boundary + timedelta(days=25))
        self.assertEqual(april, same_month)

        future_rows = [self.row(timestamp="2024-05-01 00:00:00", spread="99.0") for _ in range(1000)]
        may = model.architecture_b_tail_cost_for_timestamp(future_rows, datetime(2024, 5, 20, tzinfo=timezone.utc))
        self.assertEqual(may["status"], "unavailable")
        self.assertIsNone(may["estimate"])

    def test_tail_hardening_gate_passes_when_coverage_and_inputs_are_clean(self):
        tail_hardening = {
            "selected_rule": {
                "minimum_realized_coverage": 0.95,
                "thin_data_folds": [],
            },
            "warning_review_rows_in_baseline": 0,
            "future_data_leakage_detected": False,
        }
        gate, reasons = model.determine_tail_hardening_gate(tail_hardening)
        self.assertEqual(gate, "READY_FOR_STRATEGY_INTEGRATION_WITH_CONDITIONS")
        self.assertTrue(any("mechanical" in reason for reason in reasons))

    def test_tail_hardening_gate_rejects_warning_leakage(self):
        tail_hardening = {
            "selected_rule": {
                "minimum_realized_coverage": 0.95,
                "thin_data_folds": [],
            },
            "warning_review_rows_in_baseline": 1,
            "future_data_leakage_detected": False,
        }
        gate, reasons = model.determine_tail_hardening_gate(tail_hardening)
        self.assertEqual(gate, "EXECUTION_COST_MODEL_NEEDS_SMALL_FOLLOWUP")
        self.assertTrue(any("Warning-review" in reason for reason in reasons))


if __name__ == "__main__":
    unittest.main()
