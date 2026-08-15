# OANDA Practice Historical BID/ASK Feasibility

Date: 2026-08-10
Status: feasibility and permission-design artifact only
Gate result: OANDA_ONLY_COARSE_CORROBORATION

## Mission scope

This report determines whether a dedicated OANDA fxTrade Practice account could defensibly provide independent historical XAUUSD BID/ASK evidence for the existing pre-modelling spread evidence policy and targeted external corroboration design.

This report does not create or access an OANDA account, generate or use an API token, acquire market data, access broker/trading endpoints, place or simulate orders, modify raw BID/ASK evidence, change methodology, change schemas, change session definitions, change quality rules, or change research policy.

The `/workspace/XAUUSD_Lab` path was not mounted in this execution environment. The active Lab copy visible here is `/home/openclaw/.openclaw/workspace/XAUUSD_Lab`; this artifact was written under that Lab copy only.

## Lab state read

Directly read:

- `reports/pre_modelling_spread_evidence_policy.md`
- `reports/targeted_external_bid_ask_corroboration_2024.md`
- `reports/targeted_external_bid_ask_corroboration_windows_2024.csv`

Confirmed target evidence requirement:

- Warning-review active clusters cannot enter baseline execution-cost modelling before targeted external/source corroboration and a later recorded modelling gate.
- The smallest defensible corroboration campaign covers all currently reviewed `warning_review_pair` active rows with spread >= 2.0 where practicable, or at minimum the full 2024-12-11 cluster plus every other date containing warning-review active spread >= 2.0, with controls.
- The external source must provide BID and ASK, not only mid/last price, and should allow comparison of timestamp alignment, BID, ASK, spread direction/magnitude, and whether widening appears around the same minute/hour/session window.
- Agreement may advance warning-review clusters to a modelling-policy gate; disagreement keeps affected warning rows out of baseline modelling; lack of matching coverage is inconclusive, not confirmation.
- External corroboration must not overwrite raw evidence or reclassify existing rows without a separate data-integrity artifact.

Confirmed target population and windows:

- Active `warning_review_pair` rows with spread >= 2.0: 84.
- Dates: 2024-01-25, 2024-02-18, 2024-05-01, 2024-05-15, 2024-07-11, 2024-09-11, 2024-10-10, 2024-12-11, 2024-12-12.
- Count by date: 2024-01-25=3, 2024-02-18=12, 2024-05-01=1, 2024-05-15=1, 2024-07-11=1, 2024-09-11=1, 2024-10-10=1, 2024-12-11=62, 2024-12-12=2.
- Existing design has 16 `warning_ge2_target` windows, 3 `warning_p99_major_control` windows, and 3 additional controls:
  - `warning_p99_major_control`: 2024-12-26, 2024-12-30, 2024-05-22.
  - `control_warning_non_extreme`: 2024-01-02.
  - `control_strict_normal`: 2024-03-15.
  - `control_strict_extreme`: 2024-04-05.

## First-party OANDA sources consulted

- OANDA, "Introduction", `https://developer.oanda.com/rest-live-v20/introduction/`
- OANDA, "Pricing", `https://developer.oanda.com/rest-live-v20/pricing-ep/`
- OANDA, "Instrument Definitions", `https://developer.oanda.com/rest-live-v20/instrument-df/`
- OANDA, "Primitive Definitions", `https://developer.oanda.com/rest-live-v20/primitives-df/`
- OANDA, "Account", `https://developer.oanda.com/rest-live-v20/account-ep/`
- OANDA, "OANDA Financial Instruments Specification", `https://www.oanda.com/eu-en/instruments-specification`
- OANDA, "Currency Pairs & Instruments | Major Forex Pairs | OANDA", `https://www.oanda.com/uk-en/trading/instruments/`

Only first-party OANDA pages were used for capability checks.

## OANDA capability findings

### XAU_USD availability

