# Changelog

## Unreleased

- Added `linked_observation_report.py` for orchestrated, provenance-linked
  daily/session observation reports without changing the existing session-report
  or data-manifest schemas.
- Added linked-output schema versioning, active-filter rule identity,
  deterministic session-definition checksums, software revision recording,
  separate source/status fields, linkage reason codes, and quality tiers.
- Added same-source tests that verify linked rows are produced from one
  controlled raw-byte operation rather than from independently generated CSVs.
- Added `historical_baseline_report.py` for the first descriptive baseline
  report from an existing linked observation CSV, keeping strict-valid and
  warning-review range summaries separate.
- Added `internal_flat_zero_volume_diagnostic.py` for deterministic structural
  run-location reports from existing manifest, linked observation, and raw CSV
  files without changing filtering or warning policy.
- Verified the February 2024 single-month pipeline for 29 requested dates,
  including February 29, with 29 downloaded raw daily CSVs, 5 strict-valid
  observations, 20 warning-review observations, 4 calendar-only observations,
  0 excluded/unusable observations, 20 `INTERNAL_FLAT_ZERO_VOLUME` warning
  dates, 29 internal flat zero-volume runs, and successful cross-report,
  provenance-checksum, and diagnostic arithmetic reconciliation.
- Verified the March 2024 single-month pipeline for 31 requested dates with 31
  downloaded raw daily CSVs, 9 strict-valid observations, 16 warning-review
  observations, 6 calendar-only observations, 0 excluded/unusable observations,
  16 `INTERNAL_FLAT_ZERO_VOLUME` warning dates, 23 internal flat zero-volume
  runs, reconciled provenance/checksum and diagnostic arithmetic checks, and
  direct before-and-after hash verification that January and February files were
  unchanged.
- Documented adoption of `warning_treatment_v1` as a research-governance
  contract for warning-review observations, with no code, schema,
  classification, filtering, report-generation, raw-data, or configuration
  change.
- Recorded the January-March 2024 daily-range descriptive finding under
  `warning_treatment_v1` as a documentation and research-evidence milestone,
  with no source-code, schema, classification, filtering, data, or dependency
  change.
- Recorded the January-March 2024 daily-extrema UTC-hour descriptive finding
  and tie-handling sensitivity result under `warning_treatment_v1` as a
  documentation and research-evidence milestone, with no source-code, schema,
  filtering, classification, data, or dependency change.

## v0.11

- Added `data_quality.py` for pure raw CSV provenance, structural validation, and conservative quality classification.
- Added `data_manifest.py` for inclusive date-range data quality manifests in `reports/`.
- Added file statuses for missing, empty, parse-failed, no-active-candle, and processed raw files.
- Added quality statuses and deterministic reason codes for source-contract defects, missing minutes, and internal flat zero-volume rows.
- Added day-boundary coverage fields and `PARTIAL_DAY_COVERAGE` warnings for processed files whose timestamps do not cover the requested UTC day.
- Enforced the exact `YYYY-MM-DD HH:MM:SS` timestamp text format, with fractional-second timestamp text counted as invalid.
- Defined first and last manifest timestamps as chronological minimum and maximum parsed timestamps.
- Added SHA-256 source checksums and source byte-size fields for readable raw files.
- Added documentation for the data quality manifest contract, CLI, statuses, reason codes, validation definitions, and limitations.
- Added self-contained synthetic tests for manifest output, validation rules, deterministic output, status reconciliation, and raw-file immutability.

## v0.10.1

- Made the automated test suite independent of ignored local `data_raw/` CSV files.
- Added deterministic synthetic CSV fixture helpers for tests.
- Replaced January 2024 personal-data test dependencies with temporary synthetic fixtures.
- Added session-report reconciliation coverage for complete, missing file, no-active-candle, and failed statuses.
- Kept chart tests headless with synthetic data and non-interactive matplotlib rendering.

## v0.10

- Added `session_report.py` for multi-day session research reports.
- Added one output row per requested date with daily and configured-session statistics.
- Added report statuses for complete, missing file, no active candles, and failed dates.
- Added `reports/.gitkeep` and ignored generated report CSV files.
- Added tests for report row counts, missing files, stable column order, and single-day value matching.
- Added a terminal summary count for no-active-candle dates.

## v0.9

- Added `session_tools.py` for shared session loading, timezone conversion, candle selection, and session statistics.
- Added `python explorer.py YYYY-MM-DD --sessions` for Tokyo, London, and New York session statistics.
- Kept chart session overlays working through the shared session tools.
- Added `requirements.txt` with `matplotlib` and `tzdata`.
- Added tests for January 26, 2024 session statistics and July 1, 2024 daylight-saving conversions.

## v0.8

- Added optional Tokyo, London, and New York research-session overlays to `chart.py`.
- Added `sessions.json` for configurable local-time session definitions.
- Converted session windows to UTC with Python `zoneinfo`, including daylight-saving support.
- Added tests for January 26, 2024 session UTC windows and chart scaling with overlays.

## v0.7.1

- Added shared detection for leading/trailing market-closed placeholder rows.
- Updated `chart.py` to skip edge placeholder candles without editing raw CSV files.
- Updated `explorer.py` to report total rows, active candles, and inactive placeholder rows.
- Added regression tests for January 26, 2024 market-close placeholders and chart autoscaling.

## v0.7

- Added optional dark mode to `chart.py` with `--dark`.
- Added hover cursor information for candlestick timestamp, open, high, low, and close values.
- Improved chart spacing, gridlines, and candle colour readability.

## v0.6

- Added `chart.py` for basic candlestick chart viewing.
- Added 1-minute candlesticks with time on the x-axis and price on the y-axis.
- Updated documentation with chart viewer usage.

## v0.5

- Added `explorer.py` for basic daily CSV exploration.
- Added open, high, low, close, daily range, high/low time, candle count, and average volume output.
- Updated documentation with explorer usage.

## v0.4

- Added `config.json` for default downloader settings.
- Added no-argument mode: `python data_downloader.py`.
- Kept command-line date mode working as before.
- Updated documentation for config-file and command-line usage.

## v0.3

- Added retry logic for temporary Dukascopy failures such as HTTP 503.
- The downloader retries each day up to 3 times before marking it as failed.
- Failed dates are logged only after all retry attempts fail.

## v0.2

- Added date range support.
- Added skip-existing-file behaviour.
- Added failed download logging to `logs/failed_downloads.txt`.
- Continued to the next date if one date failed.

## v0.1

- Added one-day Dukascopy downloader.
- Downloaded XAU/USD 1-minute BID candle data.
- Converted Dukascopy `.bi5` data into CSV.
- Saved CSV files into `data_raw/`.
