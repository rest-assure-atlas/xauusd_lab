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

## 2026-07-26 - January-December 2024 Daily-Range Distribution

Status: `descriptive finding`

Extended through April 2024 on 2026-07-27 without material revision.
Extended through December 2024 on 2026-07-28 without material revision.

Classification: `extension without material revision`

### Question

For each validated month from January through December 2024, what is the
descriptive distribution of daily range for `strict_valid` linked observations,
with `warning_review` daily range reported separately as a labelled sensitivity
view and `calendar_only`/`excluded_unusable` reported only as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1min
- Timezone: UTC
- Calendar period: January-December 2024
- Primary input: provenance-linked daily observation reports
- Access contract: `research_observation_contract_v1`
- Quality treatment: `warning_treatment_v1`

The evidence is the documented Dukascopy XAUUSD one-minute BID record in UTC.
This is not a universal XAU/USD record.

### Source Reports

Primary row-level source reports were the twelve monthly linked observation
reports from:

```text
reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
...
reports/linked_observation_report_2024-12-01_to_2024-12-31.csv
```

Reconciliation used the corresponding twelve monthly historical baseline
reports from:

```text
reports/historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv
...
reports/historical_baseline_linked_observation_report_2024-12-01_to_2024-12-31.csv
```

Warning context used the corresponding monthly manifests and internal flat
zero-volume diagnostics only for warning-reason counts and diagnostic context.

### Calculation Contract

The extension used the linked fields `date`, `quality_tier`, `daily_high`,
`daily_low`, `daily_range`, `manifest_quality_reasons`, `provider`,
`instrument`, `quote_side`, `timeframe`, `software_revision`, and source report
provenance. For every eligible `strict_valid` and `warning_review` observation,
exact `Decimal` arithmetic verified:

```text
daily_range = daily_high - daily_low
```

Every stored range matched its recalculated value. Daily-range arithmetic
mismatches were `0`. Missing daily-range values occurred only on
`calendar_only` rows and remained unavailable rather than being interpreted as
zero.

Monthly descriptive statistics use the existing baseline convention: exact
`Decimal` calculations reported to three decimal places with `ROUND_HALF_UP` to
`0.001`.

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |
| April | 30 | 8 | 18 | 4 | 0 |
| May | 31 | 9 | 18 | 4 | 0 |
| June | 30 | 9 | 16 | 5 | 0 |
| July | 31 | 8 | 19 | 4 | 0 |
| August | 31 | 9 | 17 | 5 | 0 |
| September | 30 | 9 | 17 | 4 | 0 |
| October | 31 | 8 | 19 | 4 | 0 |
| November | 30 | 9 | 16 | 5 | 0 |
| December | 31 | 12 | 15 | 4 | 0 |

Unavailable daily-range values occurred only for `calendar_only` observations
and remained unavailable rather than being converted to zero.

Combined January-December coverage was 366 observations: 104 `strict_valid`,
209 `warning_review`, 53 `calendar_only`, and 0 `excluded_unusable`. All
`strict_valid` and `warning_review` observations were eligible for daily-range
summaries.

### Primary Strict-Valid Result

Primary descriptive result under `warning_treatment_v1`:

| Month | Count | Min | Median | Mean | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 9 | 2.370 | 7.199 | 13.440 | 39.583 |
| February | 5 | 2.227 | 3.514 | 11.788 | 29.910 |
| March | 9 | 3.710 | 12.420 | 19.669 | 49.300 |
| April | 8 | 4.690 | 25.977 | 36.707 | 97.630 |
| May | 9 | 4.370 | 22.060 | 24.435 | 48.787 |
| June | 9 | 4.270 | 11.283 | 26.772 | 100.967 |
| July | 8 | 5.383 | 21.342 | 24.513 | 47.543 |
| August | 9 | 6.470 | 20.069 | 26.784 | 66.830 |
| September | 9 | 2.709 | 7.880 | 18.560 | 44.110 |
| October | 8 | 3.740 | 20.537 | 19.833 | 37.997 |
| November | 9 | 6.617 | 28.953 | 24.281 | 47.447 |
| December | 12 | 3.321 | 11.614 | 18.932 | 46.650 |

Retained April strict-valid observation detail from the January-April finding:

```text
2024-04-05: 62.740
2024-04-07: 24.550
2024-04-12: 97.630
2024-04-14: 25.700
2024-04-19: 44.940
2024-04-21: 7.150
2024-04-26: 26.253
2024-04-28: 4.690
```

### Warning-Review Sensitivity

`warning-review sensitivity`:

| Month | Count | Min | Median | Mean | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 18 | 12.830 | 19.627 | 22.218 | 35.320 |
| February | 20 | 6.310 | 15.765 | 17.875 | 42.860 |
| March | 16 | 14.230 | 26.350 | 30.299 | 73.400 |
| April | 18 | 25.493 | 40.305 | 40.896 | 68.177 |
| May | 18 | 17.790 | 30.805 | 34.104 | 56.757 |
| June | 16 | 10.884 | 28.409 | 27.600 | 39.930 |
| July | 19 | 12.021 | 34.610 | 33.459 | 53.020 |
| August | 17 | 18.123 | 32.210 | 36.077 | 94.491 |
| September | 17 | 14.400 | 28.427 | 30.534 | 53.350 |
| October | 19 | 19.120 | 26.520 | 30.364 | 58.590 |
| November | 16 | 16.377 | 37.039 | 46.903 | 114.890 |
| December | 15 | 20.770 | 32.060 | 35.207 | 69.261 |

Retained April warning-review observation detail from the January-April
finding:

```text
2024-04-01: 37.190
2024-04-02: 41.600
2024-04-03: 37.150
2024-04-04: 25.737
2024-04-08: 51.080
2024-04-09: 27.460
2024-04-10: 40.800
2024-04-11: 53.800
2024-04-15: 68.177
2024-04-16: 35.284
2024-04-17: 41.013
2024-04-18: 28.659
2024-04-22: 61.900
2024-04-23: 43.040
2024-04-24: 25.493
2024-04-25: 39.810
2024-04-29: 26.857
2024-04-30: 51.080
```

### Secondary Annual Nested Summary

The annual rows below are secondary summaries of daily observations nested
within calendar months. They are not twelve independent monthly observations
and do not establish that every statistic behaved consistently across months.

| Population | Count | Min | Median | Mean | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| strict_valid | 104 | 2.227 | 16.690 | 22.308 | 100.967 |
| warning_review sensitivity | 209 | 6.310 | 28.470 | 31.853 | 114.890 |

### Warning Context

All 209 `warning_review` observations had warning reason
`INTERNAL_FLAT_ZERO_VOLUME`. This reason remains unresolved.

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows | Tokyo overlap rows | London overlap rows | New York overlap rows |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 | 0 | 0 | 152 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 | 2 | 0 | 157 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 | 3 | 0 | 1 |
| April | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 18 | 1,081 | 0 | 0 | 0 |
| May | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 23 | 1,237 | 0 | 0 | 152 |
| June | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 18 | 1,113 | 0 | 0 | 150 |
| July | `INTERNAL_FLAT_ZERO_VOLUME` | 19 | 22 | 1,293 | 0 | 0 | 153 |
| August | `INTERNAL_FLAT_ZERO_VOLUME` | 17 | 17 | 1,020 | 0 | 0 | 0 |
| September | `INTERNAL_FLAT_ZERO_VOLUME` | 17 | 21 | 1,175 | 0 | 0 | 151 |
| October | `INTERNAL_FLAT_ZERO_VOLUME` | 19 | 23 | 1,144 | 0 | 0 | 0 |
| November | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 17 | 1,112 | 0 | 0 | 151 |
| December | `INTERNAL_FLAT_ZERO_VOLUME` | 15 | 19 | 915 | 7 | 1 | 0 |

The diagnostic run counts and run rows are warning context only. They are not
additional daily-range statistics. Diagnostic reconciliation establishes
counting and location consistency only. It does not establish cause,
harmlessness, expected behaviour, market closure, provider outage, corruption,
reliability, or that the warning caused the observed range differences.

### Reconciliation

- The statistics were independently calculated from linked observation rows
  loaded through `research_observations.load_linked_reports(...)`.
- All 24 monthly strict-valid and warning-review population summaries matched
  their corresponding historical-baseline `range_summary` rows exactly at
  three decimals.
- All 12 monthly warning-reason summaries matched their corresponding
  historical-baseline `range_summary_by_warning_reason` rows.
- Baseline mismatches were `0`, including rounding-only differences.
- No provenance or schema incompatibility was found.
- 366 observations loaded; chronological and compatibility validation passed;
  five software revisions were retained; duplicate identities were `0`; blank
  calendar-only ranges remained unavailable; no primary linked-row ad hoc CSV
  parsing or loader expansion was needed.
- During the preceding read-only analysis execution, no repository files were
  modified.

Raw files were not revalidated during this specific analysis. Earlier pipeline
validations remain separate evidence.

### Descriptive Conclusion

Across January-December 2024 Dukascopy XAUUSD one-minute BID linked
observations, warning-review sensitivity median and mean daily ranges were
higher than strict-valid median and mean daily ranges in every validated month.
The secondary annual nested daily-observation summary showed the same
direction: warning-review median `28.470` versus strict-valid median `16.690`,
and warning-review mean `31.853` versus strict-valid mean `22.308`.

This extends the January-April daily-range finding without material revision.
Distributional comparisons remain statistic-specific: strict-valid monthly
maxima were higher in January, April, and June, while warning-review maxima
were higher in the other nine months. Warning-review minima were higher in all
twelve months.

Monthly results remain primary. The annual nested summary can hide monthly
exceptions, including the strict-valid monthly maximum exceptions. No
inferential testing was performed.

