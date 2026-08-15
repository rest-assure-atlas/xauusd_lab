# Full-Year 2024 ASK Warning Review

Date: 2026-08-09

Scope: review only. No data was acquired, no raw BID or ASK files were modified, and no methodology, schemas, quality rules, session definitions, classifications, BID/ASK reconciliation, or spread characterization were changed.

Authoritative source artifacts reviewed:

- `reports/linked_observation_report_ASK_2024-01-01_to_2024-12-31.csv`
- `reports/data_manifest_ASK_2024-01-01_to_2024-12-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-12-31.csv`
- `docs/ASK_FULL_YEAR_2024_CAMPAIGN.md`

## Summary

- warning_review dates: 209
- distinct warning codes: `INTERNAL_FLAT_ZERO_VOLUME` = 209
- multi-warning dates: 0
- expected/structural: 190 dates. These warning dates have diagnostic runs entirely outside the configured Tokyo, London, and New York session windows. All retain the existing `warning_review` classification and `INTERNAL_FLAT_ZERO_VOLUME` reason.
- usable-with-caution: 209 dates. All warning-review dates are usable only under the existing warning-treatment limits: separately labelled warning-review descriptive or sensitivity analysis, not pooled with `strict_valid` primary/headline results.
- potentially data-quality-threatening: 19 dates. These have at least one diagnostic run overlapping a configured session window and therefore require explicit caution in downstream descriptive use. This does not reclassify the dates and does not prove any field is invalid or harmless.
- reconciliation-blocking dates: 0. No warning-review date had missing linked/raw provenance, checksum mismatch, duplicate timestamp, invalid timestamp, internal gap, missing minute, invalid numeric row, OHLC consistency failure, negative volume, or `excluded_unusable` classification in the reviewed full-year ASK artifacts.
- INTERNAL_FLAT_ZERO_VOLUME summary: 250 diagnostic runs across the same 209 warning-review dates; 178 dates had one run, 24 had two runs, 5 had three runs, 1 had four runs, and 1 had five runs.
- other anomalies: none found in the reviewed warning-review population beyond the preserved `INTERNAL_FLAT_ZERO_VOLUME` warning and its diagnostic session-overlap context. Manifest structural defect counters were zero for all 209 warning-review rows.
- validation: focused existing unit suite passed, 112 tests OK. Linked/raw source verification checked 313 non-calendar-only rows, including all 209 warning-review rows, with 0 file-size or SHA-256 mismatches.
- conclusion: safe-for-reconciliation, with warning findings preserved and carried forward as side-level warning context.
- recommended next step: run one bounded full-year BID/ASK reconciliation using the explicit full-year BID and ASK linked reports, preserving all side warning reasons in the reconciliation artifact.

## Warning Codes

| warning code | warning-review dates |
| --- | ---: |
| `INTERNAL_FLAT_ZERO_VOLUME` | 209 |

All 209 warning-review rows have exactly one warning code: `INTERNAL_FLAT_ZERO_VOLUME`.

## Diagnostic Context

The full-year diagnostic artifact contains 250 `INTERNAL_FLAT_ZERO_VOLUME` runs across the 209 ASK warning-review dates.

Run-count distribution by date:

| diagnostic runs on date | dates |
| ---: | ---: |
| 1 | 178 |
| 2 | 24 |
| 3 | 5 |
| 4 | 1 |
| 5 | 1 |

Session-overlap split:

| category | dates | reason |
| --- | ---: | --- |
| expected/structural context | 190 | all diagnostic run rows were outside configured sessions |
| cautionary session-overlap context | 19 | at least one diagnostic run overlapped Tokyo, London, or New York configured session windows |

Cautionary session-overlap dates:

- 2024-01-15
- 2024-02-06
- 2024-02-09
- 2024-02-14
- 2024-02-19
- 2024-02-23
- 2024-02-27
- 2024-02-29
- 2024-03-06
- 2024-03-08
- 2024-03-11
- 2024-03-14
- 2024-05-13
- 2024-05-27
- 2024-06-19
- 2024-07-04
- 2024-09-02
- 2024-11-28
- 2024-12-12

Warning-review dates with fewer than 1,440 active rows in the manifest:

- 2024-02-09: active rows 1320, internal inactive rows 1
- 2024-02-18: active rows 60, internal inactive rows 12
- 2024-02-23: active rows 1320, internal inactive rows 1
- 2024-03-08: active rows 1320, internal inactive rows 1
- 2024-03-11: active rows 1439, internal inactive rows 61
- 2024-10-09: active rows 1385, internal inactive rows 60
- 2024-10-10: active rows 1429, internal inactive rows 60
- 2024-12-11: active rows 1439, internal inactive rows 62
- 2024-12-12: active rows 1437, internal inactive rows 68

These rows preserve the existing manifest and linked-observation classifications. No field-level eligibility, harmlessness, or invalidity conclusion is made here.

## Structural Checks

For all 209 warning-review rows:

- `manifest_quality_reasons` = `INTERNAL_FLAT_ZERO_VOLUME`
- `manifest_file_status` = `processed`
- `quality_tier` = `warning_review`
- `total_row_count` = 1440
- `missing_minute_count` = 0
- `internal_gap_count` = 0
- `maximum_internal_gap_minutes` = 0
- `duplicate_timestamp_count` = 0
- `invalid_timestamp_count` = 0
- `invalid_numeric_row_count` = 0
- `ohlc_consistency_failure_count` = 0
- `negative_volume_count` = 0

