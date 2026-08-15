# January 2024 ASK Scale Pilot

## Evidence Classification

This document records a descriptive market-data scale pilot for XAUUSD 1-minute ASK data from 2024-01-01 through 2024-01-31 inclusive. It does not claim execution realism, strategy edge, profitability, future behavior, or broad 2024 spread behavior.

## Resume State And Scope

The mission resumed from an interrupted partial state. Existing Jan 1-26 ASK files were verified and not redownloaded. Only the missing Jan 27-31 ASK files were acquired during the resume. Prior three-day pilot artifacts and inherited BID raw files were preserved.

Interrupted unsided January reports were audited and identified as BID-side reports: `data_manifest_2024-01-01_to_2024-01-31.csv`, `session_report_2024-01-01_to_2024-01-31.csv`, and `linked_observation_report_2024-01-01_to_2024-01-31.csv` all describe BID provenance where side metadata is present. ASK provenance for this mission uses explicit `_ASK_` report filenames.

## ASK Acquisition Coverage

Expected ASK files: 31 daily CSV files named `XAUUSD_YYYY-MM-DD_1min_ASK_UTC.csv`.

Acquired ASK files: 31 of 31. Jan 1-26 were already present from the interrupted run. Jan 27-31 were downloaded during this resume, each with 1440 rows. No missing or failed ASK files remained after the resumed acquisition.

## ASK Provenance Artifacts

Created or regenerated side-aware ASK artifacts:

- `reports/data_manifest_ASK_2024-01-01_to_2024-01-31.csv`
- `reports/session_report_ASK_2024-01-01_to_2024-01-31.csv`
- `reports/linked_observation_report_ASK_2024-01-01_to_2024-01-31.csv`
- `reports/historical_baseline_linked_observation_report_ASK_2024-01-01_to_2024-01-31.csv`
- `reports/internal_flat_zero_volume_diagnostic_ASK_2024-01-01_to_2024-01-31.csv`

The legacy diagnostic command also wrote `reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv`; the ASK-labeled copy is the clearer artifact for this mission.

## Data Quality Findings

ASK manifest counts:

- Requested dates: 31
- Processed files: 27
- Missing files: 0
- Empty files: 0
- Parse failures: 0
- No-active-candle files: 4
- Valid dates: 9
- Warning dates: 18
- Invalid dates: 0
- Not-assessed dates: 4

ASK linked-observation quality tiers:

- strict_valid: 9
- warning_review: 18
- calendar_only: 4
- excluded_unusable: 0

The main recurring warning was internal flat zero-volume behavior. The diagnostic found 20 internal flat zero-volume runs across 18 warning dates. The no-active-candle/calendar-only dates were retained explicitly rather than being dropped.

## Reconciliation Findings

Output: `reports/bid_ask_reconciliation_2024-01-01_to_2024-01-31.csv`.

Reconciliation counts:

- Total BID rows: 44640
- Total ASK rows: 44640
- Exact timestamp matches: 44640
- Missing BID rows: 0
- Missing ASK rows: 0
- Duplicate BID timestamps: 0
- Duplicate ASK timestamps: 0
- Negative spreads: 0
- Zero spreads: 0
- Extreme spreads: 0
- Pair statuses: 33300 warning_review_pair, 5580 strict_valid_pair, 5760 excluded

The excluded rows are calendar-only placeholder population from both sides. They are not treated as strict-valid and were not silently removed from the reconciliation artifact. Any spread summary using the full population therefore includes calendar-only and placeholder behavior unless the row is explicitly from the non-placeholder diagnostic population.

## Spread Characterization

Outputs:

- `reports/spread_characterization_2024-01-01_to_2024-01-31_summary.csv`
- `reports/spread_characterization_2024-01-01_to_2024-01-31_wide_observations.csv`

Spread is close-price ASK minus close-price BID in absolute price units. The normalized unit is bid-relative basis points, calculated as `spread / bid_close * 10000`. No pip convention is assumed.

Overall full reconciled spread-bearing population, including warning-review, strict-valid, excluded, and placeholder rows where present. This is a descriptive reconciliation population, not an active-market or executable spread sample:

- Count: 44640
- Placeholder count: 14372
- Min: 0.085000
- Median: 0.340000
- Mean: 0.467674
- Stddev: 0.245346
- P05 / P25 / P75 / P95 / P99: 0.290000 / 0.310000 / 0.620000 / 1.100000 / 1.100000
- Max: 2.490000
- Mean bid-relative bps: 2.298811

Secondary non-placeholder diagnostic population:

- Count: 30268
- Placeholder count: 0
- Min: 0.085000
- Median: 0.327000
- Mean: 0.328571
- Stddev: 0.053503
- P05 / P25 / P75 / P95 / P99: 0.290000 / 0.300000 / 0.347000 / 0.390000 / 0.454000
- Max: 2.490000
- Mean bid-relative bps: 1.615967

## Time Structure