This does not establish that warnings caused larger ranges, that
`INTERNAL_FLAT_ZERO_VOLUME` caused the difference, that warning-review
observations are invalid, that warning-review observations are equivalent to
strict-valid observations, a volatility regime, a breakout condition, stable or
universal market behaviour, market causation, normal XAU/USD behaviour,
statistical significance, causation, prediction, support or resistance, a setup
or signal, trading edge, profitability, or execution realism.

### Unresolved Questions

- The cause and practical meaning of `INTERNAL_FLAT_ZERO_VOLUME` remain
  unresolved.
- Strict-valid monthly samples remain small; February has 5 observations, and
  April, July, and October each have 8 observations.
- Warning treatment remains observation-level.
- The evidence covers one provider, instrument, BID quote side, timeframe, and
  one calendar year.
- No statistical testing was performed.
- Overlapping or serially related observations were not modelled.
- ASK remains a future prerequisite before spread-aware or execution-aware
  testing. Spread, commission, slippage, latency, and execution assumptions were
  not included.
- Tick remains conditional on a defined need for sub-minute evidence.
- The analysis is descriptive rather than predictive.
- No next research task has been selected from this finding alone.

## 2026-07-26 - January-April 2024 Daily-Extrema UTC Hours

Status: `descriptive finding`

### Question

For each validated month from January through April 2024, at which UTC clock
hours did the recorded daily high and daily low occur for `strict_valid` linked
observations, with `warning_review` reported separately as a labelled
sensitivity view and `calendar_only`/`excluded_unusable` retained as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1 minute
- Timezone: UTC
- Calendar period: January-April 2024
- Primary input: provenance-linked daily observation reports
- Access contract: `research_observation_contract_v1`
- Quality treatment: `warning_treatment_v1`

This is not a universal XAU/USD market record.

### Source Reports

Primary row-level source reports loaded through
`research_observations.load_linked_reports(...)`:

- `reports/linked_observation_report_2024-01-01_to_2024-01-31.csv`
- `reports/linked_observation_report_2024-02-01_to_2024-02-29.csv`
- `reports/linked_observation_report_2024-03-01_to_2024-03-31.csv`
- `reports/linked_observation_report_2024-04-01_to_2024-04-30.csv`

Warning context reports:

- `reports/data_manifest_2024-01-01_to_2024-01-31.csv`
- `reports/data_manifest_2024-02-01_to_2024-02-29.csv`
- `reports/data_manifest_2024-03-01_to_2024-03-31.csv`
- `reports/data_manifest_2024-04-01_to_2024-04-30.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-02-01_to_2024-02-29.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-03-01_to_2024-03-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-04-01_to_2024-04-30.csv`

April raw CSVs were read only for the bounded repeated-extremum sensitivity
scan. Only `data_raw/XAUUSD_2024-04-09_1min_BID_UTC.csv` contained a repeated
daily extremum among eligible April observations.

### Timing-Field Semantics

- Required linked fields: `date`, `quality_tier`,
  `time_of_daily_high_utc`, `time_of_daily_low_utc`, `daily_high`, and
  `daily_low`
- Format: `HH:MM:SS`
- Timestamps are UTC one-minute candle opening times.
- All eligible timestamps had seconds equal to `00`.
- Valid hour categories are integers `0` through `23`.
- Highs and lows are classified separately.
- Both extrema belong to the requested UTC date.
- No overnight or circular-clock adjustment was applied.
- Edge flat zero-volume placeholders are removed before extrema selection.
- Current implementation records the first active-candle occurrence when equal
  extrema repeat.
- Dedicated `session_report.py` regression tests now cover equal daily-high and
  equal daily-low ties after edge flat zero-volume placeholders are removed.
- Tied modal hours are all retained rather than choosing one arbitrarily.

The timestamp fields record one occurrence. They do not represent all equal
daily-high or daily-low occurrences.

Hour definitions:

```text
daily_high_hour_utc = integer hour from time_of_daily_high_utc
daily_low_hour_utc = integer hour from time_of_daily_low_utc
```

No ordinary mean or median clock hour was calculated.

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |
| April | 30 | 8 | 18 | 4 | 0 |

Combined January-April coverage:

```text
total = 121
strict_valid = 31
warning_review = 72
calendar_only = 18
excluded_unusable = 0
```

All `strict_valid` and `warning_review` rows were eligible and had available
daily-high and daily-low timestamps. Timing values were unavailable only for
`calendar_only` rows and remained unavailable rather than being interpreted as
hour `00`. Every requested date appeared exactly once.

### Primary Strict-Valid Result

Monthly modal summary:

| Side | Month | N | Modal hour(s) | Count | Percentage | Distinct observed hours |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| High | January | 9 | 23 | 5 | 55.6% | 4 |
| High | February | 5 | 23 | 3 | 60.0% | 3 |
| High | March | 9 | 23 | 5 | 55.6% | 5 |
| High | April | 8 | 22 | 4 | 50.0% | 5 |
| Low | January | 9 | 23 | 5 | 55.6% | 5 |
| Low | February | 5 | 23 | 3 | 60.0% | 3 |
| Low | March | 9 | 22 | 4 | 44.4% | 5 |
| Low | April | 8 | 22 | 4 | 50.0% | 4 |

April strict-valid daily-high hours:

| UTC hour | Count | Percentage |
| ---: | ---: | ---: |
| 01 | 1 | 12.5% |
| 09 | 1 | 12.5% |
| 15 | 1 | 12.5% |
| 17 | 1 | 12.5% |
| 22 | 4 | 50.0% |

April strict-valid daily-low hours:

| UTC hour | Count | Percentage |
| ---: | ---: | ---: |
| 01 | 2 | 25.0% |
| 11 | 1 | 12.5% |
| 19 | 1 | 12.5% |
| 22 | 4 | 50.0% |

April strict-valid observations:

```text
2024-04-05 high 17:11 hour 17 / low 01:31 hour 01
2024-04-07 high 22:05 hour 22 / low 22:19 hour 22
2024-04-12 high 15:04 hour 15 / low 19:03 hour 19
2024-04-14 high 22:08 hour 22 / low 22:27 hour 22
2024-04-19 high 01:46 hour 01 / low 11:12 hour 11
2024-04-21 high 22:00 hour 22 / low 22:01 hour 22
2024-04-26 high 09:12 hour 09 / low 01:13 hour 01
2024-04-28 high 22:00 hour 22 / low 22:06 hour 22
```

Simple January-April audit totals were calculated only as audit context, not as
universal timing probabilities.

### Warning-Review Sensitivity

`warning-review sensitivity`

Monthly modal summary:

| Side | Month | N | Modal hour(s) | Count | Percentage | Distinct observed hours |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| High | January | 18 | 13 | 4 | 22.2% | 12 |
| High | February | 20 | 14 | 4 | 20.0% | 11 |
| High | March | 16 | 00, 13 | 3 | 18.8% | 10 |
| High | April | 18 | 22 | 4 | 22.2% | 12 |
| Low | January | 18 | 00, 14, 15, 17, 18, 19 | 2 | 11.1% | 12 |
| Low | February | 20 | 15, 16 | 3 | 15.0% | 13 |
| Low | March | 16 | 01 | 5 | 31.2% | 9 |
| Low | April | 18 | 01 | 5 | 27.8% | 11 |

April warning-review sensitivity non-zero counts:

```text
daily-high hours:
00:1
01:2
02:1
04:1
05:1
09:1
13:1
14:2
15:1
16:2
18:1
22:4

daily-low hours:
01:5
03:1
07:1
08:1
09:2
12:1
13:1
14:2
18:1
19:1
20:2
```

Warning context:

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows |
| --- | --- | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 |
| April | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 18 | 1,081 |

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
| April | strict-valid | 8 | 0 | 0 |
| April | warning-review | 18 | 1 | 1 |

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

2024-04-09 warning_review high:
  first occurrence: 09:28:00
  last occurrence: 09:30:00
  first hour: 09
  last hour: 09

2024-04-09 warning_review low:
  first occurrence: 01:04:00
  last occurrence: 01:06:00
  first hour: 01
  last hour: 01
