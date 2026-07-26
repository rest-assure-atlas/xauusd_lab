# Current State

Verified committed milestone: **v0.11**.

XAUUSD Lab is a Python research project for studying XAU/USD, meaning gold priced in US dollars. The current repository focuses on downloading Dukascopy one-minute BID data, exploring daily data, charting candles, applying configurable research-session windows, producing multi-day session research reports, creating data quality manifests for raw CSV provenance and validation, producing a separate non-canonical linked observation report, creating a first descriptive historical baseline from an existing linked observation CSV, and producing a narrow structural diagnostic for internal flat zero-volume runs.

## Repository Structure

Current tracked source and documentation files:

```text
AGENTS.md
CHANGELOG.md
README.md
candle_filters.py
chart.py
config.json
data_manifest.py
data_quality.py
data_downloader.py
explorer.py
historical_baseline_report.py
internal_flat_zero_volume_diagnostic.py
linked_observation_report.py
requirements.txt
session_report.py
session_tools.py
sessions.json
tests/
reports/.gitkeep
docs/
```

Local generated or ignored folders may include:

```text
data_raw/
logs/
reports/
__pycache__/
tests/__pycache__/
```

The local `data_raw/` folder may contain ignored downloaded XAUUSD CSV files on a development machine. Those CSV files are not included in a fresh Git clone, and the automated tests do not require them.

## Python Files

`data_downloader.py` downloads Dukascopy XAU/USD one-minute BID `.bi5` files, decompresses them, converts them into CSV rows, saves them in `data_raw/`, skips existing files, retries temporary failures, and logs failed downloads after all retries fail. It supports command-line date arguments and no-argument config-file mode.

`data_quality.py` provides pure raw CSV validation and classification logic. It records readable file provenance, validates the expected source contract, counts row-level defects, checks internal timestamp gaps and UTC day-boundary coverage, reuses shared edge-placeholder filtering, and returns deterministic manifest fields without modifying raw files.

`data_manifest.py` creates one data quality and provenance row per requested calendar date. It supports inclusive date ranges, optional `--data-dir`, deterministic output under `reports/`, and terminal summaries whose file-status and quality-status counts reconcile to the requested date count.

`linked_observation_report.py` creates one non-canonical provenance-linked observation row per requested calendar date. It reads each expected raw file into verified bytes, runs the existing manifest assessment and existing session-calculation logic from those same bytes, re-checks source identity after processing, and writes a separate linked report under `reports/` without changing the v0.10 session-report or v0.11 manifest schemas.

`historical_baseline_report.py` reads one existing linked observation report CSV and writes a descriptive baseline report under `reports/`. It reports coverage, numeric availability, and daily/Tokyo/London/New York range summaries without reading raw data, regenerating producer outputs, or making strategy, prediction, execution, or profitability claims.

`internal_flat_zero_volume_diagnostic.py` reads one existing data quality manifest, one existing linked observation report, and corresponding raw CSV files to write one structural diagnostic row per internal flat zero-volume run. It locates run start/end timestamps, counts run rows, counts Tokyo/London/New York session overlaps, counts rows outside configured sessions, and copies linked daily/session range context without changing raw data, filtering behaviour, warning policy, existing schemas, or historical-baseline behaviour.

`explorer.py` loads one daily CSV from `data_raw/` and prints daily statistics. With `--sessions`, it also prints Tokyo, London, and New York research-session statistics. It uses active candles only, after excluding leading and trailing inactive placeholder rows.

`chart.py` loads one daily CSV from `data_raw/` and displays a candlestick chart. It supports light mode, `--dark`, `--sessions`, hover OHLC labels, crosshair lines, active-time x-axis limits, and candle-based y-axis scaling.

`candle_filters.py` provides shared logic for detecting flat zero-volume placeholder candles and removing only contiguous inactive placeholder rows at the beginning or end of a candle list.

`session_tools.py` loads session definitions from `sessions.json`, converts local session windows to UTC with `zoneinfo`, selects candles using start-inclusive and end-exclusive windows, and calculates session statistics.

