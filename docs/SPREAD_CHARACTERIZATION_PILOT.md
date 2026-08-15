# Spread Characterization Pilot

Date: 2026-08-08

Mission: first descriptive BID/ASK close-spread characterization for the already-reconciled XAUUSD three-day pilot.

Approved range: 2024-01-09 through 2024-01-11 inclusive.

## Boundary

This report uses only `reports/bid_ask_reconciliation_2024-01-09_to_2024-01-11.csv` plus existing project session definitions and provenance context. It does not download additional ASK data, broaden the date range, model execution, test strategy performance, or make profitability claims.

All rows remain warning-review evidence. No row or subset is relabeled as strict-valid.

## Input Population

Input reconciliation file: `reports/bid_ask_reconciliation_2024-01-09_to_2024-01-11.csv`

Validated input checks:

- Paired rows: 4320
- Dates: 2024-01-09, 2024-01-10, 2024-01-11
- Pair-quality population: `warning_review_pair`: 4320
- Placeholder rows: 180
- Provenance identity: provider `Dukascopy`, instrument `XAUUSD`, timeframe `1min`
- Negative spread anomalies: 0
- Zero spread anomalies: 0
- Extreme spread anomalies: 0

The 180 placeholder rows are explicitly marked with `MARKET_CLOSED_PLACEHOLDER`, 60 rows per day.

## Implementation And Artifacts

Implementation file: `spread_characterization.py`

Generated artifacts:

- `reports/spread_characterization_2024-01-09_to_2024-01-11_summary.csv`
- `reports/spread_characterization_2024-01-09_to_2024-01-11_wide_observations.csv`

The summary CSV includes overall, day, UTC-hour, and configured-session summaries for two populations:

- `all_warning_review_pairs`: all 4320 warning-review reconciled pairs, including placeholders.
- `non_placeholder_diagnostic`: the 4140-row secondary diagnostic subset excluding rows with `MARKET_CLOSED_PLACEHOLDER`.

The diagnostic subset is not strict-valid evidence; it remains warning-review evidence.

## Spread Units

Absolute spread is the close-price difference from reconciliation:

`spread = ask_close - bid_close`

A secondary normalized diagnostic is included as bid-relative basis points:

`spread_bid_bps = spread / bid_close * 10000`

This basis-point value is a transparent normalization relative to the BID close. No pip convention is assumed.

## Overall Statistics

All warning-review pairs, including placeholders, n=4320:

- Minimum spread: 0.085000
- p05: 0.287000
- p25: 0.300000
- Median: 0.327000
- Mean: 0.331651
- p75: 0.347000
- p95: 0.440000
- p99: 0.520000
- Maximum: 0.837000
- Standard deviation: 0.048031
- Mean bid-relative spread: 1.633767 bps

Secondary non-placeholder diagnostic, n=4140:

- Minimum spread: 0.085000
- p05: 0.287000
- p25: 0.300000
- Median: 0.327000
- Mean: 0.325781
- p75: 0.340000
- p95: 0.380000
- p99: 0.468000
- Maximum: 0.837000
- Standard deviation: 0.038964
- Mean bid-relative spread: 1.604737 bps

## Day Summary

All warning-review pairs:

| Day | Count | Placeholder | Mean | Median | p95 | p99 | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024-01-09 | 1440 | 60 | 0.339265 | 0.330000 | 0.437000 | 0.520000 | 0.528000 |
| 2024-01-10 | 1440 | 60 | 0.324224 | 0.320000 | 0.440000 | 0.440000 | 0.607000 |
| 2024-01-11 | 1440 | 60 | 0.331465 | 0.320000 | 0.440000 | 0.490000 | 0.837000 |

The three days are broadly similar around the median. The maximum value differs materially, with the widest single observation on 2024-01-11 at 13:29 UTC. Given the three-day warning-review sample, this is an observation to preserve, not a causal conclusion.

## UTC Hour Summary

Each UTC hour has 180 observations across the three days. Placeholder rows are concentrated entirely in hour 22 UTC: 180 placeholder rows, 60 per day.

Hour-level means for all warning-review pairs range from 0.308750 to 0.466667. The highest hour mean is 22 UTC, driven by the market-closed placeholder population. Excluding placeholders as a secondary diagnostic reduces the overall mean and the upper percentiles.

The widest non-placeholder observations concentrate mostly near 23 UTC, with additional observations around 00-01 UTC and isolated rows at 13 UTC and 21 UTC. This is descriptive only and does not establish a recurring time-of-day effect.

## Session Summary

Configured session definitions from `sessions.json` were applied without changing methodology:

- Tokyo: 09:00-18:00 Asia/Tokyo
- London: 08:00-17:00 Europe/London
- New York: 08:00-17:00 America/New_York

These are overlapping research windows, not exclusive partitions of the day. The summary CSV marks session rows with `session_window_type=overlapping_research_window` and `session_window_exclusive=false`.

