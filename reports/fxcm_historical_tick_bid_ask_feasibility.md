# FXCM Historical Tick BID/ASK Feasibility

Date: 2026-08-10
Status: documentation/feasibility research only
Gate result: BLOCKED_PENDING_FXCM_CAPABILITY_CLARIFICATION

## Mission scope

This report determines whether an FXCM demo/practice account could provide true historical XAU/USD tick-level BID/ASK data suitable for the existing independent corroboration gate.

This report does not create or access an FXCM account, log into FXCM, generate or use credentials, acquire external market data, place or simulate orders, use trading/order endpoints, install ForexConnect or any package, modify raw BID/ASK evidence, change methodology, change schemas, change quality rules, change session definitions, change research policy, or touch the authoritative Windows repo.

The `/workspace/XAUUSD_Lab` path was not mounted in this execution environment. The active Lab copy visible here is `/home/openclaw/.openclaw/workspace/XAUUSD_Lab`; this artifact was written under that Lab copy only.

## Lab state read

Directly read:

- `reports/pre_modelling_spread_evidence_policy.md`
- `reports/targeted_external_bid_ask_corroboration_2024.md`
- `reports/targeted_external_bid_ask_corroboration_windows_2024.csv`
- `reports/oanda_practice_historical_bid_ask_feasibility.md`

Confirmed target evidence requirement:

- Warning-review active clusters cannot enter baseline execution-cost modelling before targeted external/source corroboration and a later recorded modelling gate.
- The target population is 84 active `warning_review_pair` rows with spread >= 2.0.
- Dates: 2024-01-25, 2024-02-18, 2024-05-01, 2024-05-15, 2024-07-11, 2024-09-11, 2024-10-10, 2024-12-11, 2024-12-12.
- Count by date: 2024-01-25=3, 2024-02-18=12, 2024-05-01=1, 2024-05-15=1, 2024-07-11=1, 2024-09-11=1, 2024-10-10=1, 2024-12-11=62, 2024-12-12=2.
- Existing design has 16 `warning_ge2_target` windows, 3 `warning_p99_major_control` windows, and 3 additional controls.
- The external source must provide BID and ASK, not only mid/last price, and should allow comparison of timestamp alignment, BID, ASK, spread direction/magnitude, and whether widening appears around the same minute/hour/session window.
- Agreement can advance warning-review clusters only to a later modelling-policy gate; disagreement keeps affected warning rows out of baseline modelling; lack of matching coverage is inconclusive, not confirmation.

OANDA comparison baseline:

- OANDA practice historical candles were classified `ADEQUATE_ONLY_FOR_COARSE/DIRECTIONAL_CORROBORATION`.
- OANDA's major limitation is S5 candle OHLC aggregation, which cannot reconstruct synchronized point-in-time BID/ASK spread.
- A true synchronized historical tick source would be materially stronger than OANDA S5 candles if availability, retention, account access, fields, and provenance are documented.

## First-party FXCM sources consulted

- FXCM GitHub organization repository metadata for `fxcm/ForexConnectAPI`, `fxcm/JavaAPI`, and `fxcm/MarketData`, `https://api.github.com/orgs/fxcm/repos?per_page=100`
- FXCM, `ForexConnectAPI` README, `https://raw.githubusercontent.com/fxcm/ForexConnectAPI/master/README.md`
- FXCM, `ForexConnectAPI` AvailableSymbols, `https://raw.githubusercontent.com/fxcm/ForexConnectAPI/master/AvailableSymbols.md`
- FXCM, `MarketData` README, `https://raw.githubusercontent.com/fxcm/MarketData/master/README.md`
- FXCM, `MarketData` TickData README, `https://raw.githubusercontent.com/fxcm/MarketData/master/TickData/README.md`
- FXCM, `MarketData` TickData Python 3.4 example, `https://raw.githubusercontent.com/fxcm/MarketData/master/TickData/TickData34.py`
- FXCM, `JavaAPI` README, `https://raw.githubusercontent.com/fxcm/JavaAPI/master/README.md`
- FXCM/ForexConnect/FXCodeBase direct help and marketing URLs attempted but blocked by Cloudflare/browser challenge or unavailable through non-browser curl:
  - `https://fxcodebase.com/wiki/index.php/Category:ForexConnect`
  - `https://fxcodebase.com/bin/forexconnect/1.6.5/help/`
  - `https://www.fxcm.com/markets/forexconnect/`

Only first-party FXCM/ForexConnect/FXCodeBase material was used.

## Capability findings

### ForexConnect history access

The `fxcm/ForexConnectAPI` README states that the SDK is designed to get trading data, trade, load price histories, and subscribe for the most recent prices. It says ForexConnect can be used on a Trading Station account with no extra setup. It requires signing the EULA, a FXCM TSII account, and downloading the ForexConnect SDK. It gives demo connection parameters:

