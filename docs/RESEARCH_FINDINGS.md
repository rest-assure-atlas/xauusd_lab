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

## 2026-07-26 - January-April 2024 Daily-Range Distribution

Status: `descriptive finding`

Extended through April 2024 on 2026-07-27 without material revision.

### Question

For each validated month from January through April 2024, what is the
descriptive distribution of daily range for `strict_valid` linked observations,
with `warning_review` daily range reported separately as a labelled sensitivity
view and `calendar_only`/`excluded_unusable` reported only as coverage?

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

This is not a universal XAU/USD record.

### Source Reports

Primary row-level source reports:

- `reports/linked_observation_report_2024-01-01_to_2024-01-31.csv`
- `reports/linked_observation_report_2024-02-01_to_2024-02-29.csv`
- `reports/linked_observation_report_2024-03-01_to_2024-03-31.csv`
- `reports/linked_observation_report_2024-04-01_to_2024-04-30.csv`

Reconciliation reports:

- `reports/historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv`
- `reports/historical_baseline_linked_observation_report_2024-02-01_to_2024-02-29.csv`
- `reports/historical_baseline_linked_observation_report_2024-03-01_to_2024-03-31.csv`
- `reports/historical_baseline_linked_observation_report_2024-04-01_to_2024-04-30.csv`

Warning context reports:

- `reports/data_manifest_2024-01-01_to_2024-01-31.csv`
- `reports/data_manifest_2024-02-01_to_2024-02-29.csv`
- `reports/data_manifest_2024-03-01_to_2024-03-31.csv`
- `reports/data_manifest_2024-04-01_to_2024-04-30.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-02-01_to_2024-02-29.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-03-01_to_2024-03-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-04-01_to_2024-04-30.csv`

### Calculation Contract

The extension used the linked fields `date`, `quality_tier`, `daily_high`,
`daily_low`, and `daily_range`. For every eligible `strict_valid` and
`warning_review` observation, exact `Decimal` arithmetic verified:

```text
recalculated_daily_range = daily_high - daily_low
```

Every stored range matched its recalculated value. Range mismatches were `0`.
Missing daily-range values occurred only on `calendar_only` rows and remained
unavailable rather than being interpreted as zero.

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |
| April | 30 | 8 | 18 | 4 | 0 |

Unavailable daily-range values occurred only for `calendar_only` observations
and remained unavailable rather than being converted to zero.

Combined January-April coverage was 121 observations: 31 `strict_valid`, 72
`warning_review`, 18 `calendar_only`, and 0 `excluded_unusable`. All
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

April strict-valid observations:

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

April warning-review observations:

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

### Warning Context

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows |
| --- | --- | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 |
| April | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 18 | 1,081 |

The diagnostic run counts and run rows are warning context only. They are not
additional daily-range statistics.

### Reconciliation

- The statistics were independently calculated from linked observation rows
  loaded through `research_observations.load_linked_reports(...)`.
- All eight monthly population summaries matched their corresponding
  historical-baseline `range_summary` rows exactly at three decimals.
- Baseline mismatches were `0`, including rounding-only differences.
- Warning-reason baseline rows also matched.
- No provenance or schema incompatibility was found.
- 121 observations loaded; chronological and compatibility validation passed;
  four software revisions were retained; duplicate identities were `0`; blank
  calendar-only ranges remained unavailable; no primary linked-row ad hoc CSV
  parsing or loader expansion was needed.
- During the preceding read-only analysis execution, no repository files were
  modified.

Raw files were not revalidated during this specific analysis. Earlier pipeline
validations remain separate evidence.

### Descriptive Conclusion

Across January through April 2024, the warning-review median and mean daily
ranges were higher than the strict-valid median and mean in each month. April
continued this previously documented comparison: warning-review median `40.305`
versus strict-valid `25.977`, and warning-review mean `40.896` versus
strict-valid `36.707`.

April had the largest strict-valid monthly median, mean, and maximum in the
current four-month sample. April also had the largest warning-review median and
mean, while the largest warning-review maximum remained March.