`session_report.py` processes an inclusive date range of downloaded daily CSV files and writes one research-ready CSV row per requested date into `reports/`.

## JSON Configuration

`config.json` controls the downloader's no-argument mode:

```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "symbol": "XAUUSD",
  "price_side": "BID",
  "timeframe": "min_1"
}
```

`sessions.json` defines configurable research-session windows. Current defaults are:

- Tokyo: `Asia/Tokyo`, 09:00-18:00 local time
- London: `Europe/London`, 08:00-17:00 local time
- New York: `America/New_York`, 08:00-17:00 local time

These local times are converted to UTC for the selected date using Python's `zoneinfo` support.

## Supported Commands

Download using `config.json`:

```powershell
python data_downloader.py
```

Download one day:

```powershell
python data_downloader.py 2024-01-02
```

Download a date range, including both dates:

```powershell
python data_downloader.py 2024-01-02 2024-01-31
```

Explore one day:

```powershell
python explorer.py 2024-01-26
```

Explore one day with session statistics:

```powershell
python explorer.py 2024-01-26 --sessions
```

Chart one day:

```powershell
python chart.py 2024-01-26
```

Chart one day in dark mode:

```powershell
python chart.py 2024-01-26 --dark
```

Chart one day with research-session overlays:

```powershell
python chart.py 2024-01-26 --sessions
```

Chart one day with dark mode and research-session overlays:

```powershell
python chart.py 2024-01-26 --dark --sessions
```

Create a multi-day session report:

```powershell
python session_report.py 2024-01-01 2024-01-31
```

Create a data quality and provenance manifest:

```powershell
python data_manifest.py 2024-01-01 2024-01-31
```

Create a manifest from an explicit raw data folder:

```powershell
python data_manifest.py 2024-01-01 2024-01-31 --data-dir data_raw
```

Create a provenance-linked daily/session observation report:

```powershell
python linked_observation_report.py 2024-01-01 2024-01-31
```

Create a linked report from an explicit raw data folder:

```powershell
python linked_observation_report.py 2024-01-01 2024-01-31 --data-dir data_raw
```

Create a descriptive historical baseline from one existing linked report:

```powershell
python historical_baseline_report.py reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
```

Create an internal flat zero-volume diagnostic from existing manifest, linked,
and raw CSV files:

```powershell
python internal_flat_zero_volume_diagnostic.py reports/data_manifest_2024-01-01_to_2024-01-31.csv reports/linked_observation_report_2024-01-01_to_2024-01-31.csv --data-dir data_raw
```

Run the full automated test suite:

```powershell
python -m unittest discover -s tests
```

## Dependencies

External dependencies from `requirements.txt`:

- `matplotlib>=3.8,<4`
- `tzdata>=2024.1`

`matplotlib` is used by `chart.py`. `tzdata` provides IANA timezone data on Windows for `zoneinfo`.

## Data, Logs, Reports, And Tests

Raw downloaded CSV files are saved in `data_raw/` with filenames like:

```text
data_raw/XAUUSD_2024-01-26_1min_BID_UTC.csv
```

Raw CSV files are source records. They are not edited by analysis, charting, or reporting tools.

Downloader failures are logged to:

```text
logs/failed_downloads.txt
```

Generated reports are saved in `reports/` with filenames like:

```text
reports/session_report_2024-01-01_to_2024-01-31.csv
reports/data_manifest_2024-01-01_to_2024-01-31.csv
reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
reports/historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv
reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv
```

`reports/.gitkeep` keeps the report folder present in Git. Generated report CSV files are ignored.

Tests live in `tests/`. The automated tests use deterministic synthetic CSV fixtures created in temporary folders, so the suite does not require downloaded raw CSV files in `data_raw/`.

## Git Treatment Of Generated Files

`.gitignore` ignores:

- `data_raw/*.csv`
- `logs/`
- `reports/*`, except `reports/.gitkeep`
- `__pycache__/`
- `*.pyc`

Source code, tests, documentation, JSON configuration, and `requirements.txt` are not ignored.

## Automated Test Status

