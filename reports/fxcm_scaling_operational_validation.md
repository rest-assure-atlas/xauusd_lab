# FXCM Scaling / Operational Validation

Date: 2026-08-10
Status: completed after recovery-only consolidation
Gate result: READY_FOR_FULL_BOUNDED_FXCM_CORROBORATION_CAMPAIGN

## Scope

This was a bounded technical and operational validation of the corrected FXCM Java historical tick retrieval system. It was not the full corroboration campaign. It did not authorize strategy research, modelling, policy changes, order/trading functionality, or modification of Dukascopy evidence.

The validation continued from the corrected asynchronous request handling established in `fxcm_historical_retrieval_technical_validation.md`: per-request state is synchronized, records are filtered by request id, `Unsupported Scope / no data found` is treated as a terminal/no-more-data marker for this JavaAPI historical flow, and request closure waits for a quiet period after the terminal marker so late `MarketDataSnapshot` records are captured.

## Predeclared Window Subset

Selected from `reports/targeted_external_bid_ask_corroboration_windows_2024.csv` before acquisition:

| role | kind | window_id | requested UTC | duration minutes | reason |
|---|---|---|---|---:|---|
| longer warning/extreme target | warning_ge2_target | 2024-12-11_ge2_03 | 2024-12-11 04:20:00 to 2024-12-11 07:06:00 | 166 | Longest predefined warning `>=2.0` target window; tests multi-hour stressed-window scaling and dense tick retrieval. |
| longer control-style window | warning_p99_major_control | 2024-05-22_warning_p99_broad | 2024-05-21 23:30:00 to 2024-05-22 22:31:00 | 1381 | Shortest of the three long p99 major-control windows; has `ge2_rows=0` and tests long-window orchestration, lower/control-style conditions, lower-density periods, and many chunk boundaries without acquiring all p99 controls. |

Exact repeat for reproducibility:

- `2024-12-11_ge2_03` was repeated once after the primary/resumed acquisition.

Recovery/resume test:

- `2024-12-11_ge2_03` was intentionally stopped locally after five new chunks, then resumed using existing chunk summaries to skip completed chunks.

## Boundary And De-Duplication Rule

Raw records received per chunk are preserved in the raw CSVs. Adjacent one-minute FXCM requests can return the same market tick at the shared boundary.

For assembled completeness/statistical views:

- exact duplicate definition: same timestamp, same BID close, same ASK close;
- de-duplication key: `timestamp + bid_close + ask_close`;
- continuous-flag differences alone do not create a separate market tick in the assembled view;
- non-identical same-timestamp BID/ASK rows are not dropped and must be reported separately.

Observed boundary behavior:

- `2024-12-11_ge2_03`: no exact duplicate rows and no non-identical same-timestamp BID/ASK rows.
- `2024-05-22_warning_p99_broad`: 6 exact duplicate rows, all at adjacent chunk boundaries, with identical timestamp/BID/ASK. No non-identical same-timestamp BID/ASK rows occurred.

Conclusion: FXCM one-minute historical request boundaries are effectively overlapping at least for some exact minute-boundary ticks. Raw data must preserve boundary duplicates; assembled data should de-duplicate only exact `(timestamp, BID, ASK)` duplicates and separately report any same-timestamp price conflicts.

## Zero-Record Rule

A zero-record chunk was not automatically classified as missing data. It was evaluated using terminal marker presence, timeout status, surrounding successful intervals, and repeat behavior where available.

Observed zero-record behavior:

- `2024-12-11_ge2_03`: 0 zero-record chunks in the primary/resumed run and 0 in the repeat.
- `2024-05-22_warning_p99_broad`: 64 zero-record chunks, all with terminal markers and no timeouts.
- The May 22 zero ranges were:
  - `2024-05-22 00:07:00` to `00:08:00`, one chunk; surrounding chunks had records.
  - `2024-05-22 21:00:00` to `22:01:00`, 61 chunks; surrounding chunks had records.
  - `2024-05-22 22:02:00` to `22:04:00`, two chunks; surrounding chunks had records.

Interpretation:

- Under the corrected request-completion rule, these zero chunks are technically complete requests: each reached a terminal marker, had no timeout, and did not show handler/request failure.
- The long 21:00-22:01 UTC gap is consistent with an FXCM XAU/USD session/liquidity lull or market-maintenance interval in demo historical data, but this validation did not independently prove the market/session cause.
- The zero-record meaning should therefore be preserved as `COMPLETE_ZERO_RECORD_CHUNK_WITH_SESSION_OR_NO_UPDATE_CAVEAT`, not silently treated as quote data.

## Acquisition Results

Machine-readable summary:

- `reports/fxcm_scaling_operational_validation_summary.json`

Raw FXCM pilot/scaling data:

- `external_corroboration/fxcm_scaling_operational_validation/`

| window | chunks | raw ticks | assembled before dedup | assembled after exact dedup | exact duplicate rows | first timestamp | last timestamp | zero chunks | timeouts | chunks without terminal marker | BID/ASK missing | negative spreads | zero spreads |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|
| 2024-12-11_ge2_03 primary/resumed | 166 | 58459 | 58459 | 58459 | 0 | 20241211-04:20:01.055 | 20241211-07:05:59.069 | 0 | 0 | 0 | 0 | 0 | 1 |
| 2024-12-11_ge2_03 repeat | 166 | 58459 | 58459 | 58459 | 0 | 20241211-04:20:01.055 | 20241211-07:05:59.069 | 0 | 0 | 0 | 0 | 0 | 1 |
| 2024-05-22_warning_p99_broad | 1381 | 435301 | 435301 | 435295 | 6 | 20240521-23:30:00.107 | 20240522-22:30:58.571 | 64 | 0 | 0 | 0 | 0 | 0 |

