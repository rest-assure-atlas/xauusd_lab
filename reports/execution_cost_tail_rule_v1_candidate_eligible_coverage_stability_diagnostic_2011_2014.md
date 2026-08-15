# Eligible Coverage Stability Diagnostic: execution_cost_tail_rule_v1_candidate 2011-2014

## Scope

Bounded diagnostic only for the rejected frozen `execution_cost_tail_rule_v1_candidate`, using existing 2011-2014 validation artifacts and reconciled BID/ASK reports. No candidate change, tuning, repair, replacement, alternative-threshold performance calculation, 2015+ acquisition/inspection, 2023/2025 holdout access, or strategy research was performed.

Frozen contract: active `strict_valid_pair` only; 30 calendar-day lookback; p99.5; minimum 1000 prior strict-valid rows; monthly boundary recalibration; no future backfill.

## Main Finding

Interpretation: `BROADER_COVERAGE_STABILITY_WEAKNESS`.

2011-08 is the only eligible month that failed the frozen monthly coverage criterion (<0.90), but it is not the only weak month. 2013-04 also fell below 0.95 while still passing the frozen monthly criterion. Across available-threshold months, realized coverage often landed below the 0.995 point target, which shows coverage variability under the frozen monthly threshold mechanism.

## Weak Or Near-Failing Months

- 2011-08: coverage 0.726984, uncovered 1376, threshold 0.604000, status fail
- 2013-04: coverage 0.944746, uncovered 305, threshold 0.534905, status pass

## 2011-08 Episode

- Prior strict-valid observations at calibration: 3780
- Frozen threshold: 0.604000
- Eligible strict-valid rows: 5040
- Realized coverage: 0.726984
- Uncovered rows: 1376
- Distance from intended 0.995 coverage: -0.268016
- First uncovered observation: 2011-08-05 00:05:00 at spread 0.740000
- First cumulative drop below the 0.90 monthly pass level after 100 rows: 2011-08-12 18:57:00
- Miss blocks: 505 total, 207 contiguous clusters, 298 single-observation blocks

Calibration vs realized distribution:

- Calibration p95/p99/p99.5/max: 0.440000 / 0.564000 / 0.604000 / 0.954000
- August eligible p95/p99/p99.5/max: 0.814000 / 0.954000 / 0.974000 / 1.572000

Assessment: evidence supports a sustained August 2011 spread-tail expansion/level shift after calibration, with misses concentrated in contiguous active-period clusters rather than only ordinary isolated tail exceedances.

## Cross-Month Stability

- Eligible months examined: 40
- Months below 0.90 frozen monthly criterion: 1 (`2011-08`)
- Months below 0.95 weak-month marker: 2
- Months below 0.995 intended point coverage: 19
- No source/reconciliation defect was identified by this stability diagnostic; artifact row counts reconciled with the existing validation monthly CSV in all eligible months.

The evidence suggests calibration thresholds can lag realized spread-regime changes when the following month's distribution expands relative to the trailing 30-day calibration window. 2011-08 is the clearest instance and is severe enough to classify as broader stability weakness rather than a purely isolated ordinary exceedance episode. This does not imply any particular parameter or methodology change is approved or sufficient.

## Contamination Record

2011-2014 have now contributed validation and diagnostic evidence for this frozen rejected candidate and must not later be represented as pristine untouched validation for any replacement candidate whose design is informed by these findings.

## Durable Outputs

- `reports/execution_cost_tail_rule_v1_candidate_eligible_coverage_stability_diagnostic_2011_2014.json`
- `reports/execution_cost_tail_rule_v1_candidate_eligible_coverage_stability_diagnostic_2011_2014.md`
- `reports/execution_cost_tail_rule_v1_candidate_eligible_coverage_stability_diagnostic_2011_2014_monthly.csv`
- `reports/execution_cost_tail_rule_v1_candidate_eligible_coverage_stability_diagnostic_2011_08_blocks.csv`
- `reports/execution_cost_tail_rule_v1_candidate_eligible_coverage_stability_diagnostic_2011_2014_critic.md`

Gate: `ELIGIBLE_COVERAGE_STABILITY_DIAGNOSTIC_ACCEPT_FOR_DIRECTOR_REVIEW`
