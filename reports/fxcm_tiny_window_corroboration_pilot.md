# FXCM Tiny-Window Corroboration Pilot

Date: 2026-08-10
Status: bounded two-window pilot complete; corrected retrieval rerun and hardening analysis complete
Latest gate result: PILOT_SUPPORTIVE_BUT_MORE_TECHNICAL_VALIDATION_REQUIRED
Original flawed-run gate result: PILOT_INCONCLUSIVE

## Scope

This pilot used the already-validated isolated FXCM Java compatibility runtime for read-only FXCM demo historical XAU/USD tick requests. It acquired only two predefined windows plus one exact repeat of the extreme window:

- Extreme target: `warning_ge2_target`, `2024-01-25_ge2_01`, `2024-01-25T22:52:00Z` to `2024-01-25T23:59:00Z`
- Normal control: `control_strict_normal`, `2024-03-15_strict_control_1200`, `2024-03-15T11:30:00Z` to `2024-03-15T12:30:00Z`

No raw Dukascopy BID/ASK evidence, Lab methodology, schemas, quality rules, session definitions, evidence policy, modelling policy, or authoritative Windows repository files were modified. No live/funded account, trading action, order simulation, account setting change, or broader campaign acquisition was performed.

## Artifacts

FXCM pilot data is stored separately from Dukascopy raw evidence:

- `external_corroboration/fxcm_tiny_window_pilot_chunked/extreme_chunked_fxcm_xauusd_ticks.csv`
- `external_corroboration/fxcm_tiny_window_pilot_chunked/control_chunked_fxcm_xauusd_ticks.csv`
- `external_corroboration/fxcm_tiny_window_pilot_chunked/extreme_repeat_chunked_fxcm_xauusd_ticks.csv`
- `external_corroboration/fxcm_tiny_window_pilot_chunked/*_chunked_request_summary.csv`
- `reports/fxcm_tiny_window_pilot_comparison.csv`

The initial full-window request attempt is retained under `external_corroboration/fxcm_tiny_window_pilot/` because it is material evidence for request behavior.

## Acquisition Results

Single full-window requests for the approved windows did not return complete windows. They returned FXCM `MarketDataRequestReject` messages with `Unsupported Scope (A)` and `no data found for instrument=XAU/USD`; the first full extreme request returned zero records.

Because the earlier validated capability test was a one-minute request, the pilot then stayed inside the same two approved windows and used minute-sized historical requests. This produced usable synchronized BID/ASK tick records, but did not establish complete or reproducible retrieval.

| window | requested UTC | FXCM ticks | first returned | last returned | minutes with ticks / requested | max FXCM spread | median FXCM spread |
|---|---|---:|---|---|---:|---:|---:|
| extreme | 2024-01-25 22:52 to 23:59 | 437 | 2024-01-25 23:03:04.503 | 2024-01-25 23:58:58.184 | 28 / 67 | 2.500000 | 0.380000 |
| control | 2024-03-15 11:30 to 12:30 | 3228 | 2024-03-15 11:31:00.006 | 2024-03-15 12:29:04.659 | 29 / 60 | 0.360000 | 0.310000 |
| extreme repeat | 2024-01-25 22:52 to 23:59 | 592 | 2024-01-25 23:03:04.503 | 2024-01-25 23:57:58.175 | 27 / 67 | 2.500000 | 0.650000 |

Data-quality checks on the written FXCM CSV rows:

- BID/ASK synchronized in the same tick record: yes
- Timestamp precision: millisecond-level
- Duplicate timestamps: none observed
- BID/ASK missingness: none observed in written rows
- Negative spreads: none observed
- Zero spreads: none observed
- Timestamp ordering: non-decreasing in each written CSV

## Unsupported Scope Behavior

The `Unsupported Scope (A)` / `no data found` reject is not simply harmless end-of-request behavior for this pilot. It appeared after valid records for many minute requests, but full-window requests returned no complete data, and the minute-chunked output had material gaps and non-reproducible tick populations. The best current interpretation is unresolved FXCM JavaAPI history behavior: likely a combination of request-size limitation, history-boundary/no-data signaling, and asynchronous response handling. It cannot be treated as proof of completeness.

Completeness cannot be established from this pilot.

## Reproducibility

The exact extreme-window acquisition was repeated once. It was not reproducible:

- First extreme acquisition: 437 written ticks
- Repeat extreme acquisition: 592 written ticks
- Exact normalized tick sequence match: no
- Common normalized timestamp/BID/ASK/flag rows: 14
- Exact cluster `2024-01-25T23:22:00Z` to `2024-01-25T23:29:59Z`: both runs reached maximum FXCM spread 2.500000 at `2024-01-25T23:23:20.065Z`, but the tick populations differed.

