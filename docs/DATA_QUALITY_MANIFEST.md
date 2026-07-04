# Data Quality And Provenance Manifest

The data quality manifest is a derived CSV report for raw Dukascopy XAU/USD
one-minute BID quote files. It does not download data, edit raw CSV files,
repair gaps, interpolate candles, or change session-report calculations.

The manifest creates one row per requested calendar date and records:

- expected raw filename;
- readable file size and SHA-256 checksum;
- structural validation counts;
- conservative suitability status for downstream minute-level research.

The source contract is:

- Provider: `Dukascopy`
- Instrument: `XAUUSD`
- Quote side: `BID`
- Timeframe: `1min`
- Expected filename: `XAUUSD_YYYY-MM-DD_1min_BID_UTC.csv`
- Expected columns, in order: `timestamp_utc, open, high, low, close, volume`
- Expected timestamp format: `YYYY-MM-DD HH:MM:SS`
- Timestamps are treated as UTC.

Timestamp text must match the expected zero-padded format exactly. Non-padded
forms such as `2024-1-2 0:0:0`, fractional-second forms such as
`2024-01-02 00:00:00.000000`, and values with leading or trailing whitespace
are invalid timestamps. A whole-second timestamp such as
`2024-01-02 00:00:30` is parseable, but is counted as off-minute because the
seconds value is not zero.

## CLI

Run a manifest for an inclusive date range:

```powershell
python data_manifest.py 2024-01-01 2024-01-31
```

Run against an explicit raw data directory:

```powershell
python data_manifest.py 2024-01-01 2024-01-31 --data-dir data_raw
```

The selected data directory must already exist. An existing empty directory is
valid and produces one `missing_file` row per requested date.

Reports are written to:

```text
reports/data_manifest_YYYY-MM-DD_to_YYYY-MM-DD.csv
```

The same date-range report is overwritten deterministically. The report does
not include a generated timestamp.

## Versions

Every row contains:

- `manifest_schema_version`: `1`
- `validation_rule_version`: `raw_data_quality_v1`

## Column Order

The manifest uses this stable column order:

```text
manifest_schema_version
validation_rule_version
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
file_status
quality_status
quality_reasons
total_row_count
active_row_count
leading_inactive_row_count
trailing_inactive_row_count
internal_inactive_row_count
first_timestamp_utc
last_timestamp_utc
first_active_timestamp_utc
last_active_timestamp_utc
duplicate_timestamp_count
out_of_order_timestamp_count
missing_minute_count
internal_gap_count
maximum_internal_gap_minutes
leading_day_gap_minutes
trailing_day_gap_minutes
invalid_timestamp_count
off_minute_timestamp_count
wrong_date_timestamp_count
invalid_numeric_row_count
ohlc_consistency_failure_count
negative_volume_count
```

## File Status

`missing_file`
: The expected raw CSV filename is absent. Filename is still recorded; size,
algorithm, and checksum are blank.

`empty_file`
: The file is zero bytes, header-only, or has zero data rows after a valid
header.

`parse_failed`
: The file cannot be assessed under the expected CSV contract. This includes
read/decode errors, incorrect header or column order, and malformed row shape.

`no_active_candles`
: The file is structurally processable and all rows are removed by the existing
leading/trailing flat zero-volume placeholder rule.

`processed`
: The file is structurally processable and contains at least one active row, or
contains row-level defects that can still be counted.

## Quality Status

`valid`
: The file is processed and no quality reasons were found.

`warning`
: The file is processed but needs review before downstream research use. In
`raw_data_quality_v1`, warnings cover missing-minute gaps, partial day-boundary
coverage, and internal flat zero-volume rows when no invalid source-contract
defect is present.

`invalid`
: The file is unsafe for current downstream minute-level research without
review because a definite source-contract violation or structural failure was
found. This is not proof that Dukascopy or the market is corrupted.

`not_assessed`
: The expected file is missing, or a clean no-active-candle file does not
contain active rows to assess for research use.

`quality_reasons` is blank only when `quality_status` is `valid`.

## Reason Codes

Reason codes are machine-readable and separated by semicolons in deterministic
order.

