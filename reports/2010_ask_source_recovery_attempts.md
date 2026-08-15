# 2010 ASK Source Recovery Attempts

- Mission: `MULTI_YEAR_ACQUISITION_PHASE1_2010_2014`
- Started UTC: `2026-08-11T04:16:00Z`
- Scope: `2010-03-26` ASK and `2010-04-13` ASK only
- Provider and method: existing Dukascopy XAUUSD `ASK_candles_min_1.bi5` acquisition through `data_downloader.py`
- Methodology changed: no
- Source provider changed: no
- BID-derived, synthetic, filled, or interpolated ASK used: no

## Starting Evidence

- Checkpoint gate was `MULTIYEAR_SOURCE_AVAILABILITY_BLOCK`.
- 2010 BID raw inventory was 365 files.
- 2010 ASK raw inventory was 363 files.
- Missing ASK dates were exactly `2010-03-26` and `2010-04-13`.
- Matching BID files existed for both missing ASK dates.
- Prior failed-download log entries for both missing ASK dates recorded Dukascopy HTTP 503 responses after bounded retry passes.

## Recovery Attempts

- `2010-03-26` ASK: ran `python3 data_downloader.py --quote-side ASK 2010-03-26 2010-03-26`; result saved `data_raw/XAUUSD_2010-03-26_1min_ASK_UTC.csv` with 1440 rows.
- `2010-04-13` ASK: ran `python3 data_downloader.py --quote-side ASK 2010-04-13 2010-04-13`; result saved `data_raw/XAUUSD_2010-04-13_1min_ASK_UTC.csv` with 1440 rows.

## Classification

- `2010-03-26` ASK: `RETRYABLE_SOURCE_RESPONSE`.
- `2010-04-13` ASK: `RETRYABLE_SOURCE_RESPONSE`.

## Rationale

Both dates were absent locally after repeated HTTP 503 responses from the approved Dukascopy path, while the same approved downloader and side-specific URL later returned valid ASK files without any path, provider, parsing, or methodology change.
