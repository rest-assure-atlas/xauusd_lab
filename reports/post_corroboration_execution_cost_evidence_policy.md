# Post-Corroboration Execution-Cost Evidence Policy

Date: 2026-08-10
Status: final after independent critic amendments
Gate result: READY_FOR_EXECUTION_COST_MODELLING_WITH_CONDITIONS

## 1. Purpose

This policy decides how the 2024 XAUUSD BID/ASK evidence classes may be used in future execution-cost modelling after the completed bounded FXCM corroboration campaign.

This is an evidence-use gate only. It does not build an execution-cost model, run strategy tests, rank strategies, optimize parameters, acquire data, change schemas, change session definitions, change quality rules, modify raw Dukascopy or FXCM evidence, or make profitability claims.

The policy is decided before any strategy profitability results are known. Future strategy outcomes MUST NOT be used to change evidence treatment retrospectively.

## 2. Evidence Basis

This policy is based on durable artifacts only:

- `reports/pre_modelling_spread_evidence_policy.md`
- `reports/fxcm_full_bounded_corroboration_2024.md`
- `reports/fxcm_full_bounded_corroboration_2024.json`
- `reports/fxcm_full_bounded_corroboration_2024_windows.csv`
- `reports/top_warning_date_spread_integrity_review_2024.md`
- `reports/strict_vs_warning_spread_sensitivity_2024-01-01_to_2024-12-31.md`
- `reports/spread_characterization_2024-01-01_to_2024-12-31_report.md`
- `reports/spread_characterization_2024-01-01_to_2024-12-31_full_year_summary.csv`
- `reports/bid_ask_reconciliation_2024-01-01_to_2024-12-31.csv`

Validated factual anchors:

- Full-year BID/ASK reconciliation rows: 527040.
- Pair status counts: `strict_valid_pair` 70165, `warning_review_pair` 380555, `excluded` 76320.
- Closed-market placeholder rows: 171149.
- Active/non-placeholder rows: 355891.
- Active strict-valid rows: 70165.
- Active warning-review rows: 285726.
- Active warning-review rows with spread `>=2.0`: 84.
- Active strict-valid rows with spread `>=2.0`: 2.
- Top warning-date review covered 84/84 active warning-review `>=2.0` rows and found 0 raw BID/ASK close mismatches among those rows.
- Warning-review active spread tail is event-cluster driven; top 5 warning dates contain 1893/2946 warning-review p99 rows.
- FXCM full bounded corroboration final gate: `CORROBORATION_PARTIALLY_SUPPORTIVE_MORE_REVIEW_REQUIRED`.
- FXCM campaign completed 16/16 target windows and 6/6 controls, all request-level complete.
- FXCM classifications: 13 `CONFIRMED_CLOSELY`, 6 `CONFIRMED_DIRECTIONALLY`, 1 `DISAGREES`, 2 `INCONCLUSIVE`.
- Warning `>=2.0` windows closely supported: `2024-01-25_ge2_01`, `2024-02-18_ge2_01`, `2024-05-15_ge2_01`, `2024-07-11_ge2_01`, `2024-10-10_ge2_01`, `2024-12-11_ge2_01`, `2024-12-11_ge2_02`, `2024-12-11_ge2_03`, `2024-12-11_ge2_05`, `2024-12-11_ge2_06`, `2024-12-12_ge2_01`.
- Warning `>=2.0` windows directionally supported: `2024-05-01_ge2_01`, `2024-09-11_ge2_01`, `2024-12-12_ge2_02`.
- Warning `>=2.0` window disagreed: `2024-12-11_ge2_04`.
- Warning `>=2.0` window unresolved: `2024-02-18_ge2_02`.
- Strict-valid extreme control unresolved: `2024-04-05_strict_ge2_01`.

## 3. Definitions

- `strict_valid_pair`: Existing active pair status that passed strict data-quality rules without warning-tier treatment.
- `warning_review_pair`: Existing active pair status that is source-linked and reviewed but carries warning context, especially `INTERNAL_FLAT_ZERO_VOLUME` in the ASK-side source lineage.
- `active row`: A row without `MARKET_CLOSED_PLACEHOLDER` in `pair_quality_reasons`.
- `placeholder/market-closed row`: A row kept for calendar/session completeness but not active market evidence.
- `confirmed artifact/invalid row`: A row with durable evidence of invalidity, source mismatch, placeholder leakage into active analysis, schema/rule failure, or another documented non-observational artifact.
- `window-level corroboration`: FXCM classification assigned to a bounded time window, not automatically to every individual Dukascopy row inside that window.
- `row-level corroboration`: Corroboration of a specific minute/row by aligned external evidence. The FXCM campaign mostly supports window-level and cluster-level use, not blanket row-level validation.
- `baseline execution-cost model`: The primary/default execution-cost assumption used for headline strategy reporting.
- `sensitivity model`: A labelled alternative used to test dependence on evidence treatment.
- `robustness analysis`: A structured comparison across evidence treatments that must be reported alongside baseline results.
- `stress-event model`: A deliberately adverse or regime-specific treatment of rare source-observed spread stress.
- `strategy ranking`: Selecting, ranking, optimizing, or discarding strategies based on performance.
- `headline strategy result`: The primary result highlighted as the main strategy outcome.
- `final research conclusion`: Any conclusion about strategy viability, readiness, or robustness.

