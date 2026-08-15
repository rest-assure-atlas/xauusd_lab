# Execution-Cost Candidate v2 Architecture Proposal

Date: 2026-08-12

## Scope

Design phase only. This proposal uses existing 2024 development evidence and now-burned 2011-2014 validation/diagnostic evidence to identify requirements for a successor to `execution_cost_tail_rule_v1_candidate`.

No candidate performance was calculated. No parameter optimization, backtest, strategy research, 2015+ acquisition or inspection, or 2023/2025 final-holdout access was performed.

`execution_cost_tail_rule_v1_candidate` is retired from advancement. It should remain preserved as a failed, rejected candidate with durable evidence, not silently modified.

## Evidence Lessons

The v2 design must address two demonstrated v1 weaknesses:

1. Availability failure: a fixed 30-calendar-day strict-valid lookback with a 1000-row minimum can return unavailable when recent strict-valid history is sparse. The 2011-2014 failure diagnostics attributed all 11990 unavailable strict-valid rows to this mechanism.
2. Coverage instability: monthly calibration can lag a material spread-regime or tail expansion after the boundary. The clearest case is 2011-08, where the frozen threshold was 0.604, realized coverage was 0.726984, and 1376 eligible rows were uncovered; 2013-04 was a weaker secondary warning month with 0.944746 coverage.

2011-2014 have now contributed validation and diagnostic evidence and must not later be represented as pristine untouched validation for any replacement candidate whose design is informed by these findings.

## Design Requirements

- Primary population remains active `strict_valid_pair` only.
- Warning-review, placeholder, calendar-only, excluded, or synthetic rows must not enter the primary baseline.
- The cost estimate must be prospective: only rows timestamped before the applicable decision/calibration time may affect a threshold.
- Sparse recent history must not silently produce either future leakage or hidden fallback to non-strict data.
- Regime response must be auditable and deterministic.
- All tunable constants must be frozen before any clean v2 testing.
- Any final design must explicitly record unavailable behavior, fallback behavior, and stress/descriptive populations separately.

## Architecture A: Expanding Strict History With Recent Tail Guard

### Threshold Estimate

Estimate a strict-only high-tail empirical threshold from all prior active `strict_valid_pair` rows available before the update boundary, subject to a recency guard that prevents the threshold from dropping below a recent strict-only tail summary when recent history exists.

### Update Cadence

Periodic boundary update, with an optional more frequent deterministic interim update if a predeclared recent-tail guard is triggered.

### Sparse-History Handling

Use expanding prior strict-valid history rather than a fixed 30-day window as the primary availability source. If total prior strict-valid history is below the frozen minimum, return unavailable. If recent strict-valid history is sparse, keep the expanding-history threshold available but mark the recent-history quality state.

### Regime/Tail Response

The recent-tail guard allows the estimate to respond when recent strict-valid spreads rise materially, while the expanding base prevents total unavailability caused by a sparse 30-day window.

### Allowed Prospective Data

Only active `strict_valid_pair` rows with timestamps earlier than the update boundary or deterministic guard evaluation time.

### Leakage Safeguards

No future rows. No warning-review baseline rows. No full-period descriptive statistics as inputs. Guard triggers must be computed only from data already available at the trigger time.

### Strengths

- Simple and interpretable.
- Directly addresses sparse-window unavailability.
- Less fragile than a pure short-window rule.
- Can still react to tail expansion through a deterministic guard.

### Failure Risks

- Expanding history can lag structural changes if the guard is too weak.
- A guard that is too sensitive could raise thresholds frequently after ordinary tail noise.
- Requires careful pre-freezing of trigger and update rules.

### Expected Implementation Complexity

Low to moderate.

### Parameters To Freeze Before Testing

Total-history minimum, tail percentile, update cadence, recent guard window definition, recent guard statistic, trigger condition, missing/sparse recent-history labels, and unavailable/error behavior.

### Structural Versus Tunable

Structural: strict-only expanding prior history; prospective-only updates; separate recent-tail guard; no non-strict baseline fallback.

Tunable: percentile, total-history minimum, update cadence, guard window, guard statistic, and guard trigger.

## Architecture B: Multi-Horizon Strict Tail Maximum

### Threshold Estimate

Compute strict-only tail estimates over multiple predeclared prior horizons and use the maximum eligible horizon estimate as the current threshold. Horizons are chosen as structural windows, not selected after viewing validation performance.

### Update Cadence

Regular calendar update with deterministic intraperiod refresh allowed only at frozen times, such as daily or weekly boundaries.

### Sparse-History Handling

Each horizon has its own minimum strict-valid count. Sparse horizons are skipped. If at least one longer horizon meets its frozen minimum, the candidate remains available. If no horizon meets the minimum, return unavailable.

### Regime/Tail Response

Shorter horizons can lift the threshold during recent spread/tail expansion. Longer horizons preserve availability and stabilize the estimate when recent data are sparse.

### Allowed Prospective Data

Only active `strict_valid_pair` rows before each update boundary.

### Leakage Safeguards

Horizon set, horizon eligibility minimums, update cadence, and aggregation rule must be frozen before testing. No horizon may be added, removed, or reweighted after seeing validation outcomes.

### Strengths

- Very auditable.
- Handles sparse short windows without silently using future data.
- Responds faster than a monthly single-window rule if shorter horizons update more often.
- The max aggregation is conservative and easy to explain.

### Failure Risks