This supports the qualitative stress signal, but fails the reproducibility requirement for complete retrieval.

## Dukascopy Comparison

| window | FXCM max spread | FXCM max time | FXCM median | Dukascopy max spread | Dukascopy max time | Dukascopy median | comparison |
|---|---:|---|---:|---:|---|---:|---|
| extreme | 2.500000 | 2024-01-25 23:23:20.065 | 0.380000 | 2.490000 | 2024-01-25 23:22:00 | 0.600000 | CONFIRMED_DIRECTIONALLY |
| control | 0.360000 | 2024-03-15 12:29:03.839 | 0.310000 | 0.440000 | 2024-03-15 12:29:00 | 0.320000 | CONFIRMED_CLOSELY |

Interpretation:

- Extreme window: FXCM independently shows a stressed spread regime in the same predefined warning-review window. The local maximum occurs about 80 seconds after the Dukascopy maximum. Because FXCM retrieval is incomplete and non-reproducible, the exact Dukascopy `>=2.0` spike is supported directionally, not conclusively confirmed.
- Control window: FXCM and Dukascopy both show ordinary tight spreads. This is closely consistent, subject to the same incomplete FXCM retrieval caveat.

Different providers are not expected to have identical quotes, and this pilot does not treat provider price differences as evidence that Dukascopy ticks are invalid.

## Critic Findings

Independent bounded critic review reinforced the conservative gate. Material findings:

- Two rows of comparison are feasibility evidence, not campaign evidence; they cannot establish behavior across dates, sessions, target types, or the 84-row warning population.
- Timestamp alignment is approximate in the extreme case: FXCM maximum spread at `2024-01-25T23:23:20.065Z` versus Dukascopy maximum at `23:22:00Z`, an `80.065` second offset.
- Retrieval is incomplete and operationally noisy: minute coverage was `41.79%` for the extreme window and `48.33%` for the control, and every chunk summary recorded `reject_seen=true`, including chunks with returned records.
- The Java runner logs include handler `NullPointerException` messages and FXCM `Connection refused` messages. Files were produced and logout completed, but this weakens confidence in completeness and runner determinism.
- Count reconciliation is not clean: tick CSV row counts are `437 / 3228 / 592` for extreme/control/repeat, while request-summary record sums are `186 / 2247 / 157`. This is consistent with asynchronous late-arriving records after per-chunk summaries were written and must be fixed before any broader acquisition.
- FXCM demo account/session pricing, account-specific symbol visibility, historical retention, and provider-specific liquidity conventions remain material caveats.
- The extreme result could reflect broad same-window volatility rather than direct confirmation of the exact Dukascopy spike.
- The single strict-normal control is not enough for comparability across session/event/microstructure conditions.

Material effect on conclusion: the criticism does not change the gate to a stronger negative result, but it clearly blocks campaign expansion. A tighter technical-validation mini-pilot would be required before any broader FXCM corroboration campaign.

## Conclusion

The pilot is scientifically useful as a warning signal: FXCM demo historical ticks can contain synchronized BID/ASK records, and the two selected windows qualitatively align with Dukascopy stressed vs normal regimes. However, the historical retrieval behavior did not satisfy the approved completeness and reproducibility standard.

Gate result: `PILOT_INCONCLUSIVE`.

Exact next approval required: approve a separate bounded FXCM technical-validation mission focused only on making historical retrieval complete and reproducible, or stop FXCM corroboration work. Do not proceed into the remaining target windows without explicit human approval.

## Credential Cleanup

The FXCM Java run logged out cleanly. No `/dev/shm/openclaw-secrets/fxcm_demo.json` file remained after the run. The persistent demo credential file was intentionally retained at `/home/openclaw/.config/openclaw-secrets/fxcm_demo.json` under the separately approved persistent-secret setup. Credential values were not printed or found in reports/artifacts under Lab control.

## Corrected Retrieval Rerun

After the technical validation in `reports/fxcm_historical_retrieval_technical_validation.md`, the two-window pilot was rerun with corrected asynchronous request handling:

- synchronized per-request state;
- request-ID filtering;
- capture of records that arrive after the FXCM `Unsupported Scope (A)` terminal marker;
- fixed quiet-period wait after the last matching message;
- no request/chunk state closure until the quiet period expires.

Runner:

- `.fxcm_compat_runtime/FxcmTwoWindowPilotCorrected.java`

Artifacts:

- `external_corroboration/fxcm_tiny_window_pilot_corrected/`
- `reports/fxcm_corrected_tiny_window_pilot_comparison.csv`

