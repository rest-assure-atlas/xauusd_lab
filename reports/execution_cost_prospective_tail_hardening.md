# Execution-Cost Prospective Tail Hardening

Date: 2026-08-11
Gate decision: EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW

## Purpose

This narrow follow-up hardens the strict-only execution-cost tail rule after the earlier global train-period p95 rule failed prospective Q4 validation. It does not run strategy tests, rank strategies, optimize parameters, acquire new data, change the evidence policy, modify raw evidence, or allow warning-review rows into the primary baseline.

## Original Failure Reproduced

- Control rule: `A_control_static_train_p95`
- Calibration period: 2024-01-01 <= timestamp < 2024-10-01
- Validation period: 2024-10-01 <= timestamp <= 2024-12-31
- Target percentile: p95
- Realized Q4 validation coverage: 0.731404
- Required coverage threshold: 0.90

## Candidates Tested

| Candidate | Type | Intended percentile | Validation basis | Realized coverage | Median/threshold cost | Selected |
|---|---|---:|---|---:|---:|---|
| A_control_static_train_p95 | static_train_only_empirical_percentile | 0.950000 | 2024-10-01 <= timestamp <= 2024-12-31 | 0.731404 | 0.457000 | no |
| B_static_train_p99 | static_train_only_empirical_percentile | 0.990000 | 2024-10-01 <= timestamp <= 2024-12-31 | 0.906698 | 0.550000 | no |
| B_static_train_p99_5 | static_train_only_empirical_percentile | 0.995000 | 2024-10-01 <= timestamp <= 2024-12-31 | 0.962561 | 0.607000 | no |
| C_rolling_30d_monthly_p99 | monthly_recalibrated_trailing_empirical_percentile | 0.990000 | 9 monthly prospective folds | 0.781613 | 0.550000 | no |
| C_selected_rolling_30d_monthly_p99_5 | monthly_recalibrated_trailing_empirical_percentile | 0.995000 | 9 monthly prospective folds | 0.960530 | 0.594050 | yes |

## Selected Rule

- Rule: `C_selected_rolling_30d_monthly_p99_5`
- Lookback: 30 calendar days
- Percentile: 0.995000
- Minimum prior strict-valid rows: 1000
- Calibration schedule: monthly boundary recalibration
- Minimum monthly realized coverage: 0.960530
- Mean monthly realized coverage: 0.987697
- Median threshold cost: 0.594050
- Selection reason: Smallest tested rolling tail rule that stayed above 90% realized coverage in every monthly prospective fold while using only prior strict-valid rows.
- Pre-critic gate: READY_FOR_STRATEGY_INTEGRATION_WITH_CONDITIONS
- Final gate after critic: EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW

Monthly prospective folds:

| Fold | Calibration rows | Validation rows | Threshold | Realized coverage | Validation p95 | Validation p99 |
|---|---:|---:|---:|---:|---:|---:|
| 2024-04 | 4319 | 5520 | 0.527000 | 0.962319 | 0.491000 | 0.650000 |
| 2024-05 | 5520 | 6780 | 0.788215 | 0.998968 | 0.450000 | 0.540000 |
| 2024-06 | 6780 | 5640 | 0.578050 | 0.995390 | 0.460000 | 0.534270 |
| 2024-07 | 5640 | 5520 | 0.558050 | 0.992210 | 0.457000 | 0.530000 |
| 2024-08 | 5520 | 6780 | 0.614050 | 0.995428 | 0.460000 | 0.560210 |
| 2024-09 | 6780 | 5640 | 0.607000 | 0.996277 | 0.477000 | 0.553220 |
| 2024-10 | 5640 | 5520 | 0.590000 | 0.994928 | 0.470000 | 0.557000 |
| 2024-11 | 5520 | 6644 | 0.594050 | 0.993227 | 0.460000 | 0.550000 |
| 2024-12 | 6644 | 8082 | 0.651570 | 0.960530 | 0.638000 | 0.800760 |

## Prospective Cost Contract

- Information allowed at time t: strict_valid_pair rows with timestamp earlier than the calibration boundary only
- Calibration schedule: monthly boundary recalibration
- Lookback days: 30
- Minimum observations: 1000
- Insufficient-history behavior: return unavailable/error until minimum prior strict-valid rows exist; do not backfill with future rows
- Session/time fallback: not used by selected primary tail rule; session diagnostics remain reporting-only
- Returned estimate: trailing strict-valid p99.5 spread threshold for the current monthly calibration period
- Full-year descriptive statistics remain research-only and must not silently become 2024 strategy inputs.

## Stress Layer Guard

- Primary baseline remains strict-only.
- Warning-review rows entered baseline: no.
- Stress/sensitivity remains separate from the primary baseline.
- Disagreed/inconclusive evidence and the unresolved strict-valid extreme remain preserved in the model spec.

## Multi-Year Scalability

- Assessment: structurally suitable for multi-year expansion as a rolling/expanding family because it uses prior strict-valid observations only and does not hard-code 2024 dates
- Additional years behavior: monthly recalibration would adapt to changing spread regimes as new prior strict-valid evidence accumulates
- Parameters that must be frozen before future holdouts: lookback_days, percentile, minimum_observations, calibration_schedule, fallback behavior
- Holdout protection: future years should be partitioned before further model refinement; failed holdouts must remain recorded rather than repeatedly tuned against

## Independent Critic Findings

Critic materially changed conclusion: yes.

- Q4 is no longer a clean holdout because the original Q4 failure was reused to select the harder rule.
- The selected p99.5 rule came from a very small candidate set and was not chosen by a robust predeclared search protocol.
- Multi-year scalability is structural only; it has not been validated across additional years, sparse periods, or regime changes.
- The p99.5 choice has tail-percentile overfitting risk unless frozen before any new holdout.
- Stress/baseline separation remains clear, but the stress layer is still a design contract rather than a complete execution-cost regime.

Responses:

- Final gate downgraded from READY_FOR_STRATEGY_INTEGRATION_WITH_CONDITIONS to EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW.
- The rolling p99.5 rule is retained as a candidate hardening result, not as an approved integration-ready policy.
- The report now labels Q4 as reused evidence rather than a clean holdout after rule selection.
- Next approval is limited to policy review of whether this 2024-calibrated rule can be frozen for a clean future holdout or must wait for multi-year partitioning.
## Gate Decision

EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW

- Independent critic found material Q4 holdout reuse / selection-leakage risk.
- The rolling p99.5 tail rule is a candidate result, not yet policy-approved for strategy integration.
- A separate policy review must decide whether to freeze this rule for a clean future holdout or wait for multi-year partitioning.

Exact next approval required: approve a policy review deciding whether the rolling p99.5 rule can be frozen before a clean future holdout or whether tail hardening must wait for multi-year partitioning. Do not begin strategy backtesting, ranking, optimization, profitability research, or multi-year acquisition.