```

Every recorded linked timestamp matched the reconstructed first occurrence in
the checked repeated-extremum observations.

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

For April, `2024-04-09` was the only eligible observation with a repeated
extremum. No April strict-valid repeated extremum was found. Neither April hour
category changed, no April frequency count changed, and no modal result
changed. The approved April assessment is `no dependence observed`. This
conclusion is limited to April and does not establish that repeated extrema
crossing an hour boundary could never matter.

The timing finding showed no material dependence on the first-occurrence tie
convention in this bounded sample. This does not prove that the convention is
universally safe.

Platform behaviour was not changed.

### Relationship To Related Extrema Findings

Extrema ordering records which recorded extremum occurred first. Elapsed
separation records the minutes between extrema. UTC-hour frequency records
placement on the UTC clock. None of the three determines the other two, and no
causal relationship among them was tested.

This UTC-hour finding is also distinct from daily-range magnitude, daily
open-to-close direction, and close location within the daily range.

### Loader Practicality Evidence

- The four linked reports were loaded with
  `research_observations.load_linked_reports(...)`.
- 121 observations were loaded.
- Population counts were `31 / 72 / 18 / 0`.
- Chronological and compatibility validation passed.
- Four software revisions were retained.
- Duplicate identities were zero.
- Calendar-only timestamp blanks remained unavailable.
- No primary linked-row ad hoc CSV parsing was required.
- Custom work was limited to timestamp parsing, hour extraction, frequency and
  modal calculations, the bounded April repeated-extremum scan, and separate
  warning-context reads.
- No loader expansion was required.

### Reconciliation

- January-March repeated-extremum sensitivity evidence was preserved from the
  existing finding.
- April raw CSVs were read only for the bounded April repeated-extremum scan.
- The April repeated-extremum scan found only `2024-04-09`.
- No April hour category, frequency count, or modal result changed under the
  last-occurrence check.
- The frequency extension used read-only temporary analysis.
- No repository files were modified during the preceding read-only timing
  execution.
- No new report was generated during the preceding read-only timing execution.

Other raw-data quality dimensions were not revalidated during this timing
analysis.

### Descriptive Conclusion

In the strict-valid January-March observations, the recorded daily-high modal
hour was `23` in each month. April did not continue that result: its
daily-high modal hour was `22`, containing four of eight observations.

April's strict-valid daily-low modal hour was also `22`, containing four of
eight observations. This matched March's modal low hour but differed from
January and February, where hour `23` was modal.

April extends the UTC-hour finding with a material qualification. The
January-March high-hour result remains valid for those months, but it must not
be generalised as continuing through April.

April strict-valid and warning-review daily-high distributions shared modal
hour `22`, but strict-valid was more concentrated there: `50.0%` versus
`22.2%`. For recorded daily lows, strict-valid modal hour was `22`, while
warning-review modal hour was `01`. The warning-review high- and low-hour
distributions also covered more distinct hours.

These differences do not establish a causal warning effect, stable timing
pattern, or preferred trading hour.

This does not establish a best trading hour, preferred entry or exit timing, a
setup or signal, prediction, trading edge, profitability, execution realism,
statistical significance, market causation, the cause or harmlessness of
`INTERNAL_FLAT_ZERO_VOLUME`, or normal or universal XAU/USD behaviour.

### Unresolved Questions

- The first-occurrence tie convention is now protected by dedicated regression
  tests, but no broader tie-handling policy change or universal recommendation
  has been adopted.
- Strict-valid samples remain small.
- February has five strict-valid observations.
- April has eight strict-valid observations.
- Timestamps are one-minute candle opening times.
- Repeated extrema within one hour may leave the hour category unchanged.
- A repeated extremum crossing an hour boundary could affect classification.
- Warning treatment remains observation-level under `warning_treatment_v1`.
- The cause and practical meaning of `INTERNAL_FLAT_ZERO_VOLUME` remain
  unresolved.
- The evidence covers one provider, instrument, BID quote side, timeframe, and
  four months.
- No statistical testing or serial-dependence modelling was performed.
- No execution assumptions were included.
- The analysis is descriptive rather than predictive.
- No next research task has been selected from this finding alone.

## 2026-07-26 - January-April 2024 Daily-Extrema Ordering

Status: `descriptive finding`

Extended through April 2024 on 2026-07-27 with a material qualification.

### Question

For each validated month from January through April 2024, how often did the
recorded daily high occur before the recorded daily low, the recorded daily low
occur before the recorded daily high, or both occur in the same recorded minute
for `strict_valid` linked observations, with `warning_review` reported
separately as a labelled sensitivity view and `calendar_only`/`excluded_unusable`
retained as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1 minute
- Timezone: UTC
- Calendar period: January-April 2024
- Primary input: provenance-linked daily observation reports
- Access contract: `research_observation_contract_v1`
- Quality treatment: `warning_treatment_v1`

This describes the ordering of recorded daily-extrema timestamps only. It is
not a universal XAU/USD market record.

### Source Reports

Primary row-level source reports:

- `reports/linked_observation_report_2024-01-01_to_2024-01-31.csv`
- `reports/linked_observation_report_2024-02-01_to_2024-02-29.csv`
- `reports/linked_observation_report_2024-03-01_to_2024-03-31.csv`
- `reports/linked_observation_report_2024-04-01_to_2024-04-30.csv`

Warning context reports:

- `reports/data_manifest_2024-01-01_to_2024-01-31.csv`
- `reports/data_manifest_2024-02-01_to_2024-02-29.csv`
- `reports/data_manifest_2024-03-01_to_2024-03-31.csv`
- `reports/data_manifest_2024-04-01_to_2024-04-30.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-02-01_to_2024-02-29.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-03-01_to_2024-03-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-04-01_to_2024-04-30.csv`

### Timestamp And Ordering Definitions

- Required linked fields: `date`, `quality_tier`, `time_of_daily_high_utc`,
  `time_of_daily_low_utc`, `daily_high`, and `daily_low`.
- Daily high field: `time_of_daily_high_utc`
- Daily low field: `time_of_daily_low_utc`
- Format: `HH:MM:SS`
- Timestamps are UTC one-minute candle opening times.
- All eligible timestamps had seconds equal to `00`.
- Edge flat zero-volume placeholders are removed before extrema selection.
- Equal extrema use the first active-candle occurrence.
- Dedicated `session_report.py` regression tests protect equal daily-high and
  equal daily-low first-occurrence behaviour.
- Linked observation reports preserve the session-report timing values.

Each eligible observation was assigned to exactly one category:

- `high_before_low`: the recorded daily-high timestamp is earlier than the
  recorded daily-low timestamp.
- `low_before_high`: the recorded daily-low timestamp is earlier.
- `same_recorded_minute`: the two recorded timestamps are identical.

Both timestamps belong to the same requested UTC date. No overnight or
circular-clock adjustment was applied. Events within the same one-minute candle
cannot be internally ordered from this evidence.

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |
| April | 30 | 8 | 18 | 4 | 0 |

All `strict_valid` and `warning_review` rows had both daily-extrema timing
fields available. Unavailable timing values occurred only for `calendar_only`
rows and remained unavailable rather than being interpreted as midnight.
Every requested date appeared exactly once.

Combined January-April coverage was 121 observations: 31 `strict_valid`, 72
`warning_review`, 18 `calendar_only`, and 0 `excluded_unusable`. All
`strict_valid` and `warning_review` observations were eligible.

### Primary Strict-Valid Result

Primary descriptive result under `warning_treatment_v1`:

| Month | Eligible | High before low | Percentage | Low before high | Percentage | Same minute | Percentage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 9 | 4 | 44.4% | 5 | 55.6% | 0 | 0.0% |
| February | 5 | 1 | 20.0% | 4 | 80.0% | 0 | 0.0% |
| March | 9 | 2 | 22.2% | 7 | 77.8% | 0 | 0.0% |
| April | 8 | 6 | 75.0% | 2 | 25.0% | 0 | 0.0% |

Strict-valid category dates:

```text
January high_before_low:
2024-01-07
2024-01-21
2024-01-26
2024-01-28

January low_before_high:
2024-01-01
2024-01-05
2024-01-12
2024-01-14
2024-01-19

February high_before_low:
2024-02-02

February low_before_high:
2024-02-04
2024-02-11
2024-02-16
2024-02-25

March high_before_low:
2024-03-15
2024-03-22

March low_before_high:
2024-03-01
2024-03-03
2024-03-10
2024-03-17
2024-03-24
2024-03-28
2024-03-31

April high_before_low:
2024-04-07 - high 22:05, low 22:19
2024-04-12 - high 15:04, low 19:03
2024-04-14 - high 22:08, low 22:27
2024-04-19 - high 01:46, low 11:12
2024-04-21 - high 22:00, low 22:01
2024-04-28 - high 22:00, low 22:06

April low_before_high:
2024-04-05 - low 01:31, high 17:11
2024-04-26 - low 01:13, high 09:12

April same_recorded_minute:
none
```

Simple January-April strict-valid audit count, not a universal probability:

```text
Eligible strict-valid observations: 31
high_before_low: 13
low_before_high: 18
same_recorded_minute: 0
```

The per-month strict-valid results remain primary.

### Warning-Review Sensitivity

`warning-review sensitivity`:

| Month | Eligible | High before low | Percentage | Low before high | Percentage | Same minute | Percentage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 18 | 13 | 72.2% | 5 | 27.8% | 0 | 0.0% |
| February | 20 | 11 | 55.0% | 9 | 45.0% | 0 | 0.0% |
| March | 16 | 5 | 31.2% | 11 | 68.8% | 0 | 0.0% |
| April | 18 | 7 | 38.9% | 11 | 61.1% | 0 | 0.0% |

April warning-review category dates:

```text
April high_before_low:
2024-04-01
2024-04-04
2024-04-10
2024-04-17
2024-04-22
2024-04-23
2024-04-30

April low_before_high:
2024-04-02
2024-04-03
2024-04-08
2024-04-09
2024-04-11
2024-04-15
2024-04-16
2024-04-18
2024-04-24
2024-04-25
2024-04-29

April same_recorded_minute:
none
```

Warning context:

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows |
| --- | --- | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 |
| April | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 18 | 1,081 |

The warning context is separate from the ordering result. It does not show that
`INTERNAL_FLAT_ZERO_VOLUME` caused any ordering-distribution difference.

Simple January-April warning-review audit count, not pooled with strict-valid:

```text
Eligible warning-review observations: 72
high_before_low: 36
low_before_high: 36
same_recorded_minute: 0
```

### Tie-Convention Sensitivity

Known repeated-extremum observations checked against raw CSVs:

```text
2024-01-15 warning_review
2024-01-31 warning_review
2024-02-02 strict_valid
2024-03-14 warning_review
2024-03-18 warning_review
```

April repeated-extremum check against raw CSVs:

```text
2024-04-09
quality tier: warning_review

repeated daily high:
  first occurrence: 09:28
  last occurrence: 09:30

repeated daily low:
  first occurrence: 01:04
  last occurrence: 01:06

ordering under first occurrences:
low_before_high

