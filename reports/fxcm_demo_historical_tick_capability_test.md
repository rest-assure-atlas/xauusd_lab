# FXCM Demo Historical Tick Capability Test

Date: 2026-08-10
Status: bounded capability test stopped before authenticated market-data access
Gate result: BLOCKED_PENDING_FXCM_RUNTIME_CAPABILITY

## Mission Scope

This artifact records the bounded FXCM demo capability test approved for historical XAU/USD tick BID/ASK feasibility only.

Allowed scope was limited to the experimental Lab environment, local safe credential handling, minimum official FXCM/ForexConnect dependency installation if strictly required, read-only historical market-data capability checks, XAU/USD availability inspection, 2024 historical tick availability inspection, returned tick schema inspection, and the smallest possible sample needed to establish whether synchronized BID and ASK are available.

No live/funded account, deposit, order placement, order modification, order cancellation, simulated order, trading/position-management endpoint, account setting change, full target/control acquisition campaign, raw BID/ASK evidence modification, methodology/schema/quality/session/policy modification, authoritative Windows repo access, or out-of-Lab work was performed.

## Existing Lab Requirement

The existing pre-modelling spread evidence policy and targeted corroboration report require independent BID/ASK source evidence before warning-review active spread clusters can enter baseline execution-cost modelling.

The target population remains 84 active `warning_review_pair` rows with spread >= 2.0 across:

- 2024-01-25
- 2024-02-18
- 2024-05-01
- 2024-05-15
- 2024-07-11
- 2024-09-11
- 2024-10-10
- 2024-12-11
- 2024-12-12

The required future corroboration source must provide independent BID and ASK evidence, preferably synchronized point-in-time historical tick records, for the already-defined target/control windows in `reports/targeted_external_bid_ask_corroboration_windows_2024.csv`.

## Secret Handling

Credentials were staged by the human in `/dev/shm/openclaw-secrets/fxcm_demo.json`.

The staged secret file was verified without printing secret values:

- File present: yes
- Mode: `600`
- Non-empty username field: yes
- Non-empty password field: yes
- Connection field: `demo`
- URL field: `www.fxcorporate.com/Hosts.jsp`

The secret values were not written to this report, command output summaries, Lab artifacts, screenshots, or Telegram.

## FXCM Interface/Tool Used

No authenticated FXCM interface was successfully used.

The intended minimum official interface was FXCM's `forexconnect` Python package from PyPI, referenced by the official `fxcm/ForexConnectAPI` README as the current Python package location:

- `https://pypi.org/project/forexconnect/`
- `https://github.com/fxcm/ForexConnectAPI`

Official dependency installation was attempted inside the Lab only, but did not complete because the local runtime lacks the required Python packaging support and ABI compatibility:

- `python3 -m venv` failed because `ensurepip` is unavailable in the system Python image.
- `python3 -m pip` is unavailable.
- PyPI metadata for `forexconnect` version `1.6.43` shows Linux wheels for CPython 3.5, 3.6, and 3.7, plus macOS ARM CPython 3.10; no compatible Linux CPython 3.12 wheel was available for the current Lab runtime.
- No system package manager install, Python downgrade, alternative runtime install, Java runtime install, or non-FXCM dependency expansion was performed because that would exceed the narrow approved dependency boundary.

## Authentication Result

Authentication was not completed.

Reason: the official FXCM/ForexConnect client runtime could not be installed or run within the approved local dependency boundary.

No credentialed FXCM login request was made.

## XAU/USD Availability

XAU/USD remains documented by the earlier first-party feasibility report for historical bar resolutions, not proven for demo-accessible historical ticks:

- `XAU/USD` m1 from `2009-02-24T16:00:00Z`
- `XAU/USD` H1 from `2009-02-24T16:00:00Z`
- `XAU/USD` D1 from `1920-01-29T17:00:00Z`

This capability test did not authenticate to inspect account-specific instrument availability.

## Test Date/Window

No market-data sample window was retrieved.

The intended smallest initial target window would have been one already-defined target/control window from `reports/targeted_external_bid_ask_corroboration_windows_2024.csv`, stopping as soon as schema and synchronized BID/ASK capability were established or disproven.

## Historical Tick Availability

2024 XAU/USD historical tick availability was not established.

No authenticated historical request was made, and no external market-data file was downloaded.

Small HTTP availability probes against the public FXCM tick-data URL pattern did not establish XAU/USD tick availability because the probed XAU-style paths returned `text/html` responses rather than a confirmed tick CSV/gzip object. These probes did not retrieve market-data content.

## Returned Field/Schema Summary

No returned tick schema was observed.

Therefore the following remain unverified:

- whether records contain BID and ASK in the same row;
- whether BID and ASK are synchronized at a single timestamp;
- timestamp precision;
- whether records are raw ticks, sampled ticks, indicative ticks, or transformed aggregates;
- whether records are demo-account-specific, Active Trader indicative, or production/live-derived.

## Synchronized BID/ASK

Synchronized BID/ASK in the same historical tick record was not established.

## Timestamp Characteristics

No authenticated returned timestamps were observed.

The earlier first-party FXCM public tick-data documentation says public tick timestamps are UTC, but this capability test did not confirm timestamp precision or timezone behavior for demo-accessible XAU/USD historical ticks.

## Demo-Account Limitations

The main limitation is runtime/access, not a negative FXCM data finding:

- Demo credentials were staged locally, but were not used for authentication.
- Account-specific XAU/USD availability was not inspected.
- Account-specific historical tick depth was not inspected.
- Returned schema was not inspected.
- Demo versus live/production pricing differences remain unresolved.

## Adequacy Classification

Classification: BLOCKED_RUNTIME_NOT_A_CAPABILITY_PROOF.

The FXCM demo path is not yet justified for full target-window acquisition because this test did not authenticate and did not prove 2024 XAU/USD synchronized BID/ASK historical ticks.

This is not evidence that FXCM lacks the required data. It is evidence that the current Lab runtime cannot perform the official ForexConnect demo capability check within the approved narrow dependency boundary.

## Full Corroboration Justification

Full target-window acquisition is not justified yet.

A future bounded test may be justified only after the human explicitly approves one of:

- a compatible official ForexConnect runtime path inside the Lab, such as an approved CPython version/runtime compatible with FXCM's Linux wheel;
- an approved Java/FIX API runtime if JavaAPI is chosen instead;
- direct first-party FXCM/API support clarification proving demo-accessible 2024 XAU/USD synchronized BID/ASK historical ticks and the exact supported client/runtime.

Any future run must still prohibit live/funded accounts, deposits, orders, trading endpoints, account changes, and full target/control acquisition until a separate approval is granted.

## Exact Next Approval Required

Explicit human approval is required for a narrowly bounded runtime/dependency expansion to make the official FXCM client usable inside the Lab, followed only by:

1. demo login/authentication;
2. account-specific XAU/USD availability check;
3. historical tick granularity/depth check for 2024;
4. smallest possible XAU/USD historical sample from an existing target/control window;
5. schema inspection for synchronized BID and ASK;
6. immediate stop and secret cleanup.

No full target-window acquisition should proceed without a later explicit approval.