The relationship was mixed by statistic. Warning-review minima, medians, and
means were higher in all four months, but monthly maxima were not consistently
ordered: strict-valid maxima were higher in January and April, while
warning-review maxima were higher in February and March.

April extends the existing finding without material revision. It preserves the
previously documented monthly median and mean comparison, while reinforcing that
broader distributional comparisons must remain statistic-specific.

This does not establish that warnings caused larger ranges, that
`INTERNAL_FLAT_ZERO_VOLUME` caused the difference, that warning-review
observations are invalid, that warning-review observations are equivalent to
strict-valid observations, a volatility regime, a breakout condition, stable or
universal market behaviour, market causation, normal XAU/USD behaviour,
statistical significance, prediction, support or resistance, a setup or signal,
trading edge, profitability, or execution realism.

### Unresolved Questions

- The cause and practical meaning of `INTERNAL_FLAT_ZERO_VOLUME` remain
  unresolved.
- Strict-valid monthly samples remain small; February has 5 observations and
  April has 8 observations.
- Warning treatment remains observation-level.
- The evidence covers one provider, instrument, BID quote side, timeframe, and
  four months.
- No statistical testing was performed.
- Overlapping or serially related observations were not modelled.
- ASK, spread, commission, slippage, latency, and execution assumptions were
  not included.
- The analysis is descriptive rather than predictive.
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

## 2026-07-27 - January-March 2024 Daily Close Location

Status: `descriptive finding`

### Question

For each validated month from January through March 2024, where did the
recorded daily close occur within that day's recorded high-to-low range for
`strict_valid` observations, with `warning_review` reported separately as a
labelled sensitivity view and `calendar_only`/`excluded_unusable` retained only
as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1 minute
- Timezone: UTC
- Calendar period: January-March 2024
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

Warning context reports:

- `reports/data_manifest_2024-01-01_to_2024-01-31.csv`
- `reports/data_manifest_2024-02-01_to_2024-02-29.csv`
- `reports/data_manifest_2024-03-01_to_2024-03-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-02-01_to_2024-02-29.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-03-01_to_2024-03-31.csv`

### Formula And Categories

Linked fields used:

- `date`
- `quality_tier`
- `daily_high`
- `daily_low`
- `daily_close`
- `daily_range`

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

Eligible counts were identical to strict-valid and warning-review counts.
Missing daily fields occurred only on `calendar_only` rows:

| Month | Missing daily fields |
| --- | ---: |
| January | 4 |
| February | 4 |
| March | 6 |

Calendar-only daily values remained unavailable rather than being interpreted
as zero.

### Primary Strict-Valid Result

Primary descriptive result under `warning_treatment_v1`:

| Month | N | Minimum | Median | Mean | Maximum | Lower half | Exact midpoint | Upper half |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 9 | 0.081956 | 0.477497 | 0.381347 | 0.581287 | 5 (55.6%) | 0 (0.0%) | 4 (44.4%) |
| February | 5 | 0.082075 | 0.582398 | 0.512864 | 0.898558 | 2 (40.0%) | 0 (0.0%) | 3 (60.0%) |
| March | 9 | 0.029143 | 0.859838 | 0.650382 | 0.936246 | 3 (33.3%) | 0 (0.0%) | 6 (66.7%) |

Strict-valid category dates:

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

Warning context:

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows |
| --- | --- | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 |

The warning context is separate from the close-location calculation. It does
not show that `INTERNAL_FLAT_ZERO_VOLUME` caused any close-location difference.

Simple warning-review audit count, not pooled with strict-valid:

```text
eligible = 54
lower_half = 24
exact_midpoint = 0
upper_half = 30
```

### Loader Practicality Evidence

- The three linked reports were loaded through
  `research_observations.load_linked_reports(...)`.
- 91 observations were loaded.
- Chronological order was preserved.
- Population counts were `23 / 54 / 14 / 0`.
- Three compatible software revisions were retained.
- No loader validation failed.
- Direct linked-row CSV parsing was not needed for the primary analysis.
- Remaining custom work was limited to the research-specific decimal
  calculation, monthly grouping, range reconciliation, and separate
  manifest/diagnostic context reads.

This does not establish that every future analysis will require no additional
work.

### Reconciliation

