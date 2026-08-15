# Top Warning-Date Spread-Tail Integrity Review, 2024

## Executive conclusion
The largest warning_review active-spread tail dates are source-consistent at the row/provenance level and are best treated as descriptive market/liquidity-regime observations, not as execution-cost model inputs yet. No invalid rows were found in the reviewed active tail. The event-cluster interpretation survives an independent artifact-focused second pass, but suitability for future execution-cost modelling is CONDITIONAL because the evidence is single-provider and warning-tier observations need an explicit downstream policy gate.

## Scope and methodology
- Source reconciliation: `/workspace/XAUUSD_Lab/reports/bid_ask_reconciliation_2024-01-01_to_2024-12-31.csv`; SHA-256 `79284720351511a68b9c8a819540f0265c5fa814a90ad281b6bf54a3d04be0d8`.
- Active rows were defined as rows whose pair quality reasons do not include `MARKET_CLOSED_PLACEHOLDER`; closed-market placeholders were excluded from all active-tail counts.
- Reviewed primary dates: 2024-12-11, 2024-12-12, 2024-12-26, 2024-12-30, 2024-05-22. Additional warning_review dates were added because they contain the remaining warning rows at spread >= 2.0: 2024-01-25, 2024-02-18, 2024-05-01, 2024-05-15, 2024-07-11, 2024-09-11, 2024-10-10.
- For each reviewed row, the extractor compared reconciled BID/ASK closes back to the corresponding raw BID and ASK CSV row, computed UTC hour/session labels from `sessions.json`, and measured before/after BID, ASK, and spread deltas.

## Coverage of extreme rows
- Warning_review active rows at spread >= 2.0: 84.
- Reviewed warning_review spread >= 2.0 rows: 84/84 (100.0%).
- Primary-date coverage alone: 64/84 (76.2%).
- Placeholder warning_review rows at spread >= 2.0 excluded from active-tail analysis: 1572.

## Per-date findings
### 2024-01-25 - inconclusive
- Warning active rows 1380; >=0.62 30; >=1.0 26; >=2.0 3; max spread 2.490.
- >=2.0 sessions {"outside_configured_sessions": 3}; UTC hours {"23": 3}.
- >=2.0 runs: ge2_run_01:2024-01-25 23:22:00..2024-01-25 23:22:00 n=1 max=2.490 | ge2_run_02:2024-01-25 23:24:00..2024-01-25 23:24:00 n=1 max=2.227 | ge2_run_03:2024-01-25 23:29:00..2024-01-25 23:29:00 n=1 max=2.130.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 1; both-sides-move 2; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: smaller additional >=2.0 cluster/date needed for full coverage; raw rows reconcile, but limited context leaves it inconclusive for modelling.

### 2024-02-18 - inconclusive
- Warning active rows 48; >=0.62 45; >=1.0 23; >=2.0 12; max spread 5.981.
- >=2.0 sessions {"outside_configured_sessions": 12}; UTC hours {"23": 12}.
- >=2.0 runs: ge2_run_04:2024-02-18 23:05:00..2024-02-18 23:05:00 n=1 max=2.080 | ge2_run_05:2024-02-18 23:07:00..2024-02-18 23:08:00 n=2 max=3.370 | ge2_run_06:2024-02-18 23:10:00..2024-02-18 23:10:00 n=1 max=3.451 | ge2_run_07:2024-02-18 23:12:00..2024-02-18 23:13:00 n=2 max=5.981 | ge2_run_08:2024-02-18 23:25:00..2024-02-18 23:30:00 n=6 max=4.440.
- Behaviour: stale-bid-only vs prior minute 1; stale-ask-only 0; both-sides-move 11; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: smaller additional >=2.0 cluster/date needed for full coverage; raw rows reconcile, but limited context leaves it inconclusive for modelling.

### 2024-05-01 - inconclusive
- Warning active rows 1380; >=0.62 9; >=1.0 2; >=2.0 1; max spread 2.100.
- >=2.0 sessions {"New York": 1}; UTC hours {"20": 1}.
- >=2.0 runs: ge2_run_09:2024-05-01 20:59:00..2024-05-01 20:59:00 n=1 max=2.100.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 0; both-sides-move 1; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: smaller additional >=2.0 cluster/date needed for full coverage; raw rows reconcile, but limited context leaves it inconclusive for modelling.

