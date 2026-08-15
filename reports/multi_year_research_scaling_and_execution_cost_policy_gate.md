# Multi-Year Research Scaling And Execution-Cost Policy Gate

Date: 2026-08-11
Status: final after independent critic amendments
Gate decision: READY_FOR_PARTITION_LOCK_AND_ACCESS_LOG_PREPARATION_ONLY

## Purpose

This design/policy gate decides how to preserve research validity before any multi-year XAUUSD data acquisition or strategy work. It responds to the current execution-cost gate:

`EXECUTION_COST_MODEL_NEEDS_POLICY_REVIEW`

No multi-year data was acquired. No strategy backtests, strategy discovery, ranking, optimization, profitability claims, raw evidence changes, schema changes, quality-rule changes, session-definition changes, or authoritative Windows repo changes were performed.

## Current Durable State

Execution-cost and corroboration facts preserved:

- 2024 is heavily used evidence: pipeline development, BID/ASK data-quality work, FXCM corroboration, execution-cost candidate development, and tail-rule hardening.
- 2024 must not be treated as a pristine strategy holdout.
- Original static Jan-Sep 2024 strict-only p95 execution-cost rule covered only 73.1404% of Q4 strict-valid rows.
- Candidate rolling 30-calendar-day monthly strict-only p99.5 rule achieved 96.0529% minimum monthly coverage and 98.7697% mean monthly coverage inside tested 2024 folds.
- The rolling p99.5 candidate used only strict-valid rows and no warning-review rows entered the baseline.
- No code-level future-data lookahead was found in the prospective timestamp function.
- The independent critic found Q4 holdout reuse / selection-leakage risk: the same 2024 evidence was used to diagnose and harden the rule.
- FXCM external corroboration remains partially supportive only: `CORROBORATION_PARTIALLY_SUPPORTIVE_MORE_REVIEW_REQUIRED`.
- Post-corroboration policy keeps active `strict_valid_pair` as the primary/default execution-cost baseline population and prohibits warning-review pooling into the primary baseline.

## Execution-Cost Candidate Freeze Decision

Decision: `FROZEN_WITH_SMALL_PREDECLARED_CLARIFICATIONS`

The rolling p99.5 rule is not accepted as fully validated. It is frozen as `execution_cost_tail_rule_v1_candidate` for clean multi-year validation. The point of freezing now is to stop further 2024 tuning and force the next evidence to be genuinely out-of-sample for this candidate.

Frozen fields:

- Population: active `strict_valid_pair` only.
- Warning-review baseline use: prohibited.
- Placeholder rows: prohibited.
- Percentile: p99.5 (`0.995`).
- Lookback: 30 calendar days.
- Recalibration cadence: monthly boundary.
- Minimum prior strict-valid observations: 1,000.
- Calibration information set: rows with timestamps earlier than the monthly calibration boundary only.
- Insufficient-history behavior: return unavailable/error; do not backfill with future rows.
- Session/time handling: not an input to the primary tail rule; session/regime summaries remain diagnostics only.
- Output: trailing strict-valid p99.5 spread threshold plus policy/version/provenance metadata.
- Policy version: `post_corroboration_execution_cost_evidence_policy:2026-08-10`.
- Candidate version: `execution_cost_tail_rule_v1_candidate`.

Clarifications:

- The candidate is calibrated on and shaped by 2024. It must be labelled 2024-developed.
- The 2024 Q4 result is no longer a clean holdout after tail-rule selection.
- Multi-year validation may pass or fail the candidate. Passing validation may support later mechanical strategy integration. Failing validation records `v1_candidate` as failed; it does not permit silent retuning.
- Any version 2 rule requires a new versioned policy/model artifact, preserved v1 results, and newly protected holdout partitions.

## Multi-Year Data Scope

Recommended ideal acquisition target: 2010-01-01 through 2025-12-31, subject to Dukascopy XAUUSD BID/ASK availability and bounded acquisition approval.

Minimum acceptable target: 2013-01-01 through 2025-12-31, plus the already consumed 2024 artifacts, if older availability or operational burden blocks a longer range.

Rationale:

- The intended program needs materially different regimes, not just more rows.
- A 2010-2025 ideal span gives pre-2024, post-2024, high-volatility, low-volatility, crisis, inflation/rate-cycle, and structural market-change candidates without relying on a single year.
- The existing filesystem and CSV/report pipeline is adequate in principle for annual or multi-year batches, provided acquisition is checkpointed and partitions are locked before use.
- Availability must be verified during a later acquisition mission; this gate does not assume every requested day will exist.

Approximate scale:

- One side, one-minute daily CSV: about 1,440 rows per day before provider gaps.
- BID+ASK over 16 years: about 16.8 million minute-side rows and about 8.4 million reconciled minute pairs before gaps/placeholders.
- CSV storage is expected to be order-of-gigabytes, not a database-scale problem, but logs/reports/checkpoints should be batched by year to stay manageable.

## Data Partition Architecture

Partitions must be assigned before acquisition outputs are inspected beyond technical completion and provenance checks.

| Partition | Years | Purpose | Can influence execution-cost v1? | Can influence strategy hypotheses? | Holdout status |
|---|---|---|---|---|---|
| A. Engineering / consumed development | 2024 | Already-used pipeline, corroboration, execution-cost development, tail hardening | Already used | No pristine use | Consumed |
| A2. Expansion shakedown | 2010 | First multi-year availability/provenance/pipeline scale check | Technical only | No | Not a strategy holdout |
| B. Execution-cost clean validation | 2011-2014 | Clean validation of frozen `execution_cost_tail_rule_v1_candidate` | Yes, validation only | No strategy discovery | Consumed after EC validation |
| C. Strategy hypothesis development | 2015-2019 | Later strategy family development after EC gate | No v1 tuning | Yes, after approval | Development |
| D. Strategy validation / walk-forward | 2020-2022 | Later walk-forward validation after strategy families are frozen | No v1 tuning | Validation only | Reserved until strategy phase |
| E. Final untouched holdout | 2023 and 2025 | Final evaluation after model, strategy families, and reporting rules are frozen | No v1 tuning | No development or validation | Untouched |

If 2025 is unavailable or incomplete, reserve fallback final holdout years in this order, provided they are complete and uncontaminated: 2023, 2022, 2021. Do not use a fallback silently; record the substitution, reason, and whether the strategy validation partition must be reassigned.

## Holdout Preservation Rules

- Do not compute descriptive spread summaries for B, D, or E before their approved release purpose.
- Do not open final holdout years for charts, exploratory statistics, candidate strategy evaluation, execution-cost retuning, or anomaly hunting.
- Technical acquisition checks may record file existence, byte size, checksums, row counts, schema validity, and terminal success/failure status without inspecting distributional content.
- Every reserved partition access must be recorded in a durable access log with timestamp, actor/tool, files touched, fields inspected, purpose, and whether the partition remains clean.
- Once a holdout is opened for its approved purpose, it is consumed for that purpose and must not later be described as untouched.
- If a policy/model change occurs after opening a holdout, establish a new untouched holdout before treating the changed model as externally validated.
- Summary statistics of final holdout years are prohibited before final release.
- Failed or inconclusive holdout results must be preserved; they cannot be discarded because they are inconvenient.

Recommended durable metadata before acquisition:

- `reports/multi_year_research_partition_plan.json`
- `reports/holdout_access_log_schema.json`
- `reports/holdout_access_log.csv`
- per-year acquisition checkpoints under `reports/`

Minimum access-log schema:

- `access_id`
- `timestamp_utc`
- `actor_or_tool`
- `partition_id`
- `year_or_range`
- `artifact_path`
- `access_purpose`
- `fields_or_operations_inspected`
- `distributional_content_inspected`
- `approved_gate_or_work_order`
- `partition_clean_before_access`
- `partition_clean_after_access`
- `consumption_status_after_access`
- `notes`

Technical-only metadata limits:

- For final holdout partitions, pre-release checks may record only annual requested-day counts, file-existence status, checksum presence/status, source identity status, terminal completion status, and coarse schema-validity status.
- Do not report per-day or per-month final-holdout row counts, placeholder counts, strict/warning counts, spread summaries, quality-reason distributions, missing-minute patterns, anomaly lists, charts, or descriptive statistics before final holdout release.
- If exact technical row counts must be generated internally by existing validation code, they must remain sealed technical logs for completion auditing and must not be surfaced to modelling or strategy researchers before release.
- For non-final reserved partitions, distributional inspection is still prohibited until the partition's approved purpose is released.