```text
MISSING_FILE
EMPTY_FILE
READ_ERROR
HEADER_MISMATCH
ROW_SHAPE_MISMATCH
INVALID_TIMESTAMP
TIMESTAMP_OFF_MINUTE
TIMESTAMP_DATE_MISMATCH
INVALID_NUMERIC
OHLC_INCONSISTENT
NEGATIVE_VOLUME
DUPLICATE_TIMESTAMP
OUT_OF_ORDER_TIMESTAMP
MISSING_MINUTES
PARTIAL_DAY_COVERAGE
INTERNAL_FLAT_ZERO_VOLUME
NO_ACTIVE_CANDLES
```

## Validation Definitions

Duplicate timestamp
: A successfully parsed timestamp occurrence after its first occurrence.

Out-of-order timestamp
: A successfully parsed timestamp earlier than the previous successfully parsed
timestamp in file order. Equal timestamps are duplicates, not out-of-order rows.

Off-minute timestamp
: A parsed timestamp whose seconds value is not zero.

Wrong-date timestamp
: A parsed timestamp whose UTC calendar date differs from the requested
manifest row date.

First timestamp
: The earliest successfully parsed timestamp chronologically. If invalid
timestamps prevent reliable bounds, this field is blank.

Last timestamp
: The latest successfully parsed timestamp chronologically. If invalid
timestamps prevent reliable bounds, this field is blank.

First active timestamp
: The earliest successfully parsed timestamp chronologically among active rows.
If any active timestamp is unparseable, this field is blank.

Last active timestamp
: The latest successfully parsed timestamp chronologically among active rows.
If any active timestamp is unparseable, this field is blank.

Missing minute
: An absent one-minute timestamp between consecutive sorted unique valid
timestamps.

Internal gap
: One sequence of one or more missing minutes between sorted unique valid
timestamps.

Leading day gap minutes
: The number of absent one-minute timestamp positions between requested-day
00:00 UTC and the earliest unique valid timestamp. A complete day has `0`.

Trailing day gap minutes
: The number of absent one-minute timestamp positions between the latest unique
valid timestamp and requested-day 23:59 UTC. A complete day has `0`.

Partial day coverage
: A processed file has partial day coverage when either day-boundary gap is
greater than zero. This produces `PARTIAL_DAY_COVERAGE` and a `warning` status
unless an invalid reason makes the file `invalid`.

Inactive edge candle
: A row where `volume == 0` and `open == high == low == close`, contiguous at
the start or end of the file.

Internal inactive candle
: The same flat zero-volume condition after leading and trailing inactive edges
have been removed. These rows are preserved and reported as warnings.

Invalid numeric row
: Any row where an OHLC or volume value is unparseable, `NaN`, or infinite.

OHLC consistency failure
: Any numeric-valid row where `high < open`, `high < close`, `low > open`,
`low > close`, or `high < low`.

Negative volume
: Any numeric-valid row where `volume < 0`.

Zero volume alone is not invalid.

Internal missing-minute metrics and boundary-coverage metrics are blank when
invalid, off-minute, or wrong-date timestamps prevent a reliable continuity
calculation. Boundary coverage uses the earliest and latest chronological unique
valid timestamps, not file order or total row count. Active-row metrics are
blank when invalid numeric rows prevent reliable placeholder filtering.

## Terminal Summary

After a successful run, the CLI prints:

- requested dates
- processed files
- missing files
- empty files
- parse failures
- no-active-candle files
- valid dates
- warning dates
- invalid dates
- not-assessed dates
- output path

The file-status counts reconcile to requested dates, and the quality-status
counts also reconcile to requested dates.

## Limitations

The manifest is structural and conservative. It does not:

- download market data;
- modify raw CSV files;
- repair or interpolate data;
- create a provider or holiday calendar;
- prove market closures, provider failures, or trading-session meaning;
- calculate aggregate market statistics;
- add trading rules, backtesting, execution modelling, or profitability
  analysis.

Internal flat zero-volume runs, missing-minute gaps, and day-boundary gaps are
structural observations requiring review before downstream research use.