The current automated test suite contains 136 tests and currently passes with:

```powershell
python -m unittest discover -s tests
```

In the bundled Codex runtime used during February validation, Matplotlib was
not available. `unittest` still discovered 136 test cases, but the five
`ChartAutoscaleRegressionTest` methods were skipped at class setup and were not
counted as run tests. Two additional Matplotlib-dependent tests were counted as
skipped. That environment-specific result was:

```text
Bundled Codex runtime:
131 tests run
3 skipped
0 failures
0 errors
Matplotlib unavailable in that runtime
```

The latest completed application milestone is v0.11.

## Recent Manually Verified Behaviour

The January 2024 session report command has been verified locally:

```powershell
python session_report.py 2024-01-01 2024-01-31
```

Observed summary:

```text
Session report complete.
Requested dates: 31
Completed dates: 27
Missing files: 0
No active candle dates: 4
Failed dates: 0
Output path: C:\Users\Lenovo\Documents\XAUUSD_Lab\reports\session_report_2024-01-01_to_2024-01-31.csv
```

The January 2024 data manifest command has also been verified locally:

```powershell
python data_manifest.py 2024-01-01 2024-01-31 --data-dir data_raw
```

Observed summary:

```text
Data manifest complete.
Requested dates: 31
Processed files: 27
Missing files: 0
Empty files: 0
Parse failures: 0
No-active-candle files: 4
Valid dates: 9
Warning dates: 18
Invalid dates: 0
Not-assessed dates: 4
Output path: C:\Users\Lenovo\Documents\XAUUSD_Lab\reports\data_manifest_2024-01-01_to_2024-01-31.csv
```

Manual January 2024 manifest observations:

- Saturdays 2024-01-06, 2024-01-13, 2024-01-20, and 2024-01-27 were `no_active_candles` and `not_assessed`, each with 1440 leading inactive rows.
- Fridays 2024-01-05, 2024-01-12, 2024-01-19, and 2024-01-26 were `processed` and `valid`, each with 120 trailing inactive rows and active data through 21:59 UTC.
- Sundays 2024-01-07, 2024-01-14, 2024-01-21, and 2024-01-28 were `processed` and `valid`, each with 1380 leading inactive rows and active data from 23:00 UTC.
- 2024-01-01 was `processed` and `valid`, with 1380 leading inactive rows and active data from 23:00 UTC.
- 2024-01-15 was `processed` with `warning` quality because of `INTERNAL_FLAT_ZERO_VOLUME`.
- The 18 warning dates in the January sample were warnings for `INTERNAL_FLAT_ZERO_VOLUME`.
- The January sample had complete 00:00 through 23:59 UTC timestamp coverage for every existing raw file, so no rows received `PARTIAL_DAY_COVERAGE`.

These are structural observations only. They do not prove market closure, provider failure, or tradability.

## February 2024 Pipeline Validation

The February 2024 single-month pipeline has been manually validated for the
inclusive date range 2024-02-01 through 2024-02-29.

Verified February 2024 counts:

```text
Requested dates: 29
Raw files: 29
Manifest processed: 25
Manifest no_active_candles: 4
Manifest valid: 5
Manifest warning: 20
Manifest not_assessed: 4

Linked strict_valid: 5
Linked warning_review: 20
Linked calendar_only: 4
Linked excluded/unusable: 0

Diagnostic warning dates: 20
Diagnostic runs: 29
Diagnostic run rows: 1,192
```

All 29 February raw CSV files were present with 1,440 data rows each. February
29 was present, processed, and classified as `warning_review` with
`INTERNAL_FLAT_ZERO_VOLUME`.

The standalone February manifest, linked observation report, historical
baseline, internal-flat diagnostic, and raw-source checksums reconciled. The
baseline kept `strict_valid` and `warning_review` numeric summaries separate,
and `calendar_only` values remained unavailable rather than being treated as
zero.

Seven February dates contained multiple separate diagnostic runs:

```text
2024-02-06: 3 runs
2024-02-12: 2 runs
2024-02-14: 2 runs
2024-02-18: 2 runs
2024-02-19: 2 runs
2024-02-27: 2 runs
2024-02-29: 3 runs
```