ordering under last occurrences:
low_before_high
```

Changing from the recorded first occurrence to the last equal-extremum
occurrence did not change the ordering category for any known January-March
repeated-extremum observation or for April's repeated-extremum observation.
April 9 was the only eligible April date with a repeated daily extremum, no
April strict-valid repeated extremum was found, no April ordering category
changed, and no April monthly count changed. The approved April assessment is
`no dependence observed` for April ordering. This does not prove that
first-occurrence handling is irrelevant in every period or for every timing
statistic.

No platform behaviour change was made or adopted.

### Reconciliation

- Each requested date appeared exactly once in its linked report.
- All `strict_valid` and `warning_review` observations with timing values were
  classified exactly once.
- `calendar_only` timing values remained unavailable.
- All four linked reports were loaded with
  `research_observations.load_linked_reports(...)`; 121 observations loaded;
  chronological and compatibility validation passed; four software revisions
  were retained; duplicate identities were `0`; and no primary linked-row ad
  hoc CSV parsing or loader expansion was required.
- The current timestamp semantics and dedicated tie regression tests were
  inspected.
- Linked observation reports preserve the session-report timing values.
- Repeated-extremum cases were checked against raw CSVs; custom work was limited
  to timestamp categorisation, the bounded April repeated-extremum scan, and
  diagnostic-context reconciliation.
- No category changed under last-occurrence selection.
- No repository file was changed during the preceding read-only ordering
  execution.
- No new report was generated during the preceding read-only ordering execution.

Other raw-data quality dimensions were not revalidated during this ordering
analysis.

### Descriptive Conclusion

In the strict-valid January-March observations, `low_before_high` was the more
frequent ordering category in each month. April did not continue that monthly
pattern: six of eight strict-valid observations were `high_before_low`, while
two were `low_before_high`.

April therefore extends the existing ordering finding with a material
qualification. The January-March result remains valid for those months, but it
must not be generalised as a monthly pattern continuing through April.

April warning-review showed the opposite monthly majority from April
strict-valid: seven of eighteen observations were `high_before_low` and eleven
were `low_before_high`.

Strict-valid and warning-review monthly majorities differed in January,
February, and April, and matched in March. These bounded differences do not
establish a causal warning effect or a stable ordering tendency. No eligible
January-April observation had both extrema recorded in the same minute.

Extrema ordering is distinct from extrema UTC-hour frequency, which records
clock-hour placement; elapsed-extrema separation, which records the number of
minutes between extrema; daily open-to-close direction; and close location
within the daily range.

This does not establish a directional tendency, reversal sequence, preferred
entry or exit timing, setup or signal, prediction, trading edge, profitability,
execution realism, statistical significance, market causation, normal or
universal XAU/USD behaviour, or that `INTERNAL_FLAT_ZERO_VOLUME` caused any
ordering difference.

### Unresolved Questions

- Strict-valid monthly samples remain small; February has 5 observations and
  April has 8 observations.
- Timestamps are one-minute candle opening times.
- Events within one candle cannot be internally ordered.
- First-occurrence semantics can matter where extrema repeat, despite no April
  category change.
- Warning treatment remains observation-level under `warning_treatment_v1`.
- The cause and practical meaning of `INTERNAL_FLAT_ZERO_VOLUME` remain
  unresolved.
- The evidence covers one provider, instrument, BID quote side, timeframe, and
  four months.
- No statistical testing or serial-dependence modelling was performed.
- No execution assumptions were included.
- The analysis is descriptive rather than predictive.
- No next research task has been selected from this finding alone.

## 2026-07-27 - January-December 2024 Daily Close Location

Status: `descriptive finding`

Extended through December 2024 on 2026-07-28 with material qualification.

Classification: `material qualification`

### Question

For each validated month from January through December 2024, where did the
recorded daily close occur within that day's recorded high-to-low range for
`strict_valid` observations, with `warning_review` reported separately as a
labelled sensitivity view and `calendar_only`/`excluded_unusable` retained only
as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1min
- Timezone: UTC
- Calendar period: January-December 2024
- Primary input: provenance-linked daily observation reports
- Access contract: `research_observation_contract_v1`
- Quality treatment: `warning_treatment_v1`

The evidence is the documented Dukascopy XAUUSD one-minute BID record in UTC.
This is not a universal XAU/USD market record.

### Source Reports

Primary row-level source reports loaded through
`research_observations.load_linked_reports(...)`:

```text
reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
...
reports/linked_observation_report_2024-12-01_to_2024-12-31.csv
```

Supporting historical baselines:

```text
reports/historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv
...
reports/historical_baseline_linked_observation_report_2024-12-01_to_2024-12-31.csv
```

Warning context reports:

```text
reports/data_manifest_2024-01-01_to_2024-01-31.csv
...
reports/data_manifest_2024-12-01_to_2024-12-31.csv
reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv
...
reports/internal_flat_zero_volume_diagnostic_2024-12-01_to_2024-12-31.csv
```

### Formula And Categories

Linked fields used:

- `date`
- `quality_tier`
- `daily_high`
- `daily_low`
- `daily_close`
- `daily_range`
- `manifest_quality_reasons`
- `provider`
- `instrument`
- `quote_side`
- `timeframe`
- `software_revision`
- source report provenance

For every eligible observation:

```text
close_location =
    (daily_close - daily_low)
    /
    (daily_high - daily_low)
```

Interpretation:

```text
0.0 = close at recorded daily low
0.5 = close at midpoint of recorded daily range
1.0 = close at recorded daily high
```

Exact decimal arithmetic was used. The value was not calculated for
zero-range observations, but no eligible zero-range observation occurred.
Before calculating `close_location`, every eligible row satisfied:

```text
stored daily_range == daily_high - daily_low
daily_high - daily_low > 0
daily_low <= daily_close <= daily_high
0 <= close_location <= 1
```

Each eligible observation was assigned to exactly one category:

- `lower_half`: `close_location < 0.5`
- `exact_midpoint`: `close_location == 0.5`
- `upper_half`: `close_location > 0.5`

No thirds, quartiles, trading zones, or additional bands were used.

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |
| April | 30 | 8 | 18 | 4 | 0 |
| May | 31 | 9 | 18 | 4 | 0 |
| June | 30 | 9 | 16 | 5 | 0 |
| July | 31 | 8 | 19 | 4 | 0 |
| August | 31 | 9 | 17 | 5 | 0 |
| September | 30 | 9 | 17 | 4 | 0 |
| October | 31 | 8 | 19 | 4 | 0 |
| November | 30 | 9 | 16 | 5 | 0 |
| December | 31 | 12 | 15 | 4 | 0 |

Eligible counts were identical to strict-valid and warning-review counts.
Missing daily fields occurred only on `calendar_only` rows:

| Month | Missing daily fields |
| --- | ---: |
| January | 4 |
| February | 4 |
| March | 6 |
| April | 4 |
| May | 4 |
| June | 5 |
| July | 4 |
| August | 5 |
| September | 4 |
| October | 4 |
| November | 5 |
| December | 4 |

Calendar-only daily values remained unavailable rather than being interpreted
as zero.

Combined January-December coverage was 366 observations: 104 `strict_valid`,
209 `warning_review`, 53 `calendar_only`, and 0 `excluded_unusable`.

### Primary Strict-Valid Result

Primary descriptive result under `warning_treatment_v1`:

| Month | N | Minimum | Median | Mean | Maximum | Lower half | Exact midpoint | Upper half |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 9 | 0.081956 | 0.477497 | 0.381347 | 0.581287 | 5 (55.6%) | 0 (0.0%) | 4 (44.4%) |
| February | 5 | 0.082075 | 0.582398 | 0.512864 | 0.898558 | 2 (40.0%) | 0 (0.0%) | 3 (60.0%) |
| March | 9 | 0.029143 | 0.859838 | 0.650382 | 0.936246 | 3 (33.3%) | 0 (0.0%) | 6 (66.7%) |
| April | 8 | 0.097613 | 0.558300 | 0.540240 | 0.965732 | 4 (50.0%) | 0 (0.0%) | 4 (50.0%) |
| May | 9 | 0.054459 | 0.409198 | 0.396403 | 0.834997 | 6 (66.7%) | 0 (0.0%) | 3 (33.3%) |
| June | 9 | 0.067220 | 0.355523 | 0.420512 | 0.875114 | 6 (66.7%) | 0 (0.0%) | 3 (33.3%) |
| July | 8 | 0.143239 | 0.665642 | 0.606180 | 0.965265 | 3 (37.5%) | 0 (0.0%) | 5 (62.5%) |
| August | 9 | 0.143740 | 0.529554 | 0.567953 | 0.952703 | 4 (44.4%) | 0 (0.0%) | 5 (55.6%) |
| September | 9 | 0.272501 | 0.504478 | 0.575267 | 0.900538 | 4 (44.4%) | 0 (0.0%) | 5 (55.6%) |
| October | 8 | 0.244275 | 0.636282 | 0.644967 | 0.967154 | 2 (25.0%) | 0 (0.0%) | 6 (75.0%) |
| November | 9 | 0.096708 | 0.645049 | 0.610682 | 0.992444 | 4 (44.4%) | 0 (0.0%) | 5 (55.6%) |
| December | 12 | 0.030868 | 0.630149 | 0.560293 | 0.875085 | 4 (33.3%) | 0 (0.0%) | 8 (66.7%) |

Retained strict-valid category dates from the original January-March finding:

```text
January lower_half:
2024-01-01
2024-01-19
2024-01-21
2024-01-26
2024-01-28

January exact_midpoint:
none

January upper_half:
2024-01-05
2024-01-07
2024-01-12
2024-01-14

February lower_half:
2024-02-02
2024-02-04

February exact_midpoint:
none

February upper_half:
2024-02-11
2024-02-16
2024-02-25

March lower_half:
2024-03-03
2024-03-15
2024-03-22

March exact_midpoint:
none