- Each requested date appeared exactly once.
- All strict-valid and warning-review observations were eligible.
- No eligible observation had a zero daily range.
- Stored `daily_range` reconciled exactly with `daily_high - daily_low`.
- Daily-range reconciliation mismatches: 0.
- Calendar-only daily values remained unavailable.
- Exact decimal arithmetic was used.
- No repository file was changed during the preceding read-only execution.
- No report was generated or regenerated during the preceding read-only
  execution.

Other raw-data quality dimensions were not revalidated during this
close-location analysis.

### Descriptive Conclusion

In the strict-valid January-March 2024 observations, closes were more often in
the lower half of the recorded daily range in January and more often in the
upper half in February and March. The separately labelled warning-review
sensitivity population had the same lower-half or upper-half majority in each
corresponding month. No eligible observation closed at the exact recorded range
midpoint.

The two quality populations were broadly similar in their coarse lower-half
versus upper-half category direction, but their medians and category
proportions differed by month. The median difference was small in February and
larger in January and March. This bounded comparison does not establish
equivalence or a causal warning effect.

This does not establish bullish or bearish bias, directional market tendency,
an entry or exit rule, support or resistance, a setup or signal, momentum or
reversal, prediction, trading edge, profitability, execution realism,
statistical significance, the cause or harmlessness of
`INTERNAL_FLAT_ZERO_VOLUME`, or normal or universal XAU/USD behaviour.

### Unresolved Questions

- Strict-valid samples were small, especially February with 5 observations.
- Warning treatment remains observation-level under `warning_treatment_v1`.
- Warning causes remain unresolved.
- The sample covers one provider, quote side, timeframe, and three-month
  period.
- No statistical testing was performed.
- No execution assumptions were included.
- No next research task has been selected from this finding alone.

## 2026-07-27 - January-March 2024 Daily Open-To-Close

Status: `descriptive finding`

### Question

For each validated month from January through March 2024, how often did the
recorded daily close finish above, below, or exactly at the recorded daily open
for `strict_valid` observations, with `warning_review` reported separately as
a labelled sensitivity view and `calendar_only`/`excluded_unusable` retained
only as coverage?

### Evidence Scope

- Provider: Dukascopy
- Instrument: XAUUSD
- Quote side: BID
- Timeframe: 1 minute
- Timezone: UTC
- Calendar period: January-March 2024
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

Warning context reports:

- `reports/data_manifest_2024-01-01_to_2024-01-31.csv`
- `reports/data_manifest_2024-02-01_to_2024-02-29.csv`
- `reports/data_manifest_2024-03-01_to_2024-03-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-02-01_to_2024-02-29.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-03-01_to_2024-03-31.csv`

### Category And Magnitude Definitions

Linked fields used:

- `date`
- `quality_tier`
- `daily_open`
- `daily_close`

Exact decimal arithmetic was used:

```text
open_to_close_change = daily_close - daily_open
absolute_open_to_close_change = abs(daily_close - daily_open)
```

Each eligible observation was assigned to exactly one category:

- `close_above_open`: `daily_close > daily_open`
- `close_below_open`: `daily_close < daily_open`
- `close_equal_open`: `daily_close == daily_open`

No tolerance or approximate-equality category was used. Price changes are
descriptive quote-unit differences, not returns, profit, or tradable P&L.

### Coverage

| Month | Requested | Strict valid | Warning review | Calendar only | Excluded/unusable |
| --- | ---: | ---: | ---: | ---: | ---: |
| January | 31 | 9 | 18 | 4 | 0 |
| February | 29 | 5 | 20 | 4 | 0 |
| March | 31 | 9 | 16 | 6 | 0 |

Eligible counts were identical to strict-valid and warning-review counts.
Missing daily-open or daily-close values occurred only on `calendar_only`
rows:

| Month | Missing daily open/close values |
| --- | ---: |
| January | 4 |
| February | 4 |
| March | 6 |

Calendar-only daily-open and daily-close values remained unavailable rather
than being interpreted as zero.

### Primary Strict-Valid Result

Primary descriptive result under `warning_treatment_v1`:

| Month | N | Close above open | Close below open | Close equal open | Minimum change | Median change | Mean change | Maximum change | Median absolute change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 9 | 4 (44.4%) | 5 (55.6%) | 0 (0.0%) | -2.710 | -0.190 | 1.450 | 13.620 | 2.180 |
| February | 5 | 2 (40.0%) | 3 (60.0%) | 0 (0.0%) | -15.450 | -0.360 | -1.058 | 9.610 | 1.850 |
| March | 9 | 7 (77.8%) | 2 (22.2%) | 0 (0.0%) | -16.680 | 2.530 | 8.126 | 42.133 | 5.970 |

Strict-valid category dates:

```text
January close_above_open:
2024-01-01
2024-01-05
2024-01-12
2024-01-19

January close_below_open:
2024-01-07
2024-01-14
2024-01-21
2024-01-26
2024-01-28

January close_equal_open:
none

February close_above_open:
2024-02-11
2024-02-16

February close_below_open:
2024-02-02
2024-02-04
2024-02-25

February close_equal_open:
none

March close_above_open:
2024-03-01
2024-03-03
2024-03-10
2024-03-17
2024-03-24
2024-03-28
2024-03-31

March close_below_open:
2024-03-15
2024-03-22

March close_equal_open:
none
```

Simple three-month strict-valid audit count, not a universal rate or headline
result:

```text
eligible = 23
close_above_open = 13
close_below_open = 10
close_equal_open = 0
```

The per-month strict-valid results remain primary.

### Warning-Review Sensitivity

`warning-review sensitivity`:

| Month | N | Close above open | Close below open | Close equal open | Minimum change | Median change | Mean change | Maximum change | Median absolute change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| January | 18 | 9 (50.0%) | 8 (44.4%) | 1 (5.6%) | -25.980 | 0.616 | -2.323 | 14.170 | 7.630 |
| February | 20 | 11 (55.0%) | 9 (45.0%) | 0 (0.0%) | -27.350 | 1.382 | 0.428 | 14.890 | 5.486 |
| March | 16 | 12 (75.0%) | 4 (25.0%) | 0 (0.0%) | -26.670 | 8.872 | 7.689 | 46.870 | 14.210 |

Equal-open warning-review observation:

```text
2024-01-09 warning_review
```

Warning context:

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows |
| --- | --- | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 |

The warning context is separate from the open-to-close calculation. It does
not show that `INTERNAL_FLAT_ZERO_VOLUME` caused any open-to-close difference.

Simple warning-review audit count, not pooled with strict-valid:

```text
eligible = 54
close_above_open = 32
close_below_open = 21
close_equal_open = 1
```

### Distinction From Close-Location Finding

Open-to-close classification and close location within the daily range are not
interchangeable. Verified examples:

```text
2024-01-01 strict_valid:
close above open
close located in the lower half of the daily range

2024-01-07 strict_valid:
close below open
close located in the upper half of the daily range

2024-01-09 warning_review:
close equal open
close not at the exact daily-range midpoint
```

These examples do not establish any market cause.

### Loader Practicality Evidence

- The three linked reports were loaded through
  `research_observations.load_linked_reports(...)`.
- 91 observations were loaded.
- Population counts were `23 / 54 / 14 / 0`.
- Chronological order was preserved.
- Three compatible software revisions were retained.
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

- Every requested date appeared exactly once.
- All strict-valid and warning-review observations were eligible.
- All strict-valid and warning-review observations had daily-open and
  daily-close values.
- Missing values occurred only on calendar-only rows.
- Calendar-only daily-open and daily-close values remained unavailable.
- Daily-range reconciliation mismatches: 0.
- Exact Decimal comparisons were used.
- No repository file was changed during the preceding read-only execution.
- No report was generated or regenerated during the preceding read-only
  execution.

Other raw-data quality dimensions were not revalidated during this
open-to-close analysis.

### Descriptive Conclusion

In the strict-valid January-March 2024 observations, more dates closed below
their recorded open in January and February, while more dates closed above
their recorded open in March. No strict-valid observation closed exactly at its
recorded open. In the separately labelled warning-review sensitivity
population, more dates closed above their recorded open in all three months,
with one equal-open observation in January.