## 4. Row and Window Eligibility Rule

FXCM corroboration is window-level and cluster-level evidence unless a future artifact establishes row-level support. A row inside a corroborated window is not automatically corroborated.

Future model input rows MUST carry:

- `timestamp_utc`;
- `pair_quality_status`;
- `pair_quality_reasons`;
- `active_placeholder_flag`;
- `corroboration_window_id` when applicable;
- `corroboration_scope`, one of `target_cluster`, `bounded_window_context`, `same_date_context`, `not_externally_tested`;
- `corroboration_class`, one of `CONFIRMED_CLOSELY`, `CONFIRMED_DIRECTIONALLY`, `DISAGREES`, `INCONCLUSIVE`, `not_externally_tested`;
- `allowed_use`;
- `policy_version`.

Eligibility rules:

- Target-cluster rows in closely corroborated windows may be used for closely corroborated stress calibration.
- Bounded-window context rows around closely corroborated windows may be used only for context and transition estimates, not as if each row were independently confirmed.
- Directionally corroborated rows must be labelled directional and used only for widened-uncertainty, adverse, or secondary sensitivity treatment unless a future artifact upgrades them.
- Disagreed and inconclusive rows must be excluded from favorable calibration and retained for adverse sensitivity, unresolved counts, and reporting.
- Warning-review rows outside the FXCM target/control windows are not externally corroborated by this campaign. They may remain source-consistent descriptive evidence, but they must not inherit FXCM corroboration status.

## 5. Evidence-Class Decision Table

Allowed-use codes:

- `ALLOWED`: May be used directly for the named purpose under this policy.
- `CONDITIONAL`: May be used only under the listed conditions and with mandatory reporting.
- `PROHIBITED`: Must not be used for the named purpose.

| Evidence class | Descriptive spread analysis | Baseline execution-cost model | Sensitivity model | Robustness analysis | Stress-event model | Strategy ranking | Headline strategy result | Final research conclusion |
|---|---|---|---|---|---|---|---|---|
| A. active `strict_valid_pair` | ALLOWED | ALLOWED | ALLOWED | ALLOWED | CONDITIONAL | ALLOWED | ALLOWED | ALLOWED |
| B. eligible target-cluster `warning_review_pair` in `CONFIRMED_CLOSELY` warning window | ALLOWED | PROHIBITED | ALLOWED | ALLOWED | CONDITIONAL | PROHIBITED | PROHIBITED | CONDITIONAL |
| C. eligible target-cluster `warning_review_pair` in `CONFIRMED_DIRECTIONALLY` warning window | ALLOWED | PROHIBITED | CONDITIONAL | CONDITIONAL | CONDITIONAL | PROHIBITED | PROHIBITED | CONDITIONAL |
| D. `warning_review_pair` in `DISAGREES` warning window | ALLOWED | PROHIBITED | CONDITIONAL | CONDITIONAL | CONDITIONAL | PROHIBITED | PROHIBITED | CONDITIONAL |
| E. `warning_review_pair` in `INCONCLUSIVE` warning window | ALLOWED | PROHIBITED | CONDITIONAL | CONDITIONAL | CONDITIONAL | PROHIBITED | PROHIBITED | CONDITIONAL |
| F. active stress-event clusters | ALLOWED | CONDITIONAL | ALLOWED | ALLOWED | ALLOWED | PROHIBITED | PROHIBITED | CONDITIONAL |
| G. placeholder/market-closed rows | CONDITIONAL | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED |
| H. confirmed artifact/invalid rows | CONDITIONAL | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED |

Class A conditions:

- `strict_valid_pair` remains the primary/default baseline population.
- Stress-event use is conditional because strict-valid stress observations may calibrate adverse stress treatment only when the stress-regime definition is prospective and not chosen from strategy outcomes.

Class B conditions:

