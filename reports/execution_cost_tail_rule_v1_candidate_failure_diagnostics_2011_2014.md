# Failure Diagnostics: execution_cost_tail_rule_v1_candidate 2011-2014

## Scope

Diagnostic only. This artifact explains the failed frozen clean validation without changing the candidate, thresholds, lookback, recalibration schedule, eligibility rules, partitions, or source artifacts. No 2015+ data, 2023/2025 final holdouts, strategy research, replacement candidate, or altered-parameter performance calculation was used.

## Frozen Contract Under Diagnosis

- insufficient_history_behavior: `return_unavailable_or_error_no_future_backfill`
- lookback_days: `30`
- minimum_prior_strict_valid_observations: `1000`
- percentile: `0.995`
- policy_version: `post_corroboration_execution_cost_evidence_policy:2026-08-10`
- population: `active strict_valid_pair only`
- recalibration_cadence: `monthly_boundary`

## Dominant Failure Mechanisms

1. Minimum prior strict-valid observation binding: months become unavailable when the trailing 30 calendar-day window at a monthly boundary contains fewer than 1000 prior active strict-valid rows. This accounts for all unavailable strict-valid rows.
2. Calendar-window sparsity: the binding minimum is caused by sparse strict-valid distributions inside specific 30-day calibration windows, not by missing BID/ASK source files or reconciliation failure.
3. Available threshold undercoverage: August 2011 had enough prior rows but the frozen prior-window p99.5 threshold covered only 0.726984 of eligible strict-valid rows.

## Year Findings

| Year | Unavailable rows | Undercovered-month excess rows | Source/reconciliation defect found |
|---:|---:|---:|---|
| 2011 | 1320 | 1376 | no |
| 2012 | 0 | 0 | no |
| 2013 | 3360 | 0 | no |
| 2014 | 7310 | 0 | no |

## Failed/Unavailable Month Findings

| Month | Class | Calibration rows | Validation strict rows | Unavailable rows | Eligible coverage | Notes |
|---|---|---:|---:|---:|---:|---|
| 2011-01 | minimum_prior_strict_valid_observations_binding | 0 | 1320 | 1320 | n/a | partition_sequence_start_no_prior_strict_rows_in_lookback |
| 2011-08 | available_threshold_undercoverage | 3780 | 5040 | 0 | 0.726984 | validation_spread_distribution_exceeded_prior_30d_p995_threshold |
| 2013-02 | minimum_prior_strict_valid_observations_binding | 180 | 1440 | 1440 | n/a | calendar_window_strict_valid_sparsity_below_1000 |
| 2013-10 | minimum_prior_strict_valid_observations_binding | 600 | 360 | 360 | n/a | calendar_window_strict_valid_sparsity_below_1000 |
| 2013-11 | minimum_prior_strict_valid_observations_binding | 360 | 1560 | 1560 | n/a | calendar_window_strict_valid_sparsity_below_1000 |
| 2014-01 | minimum_prior_strict_valid_observations_binding | 180 | 240 | 240 | n/a | calendar_window_strict_valid_sparsity_below_1000 |
| 2014-02 | minimum_prior_strict_valid_observations_binding | 180 | 240 | 240 | n/a | calendar_window_strict_valid_sparsity_below_1000 |
| 2014-03 | minimum_prior_strict_valid_observations_binding | 240 | 4070 | 4070 | n/a | calendar_window_strict_valid_sparsity_below_1000 |
| 2014-06 | minimum_prior_strict_valid_observations_binding | 360 | 2760 | 2760 | n/a | calendar_window_strict_valid_sparsity_below_1000 |

## Cause Counts And Proportions

- Unavailable rows from `minimum_prior_strict_valid_observations_binding`: 11990 (1.000000 of unavailable rows)
- Eligible uncovered rows from `pass_or_no_failure`: 1728
- Eligible uncovered rows from `available_threshold_undercoverage`: 1376

## Mechanical Availability Vs Data Quality

- 2011-2014 Phase-1 gates were pass and reconciliations had no missing-side rows, duplicate output timestamp rows, duplicate side timestamps, or negative spreads in the validation evidence.
- Strict baseline leakage counters are empty; warning-review, calendar-only, placeholder, and excluded rows remain separate descriptive populations.
- The observed unavailability is therefore mechanical under the frozen contract: strict-valid rows exist in the validation months, but the prior 30-day calibration window sometimes contains fewer than 1000 prior strict-valid rows.

## Contiguous Block Output

Detailed unavailable-row, sparse-calibration, and undercovered-threshold blocks are in `reports/execution_cost_tail_rule_v1_candidate_failure_diagnostics_2011_2014_blocks.csv`.

## Diagnostic Gate

DIAGNOSTIC_COMPLETE_FOR_DIRECTOR_REVIEW_FAILED_CLEAN_VALIDATION_2011_2014