- URL: `www.fxcorporate.com/Hosts.jsp`
- username
- password
- connection: `demo`

It says price history requires non-table manager and points to examples under `NonTableManagerSamples/GetHistPrices`, but those installed package examples were not accessible without downloading/installing the SDK. The README also links a historical-data downloading example archive, but the archive could not be inspected through the current non-browser path.

The `fxcm/JavaAPI` README states that the Java API is a wrapper SDK of the FIX API and includes streaming executable prices, orders, and a `MDH` test command to retrieve market data history. It requires a FXCM account, package download, username/password, and a `Demo` or `Real` connection. This confirms a second FXCM official API family can retrieve market data history, but it does not establish XAU/USD tick BID/ASK history fields.

### Public FXCM tick repository

The `fxcm/MarketData` TickData README documents free historical tick data. It says:

- "Enjoy free access to our historical Tick Data."
- The repository contains tick data from January 2019.
- Data is compiled by trading instrument for each trading week.
- Files are stored in a public directory and updated monthly.
- URL pattern: `https://tickdata.fxcorporate.com/{instrument}/{year}/{int of week of year}.csv.gz`.
- Instruments listed: AUDCAD, AUDCHF, AUDJPY, AUDNZD, CADCHF, EURAUD, EURCHF, EURGBP, EURJPY, EURUSD, GBPCHF, GBPJPY, GBPNZD, GBPUSD, NZDCAD, NZDCHF, NZDJPY, NZDUSD, USDCAD, USDCHF, USDJPY, AUDUSD, CADJPY, GBPCAD, USDTRY, EURNZD, GBPAUD.
- Years listed: 2019, 2020, 2021, 2022, 2023.
- Timestamps are UTC.
- Data points are indicative and based on the lowest spreads available exclusively on Active Trader accounts.

The public tick repository does not list XAU/USD or XAUUSD and does not list year 2024 in the current README. Because external data acquisition was prohibited, no tick CSV was downloaded to inspect its header/columns.

The `TickData34.py` example constructs URLs for the public tick files and lists FX currency symbols only. It does not document record columns, BID fields, ASK fields, or synchronized spread reconstruction.

### XAU/USD historical support

The `fxcm/ForexConnectAPI` AvailableSymbols file lists a small portion of popular symbols and timeframes for resolutions `1minute`, `1hour`, and `1day`. It includes:

- `XAU/USD` m1 from `2009-02-24T16:00:00Z`
- `XAU/USD` H1 from `2009-02-24T16:00:00Z`
- `XAU/USD` D1 from `1920-01-29T17:00:00Z`

This supports historical bar availability for XAU/USD, including coverage before 2024. It does not document tick-level XAU/USD availability.

### Historical tick record structure

The accessible first-party docs did not provide an exact historical tick CSV schema or ForexConnect tick-reader schema. Specifically, they did not establish whether each historical tick record contains:

- synchronized BID and ASK;
- separate bid/ask quote updates with a common timestamp;
- bid-only, ask-only, mid, or trade/last fields;
- indicative Active Trader fields rather than account-specific executable fields;
- raw versus filtered/sampled/transformed tick observations.

Because the current mission prohibits data acquisition, this could not be resolved by downloading a sample tick CSV.

### 2024 availability and retention

First-party material confirmed:

- Public tick files are documented as 2019 through 2023 in the current TickData README.
- Public tick files are updated monthly according to the README, but the listed years stop at 2023.
- XAU/USD bar data is documented from 2009 for m1/H1 and 1920 for D1 in the available-symbols file.

First-party material did not confirm:

- 2024 XAU/USD tick history availability.
- Demo-account access to 2024 XAU/USD tick history.
- Retention/depth limits for authenticated ForexConnect historical tick data.
- Paging/request/tick-count limits for authenticated tick retrieval.

### Demo, live, installation, and regional/account requirements

Demo/account:

- ForexConnect README explicitly says a FXCM TSII account is required and gives `connection="demo"` as a connection parameter.
- JavaAPI README says the connection name can be `Demo` or `Real`.
- The accessible docs do not state whether demo credentials can access historical XAU/USD tick data specifically.
- No live/funded account requirement was found in the accessible docs, but no documentation proved that live/funded access is unnecessary for XAU/USD tick history.

Installation:

- ForexConnect requires downloading the ForexConnect SDK for full package examples and documents.
- JavaAPI requires downloading the Java package.
- No package was installed in this mission.
- The public tick-file endpoint can be accessed as HTTP files without ForexConnect installation, but that documented public tick set does not include XAU/USD or 2024.

Regional/account:

- FXCM disclaimers identify Stratos Markets Limited and Stratos Europe Limited, among other entities. Stratos Europe Limited is Cyprus-regulated.
- The accessible documentation does not determine whether an Ireland-based user would be under a specific entity with different instrument/history permissions.
- The accessible documentation does not state whether XAU/USD tick history availability varies by regulatory/account division.

### Account-specific pricing and data caveats

The public MarketData docs state that data points are indicative and based on the lowest spreads available exclusively on Active Trader accounts. This is a material caveat:

- Public tick data, even if XAU/USD existed, would not necessarily match a demo/practice account's executable pricing.
- It could still be independent from Dukascopy, but it would need clear labelling as indicative/Active Trader-based FXCM data.
- ForexConnect authenticated history may differ from public MarketData files, but the accessible docs did not establish how.

## Data-type distinction

A. Historical ticks:

- Public FXCM tick files are documented for selected FX instruments, 2019 through 2023, weekly compressed CSVs, UTC timestamps, updated monthly.
- XAU/USD is not in the documented public tick instrument list.
- 2024 is not in the documented public tick year list.
- Accessible docs do not show tick record fields or prove synchronized BID/ASK.
- Authenticated ForexConnect tick history for XAU/USD is not proven by accessible first-party docs.

B. Historical bars/candles:

- ForexConnect/FXCM historical price loading is documented generally.
- AvailableSymbols documents XAU/USD m1/H1/D1 bar availability from 2009/2009/1920.
- Bars/candles are not equivalent to true tick-level BID/ASK corroboration unless they include synchronized bid/ask at adequate resolution, which was not established.

C. Live streaming prices:

- ForexConnect and JavaAPI support live/recent price subscriptions/streaming.
- Live streaming is not historical 2024 tick retrieval.
- Trading/order functionality is present in the same SDK/API families and must be procedurally and technically excluded from any future test.

## Comparison with OANDA

OANDA:

- Documented S5 historical BID/ASK candles.
- XAU_USD account-specific availability remains to be authenticated.
- Major limitation is candle OHLC aggregation; not synchronized historical tick spread.
- Classified `ADEQUATE_ONLY_FOR_COARSE/DIRECTIONAL_CORROBORATION`.

FXCM:

- Public tick files are stronger in principle because true tick records could, if they include synchronized bid/ask, support point-in-time spread corroboration.
- Accessible first-party docs do not prove XAU/USD public tick coverage, 2024 public tick coverage, tick CSV schema, synchronized BID/ASK fields, demo access, or authenticated ForexConnect tick availability.
- XAU/USD is documented for m1/H1/D1 bars, not ticks.

Therefore FXCM is potentially more relevant than OANDA only if an authenticated demo/practice capability check or first-party clarification proves synchronized XAU/USD historical BID/ASK ticks for 2024. Until then, OANDA is better documented for BID/ASK fields, while FXCM is better in theory but blocked on capability proof.

## Adequacy classification

Classification: D. UNCERTAIN_PENDING_DEMO_AUTHENTICATED_TEST.

Rationale:

- Do not call FXCM primary-quality unless true synchronized historical BID/ASK tick evidence is actually supported.
- First-party docs confirm historical price APIs and public tick files, but not the exact capability required: 2024 XAU/USD synchronized BID/ASK historical ticks accessible through demo/practice credentials.
- Public FXCM tick files are not enough because XAU/USD is not listed, 2024 is not listed, and record fields are not documented in the accessible sources.
- Historical bars are not enough for the exact tick-level requirement and would fall back to coarse corroboration, similar to or weaker than OANDA depending on field structure.

## Minimum-permission design

If a future authenticated demo test is approved, the smallest safe boundary should be:

- Account: dedicated FXCM demo/practice/TSII account only; no deposit; no live/funded account.
- Human gate: explicit human approval before account creation, credentials, SDK/package download, SDK/package installation, endpoint access, or data acquisition.
- Data scope: only historical market data for the already-defined target/control windows in `targeted_external_bid_ask_corroboration_windows_2024.csv`.
- Capability sequence:
  - Confirm available instruments include XAU/USD.
  - Confirm available historical granularities include tick-level for XAU/USD.
  - Confirm requested 2024 target/control windows are within retained history.
  - Confirm returned tick records contain synchronized BID and ASK or an explicitly documented equivalent point-in-time quote.
  - Stop if any of those checks fail.
- Endpoint/API allowlist:
  - Historical market-data/history calls only.
  - XAU/USD only.
  - Existing target/control windows only.
  - Read-only calls only.
- Blocklist:
  - All order, trade, position, account-change, account-configuration, live streaming/subscription, and non-history table mutation paths.
  - No order simulation or trading tests.