March upper_half:
2024-03-01
2024-03-10
2024-03-17
2024-03-24
2024-03-28
2024-03-31
```

Simple three-month strict-valid audit count, not a universal probability:

```text
eligible = 23
lower_half = 10
exact_midpoint = 0
upper_half = 13
```

The per-month strict-valid results remain primary.

### Warning-Review Sensitivity

`warning-review sensitivity`:

| Month | N | Minimum | Median | Mean | Maximum | Lower half | Exact midpoint | Upper half |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 18 | 0.128180 | 0.366983 | 0.439384 | 0.953316 | 11 (61.1%) | 0 (0.0%) | 7 (38.9%) |
| February | 20 | 0.033831 | 0.548991 | 0.523146 | 0.800620 | 9 (45.0%) | 0 (0.0%) | 11 (55.0%) |
| March | 16 | 0.189285 | 0.627238 | 0.622303 | 0.918718 | 4 (25.0%) | 0 (0.0%) | 12 (75.0%) |
| April | 18 | 0.123140 | 0.555781 | 0.546869 | 0.949257 | 7 (38.9%) | 0 (0.0%) | 11 (61.1%) |
| May | 18 | 0.089152 | 0.505951 | 0.538147 | 0.997505 | 9 (50.0%) | 0 (0.0%) | 9 (50.0%) |
| June | 16 | 0.158354 | 0.776510 | 0.628383 | 0.932677 | 6 (37.5%) | 0 (0.0%) | 10 (62.5%) |
| July | 19 | 0.027535 | 0.552301 | 0.555376 | 0.966220 | 8 (42.1%) | 0 (0.0%) | 11 (57.9%) |
| August | 17 | 0.060845 | 0.453340 | 0.531694 | 0.991756 | 10 (58.8%) | 0 (0.0%) | 7 (41.2%) |
| September | 17 | 0.234864 | 0.595340 | 0.630638 | 0.992874 | 6 (35.3%) | 0 (0.0%) | 11 (64.7%) |
| October | 19 | 0.188285 | 0.675389 | 0.600435 | 0.988180 | 7 (36.8%) | 0 (0.0%) | 12 (63.2%) |
| November | 16 | 0.030716 | 0.664787 | 0.534827 | 0.948458 | 7 (43.8%) | 0 (0.0%) | 9 (56.3%) |
| December | 15 | 0.082066 | 0.400223 | 0.488822 | 0.974925 | 8 (53.3%) | 0 (0.0%) | 7 (46.7%) |

### Secondary Annual Nested Summary

The annual rows below are secondary summaries of daily observations nested
within calendar months. They are not twelve independent monthly observations
and do not replace the primary monthly results.

| Population | N | Minimum | Median | Mean | Maximum | Lower half | Exact midpoint | Upper half |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| strict_valid | 104 | 0.029143 | 0.534461 | 0.538864 | 0.992444 | 47 (45.2%) | 0 (0.0%) | 57 (54.8%) |
| warning_review sensitivity | 209 | 0.027535 | 0.562896 | 0.552740 | 0.997505 | 92 (44.0%) | 0 (0.0%) | 117 (56.0%) |

### Monthly Comparison

| Month | Strict-valid majority | Warning-review majority | Same strict-majority direction | Median relation | Mean relation |
| --- | --- | --- | --- | --- | --- |
| January | lower-half | lower-half | yes | warning < strict | warning > strict |
| February | upper-half | upper-half | yes | warning < strict | warning > strict |
| March | upper-half | upper-half | yes | warning < strict | warning < strict |
| April | no strict majority | upper-half | no | warning < strict | warning > strict |
| May | lower-half | no strict majority | no | warning > strict | warning > strict |
| June | lower-half | upper-half | no | warning > strict | warning > strict |
| July | upper-half | upper-half | yes | warning < strict | warning < strict |
| August | upper-half | lower-half | no | warning < strict | warning < strict |
| September | upper-half | upper-half | yes | warning > strict | warning > strict |
| October | upper-half | upper-half | yes | warning > strict | warning < strict |
| November | upper-half | upper-half | yes | warning > strict | warning < strict |
| December | upper-half | lower-half | no | warning < strict | warning < strict |

April strict-valid had no strict majority, with 4 lower-half and 4 upper-half
observations. May warning-review had no strict majority, with 9 lower-half and
9 upper-half observations.

Strict-valid lower-half-majority months were January, May, and June.
Strict-valid upper-half-majority months were February, March, and July through
December. Strict-valid and warning-review had the same strict-majority
direction in January, February, March, July, September, October, and November.
The populations diverged, or one population had no strict majority, in April,
May, June, August, and December. Median and mean relationships between the two
populations were mixed across months.

No eligible observation closed exactly at the recorded daily-range midpoint.

### Warning Context

All 209 `warning_review` observations had warning reason
`INTERNAL_FLAT_ZERO_VOLUME`. This reason remains unresolved.

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows | Tokyo overlap rows | London overlap rows | New York overlap rows | Outside configured-session rows |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 | 0 | 0 | 152 | 1,080 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 | 2 | 0 | 157 | 1,033 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 | 3 | 0 | 1 | 905 |
| April | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 18 | 1,081 | 0 | 0 | 0 | 1,081 |
| May | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 23 | 1,237 | 0 | 0 | 152 | 1,085 |
| June | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 18 | 1,113 | 0 | 0 | 150 | 963 |
| July | `INTERNAL_FLAT_ZERO_VOLUME` | 19 | 22 | 1,293 | 0 | 0 | 153 | 1,140 |
| August | `INTERNAL_FLAT_ZERO_VOLUME` | 17 | 17 | 1,020 | 0 | 0 | 0 | 1,020 |
| September | `INTERNAL_FLAT_ZERO_VOLUME` | 17 | 21 | 1,175 | 0 | 0 | 151 | 1,024 |
| October | `INTERNAL_FLAT_ZERO_VOLUME` | 19 | 23 | 1,144 | 0 | 0 | 0 | 1,144 |
| November | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 17 | 1,112 | 0 | 0 | 151 | 961 |
| December | `INTERNAL_FLAT_ZERO_VOLUME` | 15 | 19 | 915 | 7 | 1 | 0 | 907 |

The warning context is separate from the close-location calculation. It does
not show that `INTERNAL_FLAT_ZERO_VOLUME` caused any close-location difference.
Diagnostic information is warning context only and does not explain the
close-location results.

### Annual Audit Counts

```text
strict_valid:
eligible = 104
lower_half = 47
exact_midpoint = 0
upper_half = 57

