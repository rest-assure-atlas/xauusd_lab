# Execution-Cost Candidate v2 Architecture B Specification Freeze

Date: 2026-08-12

## Scope

Specification/design phase only for Architecture B: `Multi-Horizon Strict Tail Maximum`. This update freezes the Director-provided contract constants; it does not implement or test v2.

No 2015+ data was acquired or inspected. No 2023/2025 final holdouts were accessed. No candidate performance was calculated. No backtest, parameter optimization, historical outcome search, or strategy research was performed.

Inputs used:

- Existing 2024 consumed development evidence.
- Existing 2011-2014 burned validation/diagnostic evidence. 2011-2014 is not pristine for v2.
- Accepted v2 architecture proposal and critic review.

## Gate Result

`READY_TO_FREEZE_V2_ARCHITECTURE_B_CONTRACT`

Reason: Director has provided the complete Architecture B contract constants for freeze. This artifact remains specification/design only and is subject to later independent critic review before implementation or clean testing.

## Candidate Identity

- Candidate family: `execution_cost_candidate_v2`
- Candidate architecture: `B_multi_horizon_strict_tail_maximum`
- v1 status: `execution_cost_tail_rule_v1_candidate` is retired from advancement and preserved as failed evidence.
- Purpose: produce a prospective strict-valid-only spread threshold for later execution-cost testing, under the frozen Architecture B contract.

## Architecture B Contract Frozen Here

These choices are structural and justified by the observed v1 failure mechanisms:

1. Multi-horizon design: use exactly 30, 90, and 365 calendar-day lookback horizons.
2. Strict-valid-only primary population: horizon thresholds use only active `strict_valid_pair` rows.
3. Horizon-specific availability: each horizon is evaluated independently and requires at least 1000 prior strict-valid observations.
4. Sparse horizon skip: an unavailable horizon is excluded from threshold combination rather than imputed, future-filled, or replaced with non-strict data.
5. Maximum aggregation: combine available horizon-specific thresholds by taking the maximum threshold across available horizons.
6. No non-strict fallback: warning-review, calendar-only, placeholder, excluded, invalid, synthetic, or descriptive-only rows must not enter primary threshold estimation.
7. Prospective-only data rule: only rows with timestamps earlier than the recalibration/update boundary may be used.
8. No future backfill: thresholds must not be recomputed with future rows for any past decision point.
9. No silent carry-forward: threshold carry-forward is prohibited. All-horizon unavailable states return unavailable/error.
10. Evidence hygiene: 2011-2014 are burned evidence for any v2 informed by these findings and must not later be represented as pristine validation.

## Implementation-Ready Rule Skeleton

At each monthly UTC update boundary `T`:

1. Select primary rows where:
   - `pair_quality_status == strict_valid_pair`;
   - `MARKET_CLOSED_PLACEHOLDER` is absent from `pair_quality_reasons`;
   - row timestamp is `< T`;
   - row timestamp falls inside horizon `h` as `[T - h, T)`.
2. For each frozen horizon `h` in 30, 90, and 365 calendar days:
   - count prior strict-valid rows in `[T - h, T)`;
   - if count is below 1000, mark horizon `h` unavailable;
   - otherwise compute p99.5 over that horizon's strict-valid spread values using V1 quantile semantics: sort ascending, rank = q * (n - 1), and linearly interpolate between floor(rank) and ceil(rank).
3. If at least one horizon is available:
   - return `max(threshold_h for all available horizons)` at full precision with no operational rounding;
   - record all available and unavailable horizon diagnostics.
4. If no horizon is available:
   - return unavailable/error;
   - do not carry forward a prior threshold;
   - do not backfill from future data;
   - do not use warning-review or descriptive populations.

## Required Specification Fields

### Exact Set Of Historical Lookback Horizons

Status: frozen.

Rule: use exactly 30, 90, and 365 calendar-day lookback horizons. Each horizon interval is left-closed and right-open: `[T - horizon, T)`.

### Eligible Population

Status: frozen.

Primary population: active `strict_valid_pair` only.

Exclusions:

- `warning_review_pair`;
- `excluded`;
- placeholders including `MARKET_CLOSED_PLACEHOLDER`;
- calendar-only rows;
- invalid/negative-spread rows;
- synthetic rows;
- descriptive stress/sensitivity populations.

### Tail Statistic / Percentile

Status: frozen.

Rule: compute p99.5 for each eligible horizon. Use the exact V1 quantile semantics recovered from `execution_cost_model.py` and `tests/test_execution_cost_model.py`: sort values ascending, compute rank `q * (n - 1)`, and linearly interpolate between `floor(rank)` and `ceil(rank)` when the rank is not an integer.

### Horizon-Specific Threshold Combination

Status: frozen.

Rule: return the maximum numeric threshold among all eligible horizon-specific thresholds at the update boundary.

If exactly one horizon is eligible, return that horizon's threshold. If no horizons are eligible, return unavailable/error.

### Recalibration / Update Frequency

Status: frozen.

Rule: recalibrate monthly at deterministic UTC update boundaries.

