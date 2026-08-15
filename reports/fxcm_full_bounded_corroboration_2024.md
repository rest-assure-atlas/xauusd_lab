# FXCM Full Bounded Corroboration 2024

Status: complete after independent critic review
Final gate: `CORROBORATION_PARTIALLY_SUPPORTIVE_MORE_REVIEW_REQUIRED`

## Scope

This bounded campaign acquired or reused validated FXCM DEMO historical XAU/USD BID/ASK ticks only for the predeclared target/control windows in `targeted_external_bid_ask_corroboration_windows_2024.csv`. It did not modify Dukascopy raw evidence, schemas, quality rules, session definitions, methodology, policy, execution-cost models, strategy logic, or account settings.

Completeness is request/chunk-level technical completeness only. It is not proof that FXCM exposed every possible market update. Terminal zero-record chunks are preserved as `COMPLETE_ZERO_RECORD_CHUNK_WITH_SESSION_OR_NO_UPDATE_CAVEAT`.

## Acquisition Summary

- Windows: 22 total, 16 warning targets, 6 controls.
- Request-level complete windows: 22.
- Technically inconclusive windows from retrieval failure: 0.
- FXCM chunks: 5647.
- FXCM raw tick rows: 1363767.
- Reused validated scaling artifacts: `2024-12-11_ge2_03`, `2024-05-22_warning_p99_broad`.

## Corroboration Summary

- `CONFIRMED_CLOSELY`: 13
- `CONFIRMED_DIRECTIONALLY`: 6
- `DISAGREES`: 1
- `INCONCLUSIVE`: 2

Warning >=2.0 windows:

- Closely supported: 2024-01-25_ge2_01, 2024-02-18_ge2_01, 2024-05-15_ge2_01, 2024-07-11_ge2_01, 2024-10-10_ge2_01, 2024-12-11_ge2_01, 2024-12-11_ge2_02, 2024-12-11_ge2_03, 2024-12-11_ge2_05, 2024-12-11_ge2_06, 2024-12-12_ge2_01
- Directionally supported: 2024-05-01_ge2_01, 2024-09-11_ge2_01, 2024-12-12_ge2_02
- Contradicted: 2024-12-11_ge2_04
- Unresolved: 2024-02-18_ge2_02

Aggregate interpretation before critic: **provider-specific but directionally consistent**.

## Per-Window Results

| window | kind | FXCM max | FXCM cluster max | Dukascopy max | class |
|---|---|---:|---:|---:|---|
| `2024-01-25_ge2_01` | `warning_ge2_target` | 2.5 | 2.5 | 2.490 | `CONFIRMED_CLOSELY` |
| `2024-02-18_ge2_01` | `warning_ge2_target` | 2.5 | 2.5 | 5.981 | `CONFIRMED_CLOSELY` |
| `2024-02-18_ge2_02` | `warning_ge2_target` | 2.5 | None | 4.440 | `INCONCLUSIVE` |
| `2024-05-01_ge2_01` | `warning_ge2_target` | 2.18 | 1.47 | 2.100 | `CONFIRMED_DIRECTIONALLY` |
| `2024-05-15_ge2_01` | `warning_ge2_target` | 2.27 | 2.25 | 2.107 | `CONFIRMED_CLOSELY` |
| `2024-07-11_ge2_01` | `warning_ge2_target` | 2.45 | 2.45 | 3.954 | `CONFIRMED_CLOSELY` |
| `2024-09-11_ge2_01` | `warning_ge2_target` | 1.88 | 1.88 | 3.224 | `CONFIRMED_DIRECTIONALLY` |
| `2024-10-10_ge2_01` | `warning_ge2_target` | 2.02 | 2.02 | 2.954 | `CONFIRMED_CLOSELY` |
| `2024-12-11_ge2_01` | `warning_ge2_target` | 2.5 | 2.5 | 2.451 | `CONFIRMED_CLOSELY` |
| `2024-12-11_ge2_02` | `warning_ge2_target` | 2.26 | 2.26 | 3.660 | `CONFIRMED_CLOSELY` |
| `2024-12-11_ge2_03` | `warning_ge2_target` | 2.5 | 2.5 | 5.120 | `CONFIRMED_CLOSELY` |
| `2024-12-11_ge2_04` | `warning_ge2_target` | 1.13 | 0.83 | 2.040 | `DISAGREES` |
| `2024-12-11_ge2_05` | `warning_ge2_target` | 2.39 | 2.39 | 3.617 | `CONFIRMED_CLOSELY` |
| `2024-12-11_ge2_06` | `warning_ge2_target` | 2.37 | 2.37 | 2.097 | `CONFIRMED_CLOSELY` |
| `2024-12-12_ge2_01` | `warning_ge2_target` | 2.5 | 2.25 | 2.510 | `CONFIRMED_CLOSELY` |
| `2024-12-12_ge2_02` | `warning_ge2_target` | 1.28 | 1.28 | 2.744 | `CONFIRMED_DIRECTIONALLY` |
| `2024-12-26_warning_p99_broad` | `warning_p99_major_control` | 2.5 | 2.5 | 1.980 | `CONFIRMED_DIRECTIONALLY` |
| `2024-12-30_warning_p99_broad` | `warning_p99_major_control` | 1.48 | 1.48 | 1.380 | `CONFIRMED_DIRECTIONALLY` |
| `2024-05-22_warning_p99_broad` | `warning_p99_major_control` | 2.48 | 2.48 | 1.440 | `CONFIRMED_DIRECTIONALLY` |
| `2024-01-02_warning_control_1200` | `control_warning_non_extreme` | 0.56 | 0.36 | 0.590 | `CONFIRMED_CLOSELY` |
| `2024-03-15_strict_control_1200` | `control_strict_normal` | 0.7 | 0.32 | 0.570 | `CONFIRMED_CLOSELY` |
| `2024-04-05_strict_ge2_01` | `control_strict_extreme` | 0.54 | None | 2.810 | `INCONCLUSIVE` |

