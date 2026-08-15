# Execution-Cost Model Implementation

Date: 2026-08-11
Status: implemented and validated; not strategy-integrated
Gate decision: EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW

## Purpose

This artifact implements the execution-cost modelling layer authorized by the post-corroboration evidence policy. It builds a spread-only primary baseline from active strict-valid evidence and keeps warning-review evidence out of the baseline.

No strategy backtests, ranking, optimization, profitability claims, external acquisition, raw evidence changes, schema changes, or session-definition changes were performed.

## Policy Source

- Policy version: `post_corroboration_execution_cost_evidence_policy:2026-08-10`
- Policy artifact: `reports/post_corroboration_execution_cost_evidence_policy.md`
- Policy JSON: `reports/post_corroboration_execution_cost_evidence_policy.json`
- Binding policy gate: `READY_FOR_EXECUTION_COST_MODELLING_WITH_CONDITIONS`

## Policy-To-Code Contract

- Primary baseline population: active `strict_valid_pair` rows only.
- Baseline exclusion rule: `warning_review_pair`, placeholders, excluded rows, and confirmed artifact/invalid rows are prohibited from the primary baseline.
- Enforcement: `select_strict_baseline_rows()` filters the population and `assert_strict_baseline_population()` raises on any warning or placeholder leakage.
- Future model rows must carry timestamp, quality status, placeholder flag, corroboration window/scope/class, allowed-use, and policy-version metadata.

## Evidence Counts

- Full reconciliation rows: 527040
- Active rows: 355891
- Placeholder rows: 171149
- Active strict-valid rows: 70165
- Active warning-review rows: 285726

## Baseline Model

- Selected form: `strict_valid_global_empirical_distribution_with_session_regime_diagnostics`
- Major conditioning variables: none for the primary global empirical baseline; configured session overlap bucket and UTC timestamp are retained for diagnostics, reporting, and sensitivity context.
- Training period: 2024-01-01 <= timestamp < 2024-10-01 (49919 strict rows)
- Validation period: 2024-10-01 <= timestamp <= 2024-12-31 (20246 strict rows)
- Strict-only full-sample median spread: 0.387000
- Strict-only full-sample p95 spread: 0.521000
- Strict-only full-sample p99 spread: 0.632000
- Strict-only full-sample max spread: 4.204000
- Lag-1 spread autocorrelation: 0.724020
- Validation risk flag: Temporal holdout p95 coverage is materially below nominal for all candidates, consistent with Q4 strict-valid spread drift. Future strategy integration must report conservative p99/tail sensitivity and not treat train-period p95 as a hard cap.
- Prospective-use guard: PROHIBITED_FOR_2024_STRATEGY_EVALUATION

Candidate validation was temporal and leakage-resistant: Jan-Sep 2024 strict-valid rows trained the candidate distributions; Oct-Dec 2024 strict-valid rows validated them. No strategy information was used.

| Candidate | Validation p95 coverage | Median MAE | Data-poor groups | Selected |
|---|---:|---:|---:|---|
| global_empirical_distribution | 0.731404 | 0.075416 | 0 | yes |
| session_bucket_empirical_distribution | 0.688333 | 0.072732 | 0 | no |
| session_hour_empirical_distribution | 0.640522 | 0.075464 | 0 | no |

Selection rationale: Selected because it is the simplest transparent baseline and had the least weak temporal holdout p95 coverage. Session/regime structure is retained as mandatory diagnostics and sensitivity context rather than promoted to a more fragile primary baseline.

Gate reasons:

- Independent critic found material Q4 holdout reuse / selection-leakage risk.
- The rolling p99.5 tail rule is a candidate result, not yet policy-approved for strategy integration.
- A separate policy review must decide whether to freeze this rule for a clean future holdout or wait for multi-year partitioning.

## Stress And Sensitivity Layer

