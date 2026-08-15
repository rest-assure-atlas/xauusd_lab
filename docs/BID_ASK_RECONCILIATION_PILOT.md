# BID/ASK Reconciliation Pilot

Date: 2026-08-08

Mission: implement and validate the first explicit BID/ASK reconciliation artifact for the already-approved XAUUSD three-day pilot range.

Approved range: 2024-01-09 through 2024-01-11 inclusive.

## Boundary

This pilot uses only existing BID and ASK evidence for the three approved dates. It does not acquire data, broaden coverage, modify raw files, regenerate broad historical evidence, build execution modelling, run strategy tests, or characterize spread behavior beyond row-level validity checks needed for reconciliation.

## Implementation

Implementation file: `bid_ask_reconciliation.py`

Output artifact:

- `reports/bid_ask_reconciliation_2024-01-09_to_2024-01-11.csv`

The implementation reads side-specific linked-observation provenance and raw CSV rows, then writes a separate paired CSV. It does not modify BID or ASK raw files or inherited side-specific reports.

Default provenance inputs:

- BID linked report: `reports/linked_observation_report_2024-01-01_to_2024-01-31.csv`
- ASK linked report: `reports/linked_observation_report_ASK_2024-01-09_to_2024-01-11.csv`
- BID raw files: `data_raw/XAUUSD_2024-01-09_1min_BID_UTC.csv`, `data_raw/XAUUSD_2024-01-10_1min_BID_UTC.csv`, `data_raw/XAUUSD_2024-01-11_1min_BID_UTC.csv`
- ASK raw files: `data_raw/XAUUSD_2024-01-09_1min_ASK_UTC.csv`, `data_raw/XAUUSD_2024-01-10_1min_ASK_UTC.csv`, `data_raw/XAUUSD_2024-01-11_1min_ASK_UTC.csv`

## Reconciliation Schema

The paired CSV includes:

- pair schema and validation-rule identifiers
- date and `timestamp_utc`
- provider, instrument, timeframe
- BID and ASK source filenames, checksum algorithm, checksums
- BID and ASK manifest quality statuses and reasons
- BID and ASK quality tiers
- BID and ASK OHLCV values
- close-price `spread` as `ask_close - bid_close`
- `pair_quality_status`
- deterministic `pair_quality_reasons`

Close-price spread is included only as a row-level reconciliation and validity field. It is not used here for spread characterization, execution modelling, or trading conclusions.

## Provenance Rules

The reconciler requires side-specific linked provenance before reading raw rows. It rejects incompatible provider, instrument, timeframe, quote side, or expected source filename.

Expected identity for every paired day:

- provider: `Dukascopy`
- instrument: `XAUUSD`
- timeframe: `1min`
- BID quote side: `BID`
- ASK quote side: `ASK`
- raw filenames include explicit `_BID_` or `_ASK_` side identity

The implementation does not rely on session-report provenance identity fields.

## Pairing And Quality Rules

Pairing uses exact timestamp matching only. The artifact emits missing-side rows rather than dropping unmatched timestamps.

Handled cases include exact matches, missing BID, missing ASK, duplicate BID timestamps, duplicate ASK timestamps, incompatible side provenance, negative spread, zero spread, extreme spread, placeholder rows, and quality-tier mismatch.

Pair states used:

- `strict_valid_pair`
- `warning_review_pair`
- `missing_bid`
- `missing_ask`
- `timestamp_mismatch`
- `invalid_spread`
- `excluded`

Strict-valid pairs require both sides to be `strict_valid`, exact one-to-one timestamp pairing, valid numeric close values, positive spread, no extreme-spread warning, and no placeholder warning. Warning-review on either side prevents a strict-valid pair.

For this pilot, both side-specific linked reports classify the selected dates as `warning_review`, so every real matched pair remains `warning_review_pair`. This is a conservative propagation, not a strict-valid upgrade.

Extreme spread threshold for this first validity check: spread greater than 10.0 is `EXTREME_SPREAD` and remains `warning_review_pair`. This threshold is a sanity guard only, not spread research.

## Counts And Anomalies

Generated artifact: `reports/bid_ask_reconciliation_2024-01-09_to_2024-01-11.csv`

