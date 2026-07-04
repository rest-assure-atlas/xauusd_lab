# Current State

Verified milestone: **v0.11**.

XAUUSD Lab is a Python research project for studying XAU/USD, meaning gold priced in US dollars. The current repository focuses on downloading Dukascopy one-minute BID data, exploring daily data, charting candles, applying configurable research-session windows, producing multi-day session research reports, and creating data quality manifests for raw CSV provenance and validation.

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

The current v0.11 test suite contains 67 tests and currently passes with:

```powershell
python -m unittest discover -s tests
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

## Known Limitations

- The current research data is BID-only and does not include ASK prices or spread.
- The project does not yet model commission, slippage, latency, or execution assumptions.
- There is no backtesting engine yet.
- There is no multi-year downloader orchestration yet.
- `explorer.py`, `chart.py`, and `session_report.py` are currently built around XAUUSD one-minute BID CSV filenames.
- `data_manifest.py` is also built around the current XAUUSD one-minute BID source contract.
- Generated reports are overwritten when the same date range is run again.
- The data quality manifest is structural. It does not repair data or prove why flat zero-volume runs, missing minutes, or day-boundary gaps occurred.
- Session windows are configurable research windows, not proof of exchange opening hours.
- The current project is a research platform, not evidence of a profitable trading system.