- Form: `separate_non_pooled_policy_stress_and_sensitivity_layer`
- Primary baseline pooling: prohibited.
- Closely corroborated target-cluster warning rows: separate non-pooled stress/sensitivity scenario only.
- Directionally corroborated warning rows: adverse, widened-uncertainty, secondary scenario only.
- Disagreed and inconclusive windows: excluded from favorable calibration and retained for adverse/unresolved reporting.
- Future stress membership must be prospective and auditable; hard-coded historical stress dates are prohibited as future membership logic.

Stress/sensitivity row counts:

- `closely_corrob_target_cluster_warning`: 144
- `directional_target_cluster_warning`: 4010
- `disagreed_target_cluster_warning`: 1
- `inconclusive_target_cluster_warning`: 6
- `untested_active_warning`: 269121

Special-case counts are split by scope so target-cluster evidence is not confused with context rows:

- `2024-02-18_ge2_02`: target_cluster=6, bounded_window_context=17, same_date_context=0, not_externally_tested=0
- `2024-04-05_strict_ge2_01`: target_cluster=0, bounded_window_context=0, same_date_context=0, not_externally_tested=0
- `2024-12-11_ge2_04`: target_cluster=1, bounded_window_context=35, same_date_context=0, not_externally_tested=0

## Special Cases Preserved

- `2024-12-11_ge2_04`: warning target disagreement; excluded from favorable calibration and retained in adverse sensitivity.
- `2024-02-18_ge2_02`: unresolved warning target; excluded from favorable calibration and retained as unresolved/adverse evidence.
- `2024-04-05_strict_ge2_01`: unresolved strict-valid extreme control; separately reported as a stress/control caveat.

## Output Contract

The model will provide future strategy tests with a strict-only baseline spread empirical distribution, conservative strict-only percentile costs, session/regime diagnostics, separate labelled stress/sensitivity scenarios, and provenance metadata.

It is spread-only. Slippage, commissions, financing, latency, order-book depth, and market impact remain missing cost components and must not be silently added.

## Tests

Focused tests cover strict-only baseline enforcement, warning/placeholder leakage prevention, deterministic statistics, session boundary handling, missing bucket fallback declaration, stress/sensitivity separation, disagreement/inconclusive preservation, and policy-version reporting.

## Independent Critic Findings

Critic materially changed implementation: yes.

- Temporal validation shows material baseline underestimation; train-period p95 covers only about 73.1% of Q4 validation rows.
- Full-year strict summaries need an explicit descriptive-only guard to avoid future-period leakage into 2024 strategy evaluation.
- Stress model remains a design contract rather than an implemented prospective stress-cost model.
- Special-case counts needed scope splitting so context rows are not confused with target-cluster evidence.

Responses:

- Final gate downgraded to EXECUTION_COST_MODEL_NEEDS_SMALL_FOLLOWUP.
- Added train-only/prospective application guard and prohibited full-year summaries as 2024 strategy cost inputs.
- Made weak p95 holdout coverage an executable gate reason.
- Split special-case counts by target-cluster, bounded-window, same-date, and not-tested scope.

## Prospective Tail Hardening Follow-Up

The first implementation gate was downgraded to `EXECUTION_COST_MODEL_NEEDS_SMALL_FOLLOWUP` because train-period p95 coverage on Q4 strict-valid rows was only 0.731404. That failed history is preserved here and in `reports/execution_cost_prospective_tail_hardening.md`.

- Hardened selected rule: `C_selected_rolling_30d_monthly_p99_5`
- Hardened minimum monthly realized coverage: 0.960530
- Pre-tail-critic gate: `READY_FOR_STRATEGY_INTEGRATION_WITH_CONDITIONS`
- Final hardened gate after critic: `EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW`
- Status: candidate hardening rule identified, but policy review is required because the same 2024/Q4 evidence was reused during rule selection.

## Gate Decision

EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW

Exact next approval required: approve a policy review deciding whether the rolling p99.5 rule can be frozen before a clean future holdout or whether tail hardening must wait for multi-year partitioning. Do not begin strategy backtesting, ranking, optimization, profitability research, or multi-year acquisition.