## Acquisition Order

Recommended approach: acquire all intended years in approved yearly batches, but lock partitions before distributional use.

Reasoning:

- Acquiring all intended years first reduces repeated infrastructure churn and lets provenance gaps be known early.
- Partition locks, access logs, and separate allowed-use rules prevent the presence of data on disk from becoming permission to inspect it.
- Yearly batches keep runtime, logs, and failure recovery bounded.

Required sequence per approved year:

1. Download BID daily CSVs.
2. Download ASK daily CSVs.
3. Generate BID and ASK data manifests.
4. Generate BID and ASK linked observation reports.
5. Reconcile BID/ASK pairs.
6. Record provenance, checksums, row counts, file status, quality status, and checkpoint status.
7. Generate spread characterization only for partitions whose purpose has been approved for distributional inspection.
8. Preserve raw files unchanged and keep provider data separate from external FXCM corroboration artifacts.

Do not introduce a database, distributed system, or new infrastructure unless yearly filesystem batches prove materially insufficient.

## Execution-Cost Validation Plan

Frozen candidate under test: `execution_cost_tail_rule_v1_candidate`.

Clean validation partition: 2011-2014.

Validation method:

- For each validation month, compute the p99.5 threshold from the prior 30 calendar days of active strict-valid rows only.
- Require at least 1,000 prior strict-valid observations.
- If insufficient history exists, mark the month unavailable rather than borrowing future rows.
- Compare validation strict-valid rows against the threshold.
- Report monthly coverage, annual coverage, minimum monthly coverage, calibration row counts, unavailable months, median threshold, maximum threshold, validation p95/p99/max, and regime/subperiod diagnostics.

Primary pass/fail criteria:

- Minimum monthly coverage across available clean validation months must be at least 90%.
- Annual coverage for each validation year must be at least 95%.
- No systematic undercoverage may persist for two consecutive validation months without being treated as a failure/caveat.
- No warning-review rows or placeholders may enter calibration or validation baseline populations.
- Full-year descriptive statistics may not be used as calibration input.

Failure handling:

- If the candidate fails, label `execution_cost_tail_rule_v1_candidate` failed or inconclusive.
- Do not tune p99.5, lookback, cadence, or fallback using the same validation years and still claim they are clean.
- Any v2 candidate must be designed under a new artifact with a new validation partition and a preserved account of v1 failure.

FXCM/external corroboration:

- Full FXCM-style corroboration is not required for every year before strict-only execution-cost validation.
- Targeted external corroboration may be required for new extreme anomalies, provider-specific concerns, or policy-changing warning-review/stress claims.
- FXCM DEMO/account-feed caveats remain; external corroboration cannot promote warning-review evidence into the primary baseline without a separate policy gate.

Targeted external corroboration triggers:

- Any proposed change to warning-review baseline eligibility.
- Any new strict-valid spread extreme above the previous 2024 strict-valid maximum or above a predeclared multi-year p99.9 threshold, whichever is lower after the threshold is frozen.
- Any contiguous stress cluster that would materially change the selected execution-cost tail rule or stress scenario.
- Any provider-specific anomaly that would otherwise cause exclusion of active strict-valid evidence.
- Any inconclusive or contradictory provider behavior that would be used to support a policy change.

## Strategy Research Readiness

Serious strategy discovery must not begin until all of the following are true:

- Multi-year BID/ASK acquisition is complete enough for the approved partitions.
- Provenance, checksums, source identity, quality status, and reconciliation reports are complete for the years to be used.
- The frozen execution-cost candidate has passed clean validation or a new policy explicitly handles failure.
- Partition locks and access logs are active.
- Strategy-development, walk-forward, and final holdout years are reserved and not pre-inspected for strategy signal content.
- Backtest infrastructure can apply spread-only baseline costs, stress/sensitivity labels, missing-cost disclosures, and policy metadata without warning-review baseline leakage.
- Stress/sensitivity treatment remains separate from strict-only baseline results.
- Reporting templates require strict-only baseline, stress/sensitivity, missing-cost components, holdout status, and no-retrospective-optimization statements.