warning_review:
eligible = 209
lower_half = 92
exact_midpoint = 0
upper_half = 117
```

### Loader Practicality Evidence

- The twelve linked reports were loaded through
  `research_observations.load_linked_reports(...)`.
- 366 observations were loaded.
- Chronological order was preserved.
- Population counts were `104 / 209 / 53 / 0`.
- Five compatible software revisions were retained.
- No loader validation failed.
- Direct linked-row CSV parsing was not needed for the primary analysis.
- Remaining custom work was limited to the research-specific decimal
  calculation, monthly grouping, range reconciliation, and separate
  manifest/diagnostic context reads.

No production implementation was required.

### Reconciliation

- Each requested date appeared exactly once.
- All strict-valid and warning-review observations were eligible.
- No eligible observation had a zero daily range.
- Stored `daily_range` reconciled exactly with `daily_high - daily_low`.
- Daily-range reconciliation mismatches: 0.
- Daily-close bound violations: 0.
- Close-location bound violations: 0.
- Category-assignment errors: 0.
- Category-reconciliation errors: 0.
- Exact-midpoint eligible observations: 0.
- January-March documented results reproduced with 0 mismatches.
- Calendar-only daily values remained unavailable.
- Exact decimal arithmetic was used.
- Supporting historical-baseline checks produced 0 mismatches.
- During the preceding read-only analysis execution, no repository file was
  changed and no report was generated or regenerated.

The historical baseline reports do not contain a `close_location` metric.
Close-location results were therefore reconciled through exact reproduction of
the existing January-March finding and direct linked-field arithmetic and
category invariants. Historical baselines were used only for the supporting
metrics they contain.

Other raw-data quality dimensions were not revalidated during this
close-location analysis.

### Descriptive Conclusion

Across January-December 2024 Dukascopy XAUUSD one-minute BID linked
observations, strict-valid closes did not follow one stable monthly lower-half
or upper-half category direction. January, May, and June had lower-half
strict-valid majorities; February, March, and July through December had
upper-half strict-valid majorities; April had no strict majority because
lower-half and upper-half counts were tied.

The warning-review sensitivity population had the same strict-majority
direction as strict-valid in January, February, March, July, September,
October, and November. The populations diverged, or one population had no
strict majority, in April, May, June, August, and December. No eligible
observation closed exactly at the recorded daily-range midpoint.

The secondary annual nested daily-observation summaries had upper-half
majorities in both populations: 57 of 104 strict-valid observations, or 54.8%,
and 117 of 209 warning-review observations, or 56.0%. These annual summaries
hide monthly changes and strict-valid/warning-review divergence and do not
replace the primary monthly results.

This extends the January-March finding with a material qualification. It is not
a reversal because the January-March month-specific results reproduced exactly
and remain factual.

This does not establish bullish or bearish bias, directional market tendency,
support or resistance, entry or exit rules, a setup or signal, momentum or
reversal, prediction, trading edge, profitability, execution realism,
statistical significance, causation, the cause or harmlessness of
`INTERNAL_FLAT_ZERO_VOLUME`, or normal or universal XAU/USD behaviour. A
close-location value above `0.5` is not interpreted as bullish, and a value
below `0.5` is not interpreted as bearish.

### Unresolved Questions

- Strict-valid samples were small, especially February with 5 observations and
  April, July, and October with 8 observations.
- Warning treatment remains observation-level under `warning_treatment_v1`.
- `INTERNAL_FLAT_ZERO_VOLUME` remains unresolved and has not been classified as
  harmless, expected, market closure, provider outage, corruption, causal,
  explained, or reliable.
- The sample covers one provider, quote side, timeframe, and one calendar year.
- No statistical testing was performed.
- ASK remains a future prerequisite before spread-aware or execution-aware
  testing. Spread, commission, slippage, latency, and execution assumptions were
  not included.
- Tick remains conditional on a defined need for sub-minute evidence.
- No next research task has been selected from this finding alone.

## 2026-07-27 - January-December 2024 Daily Open-To-Close

Status: `descriptive finding`

Extension note: 2026-07-29 extension through January-December 2024.
Classification: `material qualification`.

### Question

For each validated month from January through December 2024, how often did the
recorded daily close finish above, below, or exactly at the recorded daily open
for `strict_valid` observations, with `warning_review` reported separately as
a labelled sensitivity view and `calendar_only`/`excluded_unusable` retained
only as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1min
- Timezone: UTC
- Calendar period: January-December 2024
- Primary input: provenance-linked daily observation reports
- Access contract: `research_observation_contract_v1`
- Quality treatment: `warning_treatment_v1`

This is not a universal XAU/USD market record.

### Source Reports

Primary row-level source reports loaded through
`research_observations.load_linked_reports(...)`:

- `reports/linked_observation_report_2024-01-01_to_2024-01-31.csv`
- `reports/linked_observation_report_2024-02-01_to_2024-02-29.csv`
- `reports/linked_observation_report_2024-03-01_to_2024-03-31.csv`
- `reports/linked_observation_report_2024-04-01_to_2024-04-30.csv`
- `reports/linked_observation_report_2024-05-01_to_2024-05-31.csv`
- `reports/linked_observation_report_2024-06-01_to_2024-06-30.csv`
- `reports/linked_observation_report_2024-07-01_to_2024-07-31.csv`
- `reports/linked_observation_report_2024-08-01_to_2024-08-31.csv`
- `reports/linked_observation_report_2024-09-01_to_2024-09-30.csv`
- `reports/linked_observation_report_2024-10-01_to_2024-10-31.csv`
- `reports/linked_observation_report_2024-11-01_to_2024-11-30.csv`
- `reports/linked_observation_report_2024-12-01_to_2024-12-31.csv`

Supporting context used the corresponding twelve existing monthly data
manifests, historical baseline reports, and internal flat zero-volume diagnostic
reports. Historical baseline reports do not contain `daily_open`,
`daily_close`, or `open_to_close_change`, so they were used only for the
supporting coverage, availability, and daily-range metrics they contain.

### Category And Magnitude Definitions

Linked fields used:

- `date`
- `quality_tier`
- `daily_open`
- `daily_close`

Exact decimal arithmetic was used:

```text
open_to_close_change = daily_close - daily_open
absolute_open_to_close_change = abs(open_to_close_change)
```

Quote-unit statistics are displayed to three decimal places using
`ROUND_HALF_UP` to `0.001`. Category percentages are displayed to one decimal
place using `ROUND_HALF_UP` to `0.1`.

Each eligible observation was assigned to exactly one category:

- `close_above_open`: `open_to_close_change > 0`
- `close_below_open`: `open_to_close_change < 0`
- `close_equal_open`: `open_to_close_change == 0`

No tolerance or approximate-equality category was used. Price changes are
descriptive quote-unit differences, not returns, profit, or tradable P&L.

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |
| April | 30 | 8 | 18 | 4 | 0 |
| May | 31 | 9 | 18 | 4 | 0 |
| June | 30 | 9 | 16 | 5 | 0 |
| July | 31 | 8 | 19 | 4 | 0 |
| August | 31 | 9 | 17 | 5 | 0 |
| September | 30 | 9 | 17 | 4 | 0 |
| October | 31 | 8 | 19 | 4 | 0 |
| November | 30 | 9 | 16 | 5 | 0 |
| December | 31 | 12 | 15 | 4 | 0 |
| Total | 366 | 104 | 209 | 53 | 0 |

Eligible counts were identical to strict-valid and warning-review counts.
Missing daily-open or daily-close values occurred only on `calendar_only`
rows. Calendar-only daily-open and daily-close values remained unavailable
rather than being interpreted as zero.

Eligible open-to-close observations: 313.

### Primary Strict-Valid Result

Primary descriptive result under `warning_treatment_v1`:

| Month | N | Close above open | Close below open | Close equal open | Minimum change | Median change | Mean change | Maximum change | Median absolute change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 9 | 4 (44.4%) | 5 (55.6%) | 0 (0.0%) | -2.710 | -0.190 | 1.450 | 13.620 | 2.180 |
| February | 5 | 2 (40.0%) | 3 (60.0%) | 0 (0.0%) | -15.450 | -0.360 | -1.058 | 9.610 | 1.850 |
| March | 9 | 7 (77.8%) | 2 (22.2%) | 0 (0.0%) | -16.680 | 2.530 | 8.126 | 42.133 | 5.970 |
| April | 8 | 4 (50.0%) | 4 (50.0%) | 0 (0.0%) | -33.680 | 3.245 | 2.773 | 39.520 | 11.310 |
| May | 9 | 5 (55.6%) | 4 (44.4%) | 0 (0.0%) | -16.870 | 0.740 | 2.504 | 36.740 | 3.087 |
| June | 9 | 2 (22.2%) | 7 (77.8%) | 0 (0.0%) | -83.260 | -1.677 | -10.981 | 30.039 | 3.690 |
| July | 8 | 5 (62.5%) | 3 (37.5%) | 0 (0.0%) | -40.663 | 4.835 | 3.378 | 34.050 | 9.684 |
| August | 9 | 4 (44.4%) | 5 (55.6%) | 0 (0.0%) | -16.530 | -1.993 | 6.501 | 49.619 | 4.510 |
| September | 9 | 5 (55.6%) | 4 (44.4%) | 0 (0.0%) | -20.120 | 0.300 | 2.681 | 34.379 | 5.483 |
| October | 8 | 4 (50.0%) | 4 (50.0%) | 0 (0.0%) | -8.433 | 1.587 | 7.061 | 27.440 | 5.825 |
| November | 9 | 6 (66.7%) | 3 (33.3%) | 0 (0.0%) | -22.700 | 4.937 | 4.511 | 46.797 | 6.997 |
| December | 12 | 6 (50.0%) | 6 (50.0%) | 0 (0.0%) | -33.149 | -0.281 | -0.509 | 29.070 | 5.090 |

Strict-valid strict-majority interpretation:

- Above-open strict-majority months: March, May, July, September, November.
- Below-open strict-majority months: January, February, June, August.
- No-strict-majority months: April, October, December.

The no-majority strict-valid months had tied above-open and below-open counts.
No strict-valid equality occurred.

Strict majority means the category count exceeds half of eligible observations;
largest category is not used as a synonym for strict majority.

### Warning-Review Sensitivity

`warning-review sensitivity`:

| Month | N | Close above open | Close below open | Close equal open | Minimum change | Median change | Mean change | Maximum change | Median absolute change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 18 | 9 (50.0%) | 8 (44.4%) | 1 (5.6%) | -25.980 | 0.617 | -2.323 | 14.170 | 7.630 |
| February | 20 | 11 (55.0%) | 9 (45.0%) | 0 (0.0%) | -27.350 | 1.382 | 0.428 | 14.890 | 5.487 |
| March | 16 | 12 (75.0%) | 4 (25.0%) | 0 (0.0%) | -26.670 | 8.872 | 7.689 | 46.870 | 14.210 |
| April | 18 | 10 (55.6%) | 8 (44.4%) | 0 (0.0%) | -52.740 | 1.891 | 1.291 | 41.230 | 15.430 |
| May | 18 | 9 (50.0%) | 9 (50.0%) | 0 (0.0%) | -50.207 | 0.504 | 0.067 | 37.609 | 18.492 |
| June | 16 | 11 (68.8%) | 5 (31.3%) | 0 (0.0%) | -21.817 | 6.522 | 5.951 | 31.430 | 14.999 |
| July | 19 | 10 (52.6%) | 9 (47.4%) | 0 (0.0%) | -35.010 | 3.273 | 5.011 | 45.740 | 15.870 |
| August | 17 | 8 (47.1%) | 9 (52.9%) | 0 (0.0%) | -36.190 | -0.210 | -0.142 | 47.590 | 11.341 |
| September | 17 | 10 (58.8%) | 7 (41.2%) | 0 (0.0%) | -27.823 | 4.530 | 6.379 | 46.569 | 9.850 |
| October | 19 | 11 (57.9%) | 8 (42.1%) | 0 (0.0%) | -38.729 | 8.590 | 3.761 | 30.570 | 13.190 |
| November | 16 | 9 (56.3%) | 7 (43.8%) | 0 (0.0%) | -109.350 | 3.200 | -8.359 | 42.900 | 22.130 |
| December | 15 | 8 (53.3%) | 7 (46.7%) | 0 (0.0%) | -59.217 | 0.280 | -2.720 | 35.383 | 14.204 |

Warning-review strict-majority interpretation:

- Above-open strict-majority months: February, March, April, June, July,
  September, October, November, December.
- Below-open strict-majority month: August.
- No-strict-majority months: January, May.

Equal-open warning-review observation:

```text
2024-01-09 warning_review close_equal_open
```

January warning-review had `close_above_open` as the largest category but not a
strict majority. May warning-review had tied above-open and below-open counts.
No eligible equality occurred after January.

Both populations had the same strict-majority category in March, July, August,
September, and November. Other months diverged or included a no-majority
population.

### Annual Nested Summary

January-December nested summaries of daily observations within calendar months:

| Population | N | Close above open | Close below open | Close equal open | Minimum change | Median change | Mean change | Maximum change | Median absolute change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| strict_valid | 104 | 54 (51.9%) | 50 (48.1%) | 0 (0.0%) | -83.260 | 0.420 | 2.187 | 49.619 | 5.412 |
| warning_review sensitivity | 209 | 118 (56.5%) | 90 (43.1%) | 1 (0.5%) | -109.350 | 2.441 | 1.472 | 47.590 | 12.853 |

These are secondary nested summaries of daily observations within calendar
months. They do not treat the twelve months as independent observations, and
they do not replace the monthly findings. Independently rounded warning-review
category percentages total 100.1%. This is a display-rounding effect; the exact
category counts reconcile to 209.

### Magnitude Comparison

Category counts and signed magnitude summaries answer different questions. A
month can contain more below-open observations but still have a positive mean
when a smaller number of positive changes are larger in magnitude. Signed means
and medians are descriptive quote-unit summaries only, not market bias, profit,
or trade performance.

Warning-review median absolute open-to-close change exceeded the strict-valid
median absolute open-to-close change in all twelve months. This descriptive
difference does not show that the warning condition caused or explains the
larger observed magnitudes.

### Quality And Diagnostic Context

Warning-review reason context:

```text
INTERNAL_FLAT_ZERO_VOLUME = 209 warning_review observations
```

Calendar-only reason context:

```text
NO_ACTIVE_CANDLES = 53 calendar_only observations
```

Diagnostic annual totals:

```text
affected dates: 209
runs: 250
run rows: 13,423
Tokyo overlap rows: 12
London overlap rows: 1
New York overlap rows: 1,067
outside configured session rows: 12,343
```

The diagnostic context is separate from the open-to-close calculation. It does
not show that `INTERNAL_FLAT_ZERO_VOLUME` caused any open-to-close category,
difference, or magnitude.

### Distinction From Close-Location Finding

Open-to-close classification and close location within the daily range are not
interchangeable. A daily close can finish above the recorded open while still
being located in the lower half of the daily range, or finish below the recorded
open while being located in the upper half of the daily range. These examples
do not establish any market cause.

### Loader Practicality Evidence

- The twelve linked reports were loaded through
  `research_observations.load_linked_reports(...)`.
- 366 observations were loaded.
- Population counts were `104 / 209 / 53 / 0`.
- Chronological order was preserved.
- Five compatible software revisions were retained.
- No loader validation failed.
- Primary linked rows did not require ad hoc CSV parsing.
- The loader handled loading, validation, provenance retention, blank
  semantics, and population separation.
- Remaining custom work was limited to the research-specific decimal
  calculations, monthly grouping, magnitude summaries, cross-finding checks,
  and separate warning-context reads.

This does not establish that every future analysis will require no loader
expansion.

### Reconciliation

- The corrected January-March tables reproduced with zero mismatches.
- All 313 eligible observations had usable Decimal daily-open and daily-close
  values.
- Ineligible eligible-tier rows: 0.
- Invalid Decimal rows: 0.
- Signed-change arithmetic errors: 0.
- Absolute-change errors: 0.
- Category-assignment errors: 0.
- Category/sign mismatches: 0.
- Category-total mismatches: 0.
- Every eligible row received exactly one sign-consistent category.
- Monthly category totals reconciled.
- The only equal-open row reproduced: `2024-01-09 warning_review
  close_equal_open`.
- Historical baseline reports do not contain `daily_open`, `daily_close`, or
  `open_to_close_change`. Open-to-close results were therefore reconciled
  through corrected January-March reproduction and direct linked-field Decimal
  arithmetic and category invariants.
- Historical baselines were used only for the supporting metrics they contain.
- Supported baseline rows checked: 192.
- Baseline missing-row count: 0.
- Baseline duplicate-row count: 0.
- Baseline value-mismatch count: 0.
- No report was generated or regenerated during the read-only execution.

### Descriptive Conclusion

Across January-December 2024 Dukascopy XAUUSD one-minute BID linked
observations, strict-valid daily close-versus-open classification varied by
month rather than following one stable monthly direction. Strict-valid had
above-open strict majorities in five months, below-open strict majorities in
four months, and tied above/below counts in three months.

The warning-review sensitivity population had above-open strict majorities in
nine months, a below-open strict majority in August, and no strict majority in
January or May. Both populations had the same strict-majority category in
March, July, August, September, and November.

Warning-review median absolute open-to-close change exceeded the strict-valid
median absolute change in all twelve months. This descriptive difference does
not show that the warning condition caused or explains the larger observed
magnitudes.

The secondary annual nested summaries had above-open strict majorities in both
populations, but the annual view hides monthly ties, below-open months, and
quality-tier divergence.

This extension is classified as `material qualification`. It is not a reversal
because the committed January-March month-specific observations reproduced
exactly and remain factual.

### Interpretation Limits

This finding does not establish bullish or bearish bias, directional market
tendency, support or resistance, entry or exit rules, a setup or signal,
momentum or reversal, prediction, trading edge, profitability, execution
realism, statistical significance, causation, the cause or harmlessness of
`INTERNAL_FLAT_ZERO_VOLUME`, or normal or universal XAU/USD behaviour.

The evidence remains the documented Dukascopy XAUUSD one-minute BID record in
UTC. ASK remains a future prerequisite for spread-aware or execution-aware
testing. Tick remains conditional on a defined sub-minute requirement.

### Unresolved Questions

- Strict-valid samples were small, especially February with 5 observations and
  April, July, and October with 8 observations.
- Warning treatment remains observation-level under `warning_treatment_v1`.
- Warning causes remain unresolved.
- The sample covers one provider, instrument, quote side, timeframe, and
  one calendar year.
- No statistical testing was performed.
- ASK, spread, commission, slippage, latency, and execution assumptions were
  not included.
- No next research task has been selected from this finding alone.

## 2026-07-27 - January-April 2024 Elapsed Time Between Daily Extrema

Status: `descriptive finding`

### Question

For each validated month from January through April 2024, how much elapsed
time separated the recorded daily high and recorded daily low for
`strict_valid` observations, with `warning_review` reported separately as a
labelled sensitivity view and `calendar_only`/`excluded_unusable` retained
only as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1 minute
- Timezone: UTC
- Calendar period: January-April 2024
- Primary input: provenance-linked daily observation reports
- Access contract: `research_observation_contract_v1`
- Quality treatment: `warning_treatment_v1`

This is not a universal XAU/USD market record.

### Source Reports

Primary row-level source reports loaded through
`research_observations.load_linked_reports(...)`:

- `reports/linked_observation_report_2024-01-01_to_2024-01-31.csv`
- `reports/linked_observation_report_2024-02-01_to_2024-02-29.csv`
- `reports/linked_observation_report_2024-03-01_to_2024-03-31.csv`
- `reports/linked_observation_report_2024-04-01_to_2024-04-30.csv`

Warning context reports:

- `reports/data_manifest_2024-01-01_to_2024-01-31.csv`
- `reports/data_manifest_2024-02-01_to_2024-02-29.csv`
- `reports/data_manifest_2024-03-01_to_2024-03-31.csv`
- `reports/data_manifest_2024-04-01_to_2024-04-30.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-02-01_to_2024-02-29.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-03-01_to_2024-03-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-04-01_to_2024-04-30.csv`

Raw CSVs were read only for bounded repeated-extremum tie checks:

- `data_raw/XAUUSD_2024-01-15_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-01-31_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-02-02_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-03-14_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-03-18_1min_BID_UTC.csv`
- eligible April raw CSVs for the April repeated-extremum scan; only
  `data_raw/XAUUSD_2024-04-09_1min_BID_UTC.csv` contained a repeated daily
  extremum.

### Timestamp And Gap Definitions

Linked fields used:

- `date`
- `quality_tier`
- `time_of_daily_high_utc`
- `time_of_daily_low_utc`
- `daily_high`
- `daily_low`

The timestamps are UTC one-minute candle opening times in `HH:MM:SS` format.
All eligible timestamps had seconds equal to `00`, so integer minute
differences were reported. Both extrema belong to the same requested UTC date;
no overnight or circular-clock adjustment was applied. Equal extrema use the
first active-candle occurrence after edge filtering, and that behaviour is
protected by dedicated `session_report.py` regression tests for equal
daily-high and equal daily-low ties. Events occurring within one candle cannot
be internally ordered.

Calculations:

```text
signed_gap_minutes =
    recorded daily-high timestamp
    minus recorded daily-low timestamp