Corrected run results:

| window | requested UTC | chunks | ticks | first returned | last returned | timeouts | chunks without reject | duplicate timestamps | repeat exact |
|---|---|---:|---:|---|---|---:|---:|---:|---|
| extreme | 2024-01-25 22:52 to 23:59 | 67 | 3544 | 2024-01-25 23:01:00.053 | 2024-01-25 23:58:58.184 | 0 | 0 | 0 | yes |
| control | 2024-03-15 11:30 to 12:30 | 60 | 18256 | 2024-03-15 11:30:00.021 | 2024-03-15 12:29:59.813 | 0 | 0 | 1 | yes |

All chunks received terminal `Unsupported Scope (A)` markers and completed without timeout. Exact repeat files matched normalized timestamp/BID/ASK/order sequences:

- extreme: SHA `7464fab95d130d3ce635cd4734e8173e84fc4341e310e3cae37de44f892dafb5`
- control: SHA `977849a76477006d79e859ace5a8d962acb5a47930bc74561d65f5879b9944f8`

Corrected FXCM spread comparison:

| window | FXCM max spread | FXCM max time | FXCM median | Dukascopy max spread | Dukascopy max time | Dukascopy median | comparison |
|---|---:|---|---:|---:|---|---:|---|
| extreme | 2.500000 | 2024-01-25 23:23:20.065 | 0.810000 | 2.490000 | 2024-01-25 23:22:00 | 0.600000 | CONFIRMED_DIRECTIONALLY |
| control | 0.700000 | 2024-03-15 12:03:44.258 | 0.310000 | 0.440000 | 2024-03-15 12:29:00 | 0.320000 | CONFIRMED_DIRECTIONALLY |

Interpretation:

- The corrected retrieval implementation makes the two approved windows technically complete and reproducible under the quiet-period/request-ID rule.
- The extreme window independently supports a stressed spread regime near the Dukascopy warning cluster, with FXCM maximum about 80 seconds after the Dukascopy maximum.
- The control window independently supports a normal/tight typical-spread regime, but its local maximum does not closely align in timing or magnitude, so it is directionally consistent rather than closely confirmed.
- The corrected pilot materially changes the technical retrieval gate, but it does not by itself establish campaign-level evidence across all predefined target/control windows.

Independent critic result: `PILOT_SUPPORTIVE_BUT_MORE_TECHNICAL_VALIDATION_REQUIRED`.

## Corrected Pilot Hardening Analysis

Hardening artifact:

- `reports/fxcm_corrected_pilot_hardening_analysis.json`

The critic found that the corrected two-window pilot is substantially stronger than the original flawed run, but not yet enough to justify full campaign expansion.

Hardening findings:

- Exact normalized repeat equality was confirmed for both corrected pilot windows.
- The control duplicate timestamp was isolated to `20240315-12:06:00.000`, appearing once at the end of the `12:05` chunk and once at the start of the `12:06` chunk with identical BID/ASK but different FXCM continuous flags.
- Raw FXCM rows should be preserved unchanged. Assembled analysis should use a predeclared boundary de-duplication view keyed on timestamp+BID+ASK for completeness statistics, while retaining raw continuous-flag rows for audit.
- The extreme zero-record chunks were the same nine opening chunks in the first run and exact repeat: `22:52` through `23:01` UTC. They had terminal reject markers and no timeouts, so they are reproducible FXCM zero-record chunks, but still cannot independently prove absence of all possible market quotes.
- The corrected run still produced very noisy FXCM JavaAPI transport stderr: 5715 `Connection refused` lines and 1905 `CommunicationException` occurrences, despite clean output files and `LOGOUT=done`.
- The full predefined campaign would require about 5647 one-minute chunks, with the three p99 control windows alone requiring 1496, 1492, and 1381 chunks. This scaling and recovery behavior was not validated by the two-window corrected pilot.

Conclusion after hardening:

- Corrected retrieval is technically promising and no longer blocked at the original pilot failure.
- Full predefined campaign acquisition is not yet a GREEN autonomous step.
- The next scientifically defensible step is a small approved scaling/operational validation, not the full 22-window campaign.

Latest gate result: `PILOT_SUPPORTIVE_BUT_MORE_TECHNICAL_VALIDATION_REQUIRED`.

Exact next approval required: approve a bounded FXCM scaling/operational validation that tests corrected runner behavior on a small predeclared subset of longer already-defined windows, explicitly defines raw-vs-assembled boundary de-duplication, and sets log/noise/recovery acceptance criteria before the full campaign.
