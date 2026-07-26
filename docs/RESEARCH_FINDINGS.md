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
