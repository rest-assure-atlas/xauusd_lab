# FXCM Historical Retrieval Technical Validation

Date: 2026-08-10
Status: bounded technical validation complete
Gate result: FXCM_RETRIEVAL_FIX_NEEDS_SMALL_FOLLOWUP

## Scope

This validation inspected the FXCM Java request/response implementation used in the tiny two-window pilot and tested only very small XAU/USD historical tick slices inside the already-approved windows:

- Extreme window: `2024-01-25T22:52:00Z` to `2024-01-25T23:59:00Z`
- Control window: `2024-03-15T11:30:00Z` to `2024-03-15T12:30:00Z`

No additional corroboration campaign windows were acquired. No Dukascopy raw evidence, methodology, schemas, research policy, modelling code, or trading/order functionality was touched.

## Implementation Inspection

The tiny pilot Java runners had a local asynchronous-response handling flaw:

- `FxcmTwoWindowPilot.java` counted a request as finished immediately when `MarketDataRequestReject` arrived.
- `FxcmTwoWindowPilotChunked.java` did the same per chunk, then wrote the per-chunk summary and set `activeChunk = null`.
- FXCM JavaAPI can still deliver matching `MarketDataSnapshot` records after the `Unsupported Scope (A)` reject event.
- Late records after `activeChunk = null` caused handler `NullPointerException` messages and count inconsistencies between stdout, request summaries, and tick CSVs.

This explains why the two-window pilot had usable ticks but inconsistent counts and non-reproducible full-window artifacts.

## Validation Runner

Added a narrow validation runner:

- `.fxcm_compat_runtime/FxcmRetrievalValidation.java`

It keeps one synchronized active request state, filters messages by request ID, records whether snapshots arrive before or after reject, and waits for a quiet period after the reject before closing a request.

Validation artifacts:

- `external_corroboration/fxcm_retrieval_validation/fxcm_retrieval_validation_summary.csv`
- `external_corroboration/fxcm_retrieval_validation/fxcm_retrieval_validation_ticks.csv`
- `external_corroboration/fxcm_retrieval_validation/run_stdout.log`
- `external_corroboration/fxcm_retrieval_validation/run_stderr.log`

## Request Results

| request | requested UTC | records | first returned | last returned | reject seen | records after reject | repeat status |
|---|---|---:|---|---|---|---:|---|
| extreme_1m_a | 2024-01-25 23:22:00 to 23:23:00 | 93 | 23:22:03.201 | 23:22:54.117 | yes | 93 | identical to b/c |
| extreme_1m_b | 2024-01-25 23:22:00 to 23:23:00 | 93 | 23:22:03.201 | 23:22:54.117 | yes | 93 | identical to a/c |
| extreme_1m_c | 2024-01-25 23:22:00 to 23:23:00 | 93 | 23:22:03.201 | 23:22:54.117 | yes | 93 | identical to a/b |
| extreme_30s | 2024-01-25 23:22:00 to 23:22:30 | 91 | 23:22:03.201 | 23:22:10.118 | yes | 91 | boundary shape |
| extreme_next_1m | 2024-01-25 23:23:00 to 23:24:00 | 5 | 23:23:20.059 | 23:23:36.058 | yes | 0 | adjacent slice |
| control_1m_a | 2024-03-15 12:29:00 to 12:30:00 | 380 | 12:29:00.009 | 12:29:59.813 | yes | 380 | identical to b/c |
| control_1m_b | 2024-03-15 12:29:00 to 12:30:00 | 380 | 12:29:00.009 | 12:29:59.813 | yes | 380 | identical to a/c |
| control_1m_c | 2024-03-15 12:29:00 to 12:30:00 | 380 | 12:29:00.009 | 12:29:59.813 | yes | 380 | identical to a/b |
| control_mid_1m | 2024-03-15 12:00:00 to 12:01:00 | 365 | 12:00:00.224 | 12:00:59.869 | yes | 365 | single control slice |

All written validation rows had synchronized BID/ASK in the same record, no duplicate timestamps, no missing BID/ASK values, no negative spreads, no zero spreads, and ordered timestamps.

## Unsupported Scope Explanation

For these tiny requests, `Unsupported Scope (A)` / `no data found for instrument=XAU/USD` is not evidence that no records exist. It appeared on every tested request, including requests that returned hundreds of valid tick records.

Observed behavior supports this interpretation:

- The reject is a terminal/no-more-data marker or end-of-history signal in this JavaAPI response flow.
- It can arrive before the matching snapshots are delivered to the generic listener.
- Closing a request immediately on the reject loses late records and creates count inconsistency.
- Waiting for a quiet period after the reject produced stable, exactly reproducible one-minute requests.

This explains the tiny pilot's local runner failures. It does not prove that all larger windows can be retrieved in one request.

## Completeness Rule

For FXCM Java historical tick retrieval, completeness should not mean “some ticks were returned.”

For a tiny request, treat the request as operationally complete only if all of the following hold:

- request ID is known and all accepted messages match that request ID;
- a terminal reject/end marker is seen;
- the collector waits for a fixed quiet period after the last matching message;
- no timeout occurs;
- timestamps are ordered;
- there are no duplicate timestamps;
- BID and ASK are present in every row;
- no negative spreads are present;
- exact repeat requests produce identical timestamp/BID/ASK/order sequences;
- returned timestamps fall inside the requested UTC interval, allowing that no market tick may exist exactly at the boundary.

Under this rule, the repeated one-minute extreme and control slices were complete and reproducible. The previous two-window full acquisition is not complete under this rule.

## Remaining Limitations

The Java runtime still logs FXCM `Connection refused` messages during background communication/logout. The validation runner produced clean request outputs despite these messages, but they remain an operational caveat.

This mission did not validate long windows, all campaign rows, pagination over many chunks, recovery from network interruptions, or persistence/resume behavior. It also did not convert the pilot campaign runner into a production-quality acquisition tool.

## Conclusion

Root cause identified: yes. The main observed problem was local asynchronous response handling, especially treating the FXCM `Unsupported Scope` reject as an immediate hard failure and closing request state before late snapshots arrived.

Tiny request reproducibility: passed for the tested one-minute extreme and control slices.

FXCM is not yet ready for broader corroboration campaign acquisition. The next defensible step is a small follow-up that replaces the pilot acquisition runner with the validated synchronized/quiet-period request handling and reruns only the same two-window pilot or another tiny fixed-runner smoke test before any expansion.

Gate result: `FXCM_RETRIEVAL_FIX_NEEDS_SMALL_FOLLOWUP`.