Full-year linked-observation quality population remained:

- `strict_valid`: 104
- `warning_review`: 209
- `calendar_only`: 53
- `excluded_unusable`: 0

## Warning-Review Dates

- 2024-01-02, 2024-01-03, 2024-01-04, 2024-01-08, 2024-01-09, 2024-01-10, 2024-01-11, 2024-01-15, 2024-01-16, 2024-01-17, 2024-01-18, 2024-01-22
- 2024-01-23, 2024-01-24, 2024-01-25, 2024-01-29, 2024-01-30, 2024-01-31, 2024-02-01, 2024-02-05, 2024-02-06, 2024-02-07, 2024-02-08, 2024-02-09
- 2024-02-12, 2024-02-13, 2024-02-14, 2024-02-15, 2024-02-18, 2024-02-19, 2024-02-20, 2024-02-21, 2024-02-22, 2024-02-23, 2024-02-26, 2024-02-27
- 2024-02-28, 2024-02-29, 2024-03-04, 2024-03-05, 2024-03-06, 2024-03-07, 2024-03-08, 2024-03-11, 2024-03-12, 2024-03-13, 2024-03-14, 2024-03-18
- 2024-03-19, 2024-03-20, 2024-03-21, 2024-03-25, 2024-03-26, 2024-03-27, 2024-04-01, 2024-04-02, 2024-04-03, 2024-04-04, 2024-04-08, 2024-04-09
- 2024-04-10, 2024-04-11, 2024-04-15, 2024-04-16, 2024-04-17, 2024-04-18, 2024-04-22, 2024-04-23, 2024-04-24, 2024-04-25, 2024-04-29, 2024-04-30
- 2024-05-01, 2024-05-02, 2024-05-06, 2024-05-07, 2024-05-08, 2024-05-09, 2024-05-13, 2024-05-14, 2024-05-15, 2024-05-16, 2024-05-20, 2024-05-21
- 2024-05-22, 2024-05-23, 2024-05-27, 2024-05-28, 2024-05-29, 2024-05-30, 2024-06-03, 2024-06-04, 2024-06-05, 2024-06-06, 2024-06-10, 2024-06-11
- 2024-06-12, 2024-06-13, 2024-06-17, 2024-06-18, 2024-06-19, 2024-06-20, 2024-06-24, 2024-06-25, 2024-06-26, 2024-06-27, 2024-07-01, 2024-07-02
- 2024-07-03, 2024-07-04, 2024-07-08, 2024-07-09, 2024-07-10, 2024-07-11, 2024-07-15, 2024-07-16, 2024-07-17, 2024-07-18, 2024-07-22, 2024-07-23
- 2024-07-24, 2024-07-25, 2024-07-29, 2024-07-30, 2024-07-31, 2024-08-01, 2024-08-05, 2024-08-06, 2024-08-07, 2024-08-08, 2024-08-12, 2024-08-13
- 2024-08-14, 2024-08-15, 2024-08-19, 2024-08-20, 2024-08-21, 2024-08-22, 2024-08-26, 2024-08-27, 2024-08-28, 2024-08-29, 2024-09-02, 2024-09-03
- 2024-09-04, 2024-09-05, 2024-09-09, 2024-09-10, 2024-09-11, 2024-09-12, 2024-09-16, 2024-09-17, 2024-09-18, 2024-09-19, 2024-09-23, 2024-09-24
- 2024-09-25, 2024-09-26, 2024-09-30, 2024-10-01, 2024-10-02, 2024-10-03, 2024-10-07, 2024-10-08, 2024-10-09, 2024-10-10, 2024-10-14, 2024-10-15
- 2024-10-16, 2024-10-17, 2024-10-21, 2024-10-22, 2024-10-23, 2024-10-24, 2024-10-28, 2024-10-29, 2024-10-30, 2024-10-31, 2024-11-04, 2024-11-05
- 2024-11-06, 2024-11-07, 2024-11-11, 2024-11-12, 2024-11-13, 2024-11-14, 2024-11-18, 2024-11-19, 2024-11-20, 2024-11-21, 2024-11-25, 2024-11-26
- 2024-11-27, 2024-11-28, 2024-12-02, 2024-12-03, 2024-12-04, 2024-12-05, 2024-12-09, 2024-12-10, 2024-12-11, 2024-12-12, 2024-12-16, 2024-12-17
- 2024-12-18, 2024-12-19, 2024-12-23, 2024-12-26, 2024-12-30

## Commands Run

```bash
python3 - <<'PY'
# CSV review of linked warning rows, manifest warning reasons/structural counters,
# diagnostic run distribution, session overlap, and linked/raw checksum matching.
PY
```

```bash
PYTHONPATH=tests:. python3 -m unittest tests.test_source_contracts tests.test_data_manifest tests.test_session_report tests.test_linked_observation_report tests.test_historical_baseline_report tests.test_internal_flat_zero_volume_diagnostic
```

Validation result: 112 tests passed.