OANDA's public regional instrument pages document metals/commodities CFD availability and live instrument tables for the OANDA Europe/UK user-facing sites. The v20 API docs define `InstrumentName` as a base and quote currency delimited by an underscore and document that the account instruments endpoint returns tradeable instruments for a given account.

Feasibility conclusion: XAU_USD is plausibly available only after account/division confirmation. The first-party docs inspected do not provide a static unauthenticated v20 list proving that an Ireland-based practice account will expose `XAU_USD`. The minimum bounded practice test would need a read-only `GET /v3/accounts/{accountID}/instruments?instruments=XAU_USD` capability check before any candle request.

### Historical candlestick BID/ASK

The OANDA Pricing endpoint documents `GET /v3/accounts/{accountID}/instruments/{instrument}/candles` for fetching candlestick data for an instrument. The request requires:

- `Authorization` bearer token.
- `accountID` path parameter.
- `instrument` path parameter.
- Optional `price` query parameter for price components, default `M`.
- Optional `granularity`, default `S5`.
- Optional `count`, default 500 and maximum 5000.
- Optional `from` and `to` DateTime parameters.
- Optional `smooth`, default false.
- Optional `includeFirst`, default true.
- Optional `dailyAlignment`, `alignmentTimezone`, `weeklyAlignment`.
- Optional `units`, used to calculate volume-weighted average bid and ask prices in returned candles, default 1.

The Primitive Definitions page defines `PricingComponent` as any combination of `M`, `B`, and `A`, meaning midpoint, bid, and ask candles can be requested. The Instrument Definitions page defines `Candlestick` with separate `bid`, `ask`, and `mid` fields, each only provided if that candle type was requested. `CandlestickData` contains OHLC fields: open, high, low, and close. `Candlestick` includes start time, volume, and complete flag.

Feasibility conclusion: OANDA historical candlestick BID/ASK is documented and likely sufficient to check whether a broad same-window stress condition appears in OANDA, provided a practice account exposes XAU_USD and 2024 history for that account/division.

### Historical granularity and pagination

The Instrument Definitions page lists candlestick granularities:

- S5, S10, S15, S30.
- M1, M2, M4, M5, M10, M15, M30.
- H1, H2, H3, H4, H6, H8, H12.
- D, W, M.

The finest documented historical candle granularity is S5, aligned to the minute. The Pricing endpoint limits `count` to maximum 5000 candles per response. With S5 candles, 5000 candles cover about 6 hours 56 minutes 40 seconds. The existing target/control windows are much shorter than this except the broad p99 controls, which still fit within a small number of paginated S5 requests.

The Introduction page states that OANDA offers access to historical pricing information dating back to 2005. This supports likely 2024 historical availability in general, but it does not independently prove XAU_USD S5 BID/ASK availability for an Ireland-based practice account without an authenticated account-specific check.

### Timestamps

OANDA `DateTime` supports RFC3339 or UNIX representation. The docs state RFC3339 output uses a `YYYY-MM-DDTHH:MM:SS.nnnnnnnnnZ` format, and daily-aligned candle settings still return times represented in UTC. This is compatible with the existing UTC target/control-window design.

### Historical tick/quote data

The Pricing endpoint also documents:

- `GET /v3/accounts/{accountID}/pricing` for current pricing for a specified list of instruments in an account. It supports a `since` filter that returns prices and conversions later than that filter, but this is a current/polling endpoint, not a documented historical archive endpoint.
- `GET /v3/accounts/{accountID}/pricing/stream` for a live stream starting when the request is made. The docs explicitly state the stream does not include every single price, provides at most 4 prices per second per instrument, sends only the price in effect at the end of a 250 ms window if multiple prices occur, and connection window alignment can make different subscribers observe different prices during rapid movement.

No first-party v20 endpoint was found that provides true historical tick-level BID/ASK quote data for practice/API users. The documented historical path is candlesticks, not tick history.

### Account and authentication requirements

