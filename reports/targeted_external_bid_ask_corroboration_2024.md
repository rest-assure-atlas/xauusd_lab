# Targeted External BID/ASK Corroboration 2024

Status: source-selection stop; no external market data acquired.
Gate result: BLOCKED_EXTERNAL_ACCESS_REQUIRES_APPROVAL

## Executive conclusion
The existing Lab evidence was sufficient to define the targeted corroboration campaign, but no defensible independent historical XAUUSD BID/ASK source passed the approved no-account/no-payment/no-secret/no-broker-API stop rule. The best technically relevant options appear to require vendor payment/licensing or broker/API account access. Acquisition therefore stopped before external data retrieval.

## Evidence basis read
- `reports/pre_modelling_spread_evidence_policy.md`
- `reports/top_warning_date_spread_integrity_review_2024.md`
- `reports/strict_vs_warning_spread_sensitivity_2024-01-01_to_2024-12-31.md`
- `reports/active_spread_tail_audit_2024-01-01_to_2024-12-31.md`
- `reports/bid_ask_reconciliation_2024-01-01_to_2024-12-31.csv`

## Target verification
- Active warning_review_pair rows with spread >= 2.0: 84.
- Dates containing those rows: 2024-01-25, 2024-02-18, 2024-05-01, 2024-05-15, 2024-07-11, 2024-09-11, 2024-10-10, 2024-12-11, 2024-12-12.
- Count by date: 2024-01-25=3, 2024-02-18=12, 2024-05-01=1, 2024-05-15=1, 2024-07-11=1, 2024-09-11=1, 2024-10-10=1, 2024-12-11=62, 2024-12-12=2.
- Placeholder/market-closed warning_review rows with spread >= 2.0, excluded from active target selection: 1572.
- Active row counts cross-check: all active 355891; warning_review active 285726; strict_valid active 70165.
- Prompt-listed p99 warning dates without active warning spread >= 2.0: 2024-12-26, 2024-12-30, 2024-05-22. These remain useful stress/date controls but are not part of the 84-row >=2.0 target population.

## Target windows
Machine-readable windows: `reports/targeted_external_bid_ask_corroboration_windows_2024.csv`.

| kind | date | window UTC | cluster UTC | ge2 rows | max spread | notes |
|---|---:|---|---|---:|---:|---|
| warning_ge2_target | 2024-01-25 | 2024-01-25 22:52 to 2024-01-25 23:59 | 23:22 to 23:29 | 3 | 2.490000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-02-18 | 2024-02-18 22:35 to 2024-02-18 23:43 | 23:05 to 23:13 | 6 | 5.981000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-02-18 | 2024-02-18 22:55 to 2024-02-19 00:00 | 23:25 to 23:30 | 6 | 4.440000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-05-01 | 2024-05-01 20:29 to 2024-05-01 21:29 | 20:59 to 20:59 | 1 | 2.100000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-05-15 | 2024-05-15 11:59 to 2024-05-15 12:59 | 12:29 to 12:29 | 1 | 2.107000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-07-11 | 2024-07-11 11:59 to 2024-07-11 12:59 | 12:29 to 12:29 | 1 | 3.954000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-09-11 | 2024-09-11 11:59 to 2024-09-11 12:59 | 12:29 to 12:29 | 1 | 3.224000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-10-10 | 2024-10-10 11:59 to 2024-10-10 12:59 | 12:29 to 12:29 | 1 | 2.954000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-12-11 | 2024-12-11 03:14 to 2024-12-11 04:19 | 03:44 to 03:49 | 2 | 2.451000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-12-11 | 2024-12-11 04:02 to 2024-12-11 05:07 | 04:32 to 04:37 | 5 | 3.660000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-12-11 | 2024-12-11 04:20 to 2024-12-11 07:06 | 04:50 to 06:36 | 50 | 5.120000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-12-11 | 2024-12-11 06:42 to 2024-12-11 07:42 | 07:12 to 07:12 | 1 | 2.040000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-12-11 | 2024-12-11 12:59 to 2024-12-11 13:59 | 13:29 to 13:29 | 1 | 3.617000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-12-11 | 2024-12-11 22:41 to 2024-12-11 23:43 | 23:11 to 23:13 | 3 | 2.097000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-12-12 | 2024-12-12 01:00 to 2024-12-12 02:00 | 01:30 to 01:30 | 1 | 2.510000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_ge2_target | 2024-12-12 | 2024-12-12 12:59 to 2024-12-12 13:59 | 13:29 to 13:29 | 1 | 2.744000 | active warning_review spread >=2.0 cluster with 30m context |
| warning_p99_major_control | 2024-12-26 | 2024-12-25 23:30 to 2024-12-27 00:26 | 00:00 to 23:56 | 0 | 1.980000 | prompt-listed warning p99/date cluster; verified no active warning spread >=2.0 rows |
| warning_p99_major_control | 2024-12-30 | 2024-12-29 23:33 to 2024-12-31 00:25 | 00:03 to 23:55 | 0 | 1.380000 | prompt-listed warning p99/date cluster; verified no active warning spread >=2.0 rows |
| warning_p99_major_control | 2024-05-22 | 2024-05-21 23:30 to 2024-05-22 22:31 | 00:00 to 22:01 | 0 | 1.440000 | prompt-listed warning p99/date cluster; verified no active warning spread >=2.0 rows |
| control_warning_non_extreme | 2024-01-02 | 2024-01-02 11:30 to 2024-01-02 12:30 | 12:00 to 12:00 | 0 | 0.590000 | normal warning_review control; date max spread <0.62 |
| control_strict_normal | 2024-03-15 | 2024-03-15 11:30 to 2024-03-15 12:30 | 12:00 to 12:00 | 0 | 0.570000 | normal strict_valid control; date max spread <0.62 |
| control_strict_extreme | 2024-04-05 | 2024-04-05 20:29 to 2024-04-05 21:29 | 20:59 to 20:59 | 1 | 2.810000 | strict_valid active spread >=2.0 control |