### Minimum Prior-Observation Requirement Per Horizon

Status: frozen.

Rule: each horizon independently requires at least 1000 prior active strict-valid rows in its `[T - h, T)` interval.

### Handling When One Horizon Is Unavailable

Status: frozen.

Rule: skip that horizon for the current update boundary and record an unavailable-horizon diagnostic with the horizon name, prior strict-valid count, required minimum `1000`, and reason `minimum_prior_strict_valid_observations_not_met`.

### Handling When Multiple Horizons Are Unavailable

Status: frozen.

Rule: skip all unavailable horizons. If at least one horizon remains eligible, combine eligible thresholds using the frozen maximum rule. If all horizons are unavailable, return unavailable/error.

### Startup / Warm-Up Behavior

Status: frozen.

Rule: warmup is unavailable until any horizon is eligible. Once at least one horizon meets the 1000-row minimum, compute from eligible horizons only. Do not future-backfill, carry forward, or use non-strict data.

### Threshold Carry-Forward

Status: frozen.

Rule: no threshold may remain carried forward from a prior update. Every threshold must be computed from currently eligible horizon data at the update boundary. If all horizons are unavailable, return unavailable/error.

### Timestamp And Prospective-Only Rules

Status: frozen.

- A row is eligible for update boundary `T` only if `timestamp_utc < T`.
- Rows with `timestamp_utc >= T` are future information and prohibited.
- Update-boundary timestamps must be timezone-explicit UTC.
- Horizon intervals are left-closed, right-open: `[T - horizon, T)`.

### No-Future-Backfill Rule

Status: frozen.

Past thresholds must never be recomputed using rows that were unavailable at the original update boundary. Any rerun must reproduce the same information set for each boundary.

### Leakage Protections

Status: frozen.

- No warning-review rows in primary baseline.
- No placeholder/calendar-only/excluded rows in primary baseline.
- No full-period or future-period descriptive statistics as threshold inputs.
- No access to 2023 or 2025 final holdouts before explicit final release.
- No 2015+ data acquisition or inspection under this mission.
- No parameter selection by comparing candidate outcomes on 2011-2014.
- 2011-2014 is burned evidence and must not be represented as pristine validation for v2.
- Partitions are unchanged from the accepted Architecture B proposal.
- All implementation outputs must record source artifact paths, policy version, horizon availability diagnostics, and update-boundary timestamp.

### Rounding / Numerical Conventions

Status: frozen.

- Spreads are interpreted as decimal numeric values in the same units as the reconciliation `spread` column.
- Percentiles use V1 rank/interpolation semantics exactly: `rank = q * (n - 1)` with linear interpolation.
- Output thresholds preserve full precision with no operational rounding.
- Threshold application comparison convention: an observation is covered iff `observed_spread <= threshold`.

## Frozen Constants And Contract Values

| Field | Frozen value |
|---|---|
| candidate_family | `execution_cost_candidate_v2` |
| architecture | `B_multi_horizon_strict_tail_maximum` |
| horizons | `30`, `90`, `365` calendar days |
| horizon_interval | left-closed/right-open `[T - horizon, T)` |
| minimum_prior_strict_valid_count | `1000` for each horizon |
| tail_percentile | `p99.5` for each horizon |
| percentile_interpolation_method | V1 semantics: `rank = q * (n - 1)` with linear interpolation |
| update_cadence | monthly |
| primary_population | active `strict_valid_pair` only |
| placeholder_use | prohibited |
| warning_review_baseline_use | prohibited |
| excluded_population_use | prohibited |
| synthetic_rows_use | prohibited |
| horizon_combination_rule | maximum of eligible horizon thresholds |
| unavailable_horizon_behavior | skip horizon and record diagnostic |
| all_horizons_unavailable_behavior | return unavailable/error |
| warmup_behavior | unavailable until any horizon is eligible |
| future_backfill | prohibited |
| threshold_carry_forward | prohibited |
| threshold_numeric_precision_rounding | full precision; no operational rounding |
| threshold_application_comparison | covered iff `observed_spread <= threshold` |
| row_timestamp_rule | `timestamp_utc < update_boundary_utc` |
| partition_contract | partitions unchanged; 2011-2014 burned/not pristine for v2 |
| final_holdout_status | 2023 and 2025 remain `FINAL_UNTOUCHED_HOLDOUT` |

## Unresolved Constants Requiring Director Decision

None in this freeze artifact. Director has provided the Architecture B contract constants.

## Director Decision

Director has provided the complete Architecture B contract constants represented above. Implementation/testing remains out of scope for this artifact and must not run candidate performance, backtests, strategy research, 2015+ acquisition/inspection, or final-holdout access.

## Independent Critic Review

This Director-provided contract freeze is subject to later independent critic review. The existing critic artifact was not edited.

Durable critic artifact to leave unchanged: `reports/execution_cost_candidate_v2_architecture_b_specification_freeze_critic.md`

## Gate

`READY_TO_FREEZE_V2_ARCHITECTURE_B_CONTRACT`
