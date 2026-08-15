# Full-Year 2024 ASK Campaign

## Scope

Approved campaign: complete XAUUSD 1-minute ASK market-data coverage for 2024-01-01 through 2024-12-31 inclusive, then generate side-aware ASK provenance, BID/ASK reconciliation, and descriptive spread characterization.

Evidence boundary: descriptive market-data research only. This campaign does not claim execution realism, trading edge, profitability, future performance, or strategy validity. No missing data should be acquired until this preflight inventory has been reviewed.

## Preflight Status

Lab path inspected: `/workspace/XAUUSD_Lab`.

Worktree status: dirty before this preflight, with existing side-aware infrastructure/docs/tests and local artifacts. Treat those as existing workflow state; this preflight only updates this campaign document.

January preservation rule: January ASK work is already validated and must not be redone. Existing January raw files and January side-aware outputs are preserved as the baseline.

Current raw coverage from `/workspace/XAUUSD_Lab/data_raw`:

- BID 2024 coverage: 366/366 dates present, 2024-01-01 through 2024-12-31, no missing dates.
- ASK 2024 coverage: 126/366 dates present.
- ASK present coverage: all January; 2024-02-01 through 2024-02-13; 2024-02-16 through 2024-05-07.
- ASK missing coverage: 240 dates.

Missing ASK ranges after preserving validated January:

- 2024-02-14 through 2024-02-15: 2 dates.
- 2024-05-08 through 2024-12-31: 238 dates.

Missing ASK by month:

- 2024-02: 2
- 2024-05: 24
- 2024-06: 30
- 2024-07: 31
- 2024-08: 31
- 2024-09: 30
- 2024-10: 31
- 2024-11: 30
- 2024-12: 31

## Existing Artifact Inventory

Validated January ASK artifacts to preserve:

- `/workspace/XAUUSD_Lab/reports/data_manifest_ASK_2024-01-01_to_2024-01-31.csv`
- `/workspace/XAUUSD_Lab/reports/session_report_ASK_2024-01-01_to_2024-01-31.csv`
- `/workspace/XAUUSD_Lab/reports/linked_observation_report_ASK_2024-01-01_to_2024-01-31.csv`
- `/workspace/XAUUSD_Lab/reports/historical_baseline_linked_observation_report_ASK_2024-01-01_to_2024-01-31.csv`
- `/workspace/XAUUSD_Lab/reports/internal_flat_zero_volume_diagnostic_ASK_2024-01-01_to_2024-01-31.csv`
- `/workspace/XAUUSD_Lab/reports/bid_ask_reconciliation_2024-01-01_to_2024-01-31.csv`
- `/workspace/XAUUSD_Lab/reports/spread_characterization_2024-01-01_to_2024-01-31_summary.csv`
- `/workspace/XAUUSD_Lab/reports/spread_characterization_2024-01-01_to_2024-01-31_wide_observations.csv`

Existing legacy BID monthly provenance/artifacts include month-level `data_manifest_2024-MM-...`, `linked_observation_report_2024-MM-...`, `historical_baseline_linked_observation_report_2024-MM-...`, and diagnostic outputs across 2024. Several legacy filenames omit `BID` and should be treated as legacy BID unless row metadata proves otherwise.

Existing pilot artifacts also include three-day ASK/BID reconciliation and spread characterization for 2024-01-09 through 2024-01-11.

## Tooling Preflight

Available acquisition command:

- Downloader: `python3 /workspace/XAUUSD_Lab/data_downloader.py START END` uses command-line dates but keeps the module/default `PRICE_SIDE = "BID"`. To acquire ASK with the current CLI, set `/workspace/XAUUSD_Lab/config.json` to ASK and run with no date arguments, or use an explicit Python function call that sets `data_downloader.PRICE_SIDE = "ASK"` before invoking downloads. Do not run acquisition yet from this preflight.

Available side-aware provenance functions:

