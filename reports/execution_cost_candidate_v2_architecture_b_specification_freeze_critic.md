# Independent Critic Review: Execution-Cost Candidate V2 Architecture B Specification Freeze

Date: 2026-08-13

## Scope

Read-only independent critic review of:

- `reports/execution_cost_candidate_v2_architecture_b_specification_freeze.json`
- `reports/execution_cost_candidate_v2_architecture_b_specification_freeze.md`
- `execution_cost_model.py`
- `tests/test_execution_cost_model.py`

This review did not inspect raw data, outcome files, strategy results, 2023 data, 2025 data, or any protected final holdout. No tests, backtests, strategy research, acquisition, implementation work, performance calculations, partition changes, or outcome-dependent comparisons were run. The only file modified by this critic was this review artifact.

## Verdict

No blocking defects found.

The specification-freeze artifacts now contain a complete Director-provided Architecture B contract. The contract resolves the prior methodological degrees of freedom explicitly rather than leaving them to implementer discretion, and it preserves the required evidence boundaries.

The frozen artifacts' `pending_later_independent_critic` / “subject to later independent critic review” text records their status at the moment of specification freeze. This completed dedicated critic artifact supersedes that temporal marker; it is not a contract ambiguity and does not require modifying the frozen specification.

## Verified Contract Constants

The following freeze constants are explicit and internally consistent across the JSON and Markdown artifacts:

- Candidate family: `execution_cost_candidate_v2`
- Architecture: `B_multi_horizon_strict_tail_maximum`
- Horizons: exactly `30`, `90`, and `365` calendar days
- Horizon interval convention: left-closed/right-open `[T - horizon, T)`
- Primary population: active `strict_valid_pair` only
- Per-horizon minimum prior strict-valid count: `1000`
- Per-horizon tail percentile: `p99.5`, represented as fraction `0.995`
- Percentile semantics: sort ascending, `rank = q * (n - 1)`, linear interpolation between floor and ceil ranks
- Update cadence: monthly UTC update boundaries
- Combination rule: maximum numeric threshold among eligible horizons
- Unavailable horizon behavior: skip unavailable horizon and record diagnostic
- All-horizons-unavailable behavior: return unavailable/error
- Warmup behavior: unavailable until any horizon is eligible
- Carry-forward: prohibited
- Future backfill: prohibited
- Numeric precision: full precision, no operational rounding
- Application comparison convention: covered iff `observed_spread <= threshold`
- Final holdout status: `2023` and `2025` remain `FINAL_UNTOUCHED_HOLDOUT`
- Validation partition status: `2011_2014` is `BURNED_NOT_PRISTINE_FOR_V2`
- V1 status: `execution_cost_tail_rule_v1_candidate` remains retired from advancement, preserved as failed evidence, and was not changed or retuned by this review

## Verification Against Durable V1 Evidence

`execution_cost_model.py` supports the durable V1 mechanics used by the freeze:

- `percentile()` implements the stated sorted linear interpolation semantics with `position = fraction * (len(sorted_values) - 1)`.
- V1 tail constants are `TAIL_RULE_LOOKBACK_DAYS = 30`, `TAIL_RULE_PERCENTILE = 0.995`, and `TAIL_RULE_MINIMUM_OBSERVATIONS = 1000`.
- `prospective_tail_cost_for_timestamp()` uses the prior monthly boundary, strict rows between calibration start and calibration end, rejects insufficient history, and reports active strict-valid-only metadata.
- `validate_tail_hardening()` records the V1 selected rolling 30-day monthly p99.5 candidate and requires prior strict-valid evidence only.
- The model text records the V1 critic concerns: Q4 reuse, p99.5 overfitting risk, need to freeze parameters before future holdouts, and failed holdouts remaining recorded.

`tests/test_execution_cost_model.py` supports the same durable mechanics:

- `test_percentile_is_deterministic_linear_interpolation` verifies linear interpolation.
- strict-baseline tests reject warning-review and placeholder leakage.
- `test_prospective_tail_cost_uses_only_prior_month_boundary_rows` verifies that a row at the calibration boundary is excluded from the prior-month estimate.
- `test_prospective_tail_cost_rejects_insufficient_history` verifies unavailable/error behavior for inadequate prior strict-valid observations.
- tail-hardening gate tests verify warning-review leakage rejection and the clean-input gate path.

Architecture B extends V1 by Director contract to multiple horizons and maximum aggregation. I found no evidence in the reviewed artifacts that the new `90`/`365` horizons or max rule were chosen by new outcome comparisons in this freeze artifact; they are presented as frozen Director constants.

## Methodology Degrees Of Freedom

No unresolved methodology degrees of freedom remain in the freeze artifacts for the specification/design phase. Horizon set, population, interval convention, minimum counts, percentile, percentile semantics, update cadence, availability handling, aggregation, warmup, carry-forward, future backfill, precision, comparison convention, partition status, and holdout prohibitions are all explicitly frozen.

## Boundary And Attestation Review

The artifacts explicitly attest that:

- no 2015+ data was acquired or inspected;
- no 2023/2025 final holdout access occurred;
- no candidate performance was calculated;
- no backtests were run;
- no historical outcome optimization or strategy research occurred;
- no alternative parameter values were compared on 2011-2014;
- V1 remains retired and unchanged; no V1 retuning occurred;
- partitions remain unchanged from the accepted Architecture B proposal;
- 2011-2014 is burned/not pristine for V2.

I found no contradiction to those attestations within the reviewed files.

## Findings

No blocking findings.

Non-blocking implementation caution: future implementation must preserve the exact Director contract and should not reinterpret the max aggregation, UTC monthly boundaries, per-horizon diagnostics, or full-precision threshold output as tunable engineering details.

## Recommended Gate

`READY_TO_FREEZE_V2_ARCHITECTURE_B_CONTRACT`