### 2024-05-15 - inconclusive
- Warning active rows 1380; >=0.62 5; >=1.0 2; >=2.0 1; max spread 2.107.
- >=2.0 sessions {"London+New York": 1}; UTC hours {"12": 1}.
- >=2.0 runs: ge2_run_10:2024-05-15 12:29:00..2024-05-15 12:29:00 n=1 max=2.107.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 0; both-sides-move 1; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: smaller additional >=2.0 cluster/date needed for full coverage; raw rows reconcile, but limited context leaves it inconclusive for modelling.

### 2024-05-22 - probably_source_consistent
- Warning active rows 1378; >=0.62 77; >=1.0 2; >=2.0 0; max spread 1.440.
- >=2.0 sessions {}; UTC hours {}.
- >=2.0 runs: none.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 0; both-sides-move 0; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: primary tail date has broad warning p99 contribution but no spread >=2.0 active warning rows; source-consistent for descriptive spread analysis, with modelling suitability conditional.

### 2024-07-11 - inconclusive
- Warning active rows 1380; >=0.62 2; >=1.0 2; >=2.0 1; max spread 3.954.
- >=2.0 sessions {"London+New York": 1}; UTC hours {"12": 1}.
- >=2.0 runs: ge2_run_11:2024-07-11 12:29:00..2024-07-11 12:29:00 n=1 max=3.954.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 0; both-sides-move 1; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: smaller additional >=2.0 cluster/date needed for full coverage; raw rows reconcile, but limited context leaves it inconclusive for modelling.

### 2024-09-11 - inconclusive
- Warning active rows 1380; >=0.62 7; >=1.0 2; >=2.0 1; max spread 3.224.
- >=2.0 sessions {"London+New York": 1}; UTC hours {"12": 1}.
- >=2.0 runs: ge2_run_12:2024-09-11 12:29:00..2024-09-11 12:29:00 n=1 max=3.224.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 0; both-sides-move 1; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: smaller additional >=2.0 cluster/date needed for full coverage; raw rows reconcile, but limited context leaves it inconclusive for modelling.

### 2024-10-10 - inconclusive
- Warning active rows 1369; >=0.62 8; >=1.0 1; >=2.0 1; max spread 2.954.
- >=2.0 sessions {"London+New York": 1}; UTC hours {"12": 1}.
- >=2.0 runs: ge2_run_13:2024-10-10 12:29:00..2024-10-10 12:29:00 n=1 max=2.954.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 0; both-sides-move 1; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: smaller additional >=2.0 cluster/date needed for full coverage; raw rows reconcile, but limited context leaves it inconclusive for modelling.

### 2024-12-11 - probably_source_consistent
- Warning active rows 1377; >=0.62 581; >=1.0 199; >=2.0 62; max spread 5.120.
- >=2.0 sessions {"London+New York": 1, "Tokyo": 58, "outside_configured_sessions": 3}; UTC hours {"03": 2, "04": 9, "05": 32, "06": 14, "07": 1, "13": 1, "23": 3}.
- >=2.0 runs: ge2_run_14:2024-12-11 03:44:00..2024-12-11 03:44:00 n=1 max=2.451 | ge2_run_15:2024-12-11 03:49:00..2024-12-11 03:49:00 n=1 max=2.011 | ge2_run_16:2024-12-11 04:32:00..2024-12-11 04:32:00 n=1 max=2.187 | ge2_run_17:2024-12-11 04:34:00..2024-12-11 04:37:00 n=4 max=3.660 | ge2_run_18:2024-12-11 04:50:00..2024-12-11 04:50:00 n=1 max=2.260 | ge2_run_19:2024-12-11 04:52:00..2024-12-11 04:52:00 n=1 max=2.000 | ge2_run_20:2024-12-11 04:55:00..2024-12-11 04:56:00 n=2 max=2.064 | ge2_run_21:2024-12-11 05:03:00..2024-12-11 05:05:00 n=3 max=3.310 | ge2_run_22:2024-12-11 05:11:00..2024-12-11 05:11:00 n=1 max=2.380 | ge2_run_23:2024-12-11 05:14:00..2024-12-11 05:18:00 n=5 max=5.120 | ge2_run_24:2024-12-11 05:20:00..2024-12-11 05:20:00 n=1 max=4.630 | ge2_run_25:2024-12-11 05:23:00..2024-12-11 05:25:00 n=3 max=3.250 | ge2_run_26:2024-12-11 05:29:00..2024-12-11 05:29:00 n=1 max=2.290 | ge2_run_27:2024-12-11 05:39:00..2024-12-11 05:48:00 n=10 max=4.587 | ge2_run_28:2024-12-11 05:50:00..2024-12-11 05:51:00 n=2 max=3.734 | ge2_run_29:2024-12-11 05:54:00..2024-12-11 05:59:00 n=6 max=3.225 | ge2_run_30:2024-12-11 06:01:00..2024-12-11 06:01:00 n=1 max=4.560 | ge2_run_31:2024-12-11 06:09:00..2024-12-11 06:13:00 n=5 max=4.504 | ge2_run_32:2024-12-11 06:15:00..2024-12-11 06:15:00 n=1 max=3.152 | ge2_run_33:2024-12-11 06:24:00..2024-12-11 06:27:00 n=4 max=2.521 | ge2_run_34:2024-12-11 06:30:00..2024-12-11 06:31:00 n=2 max=4.451 | ge2_run_35:2024-12-11 06:36:00..2024-12-11 06:36:00 n=1 max=2.352 | ge2_run_36:2024-12-11 07:12:00..2024-12-11 07:12:00 n=1 max=2.040 | ge2_run_37:2024-12-11 13:29:00..2024-12-11 13:29:00 n=1 max=3.617 | ge2_run_38:2024-12-11 23:11:00..2024-12-11 23:13:00 n=3 max=2.097.
- Behaviour: stale-bid-only vs prior minute 1; stale-ask-only 4; both-sides-move 57; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: sustained multi-minute active clusters with coherent BID/ASK movement and raw row agreement; no timestamp mismatch or placeholder leakage found. Safe for descriptive spread analysis; not yet suitable for execution-cost modelling without a warning-tier policy.

