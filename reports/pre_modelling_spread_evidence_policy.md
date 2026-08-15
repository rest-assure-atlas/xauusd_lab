# Pre-Modelling Spread Evidence Policy

Date: 2026-08-09
Status: active policy draft for pre-modelling gates
Gate outcome: READY_FOR_TARGETED_EXTERNAL_CORROBORATION

## 1. Purpose

This policy defines how 2024 XAUUSD BID/ASK spread evidence MAY and MUST NOT be used before strategy work or execution-cost modelling. It is evidence governance only. It does not acquire data, delete data, reclassify rows, change schemas, alter session definitions, revise quality rules, build execution-cost models, or make profitability claims.

The policy is designed to be applied before any strategy profitability result is known. Strategy returns, ranking, drawdown, trade frequency, or optimization output MUST NOT be used to choose evidence populations, exclude dates, soften warning treatment, or amend this policy retrospectively.

## 2. Evidence Basis

This policy is based on existing durable artifacts only:

- `reports/full_year_ASK_2024_warning_review.md`
- `reports/linked_observation_report_ASK_2024-01-01_to_2024-12-31.csv`
- `reports/data_manifest_ASK_2024-01-01_to_2024-12-31.csv`
- `reports/bid_ask_reconciliation_2024-01-01_to_2024-12-31.csv`
- `reports/spread_characterization_2024-01-01_to_2024-12-31_report.md`
- `reports/spread_characterization_2024-01-01_to_2024-12-31_full_year_summary.csv`
- `reports/strict_vs_warning_spread_sensitivity_2024-01-01_to_2024-12-31.md`
- `reports/top_warning_date_spread_integrity_review_2024.md`

Validated factual anchors:

- ASK linked-observation quality population: `strict_valid` 104 dates, `warning_review` 209 dates, `calendar_only` 53 dates, `excluded_unusable` 0 dates.
- Full-year BID/ASK reconciliation rows: 527,040 minute rows.
- Reconciliation status counts: `strict_valid_pair` 70,165 rows, `warning_review_pair` 380,555 rows, `excluded` 76,320 rows.
- Closed-market placeholder rows: 171,149 rows.
- Active/non-placeholder reconciliation rows: 355,891 rows.
- Warning-review active rows in strict-vs-warning sensitivity: 285,726 rows.
- Strict-valid active rows in strict-vs-warning sensitivity: 70,165 rows.
- ASK warning-review dates all carry `INTERNAL_FLAT_ZERO_VOLUME`; no reviewed warning-review date had missing linked/raw provenance, checksum mismatch, duplicate timestamp, invalid timestamp, internal gap, missing minute, invalid numeric row, OHLC failure, negative volume, or `excluded_unusable` classification.
- ASK warning diagnostic context: 190 warning-review dates had all diagnostic runs outside configured sessions; 19 dates had at least one diagnostic run overlapping Tokyo, London, or New York session windows.
- Spread characterization showed non-placeholder active spread p99 0.620 and max 5.981; strict-valid active p99 0.632 and max 4.204; warning-review active p99 0.610 and max 5.981 in sensitivity analysis.
- Warning-review active rows at spread >= 2.0: 84. The top warning-date integrity review reviewed 84/84 of those rows and found 0 raw BID/ASK close mismatches among reviewed warning >=2.0 rows.
- Warning-review tail behavior was classified as event-cluster driven, with top 5 warning dates containing 1,893/2,946 warning-review p99 rows, or 64.3%.

## 3. Definitions

- `strict_valid`: Existing quality tier or pair status that passed strict data-quality rules without warning-tier treatment.
- `warning_review`: Existing quality tier or pair status that is source-linked and reviewed but carries preserved warning context. In the reviewed ASK population this means `INTERNAL_FLAT_ZERO_VOLUME`.
- `reviewed/source-consistent warning_review`: A warning-review row/date whose raw source rows and reconciliation values agree under existing review artifacts, without detected placeholder leakage or row-level invalidity.
- `warning_review inconclusive`: A warning-review row/date whose raw rows may reconcile but whose context is too limited, sparse, clustered, single-provider, or otherwise unresolved for model inclusion.
- `confirmed artifact/invalid`: A row/date with durable evidence of invalidity, source mismatch, placeholder leakage into active analysis, schema/rule failure, or market-closed-only status.
- `active row`: A row not carrying `MARKET_CLOSED_PLACEHOLDER` and not a calendar-only placeholder.
- `placeholder/market-closed row`: A row or date present for calendar/session completeness but not active market evidence.
- `stress-event cluster`: Concentrated spread widening by date/hour/session that is source-observed and active, including warning-review clusters such as the December 2024 warning tail.
- `baseline cost model`: The primary execution-cost assumption used for headline strategy evaluation.
- `sensitivity model`: A non-headline alternative cost assumption used to test robustness to evidence treatment.
- `stress model`: A deliberately adverse scenario preserving or amplifying rare but source-observed spread regimes.