## Caveats

- FXCM DEMO pricing is independent from Dukascopy but may be account/feed specific.
- FXCM and Dukascopy quotes are not expected to be identical; classifications use spread-regime and timing corroboration, not exact price equality.
- `2024-02-18_ge2_02` is unresolved because FXCM returned no ticks inside the exact target cluster under terminal/no-timeout chunks.
- `2024-12-11_ge2_04` disagrees at the narrow window level because FXCM had cluster ticks but did not show material stress there, even though the broader Dec 11 stress episode is strongly corroborated by adjacent windows.
- `2024-04-05_strict_ge2_01` is inconclusive as a strict-valid extreme control because FXCM returned no ticks inside the exact cluster; this is not warning-review evidence but remains important unresolved control evidence.
- These results do not promote warning-review rows into baseline execution-cost modelling. They only support the next separate policy/execution-cost gate.

## Durable Artifacts

- `/home/openclaw/.openclaw/workspace/XAUUSD_Lab/reports/fxcm_full_bounded_corroboration_2024.json`
- `/home/openclaw/.openclaw/workspace/XAUUSD_Lab/reports/fxcm_full_bounded_corroboration_2024_windows.csv`
- `/home/openclaw/.openclaw/workspace/XAUUSD_Lab/reports/fxcm_full_corroboration_checkpoint.json`
- `/home/openclaw/.openclaw/workspace/XAUUSD_Lab/external_corroboration/fxcm_full_bounded_corroboration_2024`
- `/home/openclaw/.openclaw/workspace/XAUUSD_Lab/external_corroboration/fxcm_scaling_operational_validation`

## Independent Critic Review

The independent read-only critic did not modify files, access credentials, authenticate, or make external requests.

Material critic findings:

- FXCM corroboration is broker-DEMO/account-feed corroboration, not market-level truth. The evidence supports another executable-looking broker feed showing similar stress, not definitive market-wide spread truth.
- Request-level completeness is handled carefully, but it remains request-level rather than market-level completeness.
- `2024-04-05_strict_ge2_01` is unresolved as a strict-valid extreme control, weakening confidence that FXCM always observes comparable exact-minute stress.
- `2024-12-11_ge2_04` materially disagrees at the exact warning window, even though adjacent Dec 11 windows reduce the campaign-level concern.
- Directional corroboration for sub-threshold FXCM windows is fair but must not be counted as close support.
- Broad p99 controls support regime plausibility, not row-level validation.
- Exact de-duplication looks acceptable; duplicate counts are tiny relative to total rows and same-timestamp conflicting price count is zero.
- Cherry-picking risk is bounded by the predeclared all-warning-`>=2.0` target set plus controls, but this remains targeted corroboration rather than full independent replication.

Critic materially changed conclusion: no. The critic preserved the pre-critic gate and rejected both stronger support and materially-disagree/inconclusive gates.

## Gate

Final gate: `CORROBORATION_PARTIALLY_SUPPORTIVE_MORE_REVIEW_REQUIRED`.

This campaign supports moving to a separate modelling-policy gate. It does not itself promote warning-review rows into baseline execution-cost modelling or authorize strategy work.
