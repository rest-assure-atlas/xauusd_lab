# Independent Critic Review: Failure Diagnostics 2011-2014

Status: completed read-only

## Findings

- Diagnostics are internally consistent with the frozen clean validation artifact across all 48 monthly rows.
- Frozen contract is correctly stated and applied: active strict_valid_pair only, 30 calendar-day lookback, p99.5, minimum 1000 prior strict-valid rows, monthly boundary recalibration, no future backfill.
- Immediate binding cause for unavailable rows is correctly identified: every unavailable month has calibration rows below 1000, summing to 11990 unavailable rows.
- Calendar-window sparsity and monthly-boundary effects are evidenced by monthly diagnostics and block file, especially 2013-02, 2013-10/11, 2014-01/02/03/06.
- Source/reconciliation defects are correctly separated from mechanical availability failure: no missing-side rows, duplicate timestamps, negative spreads, or strict-baseline leakage.
- The one non-availability failure is correctly isolated as August 2011 threshold undercoverage: 3780 prior rows, threshold 0.604, realized coverage 0.726984, 1376 uncovered eligible rows.
- No prohibited work appeared: no 2015+ inspection, no 2023/2025 holdout access, no altered-parameter performance calculation, no replacement candidate, and no strategy research.

## Minor Caveat

- The block type calibration_dates_below_1000_daily_strict_rows is somewhat confusing because it is used as sparsity context, including 2011-08 where availability was not binding. This is not a diagnostic blocker because causal class and monthly totals remain correct.

## Diagnostic Gate

DIAGNOSTIC_ACCEPT_FOR_DIRECTOR_REVIEW_FAILED_CLEAN_VALIDATION_2011_2014
