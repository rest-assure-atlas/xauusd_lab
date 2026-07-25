# XAUUSD Lab

XAUUSD Lab is a long-term Python research project for studying XAU/USD, which is Gold priced in US Dollars.

The project will grow step by step into a research platform for downloading historical market data, storing it cleanly, analysing price behaviour, testing trading strategies, and eventually building a desktop research application.

Current version: **v0.11**

## Project Documentation

- [Agent guide](AGENTS.md)
- [Current state](docs/CURRENT_STATE.md)
- [Durable decisions](docs/DECISIONS.md)
- [Roadmap](docs/ROADMAP.md)
- [Workflow](docs/WORKFLOW.md)
- [Changelog](CHANGELOG.md)
- [Data quality manifest](docs/DATA_QUALITY_MANIFEST.md)

## Current Features

### Downloader

The downloader gets Dukascopy data for:

- XAU/USD
- 1-minute candles
- BID prices
- UTC timestamps

It downloads Dukascopy `.bi5` files, converts them into CSV format, and saves the CSV files locally.

## How To Run

You can run the downloader in two ways.

### Option 1: Use config.json

If you run the script without dates, it reads the date range and market settings from `config.json`:

```powershell
python data_downloader.py
```

The current `config.json` file contains:

```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "symbol": "XAUUSD",
  "price_side": "BID",
  "timeframe": "min_1"
}
```

### Option 2: Type Dates In The Terminal

Download one day:

```powershell
python data_downloader.py 2024-01-02
```

Download a date range:

```powershell
python data_downloader.py 2024-01-02 2024-01-31
```

The date range includes both the start date and the end date.

### Data Explorer

Use `explorer.py` to print basic daily statistics for one downloaded CSV file.

```powershell
python explorer.py 2024-01-26
```

For that command, the explorer loads:

```text
data_raw/XAUUSD_2024-01-26_1min_BID_UTC.csv
```

It prints the open, high, low, close, daily range, time of high, time of low, total CSV rows, active candles, inactive market-closed placeholder rows, and average volume for active candles.

You can also print Tokyo, London, and New York research-session statistics:

```powershell
python explorer.py 2024-01-26 --sessions
```

Session statistics include each session's local-time window, UTC window, open, high, low, close, range, time of high, time of low, and active candle count.

### Session Report

Use `session_report.py` to create one research-ready CSV row per requested date.

```powershell
python session_report.py 2024-01-01 2024-01-31
```

For that command, the report is saved to:

```text
reports/session_report_2024-01-01_to_2024-01-31.csv
```

The report includes daily active-candle statistics, inactive placeholder counts, and one set of Tokyo, London, and New York session statistics per date. Missing daily CSV files are kept in the report with `missing_file` status instead of stopping the run.

### Data Quality Manifest

Use `data_manifest.py` to create one derived provenance and validation row per requested date.

```powershell
python data_manifest.py 2024-01-01 2024-01-31
```

You can also choose a raw data folder explicitly:

```powershell
python data_manifest.py 2024-01-01 2024-01-31 --data-dir data_raw
```

For that command, the manifest is saved to:

```text
reports/data_manifest_2024-01-01_to_2024-01-31.csv
```

The manifest records expected raw filenames, file size, SHA-256 checksums, row-level validation counts, UTC day-boundary coverage, file status, quality status, and stable reason codes. Timestamp text must match `YYYY-MM-DD HH:MM:SS` exactly. The manifest does not edit, repair, reorder, or normalize raw CSV files.

### Linked Observation Report

Use `linked_observation_report.py` to create a separate, non-canonical
provenance-linking report for daily and configured-session observations.

```powershell
python linked_observation_report.py 2024-01-01 2024-01-31
```

You can also choose a raw data folder explicitly:

```powershell
python linked_observation_report.py 2024-01-01 2024-01-31 --data-dir data_raw
```

For that command, the linked report is saved to:

```text
reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
```

The linked report runs the existing manifest assessment and existing
session-calculation logic against the same verified raw source bytes during one
controlled operation. It keeps session status, manifest file status, and
manifest quality status separate, retains warning rows for review, and excludes
warnings from the strict-valid subset by default. It does not replace the
session report or data quality manifest.

### Historical Baseline Report

Use `historical_baseline_report.py` to create a descriptive baseline from one
existing linked observation report CSV.

```powershell
python historical_baseline_report.py reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
```

For that command, the baseline report is saved to:

```text
reports/historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv
```

The baseline report reads only the linked report. It does not read raw data,
regenerate reports, download data, or change source files. It reports coverage
counts, numeric availability counts, and descriptive daily/Tokyo/London/New York
range summaries. Strict-valid observations are the headline numeric baseline;
warning-review observations are shown separately and split by warning reason
code where available. Calendar-only and excluded/unusable rows are included in
coverage counts but excluded from numeric range summaries.

### Chart Viewer

Use `chart.py` to display a candlestick chart for one downloaded CSV file.

```powershell
python chart.py 2024-01-26
```

You can also open the chart in dark mode:

```powershell
python chart.py 2024-01-26 --dark
```

You can add Tokyo, London, and New York research-session overlays:

```powershell
python chart.py 2024-01-26 --sessions
```

Dark mode and session overlays can be combined:

```powershell
python chart.py 2024-01-26 --dark --sessions
```

For that command, the chart viewer loads:

```text
data_raw/XAUUSD_2024-01-26_1min_BID_UTC.csv
```

The chart shows 1-minute candlesticks with time on the x-axis and price on the y-axis. Hover near a candle to see its timestamp, open, high, low, and close values.

The session overlays and explorer session statistics are configurable research windows, not universal exchange opening hours. Their defaults live in `sessions.json` and use local time zones, which are converted to UTC for the selected date using Python's `zoneinfo` support.

Raw CSV files are never edited. Charting and statistics ignore only contiguous flat, zero-volume placeholder rows at the beginning or end of a daily file, which prevents market-closed rows from distorting charts and calculations.

External Python packages are listed in `requirements.txt`. Install them with:

```powershell
python -m pip install -r requirements.txt
```

Session timezone conversion uses Python's standard-library `zoneinfo` module. On Windows, `tzdata` from `requirements.txt` gives Python the IANA time zone names such as `America/New_York`.

## Testing

Run the automated test suite with:

```powershell
python -m unittest discover -s tests
```

The tests create deterministic synthetic CSV fixtures in temporary folders. They do not require downloaded raw CSV files in `data_raw/`.


## Output Files

Downloaded CSV files are saved in the `data_raw/` folder.

Example:

```text
data_raw/XAUUSD_2024-01-02_1min_BID_UTC.csv
```

If a CSV file already exists, the downloader skips that day instead of downloading it again.

Generated research reports are saved in the `reports/` folder.

Data quality manifests are also saved in the `reports/` folder.

Linked observation reports are saved in the `reports/` folder as separate
non-canonical reconciliation artifacts.

Historical baseline reports are saved in the `reports/` folder as descriptive
summaries of existing linked observation reports.

## Failed Downloads

Failed downloads are logged in:

```text
logs/failed_downloads.txt
```

The downloader retries each failed day up to 3 times before writing it to the failed download log.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for completed milestones and clearly labelled proposed future work.
