# FXCM Compatibility Runtime and Demo Tick Test

Date: 2026-08-10
Status: bounded compatibility/runtime and tiny authenticated demo capability test complete
Gate result: FXCM_DEMO_TICK_CAPABILITY_CONFIRMED_FOR_TINY_SAMPLE

## Mission Scope

This report records the bounded FXCM compatibility-runtime mission and the previously approved minimal authenticated FXCM demo historical XAU/USD tick capability test.

The mission did not downgrade, replace, or alter the Lab's Python 3.12 environment. It did not modify Lab methodology, schemas, quality rules, source BID/ASK evidence, raw BID/ASK data, session definitions, or research policy. It did not use a live/funded FXCM account, deposit money, place orders, modify orders, cancel orders, simulate orders, access position-management workflows, acquire the full target/control campaign, or touch the authoritative Windows repo.

## Runtime Decision

Chosen runtime: isolated Java route.

Reasoning:

- The official FXCM `forexconnect` Python package is published at `https://pypi.org/project/forexconnect/`, but current Linux wheels for version `1.6.43` target CPython 3.5, 3.6, and 3.7 only. The Lab has Python 3.12 and no `pip`/`venv` support.
- Replacing or downgrading Lab Python would violate the mission boundary.
- FXCM's first-party JavaAPI documentation describes a Java API with an `MDH` command for market-data history and demo connection support.
- The Java route could be installed under an isolated Lab-local directory without touching the main Lab Python environment.

## Isolation Method

Runtime directory:

- `.fxcm_compat_runtime/`

Installed under that directory only:

- Temurin OpenJDK `17.0.20+8`
- FXCM Java `trading_sdk.zip`
- FXCM `fxcm-api.jar` with manifest `Implementation-Version: J6.00.1807.1311`
- FXCM `fxmsg.jar`
- Apache `commons-logging-1.3.5.jar`, required because FXCM `GatewayFactory.createGateway()` otherwise failed with `NoClassDefFoundError: org/apache/commons/logging/LogFactory`

The main Lab Python runtime remained unchanged.

The Java runtime smoke test successfully created `com.fxcm.internal.transport.FXCMGateway` and constructed a tick `MarketDataRequest`.

## Official Sources and Versions

FXCM first-party sources:

- `https://raw.githubusercontent.com/fxcm/JavaAPI/master/README.md`
- `https://apiwiki.fxcorporate.com/api/java/trading_sdk.zip`
- `https://apiwiki.fxcorporate.com/api/java/fxcm-api-7.3.3.zip` was checked as a current first-party JavaAPI package, but the authenticated smoke/test path used the fuller `trading_sdk.zip` package because it included the documented sample classes and local JavaAPI layout.
- `https://raw.githubusercontent.com/fxcm/ForexConnectAPI/master/README.md`
- `https://pypi.org/project/forexconnect/`

Runtime/dependency source:

- Temurin OpenJDK `17.0.20+8`, downloaded as an isolated Lab-local JDK tarball and checksum-verified.
- Apache `commons-logging-1.3.5`, downloaded as the minimum missing Java logging dependency needed to start the official FXCM Java gateway.

## Credential Handling

FXCM demo credentials were staged by the human in `/dev/shm/openclaw-secrets/fxcm_demo.json`.

The staged file was verified without printing secret values:

- file mode: `600`
- file size: 116 bytes
- username present: yes
- password present: yes

Credentials were read by the Java test from the tmpfs secret file, not passed as command-line arguments.

After the authenticated test, `/dev/shm/openclaw-secrets/fxcm_demo.json` was deleted.

## Authenticated Demo Test

Interface used:

- FXCM JavaAPI `IGateway` via `GatewayFactory.createGateway()`
- Demo connection
- Host URL: `http://www.fxcorporate.com/Hosts.jsp`
- Trading connection resolved by FXCM as `EUDEMO`

Test sequence:

1. Login to FXCM demo.
2. Request trading session status.
3. Enumerate account-visible securities.
4. Identify XAU/USD symbol.
5. Send one historical tick `MarketDataRequest` for a tiny pre-existing target-window slice:
   - `2024-01-25T23:22:00Z` to `2024-01-25T23:23:00Z`
   - instrument: `XAU/USD`
   - timing interval: `FXCMTimingInterval:Tick`
   - entry type set: `MDENTRYTYPESET_ALL`
   - response format: `FXCMRESPONSE`
6. Inspect returned schema and stop.
7. Logout.

No account, order, position, or trade-management request was intentionally sent.

## Results

Authentication: passed.

XAU/USD availability: yes. The authenticated demo session listed `XAU/USD`.

2024 historical tick availability: yes for the tiny tested slice. The historical tick request returned tick `MarketDataSnapshot` records for `XAU/USD` in the requested 2024 window.

Sample size: 93 tick snapshot records were observed from the one-minute request. Only schema and a five-record field summary were inspected; no full target/control campaign was acquired and no external raw market-data file was written.

Returned schema/fields observed on sampled records:

- instrument
- request ID
- open timestamp
- timestamp
- bid open
- bid high
- bid low
- bid close
- ask open
- ask high
- ask low
- ask close
- tick volume
- continuous flag

Synchronized BID/ASK: yes. Each sampled tick snapshot record contained BID and ASK values in the same record at the same timestamp.

Timestamp precision: millisecond-level timestamps were observed, for example in `YYYYMMDD-HH:MM:SS.mmm` form.

Logout: completed.

## Caveats

The one-minute historical request returned usable tick snapshots and also emitted an FXCM `MarketDataRequestReject` message with reason `Unsupported Scope (A)` and text `no data found for instrument=XAU/USD` after records had already been received. This appears to be an end/range or follow-on rejection condition from the FXCM JavaAPI response flow, not a failure to return the tiny historical sample. It should be investigated before any larger acquisition campaign.

The JavaAPI emitted `Connection refused` messages during request/logout cleanup while still completing the sample retrieval and logout. This should also be treated as an operational caveat for any future campaign runner.

This was a tiny capability proof, not corroboration. It does not compare against Dukascopy, does not validate all target/control windows, does not prove complete 2024 retention, and does not justify any modelling-policy change by itself.

The returned tick schema strongly improves feasibility relative to the earlier documentation-only state, but future use still needs bounded acquisition approval and campaign-level validation.

## Capability Classification

Classification: READY_FOR_BOUNDED_FXCM_TINY_WINDOW_CORROBORATION_CAMPAIGN_DESIGN.

Rationale:

- The isolated official Java route works.
- Demo authentication works.
- XAU/USD is visible in the demo session.
- A tiny 2024 historical tick request returned synchronized BID/ASK records with millisecond timestamps.
- The response caveats mean a campaign runner should be designed defensively and validated on a very small set before any full target/control acquisition.

## Full Corroboration Justification

Full target/control acquisition is not justified yet.

A next bounded approval is justified for a tiny-window campaign design or pilot that:

- uses the existing target/control windows only;
- begins with one or two small windows, not all 84 rows;
- records request/reject behavior clearly;
- persists only approved external sample data;
- preserves raw Lab evidence and methodology unchanged;
- keeps credentials in tmpfs or another approved secret mechanism;
- deletes or revokes credentials after use;
- stops before any modelling-policy change.

## Runtime Cleanup/Retention

Credentials were cleaned.

The isolated compatibility runtime remains installed under `.fxcm_compat_runtime/` because it is useful for an explicitly approved later pilot. It is isolated from the main Lab runtime and can be removed later by deleting that directory if no further FXCM work is approved.

Temporary download/probe files under `.fxcm_runtime_probe/` are not required for running the Java capability runtime and can also be removed later if disk cleanup is desired.

## Exact Next Approval Required

Explicit human approval is required for a bounded FXCM tiny-window corroboration pilot using the isolated Java runtime, demo credentials staged only in tmpfs, read-only historical XAU/USD tick requests only, and one or two already-defined target/control windows.

Do not acquire the full target/control campaign and do not change any modelling, policy, schema, quality rule, or raw evidence without a later approval.