Mechanical strategy integration test:

- A dummy/reference strategy may later be used only to verify plumbing, metadata propagation, and cost application.
- It must not consume final holdout evidence.
- It must not be optimized, ranked, or reported as a trading result.

Serious strategy discovery:

- Requires a separate explicit approval after the multi-year acquisition, partition locks, and execution-cost validation gate.
- Requires a frozen strategy protocol gate before any non-plumbing strategy code runs. That protocol must include a strategy-family registry, parameter bounds, development/validation split, walk-forward rules, failure-reporting requirements, final-holdout release criteria, and cost/stress reporting rules.

## Future Strategy Research Design

Future strategy research should use hypothesis families, not blind parameter mining.

Permitted future families to consider after approval:

- trend/momentum;
- mean reversion;
- breakout;
- session/time effects;
- volatility/regime behavior;
- event-related behavior;
- microstructure effects.

Principles:

- Predeclare hypothesis family, development partition, walk-forward design, parameter search bounds, cost treatment, and stop criteria.
- Keep strategy development separate from validation and final holdout partitions.
- Prefer parameter stability and robustness over single best backtest.
- Report failed families and adverse costs.
- Use independent criticism before final holdout release.
- Never change evidence/model policy because strategy results improve or worsen.

## Operational Readiness

The existing simple filesystem plus Python scripts approach appears adequate for the proposed scale if run in yearly batches with checkpoints.

Expected needs:

- BID and ASK raw daily CSVs by year.
- Per-side manifests and linked reports by year.
- BID/ASK reconciliation by year.
- Spread characterization and execution-cost validation reports only for partitions released for those purposes.
- Checkpoint/resume files for long acquisition and reconciliation batches.
- Full unittest suite and year-level artifact validation after pipeline changes.

Do not add databases, distributed runners, or complex infrastructure unless an actual acquisition/reconciliation dry run shows the current approach is materially insufficient.

## Unresolved Decisions

- Exact ideal start year depends on verified Dukascopy XAUUSD BID/ASK availability.
- Final holdout substitution rule must be applied if 2025 is unavailable or incomplete.
- Whether `execution_cost_tail_rule_v1_candidate` can be accepted after 2011-2014 clean validation remains unresolved.
- Whether targeted FXCM/external corroboration should be repeated for new multi-year anomalies depends on what validation finds.

## Independent Critic Findings

Critic materially changed the gate: yes.

Material findings:

- The pre-critic acquisition gate was too strong without concrete partition locks and access-log enforcement.
- Final holdouts are vulnerable to contamination from overly detailed acquisition checks, especially per-day/per-month row counts and quality summaries.
- Freezing the 2024-developed p99.5 candidate is defensible only as damage control to stop further 2024 tuning, not as evidence the rule is correct.
- The 2011-2014 execution-cost validation partition is defensible only if validation code/report templates are frozen before inspecting those distributions.
- Final holdouts 2023 and 2025 are useful but fragile; fallback years must be named before acquisition.
- Strategy readiness needed a separate protocol gate before any serious strategy discovery.

Responses:

- Final gate narrowed to `READY_FOR_PARTITION_LOCK_AND_ACCESS_LOG_PREPARATION_ONLY`.
- Multi-year acquisition is not authorized by this gate.
- Access-log schema and technical-only metadata limits were made explicit.
- Fallback final holdout years were predeclared.
- External corroboration trigger thresholds were made explicit.
- Strategy protocol gate requirement was added.

## Gate Decision

Pre-critic gate: `READY_FOR_BOUNDED_MULTIYEAR_ACQUISITION_WITH_LOCKED_PARTITIONS`

Final gate: `READY_FOR_PARTITION_LOCK_AND_ACCESS_LOG_PREPARATION_ONLY`

The plan supports only a preparation mission to create/enforce partition locks, access-log files, technical-only metadata rules, checkpoint naming, and acquisition refusal guards. It does not approve multi-year data acquisition, strategy discovery, strategy backtesting, optimization, profitability research, or holdout inspection.

Exact next approval required: approve partition-lock and access-log implementation/preparation. After that, a separate approval is required before any multi-year acquisition.