## 4. Primary Population Rule

The primary/default evidence population for future reporting MUST be active `strict_valid_pair` rows only.

Future reports MUST show `strict_valid_pair` active results as the baseline spread evidence population. They MAY show `warning_review_pair` active results only as separately labelled descriptive, sensitivity, robustness, or stress evidence under this policy. They MUST NOT pool strict-valid and warning-review rows into a single headline population unless the report also presents strict-only results with equal prominence and explicitly states that the pooled result is non-primary.

Placeholder, market-closed, calendar-only, and `excluded` rows MUST NOT enter active descriptive statistics, baseline cost modelling, sensitivity model inputs, stress model inputs, strategy ranking, or strategy headline results as observed executable spreads.

## 5. Warning-Review Usage Policy

Allowed uses:

- Descriptive spread analysis: reviewed/source-consistent `warning_review` active rows MAY be reported when labelled as warning-tier evidence and separated from strict-valid evidence.
- Sensitivity and robustness: reviewed/source-consistent `warning_review` active rows MAY be used in sensitivity/robustness comparisons to measure dependence on warning treatment.
- Stress scenarios: active warning-review event clusters MAY be preserved or amplified in stress models when labelled as source-observed stress evidence.

Conditional uses:

- Baseline cost modelling: `warning_review` rows MUST NOT be used in the baseline cost model until a future gate records external corroboration or an explicit policy amendment. Even then, inclusion MUST remain separately auditable and MUST include strict-only comparison results.
- Final conclusions: warning-review evidence MAY inform caveats about cost sensitivity and stress exposure, but MUST NOT be the sole basis for a favorable strategy conclusion.

Prohibited uses:

- Strategy ranking: warning-review rows MUST NOT be used to select, rank, optimize, or discard strategies unless the same ranking is also shown under strict-only baseline evidence and the warning-tier treatment is pre-registered before strategy results are inspected.
- Headline result: warning-review rows MUST NOT be the default headline execution-cost evidence before targeted external corroboration and a recorded modelling gate.
- Retrospective filtering: warning-review dates MUST NOT be included or excluded based on whether they improve or harm strategy profitability.

## 6. Stress-Event Cluster Policy

Active stress-event clusters MUST be preserved as evidence. They MUST NOT be erased by blanket outlier removal, top-date exclusion, volatility trimming, percentile winsorization, holiday filters, or rollover/session filters unless the exclusion satisfies the burden of proof in Section 8.

Stress-event clusters SHOULD be reported in three ways:

- strict-only baseline, where available;
- warning-tier sensitivity, keeping warning_review separated;
- adverse stress scenario that retains source-consistent active clusters even when they are not baseline-model inputs.

Retrospective filters MAY be used only as diagnostic views. They MUST be named, justified, and reported alongside unfiltered strict-only and warning-tier counts. A filter developed after seeing strategy results MUST NOT change headline evidence treatment for that strategy evaluation.

## 7. Inconclusive Data Treatment

Inconclusive warning-review dates/rows MAY be used for labelled descriptive spread reporting if they are active and source-reconciled. They MUST NOT be used in baseline cost modelling, strategy ranking, or strategy headline conclusions.

Inconclusive rows SHOULD be carried as separate sensitivity or stress buckets rather than deleted. If an inconclusive row is later resolved, the resolution MUST cite the new durable artifact and the policy version under which it was resolved.

## 8. Exclusion Standard and Burden of Proof

The burden of proof is on exclusion. Active rows MUST remain in their existing evidence class unless a durable artifact establishes a legitimate exclusion ground.

Legitimate exclusion grounds are limited to:

- raw/reconciled BID or ASK mismatch;
- checksum/provenance failure;
- duplicate or invalid timestamp;
- missing minute/internal gap that violates existing quality rules;
- invalid numeric row, OHLC consistency failure, or negative volume under existing rules;
- confirmed placeholder or market-closed leakage into active evidence;
- documented provider artifact that makes the quote non-observational for the timestamp;
- explicit pre-registered market-structure exclusion defined before strategy results are known.

Extreme spread size, inconvenient tail behavior, holiday/reopening timing, warning-tier status alone, poor strategy performance, or improved strategy performance MUST NOT be sufficient exclusion grounds.

## 9. External Corroboration

Before warning-review active clusters can enter any baseline execution-cost model, a targeted external/source corroboration campaign SHOULD be completed.

Smallest defensible targeted campaign:

- cover all currently reviewed warning_review active rows with spread >= 2.0 where practicable, or at minimum the full 2024-12-11 cluster plus every other date containing warning_review active spread >= 2.0;
- include at least one independent market data source or broker feed with BID and ASK, not only mid/last price;
- compare timestamp alignment, BID, ASK, spread direction/magnitude, and whether widening appears around the same minute/hour/session window;
- include negative controls from strict-valid extreme dates and warning-control dates without >=2.0 rows.

Agreement handling:

- If the independent source materially agrees on cluster timing and spread widening, warning-review clusters MAY advance to a modelling-policy gate, but strict-only baseline comparisons remain mandatory.
- If the independent source disagrees, the affected warning-review rows MUST remain excluded from baseline modelling and MAY only appear in descriptive caveats or adverse sensitivity/stress views.
- If the independent source lacks matching coverage, the result is inconclusive, not confirmation.

External corroboration MUST NOT overwrite the raw evidence or reclassify existing rows unless a separate data-integrity artifact justifies that action under existing methodology.

## 10. Mandatory Future Reporting Treatments

Every future spread, cost, or strategy report using this evidence MUST include:

- counts by evidence class: strict-valid active, warning-review active, warning-review inconclusive, confirmed invalid/excluded, placeholder/market-closed;
- explicit statement of the primary/default population;
- separate strict-only baseline spread summary;
- separate warning-review descriptive or sensitivity summary if warning rows are discussed;
- stress-event cluster table with date, active rows, max spread, threshold counts, classification, and use allowed under this policy;
- list of excluded rows/dates with exclusion ground and artifact citation;
- external corroboration status: not attempted, agreeing, disagreeing, or inconclusive;
- statement that no strategy outcome was used to select or amend evidence treatment;
- policy version and any amendments applied before modelling.

## 11. Decision Matrix

| Evidence class / condition | Descriptive analysis | Baseline cost model | Sensitivity model | Stress model | Strategy headline result |
| --- | --- | --- | --- | --- | --- |
| `strict_valid` active rows | MUST include as primary/default | MUST be default population | MAY compare | MAY use | MUST be headline basis before later gates |
| warning_review reviewed/source-consistent active rows | MAY include, separately labelled | MUST NOT include before external corroboration and modelling gate | MAY include, separately labelled | SHOULD preserve if stress-relevant | MUST NOT be sole favorable basis; not headline before later gate |
| warning_review inconclusive active rows | MAY include, labelled inconclusive | MUST NOT include | MAY include only as adverse/diagnostic sensitivity | MAY include as adverse stress evidence | MUST NOT support headline result |
| confirmed artifact/invalid rows | MUST report if relevant | MUST NOT include | MUST NOT include except data-quality diagnostic | MUST NOT include as market evidence | MUST NOT include |
| active stress-event clusters | MUST report, not delete | STRICT-only only unless warning clusters pass later gate | SHOULD include separated warning-tier view | MUST preserve or explicitly stress | MUST disclose sensitivity to cluster treatment |
| placeholder/market-closed rows | MAY report as excluded/placeholder counts | MUST NOT include | MUST NOT include | MUST NOT include as observed spread | MUST NOT include |

## 12. Amendment and Versioning

This policy is versioned by date and artifact path. Amendments MUST be written to a new policy artifact or clearly marked version section before affected strategy results are inspected.

No-retrospective-policy rule: once a strategy modelling run has begun, this policy MUST NOT be amended for that run using knowledge of profitability, rankings, drawdowns, or trade-level outcomes. Later amendments MAY govern future runs only and MUST preserve an audit trail of the prior policy.