The February diagnostic command was accidentally executed twice. Verification
showed deterministic replacement of the same output path, identical content,
no appended rows, no duplicate report artifact, and no raw-file mutation.

No saved January before-hash snapshot was available for direct January
before/after proof. Implementation inspection showed the February commands were
date-bounded to February output paths and February raw filenames, but that is
not equivalent to direct January hash evidence.

February is one additional bounded descriptive month only. January and February
must not be treated as establishing normal XAU/USD behaviour. `strict_valid`
and `warning_review` observations must remain separate. The February outputs do
not support strategy, support/resistance, signal, prediction, edge,
profitability, execution, or causal conclusions. `INTERNAL_FLAT_ZERO_VOLUME`
remains an unresolved warning and has not been proven harmless or assigned a
market or provider cause.

## v0.11 Data Quality Manifest Behaviour

`data_manifest.py` creates one CSV row per requested calendar date.

Each row includes:

- source contract metadata and expected filename
- readable source file size and SHA-256 checksum
- file status and quality status
- stable machine-readable reason codes
- row counts, edge inactive counts, internal inactive counts, timestamp continuity metrics, day-boundary coverage metrics, and row-level defect counts

File statuses are:

- `missing_file`
- `empty_file`
- `parse_failed`
- `no_active_candles`
- `processed`

Quality statuses are:

- `valid`
- `warning`
- `invalid`
- `not_assessed`

Manifest timestamps must match `YYYY-MM-DD HH:MM:SS` exactly. Fractional-second timestamp text is invalid, while non-zero whole seconds are parseable but counted as off-minute timestamps. `first_timestamp_utc` and `last_timestamp_utc` are chronological minimum and maximum parsed timestamps when invalid timestamps do not prevent reliable bounds.

See [DATA_QUALITY_MANIFEST.md](DATA_QUALITY_MANIFEST.md) for the full contract.

## v0.10 Session Report Behaviour

`session_report.py` creates one CSV row per requested calendar date.

Each row includes:

- date, weekday, and status
- daily OHLC, range, and high/low times
- total CSV row count
- active candle count
- inactive placeholder count
- Tokyo, London, and New York session OHLC, range, high/low times, and active candle count

Statuses mean:

- `complete`: the daily CSV exists, active candles were found, and daily/session statistics were calculated.
- `missing_file`: the expected daily CSV file was not found.
- `no_active_candles`: the daily CSV exists, but no active candles remained after removing leading/trailing inactive placeholders.
- `failed`: the file existed but processing failed because of a handled read, parse, data, or file error.

Verified January 2024 result:

- 31 requested dates
- 27 complete dates
- 4 no-active-candle Saturdays
- 0 missing files
- 0 failed dates

## Linked Observation Report Behaviour

`linked_observation_report.py` creates one separate non-canonical linked row per
requested calendar date. It is a provenance-linking and reconciliation artifact,
not a replacement for the v0.10 session report or the v0.11 data quality
manifest.

The physical linkage inside the controlled operation is the requested `date`.
The logical observation identity is:

```text
date + provider + instrument + quote_side + timeframe
```

Source filename, file size, checksum, rule identities, software revision, and
linked schema version are provenance and validation fields rather than join
keys.

For each existing raw file, the linked report:

1. derives the expected raw filename;
2. reads the raw file into bytes;
3. records file size and SHA-256 checksum for those bytes;
4. runs the existing manifest assessment from those same bytes;
5. runs the existing session-calculation logic from those same bytes;
6. re-reads the source identity afterward and flags source mutation.

The tool does not accept arbitrary pre-existing session-report or manifest CSVs
as provenance-linked evidence.

Quality tiers are:

- `strict_valid`: session status is `complete`, manifest file status is
  `processed`, manifest quality status is `valid`, and no linkage contradiction
  exists.
- `warning_review`: session status is `complete`, manifest file status is
  `processed`, manifest quality status is `warning`, and no linkage
  contradiction exists. Individual manifest reason codes are retained and the
  row is excluded from the strict-valid subset by default.