- `data_manifest.create_data_manifest(start, end, data_dir, source_contract_for_side(ASK), legacy_side_omitted=False)`
- `session_report.create_session_report(start, end, data_dir, source_contract_for_side(ASK), legacy_side_omitted=False)`
- `linked_observation_report.create_linked_observation_report(start, end, data_dir, source_contract_for_side(ASK), legacy_side_omitted=False)`
- `historical_baseline_report.py LINKED_OBSERVATION_REPORT_CSV` works on side-specific linked reports.
- `internal_flat_zero_volume_diagnostic.py MANIFEST_CSV LINKED_OBSERVATION_REPORT_CSV --data-dir DATA_DIR` works, but its default output filename omits quote side.

Available pairing/spread commands:

- `python3 /workspace/XAUUSD_Lab/bid_ask_reconciliation.py START END` exists, but its default linked-report paths are January/three-day pilot paths. For full-year or non-January ranges, call `create_reconciliation(...)` with explicit BID and ASK linked paths and output path.
- `python3 /workspace/XAUUSD_Lab/spread_characterization.py START END RECONCILIATION_CSV` supports explicit range/input; no-argument mode remains the three-day pilot default.

Focused tests to run after any small tooling change or artifact generation:

- `PYTHONPATH=tests:. python3 -m unittest tests.test_source_contracts tests.test_data_manifest tests.test_session_report tests.test_linked_observation_report tests.test_historical_baseline_report tests.test_internal_flat_zero_volume_diagnostic tests.test_bid_ask_reconciliation tests.test_spread_characterization`
- Optional full suite: `PYTHONPATH=tests:. python3 -m unittest discover -s tests`.

## ASK Ergonomics Audit

GREEN-scope candidates found:

- `/workspace/XAUUSD_Lab/data_downloader.py:1`, `/workspace/XAUUSD_Lab/data_downloader.py:29`, `/workspace/XAUUSD_Lab/data_downloader.py:305`: downloader docs/defaults are BID-oriented; command-line date mode does not expose `--quote-side ASK`. A small CLI flag would reduce acquisition risk before full-year ASK download.
- `/workspace/XAUUSD_Lab/data_manifest.py:266`, `/workspace/XAUUSD_Lab/session_report.py:435`, `/workspace/XAUUSD_Lab/linked_observation_report.py:964`: CLIs still call legacy BID defaults and usage examples omit side selection. Existing Python functions are side-aware, so a fix is ergonomic, not required if the campaign uses explicit function calls.
- `/workspace/XAUUSD_Lab/bid_ask_reconciliation.py:313`, `/workspace/XAUUSD_Lab/bid_ask_reconciliation.py:314`, `/workspace/XAUUSD_Lab/bid_ask_reconciliation.py:377`: default linked paths remain January/three-day pilot oriented. Full-year reconciliation should use explicit linked paths or a small CLI expansion.
- `/workspace/XAUUSD_Lab/spread_characterization.py:19`, `/workspace/XAUUSD_Lab/spread_characterization.py:23`, `/workspace/XAUUSD_Lab/spread_characterization.py:321`: no-argument defaults are the three-day pilot; explicit CLI range is available.
- `/workspace/XAUUSD_Lab/internal_flat_zero_volume_diagnostic.py:517`: diagnostic output filename is side-ambiguous. For ASK, copy/rename to an `_ASK_` artifact or add side-aware output naming.

Recommended GREEN-scope fix before acquisition: add only a `--quote-side` acquisition/provenance CLI path and side-aware diagnostic output naming if operators will use CLIs. If acquisition/provenance is run through explicit Python calls, the fix can wait.

## Next Recommended Command Sequence