## 13. Unresolved Decisions

The following decisions remain open and MUST be resolved by future gates before warning-review evidence can become baseline execution-cost input:

- whether independent BID/ASK data confirms the December 2024 warning-review active clusters and smaller >=2.0 dates;
- whether warning-review rows with `INTERNAL_FLAT_ZERO_VOLUME` can be parameterized in a baseline execution-cost model without overstating or understating executable costs;
- what exact stress multipliers, duration assumptions, and session-transition treatments are appropriate after corroboration;
- whether any pre-registered market-structure filters are justified for rollover, holiday, or sparse-session periods.

## 14. Implementation Recommendations

- Implement evidence-class filters as named, auditable query predicates rather than ad hoc date lists.
- Default report builders SHOULD compute strict-only active statistics first, then warning-tier descriptive/sensitivity tables.
- Any future model input table SHOULD carry evidence class, placeholder flag, warning reasons, external corroboration status, policy version, and allowed-use field.
- Stress scenarios SHOULD keep source-consistent active clusters visible even when excluded from baseline cost modelling.
- Date exclusions SHOULD require an artifact citation field and SHOULD fail validation if the cited reason is absent.

## 15. Independent Adversarial Review and Responses

Criticism: The draft may cherry-pick strict-valid rows as the default while sidelining 285,726 warning-review active rows.
Response: The policy does not delete or ignore warning rows. It requires separately labelled descriptive, sensitivity, and stress treatment. Strict-valid default is justified because warning-review baseline modelling remains single-provider and policy-gated.

Criticism: Warning-review language could allow accidental pooling into headline spread results.
Response: The final policy explicitly prohibits pooling as the primary headline population and requires equal-prominence strict-only reporting if pooled diagnostics are shown.

Criticism: Stress-event clusters could be removed through innocent-sounding outlier, holiday, or rollover filters.
Response: The policy places the burden of proof on exclusion and prohibits blanket trimming unless supported by durable artifacts or pre-registered market-structure rules.

Criticism: The policy could use strategy outcomes circularly, admitting warning rows only when they help or excluding them when they hurt.
Response: The final policy states that strategy outcomes MUST NOT influence evidence treatment, ranking treatment, exclusions, or retrospective amendments.

Criticism: Inconclusive rows are vague and may become a loophole.
Response: The policy defines inconclusive rows, allows only labelled descriptive/adverse diagnostic use, and prohibits their use in baseline modelling and headline strategy conclusions.

Criticism: External corroboration requirements could become too broad to execute.
Response: The policy defines the smallest defensible campaign: all warning >=2.0 rows where practicable, or at minimum the full 2024-12-11 cluster plus every other >=2.0 warning date, with controls.

Criticism: The policy may be over-conservative by blocking warning-review baseline costs despite row-level source consistency.
Response: The policy permits descriptive, sensitivity, and stress use now; baseline inclusion is only delayed pending external corroboration because the top-date review itself classified modelling suitability as conditional.

Criticism: The policy may be under-conservative by allowing warning-review descriptive analysis.
Response: Descriptive use is allowed only for active/source-reconciled rows, with labelling, separation, and mandatory caveats. It does not authorize baseline modelling or favorable headline conclusions.

Material changes from adversarial review: yes. The final policy strengthened pooling prohibitions, exclusion burden, inconclusive-row limits, external corroboration scope, and no-retrospective amendment language.

## 16. Validation Statement

The policy was cross-checked against the named durable artifacts. Counts in Section 2 were verified from the relevant CSV reports and prose artifacts. No raw evidence was deleted, edited, reclassified, or regenerated. No methodology, schema, session definition, quality definition, execution-cost model, or strategy rule was changed. The policy can be applied before strategy profitability is known because it keys only on pre-existing evidence class, row activity/placeholder status, source consistency, external corroboration status, and pre-registered policy version.

## 17. Gate Decision

Gate outcome: READY_FOR_TARGETED_EXTERNAL_CORROBORATION.

Rationale: strict-valid active evidence is ready as the default descriptive and future baseline candidate population, but warning-review active clusters are not yet ready for baseline execution-cost modelling. The next research gate SHOULD run targeted independent BID/ASK corroboration for warning-review active spread clusters while preserving strict-valid and warning-review slices separately.