Records-after-terminal markers were expected under the JavaAPI asynchronous flow and were captured by the quiet-period logic:

- Dec 11 primary/resumed: 52850 records after terminal markers.
- Dec 11 repeat: 53098 records after terminal markers.
- May 22 long control-style window: recorded in the machine-readable summary.

## Reproducibility

The repeated longer target window was reproducible under normalized market-data comparison:

- primary/resumed count: 58459;
- repeat count: 58459;
- normalized `(timestamp, BID, ASK)` sequence: identical;
- first and last timestamps: identical;
- exact duplicate handling result: identical;
- ordering and BID/ASK presence: identical.

The repeat was not byte-identical because request IDs and run metadata differ. The normalized market-data sequence is the relevant reproducibility criterion.

## Recovery / Resume

The recovery test used a simulated local stop after five Dec 11 chunks.

Observed behavior:

- partial run completed 5 chunks and logged out cleanly;
- resume skipped the 5 completed chunks;
- resume acquired the remaining 161 chunks;
- final primary/resumed window had 166 chunks and 58459 raw ticks;
- the repeated Dec 11 acquisition matched the recovered primary window exactly under normalized market-data comparison.

Conclusion: checkpoint/resume behavior is adequate for this validation scope. It avoided repeating completed chunks unnecessarily and did not duplicate final assembled data.

## Log / Stderr Handling

The FXCM Java runtime still emits heavy transport noise on stderr:

| log | bytes | lines | `Connection refused` | `CommunicationException` |
|---|---:|---:|---:|---:|
| dec11 partial stderr | 43345 | 1069 | 120 | 40 |
| dec11 resume stderr | 1341049 | 33219 | 3690 | 1230 |
| dec11 repeat stderr | 1372259 | 33983 | 3777 | 1259 |
| may22 long-control stderr | 11488501 | 284331 | 31593 | 10531 |

Handling rule:

- stdout remains concise and contains only high-level completion facts;
- stderr is kept as a separate diagnostic log under the external-corroboration validation directory;
- reports and summaries count diagnostic categories instead of importing the full stderr text;
- request-level truth comes from chunk summaries: timeout, terminal marker, records, late records, ordering, missing BID/ASK, duplicate count, and spread sanity checks.

Acceptance result:

- The noise did not dominate model context during analysis because the report uses bounded counts and separate logs.
- It did not conceal request failures in this run: every selected chunk reached a terminal marker and no timeouts occurred.
- It remains an operational caveat for campaign-scale automation and should stay in diagnostic logs with bounded summaries.

## Gate Interpretation

The corrected retrieval system scaled from one-minute validation and two ~60-minute pilot windows to:

- a 166-minute warning target with exact reproducibility and successful resume;
- a 1381-minute long control-style window with 1381 one-minute chunks, zero timeouts, all terminal markers, explicit boundary de-duplication, and preserved zero-record intervals.

The technical result and recovered independent critic review support `READY_FOR_FULL_BOUNDED_FXCM_CORROBORATION_CAMPAIGN` with these constraints:

- full campaign acquisition must use the corrected runner semantics;
- raw chunk-level FXCM data must remain separate from Dukascopy evidence;
- exact duplicate boundary rows must be preserved raw and de-duplicated only in assembled/statistical views;
- zero-record chunks must remain explicit evidence with the caveat above;
- stderr must remain separated and summarized, not hidden.

## Critic Review

Recovered after the previous agent session abort. The independent critic reviewed the scaling report, summary JSON, checkpoint JSON, and bounded CSV/log artifacts under `external_corroboration/fxcm_scaling_operational_validation/` without modifying files or accessing credentials.

Recovered recommendation: `READY_FOR_FULL_BOUNDED_FXCM_CORROBORATION_CAMPAIGN`.

Material recovered findings:

- De-duplication/boundary semantics look valid. Raw rows are preserved; assembled logic removes only exact `(timestamp, BID, ASK)` duplicates. May 22 has 6 exact cross-boundary duplicates and 0 same-timestamp price conflicts; Dec 11 has none.
- Completeness claims are supportable only as request-level technical completeness, not proof that FXCM had every possible market update.
- Zero-record interpretation is appropriately cautious. May 22 has 64 zero chunks, all terminal/no-timeout, in three ranges. The long 21:00-22:01 gap is plausible as session/no-update behavior but not independently proven.
- Exact repeat reproducibility is strong for Dec 11: 58459 rows in both primary/resumed and repeat, with identical normalized sequence. The long May 22 control was not repeated, so reproducibility evidence does not cover the largest acquisition.
- Stderr filtering remains the main operational risk. Structured chunk evidence does not show concealed request failure in this run, but noisy stderr must remain separated with bounded summaries.
- Recovery/resume behavior is adequately demonstrated: partial stop after 5 chunks, resume skipped 5 and acquired 161, and final Dec 11 output matched the exact repeat.

Final gate: `READY_FOR_FULL_BOUNDED_FXCM_CORROBORATION_CAMPAIGN`.