## Source assessment
The source-selection standard required independence from Dukascopy, historical XAUUSD BID/ASK or equivalent quote data for bounded windows, no payment, no broker/trading account, no credentials/secrets, no substantial install, and clear provenance/licensing. Network checks were limited to source/provider documentation pages or provider access pages; no external market data was downloaded.

| candidate | why considered | result | blocker |
|---|---|---|---|
| OANDA v20 / broker candle feed | Likely informative: broker-independent from Dukascopy; v20 candles can expose bid/ask style pricing for instruments where account has access. | BLOCKED_EXTERNAL_ACCESS_REQUIRES_APPROVAL | Requires OANDA account/API token and broker API access; may be trading-capable even if used read-only. |
| FXCM/ForexConnect historical candles | Potentially informative independent broker feed with historical quote/candle access. | BLOCKED_EXTERNAL_ACCESS_REQUIRES_APPROVAL | Requires account/token and often client/API package; broker API access not approved. |
| LSEG/Refinitiv, Bloomberg, AlgoSeek, FirstRate Data | Potentially high-quality independent historical quote data. | BLOCKED_EXTERNAL_ACCESS_REQUIRES_APPROVAL | Paid/licensed products and account/vendor access required. |
| Polygon/Massive forex aggregates | Accessible documentation, but not suitable under current rules. | NOT_SELECTED | API key/plan likely required; forex aggregate semantics do not establish historical XAUUSD BID+ASK quote windows sufficient for this task. |
| TrueFX | Public site reachable; may be independent for FX quotes. | NOT_SELECTED | Documentation/access did not establish free no-account historical XAUUSD BID/ASK windows; likely FX majors rather than spot gold. |
| HistData.com XAUUSD M1 download | Public XAUUSD M1 page reachable. | NOT_SELECTED | Does not establish bid+ask fields, source independence/provenance is insufficient, and historical bars are not a safe independent BID/ASK corroboration source. |
| Alpha Vantage / Twelve Data / Yahoo/Stooq-like chart feeds | Often accessible for prices/charts. | NOT_SELECTED | Mid/last/OHLC style data, not independent historical BID/ASK quote windows for spread corroboration. |

## Stop-rule decision
No candidate satisfied all approved acquisition conditions. The smallest defensible next step is not a full-year replication; it is approval for a targeted independent quote-window campaign using a vetted provider that may require one of the currently prohibited access changes, most likely a read-only broker/vendor historical-data account or a paid/licensed data source. Any such approval should specify provider, account/API boundaries, read-only use, exact windows, storage location, and secret handling before acquisition.

## Validation performed
- Recomputed the warning_review active spread >= 2.0 population directly from the reconciliation CSV: 84 rows.
- Confirmed the 84 target rows are active/non-placeholder by excluding `MARKET_CLOSED_PLACEHOLDER` in `pair_quality_reasons`.
- Reconciled date list and counts against the existing top warning-date review and sensitivity findings; noted that 2024-12-26, 2024-12-30, and 2024-05-22 are p99/date-cluster targets but not >=2.0 active warning dates.
- Created target/control windows with explicit UTC start/end and preserved the underlying cluster start/end and row counts in CSV.
- No raw BID/ASK data, inherited reports, quality definitions, session definitions, reconciliation logic, or modelling code was changed.

## Gate result
BLOCKED_EXTERNAL_ACCESS_REQUIRES_APPROVAL

## Recommended next research gate
Human/Director decision on whether to approve a tightly bounded external-source access method for these target windows only, preferably read-only historical BID/ASK quote access from a vetted independent broker/vendor source. Do not proceed to execution-cost modelling until this gate is resolved or the policy is amended.