- A long horizon can keep thresholds high after a temporary shock passes.
- A short horizon can dominate after a noisy burst if trigger/update rules are too reactive.
- Multiple horizons introduce more tunable constants than Architecture A.

### Expected Implementation Complexity

Moderate.

### Parameters To Freeze Before Testing

Horizon list, horizon-specific minimum counts, tail percentile, update cadence, aggregation rule, sparse-horizon skip behavior, and unavailable/error behavior.

### Structural Versus Tunable

Structural: predeclared multiple strict-only horizons; maximum eligible tail estimate; no non-strict fallback; prospective-only update.

Tunable: horizon lengths, minimum counts, percentile, update cadence, and treatment of tied/stale horizons.

## Architecture C: State-Labeled Strict Tail Rule

### Threshold Estimate

Maintain a strict-only baseline threshold plus a deterministic regime state label derived from prior strict-valid spread behavior. The returned threshold is selected from a small predeclared state table.

### Update Cadence

State is evaluated at fixed boundaries and may persist until the next boundary unless a predeclared emergency state trigger fires.

### Sparse-History Handling

Use a longer strict-only prior window or expanding strict-only prior history for baseline availability. If recent history is sparse, state classification can fall back to a declared `sparse_recent_history` state rather than failing silently.

### Regime/Tail Response

Designed to explicitly identify normal, elevated-tail, shock, and sparse-recent-history states. A state transition can raise the threshold or mark the estimate as cautious without evaluating strategy performance.

### Allowed Prospective Data

Only prior active `strict_valid_pair` rows and derived prior-only state features.

### Leakage Safeguards

State definitions, thresholds, persistence rules, and state-specific threshold rules must be frozen before testing. State labels must be reproducible from timestamped prior evidence only.

### Strengths

- Directly targets regime/tail expansion.
- Produces useful audit labels for later diagnostics.
- Can distinguish sparse data from elevated spread conditions.

### Failure Risks

- More complex and easier to overfit than A or B.
- State thresholds can become hidden tuning knobs.
- Requires stronger critic scrutiny before clean testing.

### Expected Implementation Complexity

Moderate to high.

### Parameters To Freeze Before Testing

State definitions, state-transition thresholds, persistence/reset rules, state-specific threshold percentiles or add-ons, baseline minimum counts, update cadence, and unavailable/error behavior.

### Structural Versus Tunable

Structural: deterministic prior-only state labels; strict-only baseline; explicit sparse/elevated/shock states; no non-strict fallback.

Tunable: state thresholds, persistence lengths, baseline/guard windows, percentiles, and state-specific threshold mapping.

## Recommendation For Director Consideration

Recommend Architecture B, `Multi-Horizon Strict Tail Maximum`, for Director consideration.

Rationale: it is simple enough to audit, directly addresses both demonstrated v1 weaknesses, and avoids the hidden complexity of state-labelled modelling. Longer horizons reduce sparse-window unavailability; shorter horizons provide a structural way to react to recent tail expansion; the maximum aggregation is conservative and deterministic. This recommendation is based on methodological fit to the observed failure mechanisms, not retrospective performance optimization.

Architecture A is the simplest fallback if Director prefers fewer moving parts. Architecture C should be reserved for later only if simple strict-only horizon mechanisms fail under clean testing, because it introduces more tuning risk.

No parameter values are selected here. Values must be frozen by a separate protocol before any clean v2 test.

## Clean Future Research-Partition Plan

Current evidence status:

- 2024: consumed development evidence.
- 2011-2014: burned validation and diagnostic evidence for v1; no longer pristine for any v2 informed by these findings.
- 2023 and 2025: preserve as `FINAL_UNTOUCHED_HOLDOUT` unless explicitly authorized otherwise.

Proposed v2 partition plan:

1. Design freeze package: use only 2024 plus burned 2011-2014 lessons to freeze one v2 architecture and all tunable constants. No performance selection on 2011-2014.
2. Development/calibration sandbox: after explicit release and acquisition approval, use Partition C years 2015-2019 for implementation plumbing, parameter pre-freeze checks, and non-final development. These years are not currently inspected or acquired by this mission.
3. Clean validation: after the v2 design is fully frozen, use Partition D years 2020-2022 as the next clean walk-forward validation block, released only by explicit protocol gate.
4. Final untouched holdout: keep 2023 and 2025 sealed as Partition E final evaluation only after a separate explicit final-release gate.
5. Evidence hygiene: if any future design decision is influenced by Partition C or D outcomes, those years must be marked consumed for that design generation and cannot be reused as pristine validation for a later candidate.

## Required Next Gate

Director review should decide whether to approve a v2 design-freeze protocol, not a test run. The next approved protocol should freeze the chosen architecture, tunable constants, implementation contract, partition releases, and critic requirements before any candidate performance calculation occurs.

## Independent Critic Review

The independent critic found no blocking defects and accepted the proposal for Director review.

Key caveats to carry into any later design-freeze protocol:

- Architecture A's optional deterministic interim update and guard trigger need especially tight freeze language, since they could become hidden tuning knobs.
- Architecture C's "reserve for later if simple mechanisms fail under clean testing" path must treat any such clean-testing evidence as consumed for that design generation.
- The critic did not inspect two extra JSON-listed source evidence files because the review was constrained to necessary source context.

Durable critic artifact: `reports/execution_cost_candidate_v2_architecture_proposal_critic.md`

DESIGN_PROPOSAL_ACCEPT_FOR_DIRECTOR_REVIEW_EXECUTION_COST_CANDIDATE_V2