- `excluded_unusable`: invalid quality states, processing failures,
  source-contract failures, source identity changes, or linkage contradictions.
- `calendar_only`: missing-file or no-active-candle calendar rows with no
  linkage contradiction.

Linked schema version `1` uses this exact column order:

```text
linked_schema_version
date
weekday
provider
instrument
quote_side
timeframe
source_filename
source_file_size_bytes
source_checksum_algorithm
source_checksum
manifest_schema_version
validation_rule_version
active_filter_rule_identity
session_definition_checksum
software_revision
session_status
manifest_file_status
manifest_quality_status
manifest_quality_reasons
linkage_status
linkage_reasons
quality_tier
manifest_total_row_count
manifest_active_row_count
session_total_csv_rows
session_active_candle_count
session_inactive_placeholder_count
daily_open
daily_high
daily_low
daily_close
daily_range
time_of_daily_high_utc
time_of_daily_low_utc
tokyo_open
tokyo_high
tokyo_low
tokyo_close
tokyo_range
tokyo_time_of_high_utc
tokyo_time_of_low_utc
tokyo_active_candle_count
london_open
london_high
london_low
london_close
london_range
london_time_of_high_utc
london_time_of_low_utc
london_active_candle_count
new_york_open
new_york_high
new_york_low
new_york_close
new_york_range
new_york_time_of_high_utc
new_york_time_of_low_utc
new_york_active_candle_count
```

Linked status values are:

- `linked`
- `calendar_only`
- `contradiction`
- `source_changed`
- `source_unavailable`

Linkage reason codes are machine-readable and separated by semicolons:

```text
DATE_COVERAGE_MISMATCH
DUPLICATE_DATE
PROVIDER_MISMATCH
INSTRUMENT_MISMATCH
QUOTE_SIDE_MISMATCH
TIMEFRAME_MISMATCH
SOURCE_FILENAME_MISMATCH
SOURCE_SIZE_MISMATCH
SOURCE_CHECKSUM_MISMATCH
SOURCE_CHECKSUM_UNAVAILABLE
SOURCE_IDENTITY_CHANGED
ROW_COUNT_MISMATCH
ACTIVE_COUNT_MISMATCH
STATUS_DISAGREEMENT
SESSION_VALUES_WITH_MANIFEST_FAILURE
MANIFEST_PROCESSED_SESSION_FAILED
```

Rule and run identity fields are:

- `manifest_schema_version`: existing manifest schema version.
- `validation_rule_version`: existing manifest validation-rule version.
- `active_filter_rule_identity`: current edge flat zero-volume active-filter
  identity, without changing filter behaviour.
- `session_definition_checksum`: deterministic SHA-256 checksum of the parsed
  session definitions.
- `software_revision`: full Git commit when the working tree is clean; the same
  commit with `-dirty` when tracked changes or non-ignored untracked files are
  present; otherwise `unknown`. The `-dirty` suffix identifies the base commit
  and warns that uncommitted changes were present. It does not uniquely identify
  the exact uncommitted code state.
- `linked_schema_version`: linked report schema version.

The implementation validates the current expected session names, generated
prefixes, calculation fields, and column order. A separate session-report schema
version and stable session identifiers remain deferred.

## Historical Baseline Report Behaviour

`historical_baseline_report.py` reads one existing linked observation report CSV
path directly:

```powershell
python historical_baseline_report.py reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
```

For that command, the output path is:

```text
reports/historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv
```

The tool validates the linked schema version, required baseline columns,
duplicate dates, `quality_tier`, and required identity/status fields before
building metrics. It does not read raw data, regenerate linked reports,
regenerate session reports, regenerate manifests, download data, or mutate
existing source files.

Baseline schema version `1` uses this exact column order:

```text
baseline_schema_version
source_report
metric_section
metric_name
observation_group
reason_code
field_name
count
min
median
mean
max
notes
```

The baseline report includes:

- coverage counts by quality tier, linkage status, session status, manifest file
  status, manifest quality status, manifest quality reasons, and linkage
  reasons;