- Total BID rows: 4320
- Total ASK rows: 4320
- Exact timestamp matches: 4320
- Missing BID rows: 0
- Missing ASK rows: 0
- Duplicate BID timestamps: 0
- Duplicate ASK timestamps: 0
- Negative spreads: 0
- Zero spreads: 0
- Extreme spreads: 0
- Warning-review pairs: 4320
- Excluded/invalid rows: 0
- Placeholder-warning rows: 180
- Observed close-spread range for validity checking only: 0.085 to 0.837

Pair status counts:

- `warning_review_pair`: 4320

Pair reason counts:

- `BID_SIDE_WARNING_REVIEW`: 4320
- `ASK_SIDE_WARNING_REVIEW`: 4320
- `MARKET_CLOSED_PLACEHOLDER`: 180

No unexpected missing-side, duplicate-timestamp, negative-spread, zero-spread, or invalid/excluded anomaly was observed in this three-day artifact.

## Tests

Synthetic reconciliation tests added in `tests/test_bid_ask_reconciliation.py` cover:

- exact BID/ASK pairing
- missing ASK
- missing BID
- mismatched timestamps
- duplicate BID timestamp
- duplicate ASK timestamp
- negative spread
- zero spread
- extreme spread
- quality-tier mismatch
- provider mismatch
- instrument mismatch
- timeframe mismatch
- incompatible quote side
- placeholder handling
- raw BID and ASK files remain untouched

Test results:

- Focused reconciliation: `Ran 18 tests`, `OK`
- Relevant side-aware tests: `Ran 80 tests`, `OK`
- Full unittest discovery: `Ran 195 tests`, `OK (skipped=3)`

The three skips are existing matplotlib-dependent chart tests. No packages were installed.

## Reviewer Findings

One independent read-only reviewer challenged the implementation and artifact. Initial findings:

- Medium: raw file provenance was repeated but not revalidated at reconciliation time.
- Medium: timestamp validation was inherited from earlier manifests rather than enforced in the reconciliation layer.
- Low: duplicate timestamp handling was conservative, but emitted one duplicate row value while flagging the timestamp mismatch.
- Low: the architecture proposal includes separate `spread_open`, `spread_high`, `spread_low`, and `spread_close`, while this first implementation intentionally emits one close-price `spread` field.

Revisions made after review:

- Added reconciliation-time raw file size and SHA-256 checksum validation against linked provenance before pairing.
- Added reconciliation-layer timestamp validation for exact format, expected date, and minute alignment. Invalid side timestamps are classified as `timestamp_mismatch` with side-specific invalid timestamp reasons.
- Added focused tests for raw checksum drift and invalid timestamp handling.

Remaining accepted limitation:

- Duplicate timestamp rows remain conservative: they block valid pairing and emit `timestamp_mismatch`, but the row-level CSV still carries one observed value for that duplicate timestamp. This is acceptable for the current real artifact because duplicate BID and ASK timestamps are both zero. A later duplicate-forensics artifact would need to preserve all conflicting duplicate rows.

Reviewer clean checks after inspection of the original output:

- Side-safe pairing was preserved; BID and ASK linked reports were loaded separately and quote-side checked.
- No accidental BID/ASK swap was found.
- Provenance for inspected raw files matched linked rows.
- Quality-tier propagation was conservative; all pairs remained warning-review.
- No inherited BID contamination was found.
- A later bounded descriptive spread-characterization mission is justified if it preserves the current warning-review status and does not advance into execution modelling or strategy claims.

## Evidence Classification

Confirmed for this three-day pilot:

- BID and ASK evidence can be paired into an explicit, side-aware reconciliation artifact.
- Exact timestamp alignment exists for all 4320 rows in the approved date range.
- Side-specific source identity is preserved in the paired artifact.
- Warning-review side quality is propagated conservatively to pair quality.
- Inherited BID raw files and newly acquired ASK raw files were not modified by reconciliation.

Not established:

- execution realism
- strategy performance
- profitability
- broad ASK coverage
- broad spread behavior
- session-level or distributional spread characterization
- production-grade execution cost modelling

## Next Step Assessment

A later bounded basic spread-characterization mission is technically justified on these same three dates only, because a side-aware paired artifact now exists and preserves source identity. That next mission should remain explicitly separate from execution modelling, strategy testing, and profitability claims.

## Escalation

No YELLOW or RED escalation was encountered during implementation or validation.
