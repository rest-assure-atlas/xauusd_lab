# ASK Real Data Pilot

Date: 2026-08-08

Mission: first tiny real ASK-data provenance pilot for XAUUSD_Lab.

This was a small external-data acquisition pilot only. It did not expand beyond the approved three-day range, did not modify inherited BID raw evidence, did not regenerate broad historical reports, did not implement BID/ASK reconciliation, did not characterize spread, did not perform execution modelling, and did not test strategies or profitability.

## Selected Date Range

Selected dates: `2024-01-09` through `2024-01-11` inclusive.

Rationale:

- exactly three consecutive ordinary Tuesday-Thursday trading days
- within existing 2024 BID coverage
- matching BID raw files already present before acquisition
- no obvious market holiday in the selected range

## Acquisition Method

Used the existing `data_downloader.py` Dukascopy acquisition functions with in-process settings:

- `SYMBOL = "XAUUSD"`
- `PRICE_SIDE = "ASK"`
- `TIMEFRAME = "min_1"`

The Dukascopy side-specific object name was `ASK_candles_min_1.bi5`, under the existing daily URL pattern:

`https://datafeed.dukascopy.com/datafeed/XAUUSD/YYYY/MM/DD/ASK_candles_min_1.bi5`

Dukascopy uses zero-based months in this path, so January is `00`.

`config.json` was not edited. No BID filename or BID downloader setting was used for the requested ASK files.

## Acquisition Result

Acquisition succeeded for all three selected dates after sandbox networking became available.

Downloader result:

- `2024-01-09`: saved `1440` rows
- `2024-01-10`: saved `1440` rows
- `2024-01-11`: saved `1440` rows
- failed dates: `0`

## ASK Files Created

ASK raw files created:

- `data_raw/XAUUSD_2024-01-09_1min_ASK_UTC.csv` (`97962` bytes)
- `data_raw/XAUUSD_2024-01-10_1min_ASK_UTC.csv` (`97962` bytes)
- `data_raw/XAUUSD_2024-01-11_1min_ASK_UTC.csv` (`97962` bytes)

All raw ASK files use explicit side-aware filenames. No legacy side-omitted filename was used.

## Provenance Artifacts Created

Side-aware ASK provenance artifacts created:

- `reports/data_manifest_ASK_2024-01-09_to_2024-01-11.csv`
- `reports/session_report_ASK_2024-01-09_to_2024-01-11.csv`
- `reports/linked_observation_report_ASK_2024-01-09_to_2024-01-11.csv`
- `reports/historical_baseline_linked_observation_report_ASK_2024-01-09_to_2024-01-11.csv`

The historical baseline was generated because the linked-report consumer naturally supports ASK side identity and preserves `provider`, `instrument`, `quote_side`, and `timeframe`.

ASK identity checks:

- provider: `Dukascopy`
- instrument: `XAUUSD`
- quote_side: `ASK`
- timeframe: `1min`
- source filenames: `XAUUSD_YYYY-MM-DD_1min_ASK_UTC.csv`
- linked rows: `linkage_status=linked`
- linked rows: `quality_tier=warning_review`

## BID Evidence Preservation

Matching inherited BID files remained present:

- `data_raw/XAUUSD_2024-01-09_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-01-10_1min_BID_UTC.csv`
- `data_raw/XAUUSD_2024-01-11_1min_BID_UTC.csv`

Each matching BID file was present after acquisition and remained at `97962` bytes. No ASK output reused a BID filename.

## Data-Quality Findings

ASK file count:

- expected ASK file count: `3`
- acquired ASK file count: `3`
- missing ASK files: `0`

Per-date raw/manifest findings:

- each ASK file has `1440` rows
- first timestamp is `00:00:00` UTC for each selected date
- last timestamp is `23:59:00` UTC for each selected date
- duplicate timestamp count: `0` for each date
- invalid timestamp count: `0` for each date
- invalid numeric row count: `0` for each date
- active row count: `1440` for each date
- zero-volume rows observed directly: `60` per date
- manifest quality status: `warning` for each date
- manifest quality reason: `INTERNAL_FLAT_ZERO_VOLUME` for each date
- linked quality tier: `warning_review` for each date