### 2024-12-12 - probably_source_consistent
- Warning active rows 1369; >=0.62 607; >=1.0 81; >=2.0 2; max spread 2.744.
- >=2.0 sessions {"London+New York": 1, "Tokyo": 1}; UTC hours {"01": 1, "13": 1}.
- >=2.0 runs: ge2_run_39:2024-12-12 01:30:00..2024-12-12 01:30:00 n=1 max=2.510 | ge2_run_40:2024-12-12 13:29:00..2024-12-12 13:29:00 n=1 max=2.744.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 0; both-sides-move 2; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: sustained multi-minute active clusters with coherent BID/ASK movement and raw row agreement; no timestamp mismatch or placeholder leakage found. Safe for descriptive spread analysis; not yet suitable for execution-cost modelling without a warning-tier policy.

### 2024-12-26 - probably_source_consistent
- Warning active rows 1375; >=0.62 243; >=1.0 2; >=2.0 0; max spread 1.980.
- >=2.0 sessions {}; UTC hours {}.
- >=2.0 runs: none.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 0; both-sides-move 0; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: primary tail date has broad warning p99 contribution but no spread >=2.0 active warning rows; source-consistent for descriptive spread analysis, with modelling suitability conditional.

### 2024-12-30 - probably_source_consistent
- Warning active rows 1380; >=0.62 224; >=1.0 1; >=2.0 0; max spread 1.380.
- >=2.0 sessions {}; UTC hours {}.
- >=2.0 runs: none.
- Behaviour: stale-bid-only vs prior minute 0; stale-ask-only 0; both-sides-move 0; flat-zero-volume >=2 rows 0.
- Quality reasons observed on date: `BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW`.
- Interpretation: primary tail date has broad warning p99 contribution but no spread >=2.0 active warning rows; source-consistent for descriptive spread analysis, with modelling suitability conditional.

## BID/ASK behavioural evidence
- Detail evidence with every reviewed tail/context row is in `reports/evidence/top_warning_date_spread_integrity_review_detail.csv`. It includes timestamp, BID, ASK, spread, quality population, warning reasons, UTC hour, configured session, previous/next deltas, volumes, and raw-match flags.
- Raw BID/ASK close mismatches among reviewed warning >=2.0 rows: 0.
- The largest 2024-12-11 >=2.0 observations form sustained bursts rather than isolated one-row spikes; spread expansion is generated by BID and ASK moving at different magnitudes and timing, not by a detected side missing from raw evidence.
- The 2024-12-12 broader warning p99 tail is clustered, while its >=2.0 rows are isolated one-minute observations at 01:30 and 13:29 UTC. Both rows reconcile to raw BID/ASK and are not explained by a single stale-side placeholder leak.
- Flat-zero-volume is present on many active warning rows and is correlated with warning-tier status, but it does not by itself invalidate the spread observations: the raw BID/ASK prices match the reconciliation rows, and the reviewed active tail excludes `MARKET_CLOSED_PLACEHOLDER`.