The Introduction page states that to use the v20 REST API a user must have a v20 trading account, available to all divisions except OANDA Global Markets and OANDA TMS BROKERS S.A. It directs users to try a free demo account or open a live account, then log into the Account Management Portal and generate a personal access token. It also states the same API can place/modify/close orders, manage account settings, and access account/trading history.

The relevant endpoints require an authorization bearer token and account ID:

- `GET /v3/accounts` requires an authorization bearer token and returns accounts authorized for the token.
- `GET /v3/accounts/{accountID}/instruments` requires an authorization bearer token and account ID.
- `GET /v3/accounts/{accountID}/instruments/{instrument}/candles` requires an authorization bearer token and account ID.
- Pricing and pricing stream endpoints also require token and account ID.

Feasibility conclusion: a practice/demo account and token are required to confirm account-specific XAU_USD availability and to request historical BID/ASK candles. This is a broker/API credential boundary even if only read-only endpoints are used.

### Regional/account caveats

First-party docs contain regional caveats material to an Ireland-based user:

- The Introduction page says v20 trading accounts are available to all divisions except OANDA Global Markets and OANDA TMS BROKERS S.A.
- The Account Instruments endpoint says the list of tradeable instruments depends on the regulatory division where the account is located.
- The OANDA Europe/UK public pages show retail CFD risk warnings and regional instrument availability pages, but they do not prove that an Ireland-based practice account exposes XAU_USD through the v20 REST endpoint.

Therefore, Ireland/EU account-division availability and XAU_USD instrument exposure remain account-specific checks.

### Sampling, aggregation, smoothing, completeness, and pricing-source caveats

Documented caveats:

- Candles are OHLC aggregations of prices over a time range, not tick-by-tick quotes.
- `smooth=false` is the default and must remain false for this mission; smoothed candles use the previous close as open and would weaken point-in-window interpretation.
- The `units` parameter affects volume-weighted average bid/ask prices in returned candles; any bounded test must set and record units explicitly.
- `complete` indicates whether a candle ending time is not in the future. For 2024 historical windows this should be complete, but validation should still require `complete=true`.
- The live pricing stream is sampled at most 4 prices per second and does not include every price; it is unsuitable as historical tick corroboration and should not be treated as equivalent.
- OANDA is an independent broker/feed relative to Dukascopy but has its own liquidity, account/division, pricing, and aggregation behavior.

## Distinction of data types

A. Historical candlestick BID/ASK:

- Documented through `GET /v3/accounts/{accountID}/instruments/{instrument}/candles`.
- Supports separate requested BID and ASK candle components.
- Finest documented granularity: S5.
- Provides OHLC per candle, volume, complete flag, and timestamp.
- Requires token and account ID.
- Potentially useful for coarse or directional corroboration of same-window spread stress.

B. Real-time pricing stream:

- Documented through `GET /v3/accounts/{accountID}/pricing/stream`.
- Starts from request time.
- Not a historical endpoint.
- Explicitly sampled and may omit intra-window prices.
- Not suitable for this mission's historical 2024 windows.

C. True historical tick/quote data:

- No first-party v20 practice/API endpoint found in the inspected docs.
- Not established as available for the required historical 2024 BID/ASK corroboration.

## Resolution adequacy test

Classification for this mission: B. ADEQUATE_ONLY_FOR_COARSE/DIRECTIONAL_CORROBORATION.

Rationale:

- OANDA S5 BID/ASK candles are finer than the Lab's minute-level target windows and can plausibly identify whether OANDA also observed spread widening in the same 5-second to minute/hour window.
- OANDA candle OHLC can show bid low/high, ask low/high, and close/open behavior across a candle. This is enough to test broad directional questions: did the OANDA source also show stress near the same UTC window; did ask and bid separate materially; did controls remain calmer?
- OANDA candle OHLC does not give a synchronized point-in-time bid and ask quote for each underlying tick. The maximum possible candle spread computed from ask high minus bid low could overstate the actual simultaneously executable spread; ask low minus bid high could understate or be nonsensical; close-to-close spread is only one boundary point and may miss intraperiod spikes.
- The existing Dukascopy evidence is minute-row BID/ASK close based. S5 OANDA candles are not a perfect provider-equivalent quote reconstruction unless a specific comparison rule is pre-registered and kept conservative.
- For single-minute targets, especially one-row spikes at 12:29 or 20:59, S5 candles materially improve over M1 but still may not prove that the exact Dukascopy minute-close spread spike occurred as a simultaneous OANDA quote spread.

Therefore OANDA practice historical candles could support coarse/directional independent corroboration, not primary point-in-time corroboration sufficient by itself to promote warning-review clusters into baseline cost modelling.

The classification would become `D. UNCERTAIN_PENDING_AUTHENTICATED_PRACTICE_TEST` only for account-specific availability questions: whether `XAU_USD` is exposed to the relevant practice account and whether 2024 S5 `BA` candles are retrievable. It would not remove the aggregation limitation.

## Minimum-permission design

If a human later approves an authenticated practice test, the smallest safe boundary should be:

- Account: a dedicated OANDA fxTrade Practice/demo account only; no deposit; no live account; no funded account.
- Human gate: explicit human approval before account creation, token generation, token entry, endpoint access, or data acquisition.
- Data scope: only historical market data for the already-defined target/control windows in `targeted_external_bid_ask_corroboration_windows_2024.csv`.
- Endpoint allowlist:
  - `GET /v3/accounts` only to identify the practice account ID authorized for the token.
  - `GET /v3/accounts/{accountID}/instruments?instruments=XAU_USD` only to verify XAU_USD availability.
  - `GET /v3/accounts/{accountID}/instruments/XAU_USD/candles` only with `price=BA`, `granularity=S5` or pre-approved fallback `M1`, `smooth=false`, explicit `from`, explicit `to`, explicit `units`, and target/control windows only.
- Endpoint blocklist: all order, trade, position, transaction mutation, account configuration, pricing stream, and live/current pricing endpoints. Do not call `POST`, `PUT`, `PATCH`, or `DELETE` at all.
- Request construction: use a small wrapper or documented manual command template that rejects non-GET methods, rejects paths outside the allowlist, rejects instruments other than XAU_USD, rejects date ranges outside the existing windows, and logs only sanitized request metadata.
- Token handling: token must never be sent in Telegram/chat, committed to files, written to reports, printed in shell history, or included in command logs. Prefer an approved local secret store or a one-shot environment variable entered directly by the human into a local terminal that does not echo. Store fetched data separately from raw Dukascopy evidence, under a new external-corroboration directory, and record token redaction checks.
- Procedural prevention: OpenClaw should run only the allowlisted wrapper and should not have general OANDA API authority. Any non-GET request, non-XAU_USD instrument, live pricing stream, or non-window date range should abort.
- Technical prevention where feasible: use a network wrapper that permits only `https://api-fxpractice.oanda.com/v3/accounts.../instruments.../candles` and account/instrument discovery paths, blocks `stream-fxpractice.oanda.com`, blocks order/trade/account-configuration paths, and denies HTTP methods other than GET.
- Validation: confirm `complete=true`, UTC timestamps, requested `BA` fields present, no smoothing, explicit units recorded, and exact windows only.
- Revocation/deletion: after the bounded test, the human revokes the personal access token in OANDA account management; locally remove the token from secret storage/environment; verify no token string appears in shell history, logs, reports, data files, or chat; preserve only sanitized request metadata and acquired historical candle data if approved.

This design is not approved or implemented by this report.

## Independent critic findings

Criticism: OANDA may not be independent enough because it is another retail broker, not an exchange-level consolidated feed.

Response: OANDA is independent from Dukascopy as a separate broker/feed, but not authoritative market truth. It can corroborate whether another venue saw similar stress; it cannot prove executable interbank spread or universal market conditions.