All warning-review pairs:

| Session | Count | Placeholder | Mean | Median | p95 | p99 | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| London | 1620 | 0 | 0.321307 | 0.320000 | 0.360000 | 0.390000 | 0.837000 |
| New York | 1620 | 0 | 0.325096 | 0.327000 | 0.367000 | 0.410000 | 0.837000 |
| Tokyo | 1620 | 0 | 0.326711 | 0.327000 | 0.390000 | 0.468000 | 0.490000 |

Session differences are small in central tendency. Because windows overlap and the pilot spans only three warning-review days, these values should not be interpreted as execution cost regimes.

## Placeholder Handling

The primary population includes all 4320 warning-review rows and does not silently exclude placeholders. A secondary diagnostic excludes the 180 `MARKET_CLOSED_PLACEHOLDER` rows to show their effect on descriptive statistics.

Placeholder effect:

- Full mean spread: 0.331651
- Non-placeholder diagnostic mean spread: 0.325781
- Full p95 spread: 0.440000
- Non-placeholder diagnostic p95 spread: 0.380000
- Full p99 spread: 0.520000
- Non-placeholder diagnostic p99 spread: 0.468000

The placeholder rows materially influence the upper tail, especially hour 22 UTC.

## Anomalies And Mechanical Patterns

Observed widest close-spread row:

- 2024-01-11 13:29 UTC: spread 0.837, BID close 2037.198, ASK close 2038.035, warning-review pair, not placeholder.

Other wide non-placeholder observations appear around 23 UTC on 2024-01-10 and 2024-01-11. The full-population p99 wide-observation artifact includes 71 rows, 60 of which are placeholder rows. The revised wide-observation CSV separates `all_warning_review_pairs` from `non_placeholder_diagnostic` and records the population-specific p99 threshold.

Repeated spread values are common. The most frequent values include 0.290, 0.340, 0.330, 0.320, and 0.300. This appears consistent with quoted-price granularity and the placeholder run, but it remains a pattern to preserve for later review rather than proof of provider behavior.

No evidence was found in this characterization that suggests BID/ASK swapping, negative spreads, zero spreads, extreme-spread reconciliation flags, provider mismatch, instrument mismatch, timeframe mismatch, missing side, or duplicate timestamp errors in the reconciled three-day artifact.

## Tests

Test results after implementation and reviewer revisions:

- Focused characterization tests: `Ran 5 tests`, `OK`
- Relevant side-aware tests: `Ran 119 tests`, `OK`
- Full unittest discovery: `Ran 200 tests`, `OK (skipped=3)`

The three skips are existing matplotlib-dependent chart tests. No package installation was performed.

## Reviewer Findings

An independent reviewer found no spread arithmetic or unit errors and confirmed `spread == ask_close - bid_close` for all 4320 rows.

Reviewer issues and revisions:

- Medium: the wide-observation artifact initially selected p99 rows only from the full population, causing placeholder rows to dominate the artifact. Revised by adding `population`, `wide_threshold_source`, and `wide_threshold_spread`, and by emitting both full-population and non-placeholder diagnostic wide observations.
- Medium: session summaries could be misread as exclusive time-of-day evidence. Revised by adding session metadata columns and documenting that configured sessions are overlapping research windows.
- Low: artifact names and metadata needed stronger caveats. Revised by adding sample start/end/days and `interpretation_scope=descriptive_pilot_not_execution_realism` to summary and wide-observation CSV rows.
- Low: three-day pilot limits should be encoded near outputs. Revised through the same metadata fields.

No RED or YELLOW issue was raised by the reviewer.

## Evidence Classification

Confirmed narrowly for this three-day warning-review pilot:

- The reconciled BID/ASK close spread can be described reproducibly from the paired artifact.
- The full warning-review population and placeholder diagnostic split are both visible.
- The upper tail is materially affected by market-closed placeholder rows.
- No pairing/data error is suggested by spread arithmetic or identity checks in this artifact.

Not established:

- execution realism
- strategy edge
- profitability
- broad 2024 spread behavior
- future spread behavior
- live trading costs
- causation from hour/session differences

## Next Step Assessment

Broader ASK acquisition is justified if the next research question is whether these descriptive patterns persist beyond the three-day pilot. That should be a separate bounded mission with explicit date scope, preserved side-aware provenance, and the same warning-review discipline.

Execution modelling is not justified yet. The current evidence is descriptive close-spread behavior from three warning-review days, not execution-grade cost evidence.

Recommended next bounded mission: acquire or reconcile a pre-approved, modestly broader ASK/BID sample for descriptive validation only, or repeat this characterization on a separately approved out-of-sample range before any execution modelling proposal.

## Escalation

No YELLOW or RED escalation was encountered. No package installation, new data download, date-range expansion, raw-file modification, strategy testing, or execution modelling was performed.