Full-population daily results were materially affected by placeholder-heavy weekends and market-closed windows. Full-population day medians reached 0.620000, 0.940000, and 1.100000 on weekend/calendar-only periods, while ordinary trading-day medians were usually around 0.320000 to 0.340000. This is descriptive only and does not imply causation.

In the full population, hour 22 UTC had the highest mean spread, with 1860 placeholders out of 1860 observations and mean 0.657226. Other high full-population hours also had substantial placeholder counts.

In the non-placeholder diagnostic population, the highest hourly mean was hour 23 UTC: count 1380, median 0.360000, mean 0.401567, p95 0.587000, max 2.490000. Hour 21 UTC followed with count 1260, median 0.350000, mean 0.354809, p95 0.430050, max 1.100000.

Configured sessions were applied as overlapping research windows, not exclusive day partitions. Non-placeholder diagnostic session means were close: Tokyo 0.323813, London 0.325032, New York 0.329119. The New York window had the highest non-placeholder max at 1.100000; London max was 0.837000 and Tokyo max was 0.490000.

## Anomalies And Mechanical Patterns

No evidence was found of negative spreads, zero spreads, extreme-spread reason codes, missing side rows, duplicate timestamps, or checksum/size drift during reconciliation.

The widest non-placeholder observations clustered around late Jan 25 23:00 UTC, led by 2024-01-25 23:22:00 with spread 2.490. Additional wide observations occurred near Jan 31 23:00 UTC and Jan 1 23:00 UTC. These are descriptive observations only. The repeated placeholder spreads on no-active-candle or market-closed periods are mechanical artifacts of placeholder rows and are kept explicit.

## Scaling Observations

The pipeline scaled from three days to January without package installation, schema weakening, BID/ASK side contamination, missing files after resume, timestamp mismatch, or reconciliation failure when explicit ASK provenance paths were supplied.

One maintainability issue was observed: several CLIs still default to legacy BID or three-day ASK paths, and the diagnostic output filename is side-ambiguous. The mission worked around this with explicit function calls and an ASK-labeled diagnostic copy. Before full-year work, side-aware CLI options and side-aware diagnostic output names would reduce operator error.

The spread-characterization validator was adjusted so pair-quality and anomaly errors are reported before row-count errors. This fixed existing focused tests and does not change January artifacts. Two guardrail issues remain for future full-year reuse: the spread script still has stale three-day default paths, and downstream spread characterization relies on reconciliation for BID/ASK source filename and checksum validation rather than independently revalidating every source-identity field.

## Tests

Relevant focused suite with `PYTHONPATH=tests:.`:

- `python3 -m unittest tests.test_bid_ask_reconciliation tests.test_spread_characterization tests.test_data_manifest tests.test_session_report tests.test_linked_observation_report tests.test_historical_baseline_report tests.test_internal_flat_zero_volume_diagnostic`
- Result: 123 tests run, OK after the validation-order fix.

Full discovery:

- `PYTHONPATH=tests:. python3 -m unittest discover -s tests`
- Result: 200 tests run, OK, 3 skipped.
- The skipped chart tests reported that Matplotlib is required; no package installation was performed.

## Reviewer Findings

Independent review found no core ASK/BID provenance failure, no obvious BID contamination in ASK artifacts, no spread arithmetic/unit error, and no reconciliation integrity failure. The reviewer confirmed that ASK reports carry `quote_side=ASK`, ASK source filenames are ASK-only, reconciliation has distinct BID and ASK filenames/checksums, and spread is calculated as `ask_close - bid_close` with bid-relative bps defined as `spread / bid_close * 10000`.

Reviewer issues and revisions:

- Medium: full spread summaries could be overread because they include 5,760 excluded rows and 14,372 placeholder rows. Revision made: population language now states that the full population is descriptive and includes calendar-only/placeholder behavior unless explicitly using the non-placeholder diagnostic population.
- Medium: spread characterization relies on the reconciled artifact for full BID/ASK source filename and checksum validation. Revision made: documented this as a future full-year pipeline guardrail; reconciliation itself performed the checksum/size and side checks for this mission.
- Low: tests require `PYTHONPATH=tests:.` because several tests import `fixture_helpers` as a top-level module. Revision made: test invocation is documented exactly.
- Low: stale three-day defaults remain in `spread_characterization.py`. Revision made: documented this as a maintainability risk for future full-year reuse.

Reviewer verdict: revisions were needed for labeling and guardrails, not for core January ASK/BID provenance. Full-year acquisition is technically justified for descriptive market-data research only, with no execution or profitability claims.

## Recommendation

Full-year 2024 ASK acquisition is technically justified as the next bounded data mission, with caveats: use explicit side-aware generation paths, preserve quality tiers, keep placeholders explicit, and do not introduce execution modelling or strategy testing. A small tooling cleanup for ASK CLI ergonomics and side-aware diagnostic filenames is recommended before or during the next bounded mission.

Execution modelling is not justified yet. The current evidence supports data acquisition and descriptive spread characterization only.