- numeric availability counts for `daily_range`, `tokyo_range`, `london_range`,
  and `new_york_range`;
- descriptive range summaries for `daily_range`, `tokyo_range`, `london_range`,
  and `new_york_range`.

Strict-valid observations are the headline numeric baseline. Warning-review
observations are reported separately and split by manifest warning reason code
where available. Calendar-only and excluded/unusable rows appear in coverage and
availability counts but are excluded from numeric range summaries. Blank session
range values are unavailable values, not zeroes.

The baseline is descriptive only. It is not a strategy, signal generator,
backtest, prediction system, profitability analysis, support/resistance tool, or
execution model.

## Internal Flat Zero-Volume Diagnostic Behaviour

`internal_flat_zero_volume_diagnostic.py` reads one existing data quality
manifest path, one existing linked observation report path, and raw CSV files
from a selected data directory:

```powershell
python internal_flat_zero_volume_diagnostic.py reports/data_manifest_2024-01-01_to_2024-01-31.csv reports/linked_observation_report_2024-01-01_to_2024-01-31.csv --data-dir data_raw
```

For that command, the output path is:

```text
reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv
```

The tool validates that the manifest and linked report cover the same dates in
the same order. It reads raw CSV files only for manifest rows whose
`quality_reasons` include `INTERNAL_FLAT_ZERO_VOLUME`.

In current software terms, an internal flat zero-volume row is a numeric-valid
row where `volume == 0` and `open == high == low == close`, after contiguous
leading and trailing flat zero-volume placeholders have been excluded by the
active-candle filter. The diagnostic reconstructs contiguous internal runs,
checks that detected run rows reconcile with the manifest
`internal_inactive_row_count`, and writes one row per run.

Diagnostic schema version `1` uses this exact column order:

```text
diagnostic_schema_version
date
weekday
source_filename
manifest_file_status
manifest_quality_status
manifest_quality_reasons
total_row_count
active_row_count
leading_inactive_row_count
trailing_inactive_row_count
internal_inactive_row_count
run_number
run_start_utc
run_end_utc
run_row_count
tokyo_overlap_rows
london_overlap_rows
new_york_overlap_rows
outside_configured_session_rows
linked_quality_tier
linked_session_status
daily_range
tokyo_range
london_range
new_york_range
tokyo_active_candle_count
london_active_candle_count
new_york_active_candle_count
```

The diagnostic does not regenerate manifests, linked reports, session reports,
baselines, charts, downloads, or raw data. It does not infer market closure,
provider outage, corruption, harmlessness, or market meaning. Filtering
behaviour, warning policy, manifest schema, linked-report schema, and
historical-baseline behaviour are unchanged.

## Known Limitations

- The current research data is BID-only and does not include ASK prices or spread.
- The project does not yet model commission, slippage, latency, or execution assumptions.
- There is no backtesting engine yet.
- There is no multi-year downloader orchestration yet.
- `explorer.py`, `chart.py`, and `session_report.py` are currently built around XAUUSD one-minute BID CSV filenames.
- `data_manifest.py` is also built around the current XAUUSD one-minute BID source contract.
- `linked_observation_report.py` is also built around the current XAUUSD one-minute BID source contract and current Tokyo, London, and New York session column contract.
- `historical_baseline_report.py` is built around linked observation report
  schema version `1` and the current daily/Tokyo/London/New York range fields.
- `internal_flat_zero_volume_diagnostic.py` is built around the current manifest,
  linked-report, raw XAUUSD one-minute BID, and Tokyo/London/New York session
  contracts.
- Generated reports are overwritten when the same date range is run again.
- The data quality manifest is structural. It does not repair data or prove why flat zero-volume runs, missing minutes, or day-boundary gaps occurred.
- The linked observation report is non-canonical and does not repair, interpolate,
  or relabel raw data.
- The historical baseline report is descriptive only and does not classify
  warning reasons as harmless.
- Session windows are configurable research windows, not proof of exchange opening hours.
- The current project is a research platform, not evidence of a profitable trading system.
