# V2 Architecture B Implementation Critic Rereview

Date: 2026-08-14

## Findings

No blocking findings.

The prior direct-conformance blocker is repaired. Architecture B now rejects non-numeric, non-finite, and negative spread values inside `_architecture_b_row_is_eligible()` before horizon counting or percentile estimation. A row mislabeled as `strict_valid_pair` with spread `not-a-number`, `nan`, `inf`, `-inf`, or a negative numeric value cannot satisfy the 1000-row minimum and cannot enter the sorted p99.5 threshold population. Numeric zero remains eligible, which is consistent with the frozen contract excluding negative/invalid spreads rather than zero-valued valid spreads.

Synthetic/mechanical confirmation: 999 valid strict rows plus one strict-labeled forbidden spread returned `unavailable`, `estimate: None`, and per-horizon counts of 999. Adding forbidden rows to 1000 valid strict rows left the estimate at the valid-row threshold and kept counts at 1000. Replacing the forbidden row with spread `0.0` made the horizons eligible with counts of 1000.

I reassessed the original frozen contract points against `execution_cost_model.py` and `tests/test_execution_cost_model.py`. The implementation directly conforms on the exact 30/90/365 calendar-day horizons, left-closed/right-open `[T - h, T)` horizon intervals, row timestamp `< update_boundary_utc`, monthly UTC update boundary, timezone-explicit UTC caller requirement, independent per-horizon 1000-row minimum, unavailable-horizon skip diagnostics, all-horizons-unavailable status/`None` estimate, no carry-forward, no future backfill, V1 percentile semantics, full-precision threshold return, maximum aggregation across eligible horizons, and inclusive `observed_spread <= threshold` coverage convention.

Population-leakage checks are now adequate for the frozen primary boundary. Tests cover warning-review, excluded, calendar-only, placeholder, synthetic marker, descriptive-only role, non-numeric, non-finite, negative, and zero-spread cases. The implementation also reports `warning_review_rows_in_baseline: 0`, source artifact paths, policy version, update boundary, cadence, combination rule, coverage comparison, and horizon availability diagnostics.

I found no evidence in the reviewed implementation/tests that V1 was retuned, that Architecture B depends on empirical performance or outcome-dependent choices, that 2011-2014 is represented as pristine for V2, that partitions/specification were changed, or that protected final holdouts or 2015+ data were accessed. Remaining timestamp parsing uses the repository's existing naive UTC row-string schema while requiring timezone-explicit UTC update timestamps; this is an implementation convention already covered by synthetic boundary tests and is not a contract blocker.

## Scope And Verification

Reviewed governance/recovery artifacts, frozen Architecture B JSON/Markdown and spec critic, campaign checkpoint JSON/Markdown, `execution_cost_model.py`, and `tests/test_execution_cost_model.py`.

Did not inspect raw CSV/history/outcome/performance/holdout files, acquire data, calculate empirical candidate performance, change specifications or partitions, or perform strategy research.

Mechanical tests run:

- `python3 -m unittest tests.test_execution_cost_model` - 26 passed.
- Direct synthetic Architecture B probe for forbidden strict-labeled spreads and valid zero handling - passed.
- `python3 -m unittest discover -s tests` - 244 passed, 3 skipped.
- `git diff --check -- execution_cost_model.py tests/test_execution_cost_model.py reports/v2_architecture_b_implementation_critic.md` - passed.

## Verdict

`PASS_READY_FOR_DIRECTOR_PROTOCOL_DECISION`