The quality-tier comparison was mixed by month. January and February had
opposite category majorities between strict-valid and warning-review, while
both populations had an above-open majority in March. The signed-change
medians and category proportions also differed. These observations do not
establish a causal warning effect or a repeatable directional pattern.

### Interpretation Limits

This finding does not establish bullish or bearish bias, future direction,
directional market tendency, momentum or reversal, an entry or exit rule,
support or resistance, a setup or signal, prediction, trading edge,
profitability, execution realism, statistical significance, the cause or
harmlessness of `INTERNAL_FLAT_ZERO_VOLUME`, or normal or universal XAU/USD
behaviour.

### Unresolved Questions

- Strict-valid samples were small, especially February with 5 observations.
- Warning treatment remains observation-level under `warning_treatment_v1`.
- Warning causes remain unresolved.
- The sample covers one provider, instrument, quote side, timeframe, and
  three-month period.
- No statistical testing was performed.
- ASK, spread, commission, slippage, latency, and execution assumptions were
  not included.
- No next research task has been selected from this finding alone.

## 2026-07-27 - January-March 2024 Elapsed Time Between Daily Extrema

Status: `descriptive finding`

### Question

For each validated month from January through March 2024, how much elapsed
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
- Calendar period: January-March 2024
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

Warning context reports:

- `reports/data_manifest_2024-01-01_to_2024-01-31.csv`
- `reports/data_manifest_2024-02-01_to_2024-02-29.csv`
- `reports/data_manifest_2024-03-01_to_2024-03-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-02-01_to_2024-02-29.csv`
- `reports/internal_flat_zero_volume_diagnostic_2024-03-01_to_2024-03-31.csv`

Raw CSVs read only for the known repeated-extremum tie checks:

- `data_raw/XAUUSD_2024-01-15_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-01-31_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-02-02_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-03-14_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-03-18_1min_BID_UTC.csv`

### Timestamp And Gap Definitions

Linked fields used:

- `date`
- `quality_tier`
- `time_of_daily_high_utc`
- `time_of_daily_low_utc`

The timestamps are UTC one-minute candle opening times in `HH:MM:SS` format.
All eligible timestamps had seconds equal to `00`, so integer minute
differences were reported. Both extrema belong to the same requested UTC date;
no overnight or circular-clock adjustment was applied. Equal extrema use the
first active-candle occurrence, and that behaviour is protected by dedicated
`session_report.py` regression tests for equal daily-high and equal daily-low
ties after edge placeholder filtering.

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

All strict-valid and warning-review observations had both extrema timestamps.
Missing timestamps occurred only on `calendar_only` rows:

| Month | Missing timestamps |
| --- | ---: |
| January | 4 |
| February | 4 |
| March | 6 |

Calendar-only timestamps remained unavailable rather than being interpreted as
midnight. No eligible observation had both extrema recorded in the same minute.

### Primary Strict-Valid Result

Primary descriptive result under `warning_treatment_v1`, in minutes:

| Month | N | Minimum absolute gap | Median absolute gap | Mean absolute gap | Maximum absolute gap | Minimum-gap date | Maximum-gap date | High before low | Low before high | Same minute |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |
| January | 9 | 4 | 26 | 183.333 | 816 | 2024-01-01 | 2024-01-12 | 4 | 5 | 0 |
| February | 5 | 4 | 24 | 84.2 | 341 | 2024-02-11 | 2024-02-16 | 1 | 4 | 0 |
| March | 9 | 19 | 119 | 408.444 | 1,236 | 2024-03-03 | 2024-03-28 | 2 | 7 | 0 |

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
```

Simple three-month strict-valid audit summary, not a universal timing
characteristic:

```text
N = 23
minimum = 4
median = 76
mean = 249.87
maximum = 1,236
```

The per-month strict-valid results remain primary.

### Warning-Review Sensitivity

`warning-review sensitivity`, in minutes:

| Month | N | Minimum absolute gap | Median absolute gap | Mean absolute gap | Maximum absolute gap | Minimum-gap date | Maximum-gap date | High before low | Low before high | Same minute |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |
| January | 18 | 58 | 444.5 | 522.889 | 1,132 | 2024-01-30 | 2024-01-16 | 13 | 5 | 0 |
| February | 20 | 11 | 444.5 | 427.2 | 835 | 2024-02-18 | 2024-02-05 | 11 | 9 | 0 |
| March | 16 | 396 | 731 | 741.688 | 1,133 | 2024-03-25 | 2024-03-12 | 5 | 11 | 0 |

Warning context:

| Month | Warning reason | Affected dates | Diagnostic runs | Diagnostic run rows |
| --- | --- | ---: | ---: | ---: |
| January | `INTERNAL_FLAT_ZERO_VOLUME` | 18 | 20 | 1,232 |
| February | `INTERNAL_FLAT_ZERO_VOLUME` | 20 | 29 | 1,192 |
| March | `INTERNAL_FLAT_ZERO_VOLUME` | 16 | 23 | 909 |

The warning context is separate from the elapsed-time calculation. It does not
show that `INTERNAL_FLAT_ZERO_VOLUME` caused any elapsed-time difference.

Simple warning-review audit summary, not pooled with strict-valid:

```text
N = 54
minimum = 11
median = 557
mean = 552.278
maximum = 1,133
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

Platform behaviour was not changed.

### Distinction From Earlier Timing Findings

This elapsed-time finding is distinct from daily-extrema ordering, which
records which event occurred first, and from daily-extrema UTC-hour frequency,
which records the clock-hour placement of each event. Elapsed separation
measures the number of minutes between the two recorded events.

### Loader Practicality Evidence

- The three linked reports were loaded through
  `research_observations.load_linked_reports(...)`.
- 91 observations were loaded.
- Population counts were `23 / 54 / 14 / 0`.
- Chronological order was preserved.
- Compatible software revisions were retained.
- No loader validation failed.
- The loader provided linked-row loading, validation, provenance retention,
  blank semantics, and quality-tier separation.
- Remaining custom work was limited to timestamp parsing, minute-gap
  calculations, monthly grouping, raw tie verification, and separate
  warning-context reads.
- No missing loader capability materially complicated the analysis.

This does not establish that every future timing analysis will need no
interface changes.

### Reconciliation

- Every requested date appeared once.
- All strict-valid and warning-review observations had both timestamps.
- All eligible timestamps had seconds equal to `00`.
- Calendar-only timestamps remained unavailable.
- Raw CSVs were read only for the five known tie checks.
- No repository file was changed during the preceding read-only execution.
- No report was generated or regenerated during the preceding read-only
  execution.

Other raw-data quality dimensions were not revalidated during this
elapsed-time analysis.

### Descriptive Conclusion

In the strict-valid January-March 2024 observations, the median absolute
separation between the recorded daily high and low was 26 minutes in January,
24 minutes in February, and 119 minutes in March. The separately labelled
warning-review sensitivity medians were 444.5, 444.5, and 731 minutes
respectively.

The warning-review sensitivity population had substantially larger median
absolute gaps than the strict-valid population in all three months. This is a
visibly different bounded descriptive distribution, but it does not establish
that the warning caused the difference or that either distribution represents
normal or repeatable XAU/USD behaviour.

March contained the largest strict-valid observed gap, 1,236 minutes on
2024-03-28. No eligible observation had both extrema recorded in the same
minute. Samples were small, particularly February strict-valid with 5
observations.

### Interpretation Limits

This finding does not establish an entry or exit time, reversal timing, a
preferred trading window, support or resistance, a setup or signal, prediction,
trading edge, profitability, execution realism, statistical significance,
market causation, the cause or harmlessness of `INTERNAL_FLAT_ZERO_VOLUME`, or
normal or universal XAU/USD behaviour.

### Unresolved Questions

- Strict-valid samples were small.
- Warning treatment remains observation-level under `warning_treatment_v1`.
- First-occurrence extrema semantics affect some values.
- Warning causes remain unresolved.
- The sample covers one provider, instrument, quote side, timeframe, and
  three-month period.
- No statistical testing was performed.
- No execution assumptions were included.
- The analysis was descriptive rather than predictive.
- No next research task has been selected from this finding alone.