- Closely corroborated warning-review evidence MUST NOT enter the primary baseline execution-cost model.
- It MAY enter a baseline-report-adjacent stress component only as a separately calibrated, separately reported, non-pooled stress or event-regime scenario.
- It MUST NOT be directly pooled into the strict-valid baseline distribution.
- It MUST NOT become the sole headline basis for strategy ranking or final favorable conclusions.
- It applies only to eligible target-cluster rows unless a future row-level artifact broadens eligibility.

Class C conditions:

- Directionally corroborated warning-review evidence MAY support sensitivity, robustness, and stress-regime calibration with lower confidence than Class B.
- It MUST be labelled as directional, not exact or close validation.
- It MUST NOT enter any primary baseline component.
- It MUST be adverse, widened-uncertainty, or secondary sensitivity evidence unless a future artifact upgrades it.

Classes D and E conditions:

- Disagreed and inconclusive warning evidence MUST remain visible.
- They MAY be used only as adverse sensitivity, robustness caveats, or stress-bound checks.
- They MUST NOT be used to calibrate favorable baseline assumptions.

Class F conditions:

- Stress-event cluster membership MUST be defined prospectively from observable market/session/event variables available before strategy results are inspected.
- Stress-event clusters MAY use Classes B and C, plus preserved D/E caveats, but must distinguish corroboration strength.

Class G and H conditions:

- Placeholder/market-closed and confirmed invalid rows MAY be reported only as excluded counts, audit trail, or data-quality context.
- They MUST NOT be treated as observed executable spread evidence.

## 6. Baseline Population Rule

Active `strict_valid_pair` rows remain the primary/default baseline population.

Rationale:

- They passed strict quality rules without warning-tier treatment.
- They are the only active evidence class ready for direct primary baseline use without external corroboration caveats.
- The FXCM result is partially supportive, not fully supportive.
- FXCM is DEMO/account/feed specific, not market-level truth.
- One exact warning target disagreed and one exact warning target remains unresolved.
- The strict-valid extreme control `2024-04-05_strict_ge2_01` remains unresolved.

Warning-review evidence MUST NOT be pooled into the baseline distribution.

The only baseline-report-adjacent warning-review allowance is a separately reported stress/event-regime scenario using eligible target-cluster rows from closely corroborated warning windows. That scenario is not the primary baseline. It must:

- remain separate from the strict-valid baseline;
- be labelled as warning-review stress evidence;
- preserve strict-only baseline results with equal or greater prominence;
- exclude disagreed and inconclusive warning windows from favorable calibration;
- include sensitivity showing the effect of including versus excluding directionally corroborated windows.

## 7. Warning-Review Rules

Closely corroborated warning-review windows:

- ALLOWED for descriptive analysis.
- ALLOWED for sensitivity and robustness.
- CONDITIONAL for a separately reported stress-event model.
- PROHIBITED from the primary baseline execution-cost model.
- CONDITIONAL for a non-pooled baseline-report-adjacent stress scenario only if the model design explicitly separates it from strict-valid baseline costs.
- PROHIBITED for direct broad pooling, strategy ranking, or headline strategy results.

Directionally corroborated warning-review windows:

- ALLOWED for descriptive analysis.
- CONDITIONAL for adverse, widened-uncertainty, or secondary sensitivity/robustness/stress-event modelling.
- PROHIBITED from primary baseline components.
- PROHIBITED for strategy ranking and headline strategy results.

Disagreed warning-review window `2024-12-11_ge2_04`:

- MUST be separately reported.
- PROHIBITED from baseline calibration.
- MAY be used as adverse sensitivity and as a caution against treating Dec 11 as uniformly corroborated at every exact minute.

Inconclusive warning-review window `2024-02-18_ge2_02`:

- MUST be separately reported.
- PROHIBITED from baseline calibration.
- MAY be used as adverse sensitivity or unresolved stress-context evidence.
- Terminal zero-record FXCM chunks MUST NOT be treated as proof that no market update existed.

Untested warning-review rows:

- Warning-review rows outside the FXCM target/control windows are not externally corroborated by this campaign.
- They MAY be used descriptively as source-consistent warning-review evidence under the older policy.
- They are PROHIBITED from baseline calibration and from any claim of external confirmation.

## 8. Stress-Regime Rule

Current evidence supports designing a separate stress-event execution regime in a future modelling mission.

This policy does not create that model. It only authorizes a future model-design step under these conditions:

- Stress-regime membership must be prospective, rule-based, and observable without knowing strategy outcomes.
- Stress-regime predicates must be written as auditable functions before model runs.
- Predicates must declare their calibration sample, lookback period, timestamp/session features, spread thresholds, and external-corroboration fields before strategy results are inspected.
- Hard-coded corroborated dates are allowed only as labelled calibration or evaluation sets, not as live model membership predicates.
- Contemporaneous spread quantiles may be used only if the lookback window and calibration population are predeclared and exclude future information.
- Candidate variables may include configured session, predeclared rollover/reopening windows, predeclared timestamp features, predeclared spread quantiles, and predeclared external-corroboration status.
- Closely corroborated warning windows may calibrate core warning-review stress behaviour.
- Directionally corroborated warning windows may calibrate a lower-confidence or widened-uncertainty variant.
- Disagreed and inconclusive warning windows must be excluded from favorable calibration but retained in adverse sensitivity and reporting.
- Broad p99 controls may support regime plausibility, not row-level validation.
- The unresolved strict-valid extreme control must remain a separate stress/control caveat.
- Stress-regime outputs must be reported separately from strict-valid baseline outputs.
- Regime-stratified counts and calibration summaries are mandatory before combining any costs. At minimum separate Tokyo, London/New York overlap, rollover/reopening/outside configured sessions, holiday/sparse-control context, and ordinary strict-valid periods where applicable.

## 9. Disagreement and Inconclusive Treatment

The following items must not disappear:

- `2024-12-11_ge2_04`: warning target disagreement. It blocks treating every Dec 11 warning minute as closely corroborated. It must be excluded from favorable baseline/stress calibration and included in adverse sensitivity.
- `2024-02-18_ge2_02`: unresolved warning target. It blocks treating the full Feb 18 warning sequence as externally confirmed. It must be excluded from favorable baseline/stress calibration and included in unresolved reporting.
- `2024-04-05_strict_ge2_01`: unresolved strict-valid extreme control. It does not directly weaken warning-review source consistency, but it warns that FXCM may miss exact-minute stress visible in Dukascopy. It must be separately reported in model evidence summaries.
- Directionally supported windows: must not be promoted to close support or used as exact row validation.

## 10. Exclusion Burden

The burden of proof remains on exclusion.

Rows may be excluded from active modelling evidence only with a durable artifact showing a legitimate exclusion ground:

- raw/reconciled BID or ASK mismatch;
- checksum/provenance failure;
- duplicate or invalid timestamp;
- missing minute/internal gap that violates existing quality rules;
- invalid numeric row, OHLC consistency failure, or negative volume under existing rules;
- confirmed placeholder or market-closed leakage into active evidence;
- documented provider artifact making the quote non-observational;
- explicit pre-registered market-structure exclusion defined before strategy results are known.

Extreme spread size, warning-tier status, holiday/reopening timing, poor strategy performance, or improved strategy performance are not sufficient exclusion grounds.

## 11. Mandatory Future Reporting Standard

Every future execution-cost or strategy report using this evidence MUST include:

- baseline population statement;
- evidence-class counts for active `strict_valid_pair`, active warning-review by corroboration class, placeholders, excluded rows, and confirmed invalid rows if any;
- row/window eligibility counts by `corroboration_scope` and `allowed_use`;
- regime-stratified counts and calibration summaries before any combined cost output;
- strict-only baseline result;
- warning/corroborated result where applicable;
- stress-regime result where applicable;
- sensitivity result including warning-review inclusion/exclusion effect;
- robustness result across strict-only, closely corroborated warning, directionally corroborated warning, disagreed/inconclusive adverse treatment, and stress treatment where applicable;
- disagreement and inconclusive treatment, explicitly naming `2024-12-11_ge2_04`, `2024-02-18_ge2_02`, and `2024-04-05_strict_ge2_01` when relevant;
- provider/corroboration status and a statement that FXCM is DEMO/account/feed specific;
- exclusions with evidence citation;
- policy artifact path and version/date;
- explicit statement that strategy outcomes were not used to choose or amend evidence policy.

Reports MUST NOT present warning-review-inclusive results as the sole headline. If warning-review or stress results are shown, strict-only baseline results must be shown with equal or greater prominence.

## 12. No-Retrospective-Optimization Rule

Evidence/model policy MUST NOT be changed because a strategy performs better or worse under a particular treatment.

Amendment procedure:

- Write a new dated policy artifact or a clearly versioned amendment section before affected model runs.
- Cite new durable evidence justifying the change.
- State whether the amendment applies only to future runs or also requires replaying prior runs.
- Preserve prior results under the policy version that governed them.
- Record both the old and new policy gates if a recommendation changes.

Legitimate reasons to amend this policy include:

- new independent BID/ASK corroboration with clear provenance;
- confirmed data-integrity defect or correction;
- documented provider artifact affecting observability;
- pre-registered market-structure rule justified before strategy outcomes;
- independent review identifying ambiguity or unenforceable rules.

Illegitimate reasons include:

- strategy profitability, ranking, drawdown, or trade frequency under one evidence treatment;
- desire to remove inconvenient stress dates;
- desire to soften costs to improve backtests;
- desire to harden costs after seeing a result one dislikes.

## 13. Unresolved Decisions

- Exact stress-regime formula, parameters, durations, and transition rules remain unbuilt.
- Whether closely corroborated warning-review stress should become a baseline-adjacent stress component or only a sensitivity/stress scenario remains a model-design decision for the next mission.
- Directionally corroborated warning windows need uncertainty treatment before quantitative calibration.
- The unresolved strict-valid extreme control needs explicit reporting in any stress-regime design.
- No execution-cost model exists yet under this policy.
- Exact row/window eligibility implementation must be validated before model execution.
- Stress-regime predicates must be written and validated before model execution.

## 14. Implementation Recommendations

- Add evidence-class labels to future model input tables: `strict_valid_baseline`, `warning_close_target_cluster`, `warning_close_context`, `warning_directional_adverse`, `warning_disagrees_adverse`, `warning_inconclusive_unresolved`, `warning_not_externally_tested`, `stress_cluster`, `placeholder`, `excluded_or_invalid`.
- Add `corroboration_window_id`, `corroboration_class`, `allowed_use`, and `policy_version` fields to derived modelling inputs.
- Add `corroboration_scope` and `stress_predicate_id` fields.
- Build strict-only baseline first.
- Build warning-review and stress variants as separate named scenarios.
- Add validation that fails if disagreed or inconclusive windows are silently included in favorable calibration.
- Add validation that fails if directionally corroborated rows are treated as close support.
- Add validation that fails if warning rows outside target/control windows inherit external corroboration.
- Add validation that fails if stress predicates hard-code evaluation dates as live membership logic.
- Add validation that fails if placeholder rows enter active spread modelling.
- Add report checks requiring strict-only results before warning-inclusive results.

## 15. Independent Critic Findings

An independent read-only critic challenged the draft for confirmation bias, row/window ambiguity, hindsight-defined stress regimes, accidental pooling, over/under-conservatism, disagreement handling, and enforceability.

Material findings and responses:

- High: Row-level vs window-level use remained an enforceability risk. Response: added the Row and Window Eligibility Rule, required explicit `corroboration_scope`, and limited close support to eligible target-cluster rows unless future row-level evidence broadens eligibility.
- High: Stress-regime predicates were too hindsight-shaped. Response: required auditable pre-model predicate functions, fixed lookbacks/calibration populations, no hard-coded corroborated dates as live predicates, and regime-stratified summaries.
- Medium: Class B baseline-adjacent wording was too permissive. Response: primary baseline warning-review use is now PROHIBITED; only a separate baseline-report-adjacent stress scenario is conditionally allowed.
- Medium: Directional corroboration had too many positive uses. Response: directionally supported rows are now adverse, widened-uncertainty, or secondary sensitivity evidence unless a future artifact upgrades them.
- Medium: Heterogeneous regimes were not fully separated. Response: mandatory future reporting now requires regime-stratified counts and calibration summaries before combining costs.
- Low: Disagreement/inconclusive handling was preserved well. Response: retained explicit named treatment and tied it to row/window eligibility checks.
- Low: Targeted-only/cherry-picking caveat needed clearer wording. Response: added that untested warning-review rows outside target/control windows are not externally corroborated.

Critic materially changed policy: yes. The critic changed row/window eligibility, stress predicate enforceability, baseline wording, directional-use restrictions, and future reporting requirements.

## 16. Gate Decision

Gate outcome: READY_FOR_EXECUTION_COST_MODELLING_WITH_CONDITIONS.

Conditions:

- Build strict-only baseline first.
- Do not pool warning-review rows into the primary baseline.
- Implement row/window eligibility fields before model execution.
- Write and validate prospective stress-regime predicates before model execution.
- Keep closely corroborated warning evidence in separate stress/sensitivity or baseline-report-adjacent stress scenarios, not the primary baseline.
- Treat directionally corroborated warning evidence as adverse/widened-uncertainty or secondary sensitivity unless future evidence upgrades it.
- Preserve disagreed and inconclusive windows in reporting and adverse sensitivity.
- Do not begin strategy ranking, optimization, or profitability claims under this gate alone.
