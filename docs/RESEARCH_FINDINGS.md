# Research Findings

This document records completed research findings that are useful to preserve
without turning `CURRENT_STATE.md` into an analysis notebook.

## Evidence Standard

Findings recorded here must identify their source reports, question, treatment
contract, population, reconciliation evidence, and limits. Generated reports and
raw data remain separate evidence. A finding entry does not change source code,
schemas, filtering, classifications, configuration, dependencies, raw data, or
generated reports.

## Status Vocabulary

- `descriptive finding`: a bounded description of existing evidence.
- `negative finding`: a bounded result that did not support the stated
  descriptive expectation.
- `inconclusive finding`: a bounded question that could not be answered from the
  available evidence.
- `superseded finding`: an older finding replaced by later approved evidence or
  treatment rules.

## 2026-07-26 - January-March 2024 Daily-Range Distribution

Status: `descriptive finding`

### Question

For each validated month from January through March 2024, what is the
descriptive distribution of daily range for `strict_valid` linked observations,
with `warning_review` daily range reported separately as a labelled sensitivity
view and `calendar_only`/`excluded_unusable` reported only as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1 minute
- Calendar period: January-March 2024
- Primary source: provenance-linked daily observation reports
- Treatment contract: `warning_treatment_v1`

This is not a universal XAU/USD record.

### Source Reports

Primary row-level source reports:

- `reports/linked_observation_report_2024-01-01_to_2024-01-31.csv`
- `reports/linked_observation_report_2024-02-01_to_2024-02-29.csv`
- `reports/linked_observation_report_2024-03-01_to_2024-03-31.csv`

Reconciliation reports:

- `reports/historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv`
- `reports/historical_baseline_linked_observation_report_2024-02-01_to_2024-02-29.csv`
- `reports/historical_baseline_linked_observation_report_2024-03-01_to_2024-03-31.csv`

Warning context reports:

- `reports/data_manifest_2024-01-01_to_2024-01-31.csv`
- `reports/data_manifest_2024-02-01_to_2024-02-29.csv`
- `reports/data_manifest_2024-03-01_to_2024-03-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-02-01_to_2024-02-29.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-03-01_to_2024-03-31.csv`

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |

Unavailable daily-range values occurred only for `calendar_only` observations
and remained unavailable rather than being converted to zero.

### Primary Strict-Valid Result

Primary descriptive result under `warning_treatment_v1`:

| Month | Count | Min | Median | Mean | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 9 | 2.370 | 7.199 | 13.440 | 39.583 |
| February | 5 | 2.227 | 3.514 | 11.788 | 29.910 |
| March | 9 | 3.710 | 12.420 | 19.669 | 49.300 |

### Warning-Review Sensitivity

`warning-review sensitivity`:

| Month | Count | Min | Median | Mean | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 18 | 12.830 | 19.627 | 22.218 | 35.320 |
| February | 20 | 6.310 | 15.765 | 17.875 | 42.860 |
| March | 16 | 14.230 | 26.350 | 30.299 | 73.400 |

### Warning Context

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows |
| --- | --- | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 |

The diagnostic run counts and run rows are warning context only. They are not
additional daily-range statistics.

### Reconciliation

- The statistics were independently calculated from linked observation rows.
- All six monthly population summaries matched their corresponding
  historical-baseline rows.
- Warning-reason baseline rows also matched.
- No provenance or schema incompatibility was found.
- During the preceding read-only analysis execution, no repository files were
  modified.

Raw files were not revalidated during this specific analysis. Earlier pipeline
validations remain separate evidence.

### Descriptive Conclusion

The warning-review sensitivity median and mean were higher than the strict-valid
median and mean in each of the three validated months. Therefore, the bounded
daily-range description is visibly sensitive to quality-tier treatment, and the
two populations must remain separately labelled.

This does not establish that `INTERNAL_FLAT_ZERO_VOLUME` caused the difference,
that warning-review observations are invalid, that warning-review observations
are equivalent to strict-valid observations, that either group represents normal
or universal XAU/USD behaviour, statistical significance, prediction, support or
resistance, a setup or signal, trading edge, profitability, or execution
realism.

### Unresolved Questions

- The cause and practical meaning of `INTERNAL_FLAT_ZERO_VOLUME` remain
  unresolved.
- Strict-valid sample counts were small, especially February with 5
  observations.
- No next research task has been selected from this finding alone.

## 2026-07-26 - January-March 2024 Daily-Extrema UTC Hours

Status: `descriptive finding`

### Question

For each validated month from January through March 2024, at which UTC clock
hours did the recorded daily high and daily low occur for `strict_valid` linked
observations, with `warning_review` reported separately as a labelled
sensitivity view and `calendar_only`/`excluded_unusable` retained as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1 minute
- Timezone: UTC
- Calendar period: January-March 2024
- Primary source: provenance-linked daily observation reports
- Treatment contract: `warning_treatment_v1`

This is not a universal XAU/USD market record.

### Source Reports

Primary row-level source reports:

- `reports/linked_observation_report_2024-01-01_to_2024-01-31.csv`
- `reports/linked_observation_report_2024-02-01_to_2024-02-29.csv`
- `reports/linked_observation_report_2024-03-01_to_2024-03-31.csv`

Warning context reports:

- `reports/data_manifest_2024-01-01_to_2024-01-31.csv`
- `reports/data_manifest_2024-02-01_to_2024-02-29.csv`
- `reports/data_manifest_2024-03-01_to_2024-03-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-02-01_to_2024-02-29.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-03-01_to_2024-03-31.csv`

### Timing-Field Semantics