1. Snapshot missing ASK dates from filenames and save the list for operator review.
2. Acquire only missing ASK dates, preserving existing validated January and existing 2024-02-01 through 2024-05-07 ASK files. Suggested batches: `2024-02-14..2024-02-15`, then month/range batches from `2024-05-08..2024-12-31`.
3. Generate side-aware ASK provenance for acquired/covered ranges with explicit `source_contract_for_side(ASK)` and `legacy_side_omitted=False`.
4. Run ASK diagnostics and ensure side-labeled diagnostic artifacts are retained.
5. Reconcile BID/ASK with explicit BID and ASK linked-report paths.
6. Run spread characterization from the explicit reconciliation artifact.
7. Run focused tests, then full discovery if scope expands.

## Evidence Classification

Preflight only. No data acquisition, execution modelling, strategy testing, or profitability analysis was performed by this document update.

## Full-Year ASK Provenance Consolidation

Date: 2026-08-09

Scope: provenance consolidation only. No new market data was acquired, no raw BID or ASK files were modified, and no BID/ASK reconciliation or spread characterization was started.

Full-year raw ASK coverage is now distinct from full-year provenance coverage:

- Raw ASK coverage: 366/366 calendar dates present in `/workspace/XAUUSD_Lab/data_raw`.
- Full-year ASK provenance coverage: 366/366 unique calendar dates in `/workspace/XAUUSD_Lab/reports/linked_observation_report_ASK_2024-01-01_to_2024-12-31.csv`.
- Duplicate full-year ASK provenance dates: 0.

Authoritative full-year ASK provenance/report artifacts:

- `/workspace/XAUUSD_Lab/reports/data_manifest_ASK_2024-01-01_to_2024-12-31.csv`
- `/workspace/XAUUSD_Lab/reports/session_report_ASK_2024-01-01_to_2024-12-31.csv`
- `/workspace/XAUUSD_Lab/reports/linked_observation_report_ASK_2024-01-01_to_2024-12-31.csv`
- `/workspace/XAUUSD_Lab/reports/historical_baseline_linked_observation_report_ASK_2024-01-01_to_2024-12-31.csv`
- `/workspace/XAUUSD_Lab/reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-12-31.csv`

Full-year linked-observation quality population:

- strict_valid: 104
- warning_review: 209
- calendar_only: 53
- excluded_unusable: 0

Checksum/source-file verification: 313 non-calendar-only linked rows matched the existing ASK raw source files by source filename, file size, and SHA-256 checksum. Calendar-only rows preserve the no-active-candle findings produced by the existing pipeline.

Validation: `PYTHONPATH=tests:. python3 -m unittest tests.test_source_contracts tests.test_data_manifest tests.test_session_report tests.test_linked_observation_report tests.test_historical_baseline_report tests.test_internal_flat_zero_volume_diagnostic` passed, 112 tests OK.

Earlier January pilot/monthly ASK artifacts remain historical artifacts. The authoritative consolidated ASK provenance population for 2024-01-01 through 2024-12-31 is the full-year side-aware report set listed above, with exactly one linked-observation row per calendar date including 2024-01-09, 2024-01-10, and 2024-01-11.

## Acquisition Progress

- 2024-11-01 through 2024-12-31 bounded chunk completed: all 61 November-December ASK files verified present with 1,440 minute rows each after targeted retries recovered transient failures, including final recovery of 2024-11-13. Side-aware ASK provenance artifacts were generated for the approved range: 21 strict-valid observations, 31 warning-review observations, 9 calendar-only observations, and 0 excluded/unusable observations. Current full-year ASK coverage: 366/366 present, 0 missing. Current missing snapshot updated at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_current.txt`; November-December checkpoint copy saved at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_after_nov_dec_chunk.txt`. Stop after acquisition/provenance validation; do not begin full-year reconciliation or spread characterization inside this checkpoint.

- 2024-10-01 through 2024-10-31 bounded chunk completed: all 31 October ASK files verified present with 1,440 minute rows each after a targeted retry recovered 2024-10-13. Side-aware ASK provenance artifacts were generated for the approved range: 8 strict-valid observations, 19 warning-review observations, 4 calendar-only observations, and 0 excluded/unusable observations. Current full-year ASK coverage: 305/366 present, 61 missing. Current missing snapshot updated at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_current.txt`; October checkpoint copy saved at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_after_october_chunk.txt`. Remaining ASK missing coverage begins at 2024-11-01. Do not continue into November inside this checkpoint.