- Installation:
  - If ForexConnect installation is required, it needs a separate approval step specifying package source, version, checksum/provenance, install location inside the Lab/sandbox only, and removal procedure.
  - No installation is authorized by this artifact.
- Credential handling:
  - Credentials must never be sent in Telegram/chat, committed to files, written to reports, printed in shell history, or included in logs.
  - Prefer an approved local secret store or one-shot human-entered environment variables in a terminal that does not echo.
  - Store only sanitized request metadata and approved output.
- Technical prevention:
  - Use a wrapper that rejects non-history calls, rejects non-XAU/USD instruments, rejects date ranges outside the windows CSV, rejects live/stream subscriptions, and rejects any method capable of orders/account changes.
  - Run in a restricted environment with no access to the authoritative Windows repo and no broader filesystem writes.
- Revocation/deletion:
  - Human changes/deletes the demo credentials or closes the demo account after the bounded test.
  - Remove local secret material from the approved store/environment.
  - Verify no credential appears in chat, logs, reports, history, or output files.

This design is not approved or implemented by this report.

## Independent critic findings

Criticism: The public FXCM tick repository may imply tick-level adequacy, but it does not list XAU/USD or 2024.

Response: Material. The conclusion is blocked pending FXCM capability clarification/authenticated demo test.

Criticism: Historical ticks might not contain synchronized BID/ASK; they could be one-sided updates, indicative fields, or filtered records.

Response: Material. The exact record schema is required before primary tick corroboration can be claimed.

Criticism: Public tick data is explicitly indicative and based on lowest Active Trader spreads, not necessarily demo or retail account pricing.

Response: Material. Even if data existed for XAU/USD, it would need careful labelling and might not be equivalent to account-specific executable pricing.

Criticism: Different providers can legitimately disagree during stress because venue liquidity, rollovers, metals CFD handling, and session treatment differ.

Response: Material. Agreement would be independent support, not market truth; disagreement would not automatically invalidate Dukascopy.

Criticism: Timestamp alignment and precision remain unresolved.

Response: Partly mitigated for public tick files by the UTC timestamp note, but precision and exact schema remain unresolved.

Criticism: FXCM API families include trading/order functionality, so a demo credential is still a broker-access boundary.

Response: Material. Any future test must enforce a read-only historical-data wrapper and require explicit human approval.

Criticism: The planned comparison could become false confirmation if a broad FXCM history result is treated as exact tick corroboration.

Response: Material. The conclusion blocks primary-quality claims until synchronized BID/ASK tick fields are documented and a comparison rule is pre-registered.

Independent critic materially changed conclusion: yes. Initial feasibility looked more promising than OANDA because FXCM publicly documents tick data, but the critic reduced the conclusion to blocked/uncertain because the public tick docs do not cover XAU/USD, 2024, or BID/ASK schema.

## Limitations

- FXCodeBase/FXCM web documentation was partially inaccessible through non-browser curl due to browser challenge.
- No FXCM account was created or accessed.
- No credentials were generated, requested, used, stored, or exposed.
- No ForexConnect/JavaAPI package was installed.
- No external market data was acquired.
- No public tick CSV was downloaded, so tick columns were not inspected.
- Authenticated ForexConnect installed-package examples were not inspected.
- 2024 XAU/USD historical tick retention, fields, paging limits, and demo access remain unresolved.

## Exact next approval required

Before any FXCM acquisition or account work, the human must approve one of these narrow next steps:

1. Documentation clarification only: contact FXCM/API support or access first-party docs to answer whether demo ForexConnect can retrieve 2024 XAU/USD historical ticks with synchronized BID/ASK fields, retention depth, limits, and schema.

2. Bounded authenticated demo test: create/use a dedicated FXCM demo account, handle credentials locally, optionally install ForexConnect only after separate package/source approval, and run read-only historical-market-data checks limited to XAU/USD and the already-defined target/control windows. Stop before acquisition unless the test plan explicitly authorizes fetching those windows.

No current approval permits account creation, credentials, package installation, or market-data acquisition.

## Gate result

BLOCKED_PENDING_FXCM_CAPABILITY_CLARIFICATION

Rationale: FXCM has documented historical price tooling and public tick files, and XAU/USD historical bars are documented, but accessible first-party documentation does not establish the required 2024 XAU/USD synchronized historical BID/ASK tick capability through a demo/practice account.

## Validation

- Durable report exists at `reports/fxcm_historical_tick_bid_ask_feasibility.md`.
- Capability claims are traceable to the first-party FXCM/ForexConnect/FXCodeBase sources listed above.
- No account, credentials, package installation, endpoint access, external market-data acquisition, trading, order simulation, raw evidence modification, methodology change, schema change, quality-rule change, session-definition change, policy change, or Windows repo access occurred.