No parse failures, empty files, missing files, malformed rows, or timestamp coverage anomalies were observed. Existing data-quality rules were not weakened.

## BID Structural Comparison

Structural/provenance-only comparison against matching BID files:

- matching BID files exist for all three selected dates
- BID and ASK row counts both equal `1440` for each date
- BID and ASK timestamp sequences align exactly for each date
- BID and ASK file hashes differ for each date
- first-bar BID and ASK open/high/low/close values differ for each date

This confirms the ASK files are structurally distinct from the matching BID files. No BID/ASK reconciliation artifact was created. No spread statistics, execution assumptions, or strategy results were calculated.

## Tests

Focused tests run after acquisition and provenance processing:

- `test_source_contracts.py`: ran 12, OK
- `test_linked_observation_report.py`: ran 47, OK
- `test_historical_baseline_report.py`: ran 21, OK

Full unittest discovery:

- ran 177 tests
- OK
- skipped 3 existing matplotlib-dependent chart tests

No packages were installed.

## Reviewer Findings

Independent reviewer/critic recommendation: approve the ASK real-data pilot for exactly `2024-01-09` through `2024-01-11`, narrowly scoped to provenance/acquisition success.

Reviewer findings:

- medium: the session report is side-aware by filename and ASK-derived values, but does not itself contain `provider`, `instrument`, `quote_side`, `timeframe`, or `source_filename` columns. Downstream provenance should rely on the manifest and linked report, not the session report alone.
- low: linked rows record a dirty software revision. This is acceptable for the pilot, but reproducibility would benefit from a clean committed revision or recorded diff before broader use.
- low: all three dates are correctly warning-review, not strict-valid, because of `INTERNAL_FLAT_ZERO_VOLUME`.

Reviewer-verified facts:

- the three ASK raw files exist only for the approved dates
- each ASK file has `1440` data rows plus header, from `00:00:00` to `23:59:00`, with `60` zero-volume rows
- manifest and linked reports each contain exactly three rows, all with `quote_side=ASK`, `provider=Dukascopy`, `instrument=XAUUSD`, and `timeframe=1min`
- ASK checksums in the manifest match the raw files
- matching BID files exist and are not byte-identical to ASK files
- first-bar ASK and BID prices/volumes differ on all three days
- BID/ASK timestamp sequences align exactly for all three dates
- ASK historical baseline preserves `quote_side=ASK`

Reviewer conclusion: the files are genuinely side-distinct ASK artifacts and not an obvious BID fallback. A bounded BID/ASK reconciliation feasibility pass on only these same three dates is justified next, limited to side pairing, timestamp alignment, and schema feasibility.

## Evidence Classification

`confirmed`: real ASK raw files were acquired for the approved three-day pilot range using side-aware filenames.

`confirmed`: the ASK manifest, session report, linked-observation report, and historical baseline preserve `quote_side=ASK` and source filename/path identity.

`confirmed`: matching inherited BID raw files remained present and were not overwritten by ASK filenames.

`confirmed`: ASK files are structurally distinct from matching BID files by file hash and first-bar price values, while timestamp coverage aligns exactly.

`not complete`: BID/ASK reconciliation, spread-awareness, execution realism, strategy testing, and profitability evidence are not established.

## Is ASK Acquisition Established?

Yes, for this narrow three-day Dukascopy XAUUSD 1-minute ASK provenance pilot only. This does not establish full ASK coverage or any trading/execution claim.

## Is BID/ASK Reconciliation Justified Next?

Yes, a bounded reconciliation feasibility mission is now technically justified because matching BID and ASK files exist for the same three dates with aligned timestamp coverage and preserved source-side identity.

## Recommended Next Mission

Run a bounded BID/ASK reconciliation feasibility mission on only the same three dates. The mission should verify side pairing, timestamp alignment, and minimal reconciliation schema without spread characterization, execution modelling, strategy testing, or profitability claims.