## Temporal and session findings
- Warning_review >=2.0 rows concentrate in Tokyo and the 22-23 UTC reopening/rollover area, with smaller London/New York overlap exposure. The inspected hours include Tokyo, 22-23 UTC, 05, 06, and 12 UTC as requested.
- The primary warning p99 dates 2024-12-26 and 2024-12-30 are elevated tail days without >=2.0 warning rows; their pattern is broad active warning spread widening rather than the extreme December 11 cluster.
- The review does not attach news or event labels. It only supports a liquidity/session-transition or source-observed cluster interpretation at the data-integrity level.

## Controls
- Warning controls selected by elevated warning activity but no >=2.0 rows: 2024-05-28, 2024-08-14, 2024-03-25, 2024-12-17.
- Strict-valid extreme controls inspected descriptively only: 2024-04-14, 2024-12-13, 2024-12-24, 2024-12-25, 2024-12-27.
- Control summaries are in `reports/evidence/top_warning_date_spread_integrity_review_controls.csv`. They show that strict-valid extremes can occur on holiday/reopening or sparse active days, while warning controls can have many >=0.62/>=1.0 rows without producing the same >=2.0 sustained clusters.

## Independent second-pass artifact review
- Checklist run: artifact explanations, unsupported storytelling, stale quote behaviour, classification mistakes, reconciliation blind spots, methodological circularity, and over-strong conclusions.
- Assessment: no invalid or suspicious_data_quality cluster was established. The report avoids external event explanations and does not convert descriptive spread observations into execution-cost assumptions. The weakest point is not row integrity but external corroboration and policy for warning-tier model inclusion.
- The event-cluster interpretation survives: clusters are multi-row, source-matched, active/non-placeholder, and concentrated in plausible session-transition/liquidity windows, while controls do not reproduce the same structure uniformly.

## Evidence classification table
| date | role | classification | safe for descriptive spread analysis | future execution-cost model suitability | evidence note |
| --- | --- | --- | --- | --- | --- |
| 2024-01-25 | additional_ge2 | inconclusive | yes | no_without_more_review | ge2=3, max=2.490 |
| 2024-02-18 | additional_ge2 | inconclusive | yes | no_without_more_review | ge2=12, max=5.981 |
| 2024-05-01 | additional_ge2 | inconclusive | yes | no_without_more_review | ge2=1, max=2.100 |
| 2024-05-15 | additional_ge2 | inconclusive | yes | no_without_more_review | ge2=1, max=2.107 |
| 2024-05-22 | primary | probably_source_consistent | yes | conditional | ge2=0, max=1.440 |
| 2024-07-11 | additional_ge2 | inconclusive | yes | no_without_more_review | ge2=1, max=3.954 |
| 2024-09-11 | additional_ge2 | inconclusive | yes | no_without_more_review | ge2=1, max=3.224 |
| 2024-10-10 | additional_ge2 | inconclusive | yes | no_without_more_review | ge2=1, max=2.954 |
| 2024-12-11 | primary | probably_source_consistent | yes | conditional | ge2=62, max=5.120 |
| 2024-12-12 | primary | probably_source_consistent | yes | conditional | ge2=2, max=2.744 |
| 2024-12-26 | primary | probably_source_consistent | yes | conditional | ge2=0, max=1.980 |
| 2024-12-30 | primary | probably_source_consistent | yes | conditional | ge2=0, max=1.380 |

## Validation
- Detail rows validated against source reconciliation by timestamp/date selection and raw BID/ASK close equality; raw mismatches among warning >=2.0 rows: 0.
- Count reconciliation: warning_review active spread >=2.0 rows recomputed as 84, matching the prior sensitivity total of 84.
- Reviewed rows account for 84/84 (100.0%) of warning >=2.0 rows; primary dates account for 64/84 (76.2%).
- Placeholder/closed-market rows excluded; excluded placeholder warning_review >=2.0 rows: 1572.
- Syntax validation: `python3 -m py_compile` succeeded for the existing reconciliation, manifest, quality, session, and spread modules.
- Unavailable validation: `pytest` is not installed in the sandbox (`No module named pytest`); no external market/source corroboration was acquired, by scope constraint.

## Unresolved questions
- The most important unresolved issue is whether a second independent market data source confirms the same active BID/ASK spread clusters, especially the non-primary January/February/April >=2.0 dates and the December 11 run.
- A future gate must decide how warning_review rows with flat-zero-volume/internal warnings may be used, if at all, in execution-cost modelling.

## Implications for next research gate
- Dataset readiness for the next modelling gate: CONDITIONAL.
- Recommended next gate: pre-modelling data policy and external/source-corroboration gate for warning_review active spread clusters, preserving strict_valid and warning_review slices separately.