- Daily high field: `time_of_daily_high_utc`
- Daily low field: `time_of_daily_low_utc`
- Format: `HH:MM:SS`
- Timestamps are UTC one-minute candle opening times.
- Edge flat zero-volume placeholders are removed before extrema selection.
- Current implementation records the first active-candle occurrence when equal
  extrema repeat.
- Dedicated `session_report.py` regression tests now cover equal daily-high and
  equal daily-low ties after edge flat zero-volume placeholders are removed.

The timestamp fields record one occurrence. They do not represent all equal
daily-high or daily-low occurrences.

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |

All `strict_valid` and `warning_review` rows had available daily-high and
daily-low timestamps. Timing values were unavailable only for `calendar_only`
rows and remained unavailable rather than being interpreted as hour `00`.

### Primary Strict-Valid Result

Recorded daily-high peak hours:

| Month | Available count | Most frequent observed UTC hour | Count | Percentage |
| --- | ---: | ---: | ---: | ---: |
| January | 9 | 23 | 5 | 55.6% |
| February | 5 | 23 | 3 | 60.0% |
| March | 9 | 23 | 5 | 55.6% |

Recorded daily-low peak hours:

| Month | Available count | Most frequent observed UTC hour | Count | Percentage |
| --- | ---: | ---: | ---: | ---: |
| January | 9 | 23 | 5 | 55.6% |
| February | 5 | 23 | 3 | 60.0% |
| March | 9 | 22 | 4 | 44.4% |

No ordinary mean or median clock hour was calculated.

### Warning-Review Sensitivity

`warning-review sensitivity`

Recorded daily-high peaks:

| Month | Available count | Most frequent observed UTC hour | Count | Percentage |
| --- | ---: | --- | ---: | ---: |
| January | 18 | 13 | 4 | 22.2% |
| February | 20 | 14 | 4 | 20.0% |
| March | 16 | 00 and 13 tied | 3 each | 18.8% each |

Recorded daily-low peaks:

| Month | Available count | Most frequent observed UTC hour | Count | Percentage |
| --- | ---: | --- | ---: | ---: |
| January | 18 | 00, 14, 15, 17, 18, and 19 tied | 2 each | 11.1% each |
| February | 20 | 15 and 16 tied | 3 each | 15.0% each |
| March | 16 | 01 | 5 | 31.2% |

Warning context:

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows |
| --- | --- | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 |

The warning context is separate from the timing frequencies. It does not show
that `INTERNAL_FLAT_ZERO_VOLUME` caused the different distributions.

### Tie Prevalence

| Month | Tier | Observations | Repeated high | Repeated low |
| --- | --- | ---: | ---: | ---: |
| January | strict-valid | 9 | 0 | 0 |
| January | warning-review | 18 | 1 | 1 |
| February | strict-valid | 5 | 1 | 0 |
| February | warning-review | 20 | 0 | 0 |
| March | strict-valid | 9 | 0 | 0 |
| March | warning-review | 16 | 1 | 1 |

Repeated-extremum observations:

```text
2024-01-15 warning_review high:
  08:45:00
  08:50:00
  recorded: 08:45:00

2024-01-31 warning_review low:
  20:07:00
  20:34:00
  recorded: 20:07:00

2024-02-02 strict_valid high:
  13:16:00
  13:17:00
  recorded: 13:16:00

2024-03-14 warning_review high:
  01:02:00
  01:05:00
  recorded: 01:02:00

2024-03-18 warning_review low:
  03:16:00
  05:23:00
  recorded: 03:16:00
```

Every recorded linked timestamp matched the reconstructed first occurrence.

### Tie-Handling Sensitivity

Three timing representations were checked without adopting a new platform rule:

1. Current first occurrence.
2. Last occurrence.
3. All equal occurrences with each date contributing total weight `1.0`.

All strict-valid peak-hour conclusions were unchanged. Warning-review
daily-high peak conclusions were unchanged. January and February warning-review
daily-low peak conclusions were unchanged. March warning-review daily-low
retained hour `01` as its peak with `5/16`; only the non-peak allocation for
`2024-03-18` changed between hours `03` and `05`.

The timing finding showed no material dependence on the first-occurrence tie
convention in this bounded sample. This does not prove that the convention is
universally safe.

### Reconciliation

- All 23 strict-valid and 54 warning-review observations were reconstructed from
  raw CSVs after the active edge-placeholder filter.
- Linked high and low timestamps matched the reconstructed first occurrences.
- No timestamp mismatches were found.
- The three sensitivity representations were calculated using read-only
  temporary analysis.
- No repository files were modified during the preceding read-only timing
  execution.
- No new report was generated during the preceding read-only timing execution.

Other raw-data quality dimensions were not revalidated during this timing
analysis.

### Descriptive Conclusion

In the strict-valid January-March 2024 sample, the recorded daily-high peak hour
was `23` in all three months. The recorded daily-low peak hour was `23` in
January and February and `22` in March. The separately labelled warning-review
sensitivity distributions had different peak hours and were generally more
dispersed across the UTC day. The principal peak-hour findings were unchanged
under the tested tie-handling sensitivity representations.

This does not establish a preferred or optimal trading hour, an entry or exit
time, a market tendency, a reversal time, support or resistance, a setup or
signal, prediction, trading edge, profitability, execution realism, statistical
significance, the cause or harmlessness of `INTERNAL_FLAT_ZERO_VOLUME`, or
universal or normal XAU/USD behaviour.

### Unresolved Questions

- The first-occurrence tie convention is now protected by dedicated regression
  tests, but no broader tie-handling policy change or universal recommendation
  has been adopted.
- The cause and practical meaning of `INTERNAL_FLAT_ZERO_VOLUME` remain
  unresolved.
- No next research task has been selected from this finding alone.