absolute_gap_minutes =
    abs(signed_gap_minutes)
```

Interpretation:

```text
positive signed gap = recorded high occurred after recorded low
negative signed gap = recorded high occurred before recorded low
zero = both were recorded in the same minute
```

No arbitrary duration bands were used.

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |
| April | 30 | 8 | 18 | 4 | 0 |

Combined January-April coverage:

```text
total = 121
strict_valid = 31
warning_review = 72
calendar_only = 18
excluded_unusable = 0
```

All strict-valid and warning-review observations had both extrema timestamps.
Missing timestamps occurred only on `calendar_only` rows:

| Month | Missing timestamps |
| --- | ---: |
| January | 4 |
| February | 4 |
| March | 6 |
| April | 4 |

Calendar-only timestamps remained unavailable rather than being interpreted as
midnight. No eligible observation had both extrema recorded in the same minute.

### Primary Strict-Valid Result

Primary descriptive result under `warning_treatment_v1`, in minutes:

| Month | N | Minimum absolute gap | Median absolute gap | Mean absolute gap | Maximum absolute gap | High before low | Low before high | Same minute |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 9 | 4 | 26 | 183.333 | 816 | 4 | 5 | 0 |
| February | 5 | 4 | 24 | 84.2 | 341 | 1 | 4 | 0 |
| March | 9 | 19 | 119 | 408.444 | 1,236 | 2 | 7 | 0 |
| April | 8 | 1 | 129 | 283 | 940 | 6 | 2 | 0 |

Strict-valid observations:

```text
January
2024-01-01 high 23:04 / low 23:00 / signed +4 / absolute 4
2024-01-05 high 15:26 / low 13:31 / signed +115 / absolute 115
2024-01-07 high 23:21 / low 23:42 / signed -21 / absolute 21
2024-01-12 high 14:37 / low 01:01 / signed +816 / absolute 816
2024-01-14 high 23:44 / low 23:31 / signed +13 / absolute 13
2024-01-19 high 13:32 / low 05:41 / signed +471 / absolute 471
2024-01-21 high 23:00 / low 23:26 / signed -26 / absolute 26
2024-01-26 high 13:30 / low 16:14 / signed -164 / absolute 164
2024-01-28 high 23:29 / low 23:49 / signed -20 / absolute 20

