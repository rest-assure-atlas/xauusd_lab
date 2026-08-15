# Clean Validation: execution_cost_tail_rule_v1_candidate on Partition B 2011-2014

## Scope

- Partition: B / EXECUTION_COST_CLEAN_VALIDATION years 2011-2014 only.
- Candidate: frozen `execution_cost_tail_rule_v1_candidate`.
- Validation sequence: continuous 2011-2014 Partition B history with monthly prospective calibration boundaries.
- Population: active `strict_valid_pair` only; warning-review, placeholder, calendar-only, and excluded rows are not primary baseline inputs.
- No methodology, threshold, schema, source artifact, partition, or candidate change was made.
- No 2015+ acquisition, strategy research, or final holdout access was performed.

## Frozen Candidate Contract

- population: `active strict_valid_pair only`
- lookback_days: `30`
- percentile: `0.995`
- minimum_prior_strict_valid_observations: `1000`
- recalibration_cadence: `monthly_boundary`
- insufficient_history_behavior: `return_unavailable_or_error_no_future_backfill`
- policy_version: `post_corroboration_execution_cost_evidence_policy:2026-08-10`

## Year Results

| Year | Strict rows | Eligible rows | Covered rows | Unavailable rows | Eligible coverage | Total strict coverage | Gate |
|---:|---:|---:|---:|---:|---:|---:|---|
| 2011 | 52260 | 50940 | 49080 | 1320 | 0.963486 | 0.939150 | fail |
| 2012 | 65450 | 65450 | 65038 | 0 | 0.993705 | 0.993705 | pass |
| 2013 | 28716 | 25356 | 24848 | 3360 | 0.979965 | 0.865302 | fail |
| 2014 | 41189 | 33879 | 33555 | 7310 | 0.990437 | 0.814659 | fail |

## Combined Result

- Combined strict-valid rows: 187615
- Combined eligible rows: 175625
- Combined covered rows: 172521
- Combined unavailable rows: 11990
- Combined eligible-row coverage: 0.982326
- Combined total strict-row coverage: 0.919548

## Evidence Separation

- 2011: strict_valid_pair=52260, warning_review_pair=395580, excluded=77760, strict leakage counters={}
- 2012: strict_valid_pair=65450, warning_review_pair=386710, excluded=74880, strict leakage counters={}
- 2013: strict_valid_pair=28716, warning_review_pair=419124, excluded=77760, strict leakage counters={}
- 2014: strict_valid_pair=41189, warning_review_pair=406651, excluded=77760, strict leakage counters={}

## Provenance And Assumptions

- Durable Phase-1 summary/checkpoint marked 2011-2014 acquisition and reconciliation gates as pass before this mission.
- BID/ASK manifests, linked reports, and annual reconciliation CSVs are the source artifacts for each year.
- Monthly estimates use only strict-valid rows earlier than the monthly calibration boundary and inside the trailing 30 calendar days.
- Months with fewer than 1000 prior strict-valid observations are unavailable, per frozen contract, not backfilled.
- 2023 and 2025 remain final untouched holdouts in the partition lock; holdout access log contains no inspection rows.
- The initial reset-by-year run is preserved as superseded negative evidence; this report uses the continuous Partition B prospective sequence.

## Gate Reasons

- 2011: annual total strict-row coverage 0.939150401836969 below required 0.95
- 2011: 1320 strict-valid rows unavailable because monthly calibration had fewer than 1000 prior strict-valid rows
- 2011: months below 0.9: ['2011-08']
- 2013: annual total strict-row coverage 0.865301574035381 below required 0.95
- 2013: 3360 strict-valid rows unavailable because monthly calibration had fewer than 1000 prior strict-valid rows
- 2014: annual total strict-row coverage 0.8146592536842361 below required 0.95
- 2014: 7310 strict-valid rows unavailable because monthly calibration had fewer than 1000 prior strict-valid rows
- combined total strict-row coverage 0.9195480105535272 below required 0.95

## Final Validation Gate

FAILED_CLEAN_EXECUTION_COST_VALIDATION_2011_2014