Criticism: Candle aggregation can hide or manufacture apparent spread extremes.

Response: Material. BID/ASK OHLC does not guarantee synchronized bid and ask observations. Conservative comparison rules must avoid treating ask high minus bid low as an executable spread. The conclusion is limited to coarse/directional corroboration.

Criticism: Timestamp alignment and timezone settings could create false matches or misses.

Response: Material. OANDA timestamps are UTC-capable and compatible with Lab windows, but the test must use RFC3339 UTC, explicit from/to windows, daily alignment defaults recorded, and no local-time conversions. S5 alignment should be documented before comparing to minute rows.

Criticism: Provider-specific liquidity can differ around market opens, holidays, rollover, and sparse sessions.

Response: Material. A disagreement would be inconclusive or adverse for baseline inclusion, not proof that Dukascopy is wrong. Agreement should be treated as independent stress evidence, not provider equivalence.

Criticism: Practice and production/live pricing may differ materially.

Response: Material uncertainty. The docs establish practice API access and endpoints, but not identical practice/live historical pricing behavior for XAU_USD. A practice result should be labelled practice-source corroboration unless OANDA documentation or support confirms parity.

Criticism: The planned comparison could become false confirmation if it only checks broad stress.

Response: Material. The report's adequacy classification is intentionally not primary. The next gate should pre-register exact comparison metrics and treat broad same-window stress as directional support only.

Independent critic materially changed conclusion: yes. The initial feasibility finding could have been framed as adequate for targeted corroboration because OANDA supports S5 BID/ASK candles. The critic reduces the conclusion to coarse/directional adequacy because candle OHLC cannot reconstruct synchronized historical tick spreads.

## Limitations

- No authenticated practice account test was performed.
- XAU_USD availability for an Ireland/EU practice account was not proven by an authenticated instrument list.
- No OANDA 2024 data was acquired.
- No first-party v20 historical tick BID/ASK endpoint was found.
- OANDA candle data would be external broker evidence, not authoritative market truth.
- S5 candle OHLC cannot by itself prove exact point-in-time executable spread equivalence to Dukascopy minute-close rows.
- OANDA regional/account division rules may affect instrument availability.
- The public docs state historical pricing back to 2005 generally, but do not independently prove every XAU_USD S5 BID/ASK window for 2024 without authenticated retrieval.

## Exact next approval required

To proceed beyond feasibility, the human must explicitly approve a bounded OANDA practice historical-data test with:

- creation or use of a dedicated OANDA fxTrade Practice/demo account only;
- generation and local secret handling of a personal access token;
- read-only GET access limited to account discovery, XAU_USD instrument availability, and historical XAU_USD BID/ASK candles for the existing target/control windows;
- no live/funded account, no deposit, no orders, no trading endpoints, no pricing stream, no account configuration changes, and no date ranges outside the already-defined windows;
- pre-registered comparison rules that distinguish directional candle corroboration from point-in-time spread confirmation.

## Gate result

OANDA_ONLY_COARSE_CORROBORATION

Rationale: OANDA practice historical S5 BID/ASK candles appear feasible as a bounded independent source for same-window directional stress checks if XAU_USD is available to the practice account, but documented OANDA v20 capabilities do not establish true historical tick-level BID/ASK or synchronized point-in-time spread reconstruction. This is not sufficient alone for primary baseline-modelling corroboration under the current evidence policy.

## Validation

- Durable report exists at `reports/oanda_practice_historical_bid_ask_feasibility.md`.
- All OANDA capability claims in this report are traceable to the first-party OANDA sources listed above.
- No OANDA account was created or accessed.
- No token was generated, requested, used, stored, or exposed.
- No external market data was acquired.
- No raw BID/ASK evidence, methodology, schema, session definition, quality rule, research policy, or Windows authoritative repo file was modified.