February
2024-02-02 high 13:16 / low 14:03 / signed -47 / absolute 47
2024-02-04 high 23:05 / low 23:00 / signed +5 / absolute 5
2024-02-11 high 23:04 / low 23:00 / signed +4 / absolute 4
2024-02-16 high 19:17 / low 13:36 / signed +341 / absolute 341
2024-02-25 high 23:24 / low 23:00 / signed +24 / absolute 24

March
2024-03-01 high 18:44 / low 08:52 / signed +592 / absolute 592
2024-03-03 high 23:19 / low 23:00 / signed +19 / absolute 19
2024-03-10 high 23:41 / low 22:59 / signed +42 / absolute 42
2024-03-15 high 09:58 / low 17:57 / signed -479 / absolute 479
2024-03-17 high 23:59 / low 22:00 / signed +119 / absolute 119
2024-03-22 high 00:38 / low 17:28 / signed -1,010 / absolute 1,010
2024-03-24 high 23:51 / low 22:35 / signed +76 / absolute 76
2024-03-28 high 20:49 / low 00:13 / signed +1,236 / absolute 1,236
2024-03-31 high 23:46 / low 22:03 / signed +103 / absolute 103

April
2024-04-05 high 17:11 / low 01:31 / signed +940 / absolute 940 / low_before_high
2024-04-07 high 22:05 / low 22:19 / signed -14 / absolute 14 / high_before_low
2024-04-12 high 15:04 / low 19:03 / signed -239 / absolute 239 / high_before_low
2024-04-14 high 22:08 / low 22:27 / signed -19 / absolute 19 / high_before_low
2024-04-19 high 01:46 / low 11:12 / signed -566 / absolute 566 / high_before_low
2024-04-21 high 22:00 / low 22:01 / signed -1 / absolute 1 / high_before_low
2024-04-26 high 09:12 / low 01:13 / signed +479 / absolute 479 / low_before_high
2024-04-28 high 22:00 / low 22:06 / signed -6 / absolute 6 / high_before_low
```

April strict-valid minimum and maximum:

```text
minimum = 1 minute on 2024-04-21
maximum = 940 minutes on 2024-04-05
```

Simple January-April strict-valid audit summary, not a universal timing
characteristic:

```text
N = 31
median = 76
mean = 258.419
```

The per-month strict-valid results remain primary.

### Warning-Review Sensitivity

`warning-review sensitivity`, in minutes:

| Month | N | Minimum absolute gap | Median absolute gap | Mean absolute gap | Maximum absolute gap | High before low | Low before high | Same minute |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 18 | 58 | 444.5 | 522.889 | 1,132 | 13 | 5 | 0 |
| February | 20 | 11 | 444.5 | 427.2 | 835 | 11 | 9 | 0 |
| March | 16 | 396 | 731 | 741.688 | 1,133 | 5 | 11 | 0 |
| April | 18 | 53 | 572 | 622.556 | 1,262 | 7 | 11 | 0 |

April warning-review sensitivity minimum and maximum:

```text
minimum = 53 minutes on 2024-04-04
maximum = 1,262 minutes on 2024-04-02
```

Warning context:

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows |
| --- | --- | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 |
| April | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 18 | 1,081 |

The warning context is separate from the elapsed-time calculation. It does not
show that `INTERNAL_FLAT_ZERO_VOLUME` caused any elapsed-time difference.

Simple January-April warning-review audit summary, not pooled with strict-valid:

```text
N = 72
median = 557
mean = 569.847
```

### Tie-Convention Sensitivity

Known repeated-extremum checks:

| Date | Tier | Repeated extremum | First-occurrence absolute gap | Last-occurrence absolute gap | Change |
| --- | --- | --- | ---: | ---: | ---: |
| 2024-01-15 | warning-review | high | 518 | 523 | +5 |
| 2024-01-31 | warning-review | low | 296 | 323 | +27 |
| 2024-02-02 | strict-valid | high | 47 | 46 | -1 |
| 2024-03-14 | warning-review | high | 879 | 876 | -3 |
| 2024-03-18 | warning-review | low | 561 | 434 | -127 |
| 2024-04-09 | warning-review | high and low | 504 | 504 | 0 |

No sequence category changed. No monthly minimum changed. No monthly maximum
changed.

Monthly statistic changes under last equal-extremum occurrence:

- February strict-valid mean changed from `84.2` to `84`.
- January warning-review median changed from `444.5` to `447`.
- January warning-review mean changed from `522.889` to `524.667`.
- March warning-review mean changed from `741.688` to `733.562`.
- All other reported monthly statistics were unchanged.

The elapsed-time result showed limited dependence on a small number of
repeated-extremum observations. The first-occurrence convention affected some
monthly means and one median, but did not change sequence categories or
monthly minimum and maximum gaps.

April repeated-extremum check:

```text
2024-04-09
quality tier: warning_review

repeated daily high:
first occurrence: 09:28
last occurrence: 09:30

repeated daily low:
first occurrence: 01:04
last occurrence: 01:06

first-occurrence gap:
signed +504
absolute 504

consistent last-occurrence gap:
signed +504
absolute 504

ordering under both:
low_before_high
```

This was the only eligible April observation with a repeated daily extremum.
No April strict-valid repeated extremum was found. The absolute-gap difference
was zero, and no April minimum, median, mean, maximum, or ordering count
changed. The April assessment was `no dependence observed`. This conclusion is
limited to April and does not prove tie handling is irrelevant in other months
or for other statistics.

Platform behaviour was not changed.

### Relationship To April Ordering

April strict-valid ordering was `6/8 high_before_low`. Ordering records
sequence, while elapsed separation records duration. April's changed ordering
majority does not itself establish any change in gap magnitude, and no causal
relationship between ordering and elapsed separation was tested.

### Distinction From Related Findings

This elapsed-time finding is distinct from daily-extrema ordering, which
records which event occurred first, and from daily-extrema UTC-hour frequency,
which records the clock-hour placement of each event. It is also distinct from
daily open-to-close direction, close location within the daily range, and
daily-range magnitude. Elapsed separation measures the number of minutes
between the two recorded events.

### Loader Practicality Evidence

- The four linked reports were loaded through
  `research_observations.load_linked_reports(...)`.
- 121 observations were loaded.
- Population counts were `31 / 72 / 18 / 0`.
- Chronological order was preserved.
- Four compatible software revisions were retained.
- Duplicate identities were zero.
- No loader validation failed.
- The loader provided linked-row loading, validation, provenance retention,
  blank semantics, and quality-tier separation.
- Remaining custom work was limited to timestamp parsing, minute-gap
  calculations, monthly grouping, the bounded April repeated-extremum scan,
  and separate warning-context reads.
- No missing loader capability materially complicated the analysis.

This does not establish that every future timing analysis will need no
interface changes.

### Reconciliation

- Every requested date appeared once.
- All strict-valid and warning-review observations had both timestamps.
- All eligible timestamps had seconds equal to `00`.
- Calendar-only timestamps remained unavailable.
- Raw CSVs were read only for the prior five known tie checks and the bounded
  April repeated-extremum scan.
- No repository file was changed during the preceding read-only execution.
- No report was generated or regenerated during the preceding read-only
  execution.

Other raw-data quality dimensions were not revalidated during this
elapsed-time analysis.

### Descriptive Conclusion

In the strict-valid January-March 2024 observations, the median absolute
separation between the recorded daily high and low was 26 minutes in January,
24 minutes in February, and 119 minutes in March. In April 2024, the
strict-valid median absolute separation was 129 minutes and the mean was 283
minutes. The minimum was one minute and the maximum was 940 minutes.

April's strict-valid median was higher than the January, February, and March
medians. Its mean was higher than January and February but lower than March.
Its minimum was the smallest of the four months, while its maximum was below
March but above January and February.

April warning-review had a median absolute gap of 572 minutes and a mean of
622.556 minutes, compared with strict-valid values of 129 and 283 minutes.
Warning-review medians were higher than strict-valid medians in every month
from January through April.

April extends the existing elapsed-time finding without material revision. The
earlier finding did not establish a stable cross-month progression, and April
adds another bounded monthly observation while preserving the separately
reported warning-review-versus-strict median comparison.

The quality-tier relationship must remain statistic-specific. April
warning-review minimum, median, mean, and maximum were all higher than the
corresponding strict-valid values, but maxima and other summaries were not
uniformly ordered across every earlier month.

March contained the largest strict-valid observed gap, 1,236 minutes on
2024-03-28. No eligible observation had both extrema recorded in the same
minute. Samples were small, particularly February strict-valid with 5
observations and April strict-valid with 8 observations.

### Interpretation Limits

This finding does not establish reversal timing, a preferred entry or exit
time, a trading window, support or resistance, a setup or signal, prediction,
trading edge, profitability, execution realism, statistical significance,
market causation, the cause or harmlessness of `INTERNAL_FLAT_ZERO_VOLUME`, or
normal or universal XAU/USD behaviour.

### Unresolved Questions

- Strict-valid samples were small.
- February had five strict-valid observations.
- April had eight strict-valid observations.
- Gaps use recorded one-minute candle opening times.
- Events inside one candle cannot be internally ordered.
- Warning treatment remains observation-level under `warning_treatment_v1`.
- First-occurrence extrema semantics may affect gap values when extrema repeat,
  despite no April effect.
- Warning causes remain unresolved.
- The sample covers one provider, instrument, quote side, timeframe, and
  four-month period.
- No statistical testing was performed.
- No serial-dependence modelling was performed.
- No execution assumptions were included.
- The analysis was descriptive rather than predictive.
- No next research task has been selected from this finding alone.