- 2024-09-08 through 2024-09-30 bounded chunk completed: all 23 September-remainder ASK files verified present with 1,440 minute rows each. Side-aware ASK provenance artifacts were generated for the approved range: 7 strict-valid observations, 13 warning-review observations, 3 calendar-only observations, and 0 excluded/unusable observations. Current full-year ASK coverage: 274/366 present, 92 missing. Current missing snapshot updated at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_current.txt`; September-remainder checkpoint copy saved at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_after_sep08_sep30_chunk.txt`. Remaining ASK missing coverage begins at 2024-10-01. Do not continue into October inside this checkpoint.

- 2024-09-01 through 2024-09-07 bounded chunk completed: all 7 September ASK files verified present with 1,440 minute rows each. Side-aware ASK provenance artifacts were generated for the approved range: 2 strict-valid observations, 4 warning-review observations, 1 calendar-only observation, and 0 excluded/unusable observations. Current full-year ASK coverage: 251/366 present, 115 missing. Current missing snapshot updated at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_current.txt`; September 1-7 checkpoint copy saved at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_after_sep01_sep07_chunk.txt`. Remaining ASK missing coverage begins at 2024-09-08. Do not continue past 2024-09-07 inside this checkpoint.

- 2024-07-01 through 2024-07-31 bounded chunk completed: all 31 July ASK files verified present with 1,440 minute rows each. Current full-year ASK coverage: 213/366 present, 153 missing. Current missing snapshot updated at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_current.txt`; July checkpoint copy saved at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_after_july_chunk.txt`. Remaining ASK missing coverage is 2024-08-01 through 2024-12-31.

- 2024-05-24, 2024-05-25, 2024-05-26, 2024-06-01, 2024-06-02, 2024-06-03, and 2024-06-26 residual retry chunk completed: all 7 unresolved ASK files recovered and verified present with 1,440 minute rows each. Current full-year ASK coverage: 182/366 present, 184 missing. Current missing snapshot updated at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_current.txt`; residual-retry checkpoint copy saved at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_after_residual_retry.txt`. Remaining ASK missing coverage is 2024-07-01 through 2024-12-31. Do not start July inside this residual retry checkpoint.

- 2024-06-01 through 2024-06-30 bounded chunk completed: 26/30 June ASK files present after run; residual June failures: 2024-06-01, 2024-06-02, 2024-06-03, 2024-06-26. Current full-year ASK coverage: 175/366 present, 191 missing. Current missing snapshot updated at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_current.txt`; June checkpoint copy saved at `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_after_june_chunk.txt`.

- Current missing ASK snapshot saved: `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_current.txt` (217 dates missing as of latest acquisition checkpoint).

- 2024-05-24 through 2024-05-27 targeted retry recovered May 27; residual transient failures after bounded retries: 2024-05-24, 2024-05-25, 2024-05-26.

- 2024-05-10 through 2024-05-14 targeted retry recovered May 10 and May 12-14; failures: 0 after retry run.

- 2024-05-08 through 2024-05-31 initial batch acquired 16/24 dates; residual May gaps after bounded retries: 2024-05-10, 2024-05-12, 2024-05-13, 2024-05-14, 2024-05-24, 2024-05-25, 2024-05-26, 2024-05-27.

- Pre-acquisition missing ASK snapshot saved: `/workspace/XAUUSD_Lab/reports/missing_ASK_2024_dates_pre_acquisition.txt` (240 dates).
- 2024-02-14 through 2024-02-15 acquired with `python3 /workspace/XAUUSD_Lab/data_downloader.py --quote-side ASK 2024-02-14 2024-02-15`; both files saved with 1,440 rows; failures: 0.
