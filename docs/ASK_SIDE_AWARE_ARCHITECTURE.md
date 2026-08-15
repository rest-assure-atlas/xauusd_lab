# ASK Side-Aware Provenance Architecture

Date: 2026-08-07

Mission: design the side-aware provenance architecture required for ASK onboarding while preserving the existing BID provenance milestone and comparability.

This artifact is design-only. It does not download ASK data, regenerate broad reports, implement schema changes, alter inherited BID evidence, establish execution realism, or support profitability claims.

## Evidence Classification

`confirmed`: the current Lab is a BID-first pipeline with existing row-level `quote_side` identity fields, BID-specific raw filename builders, BID-specific manifest/source contracts, and BID-specific docs/tests.

`promising`: the approved hybrid architecture is suitable for ASK onboarding because it keeps BID and ASK as separate provenance populations while allowing reusable infrastructure to become quote-side aware.

`invalid due to data or methodology`: any current spread-aware or execution-realistic testing that relies only on the BID pipeline or infers ASK validity from BID validity.

ASK onboarding is a data/provenance milestone only. It is not strategy evidence, execution-realism evidence, or profitability evidence.

## Observed Current Constraints

- Current documented version is `v0.11`.
- Current confirmed local data/provenance checkpoint is complete January-December 2024 Dukascopy XAUUSD one-minute BID linked-observation coverage in ignored local outputs.
- `data_downloader.py` defaults to `PRICE_SIDE = "BID"`, can read `price_side` from `config.json` in no-argument mode, and uses `PRICE_SIDE` in both Dukascopy URL construction and raw CSV filenames.
- `config.json` currently sets `"price_side": "BID"`.
- `data_quality.py` validates a side-neutral CSV shape, but its source contract constant is `QUOTE_SIDE = "BID"` and its module documentation says BID.
- `data_manifest.py` imports `QUOTE_SIDE` from `data_quality`, records it in the manifest, and hard-codes expected filenames as `XAUUSD_YYYY-MM-DD_1min_BID_UTC.csv`.
- `session_report.py`, `explorer.py`, and `chart.py` hard-code `PRICE_SIDE = "BID"` for raw file paths.
- `linked_observation_report.py` emits `quote_side`, checks it with `QUOTE_SIDE_MISMATCH`, and links manifest/session/source provenance, but the expected source side is still inherited from BID constants and filename builders.
- `research_observations.py` already includes `quote_side` in observation identity and compatibility fields, which is a useful guard against silent BID/ASK pooling.
- `historical_baseline_report.py` requires `quote_side` in linked reports but does not create side-aware source contracts itself.
- Existing generated report filenames omit quote side. They should remain stable for legacy BID comparability; new ASK and paired artifacts need explicit side-aware names.
- Existing tests encode BID behavior in fixture filename helpers, manifest expectations, linked-report source-contract tests, research-observation fixtures, and chart title expectations.

## Proposed Architecture

Use the approved hybrid architecture:

1. Keep BID and ASK as distinct provenance populations.
2. Generalize reusable infrastructure to accept an explicit quote side where appropriate.
3. Keep ordinary manifests and ordinary reports side-specific by default.
4. Do not mix BID and ASK into ordinary report populations yet.
5. Add a separate explicit BID/ASK reconciliation layer for spread work.
6. Never infer pair validity from one side alone.

### Quote-Side Abstraction

Accepted quote-side values should be exactly:

- `BID`
- `ASK`

Use uppercase values in Python constants, config, raw filenames, manifest rows, linked rows, and report metadata. Reject blank, lowercase, mixed-case, and unknown values rather than normalizing silently. If later provider conventions require additional sides, introduce them through an explicit schema/version decision.

Recommended naming conventions:

- Python parameter: `quote_side`
- Config field: `price_side` may remain for downloader compatibility, but new internal helpers should use `quote_side`.
- Raw CSV filename: `XAUUSD_YYYY-MM-DD_1min_{QUOTE_SIDE}_UTC.csv`
- Side-specific manifest filename for new ASK-aware runs: `data_manifest_{QUOTE_SIDE}_YYYY-MM-DD_to_YYYY-MM-DD.csv`
- Side-specific session report filename for new ASK-aware runs: `session_report_{QUOTE_SIDE}_YYYY-MM-DD_to_YYYY-MM-DD.csv`
- Side-specific linked report filename for new ASK-aware runs: `linked_observation_report_{QUOTE_SIDE}_YYYY-MM-DD_to_YYYY-MM-DD.csv`
- Paired reconciliation filename: `bid_ask_reconciliation_YYYY-MM-DD_to_YYYY-MM-DD.csv`

Compatibility rule: existing BID report filenames without quote side remain valid legacy BID artifacts. New code should keep producing the legacy filename by default for explicit `BID` legacy modes until a migration decision is made. ASK outputs must be rejected in legacy side-omitted output mode; ASK must use side-specific names or a side-specific location.

Components that should accept explicit `quote_side`:

- `data_downloader.py`: URL builder, output path builder, config/argument handling, terminal summary.
- New shared helper module, for example `quote_sides.py` or `source_contracts.py`: validation, accepted values, raw filename builder, side-aware report filename builder, source contract object.
- A `SourceContract` should be an immutable per-run value containing provider, instrument, quote side, timeframe, filename builder, and report naming mode. Generation code should receive this contract explicitly rather than reading mutable global side constants.
- `data_quality.py`: source contract metadata should be passed in or supplied by a side-specific contract; structural CSV validation can remain shared.
- `data_manifest.py`: expected raw filename, manifest row metadata, output path, summary context.
- `session_report.py`: input raw path and output path for side-specific runs, while preserving legacy BID defaults.
- `linked_observation_report.py`: expected manifest/source side, output path, source contract checks, linked metadata.
- `explorer.py` and `chart.py`: optional quote-side argument/title/path handling after core provenance support is stable.
- `research_observations.py`: mostly unchanged initially, because `quote_side` is already identity/compatibility; later add helpers for side-filtered loading if useful.
- `historical_baseline_report.py`: unchanged initially if it reads one side-specific linked report at a time; later reject mixed-side inputs unless explicitly designed.
- `internal_flat_zero_volume_diagnostic.py`: initially BID legacy-compatible; later side-aware only if diagnostics are needed for ASK reports.

## Side-Specific Provenance

BID and ASK must retain independent provenance. A valid BID day does not establish ASK availability or quality; a valid ASK day does not establish BID availability or quality.

Each side-specific manifest row should retain:

- `manifest_schema_version`
- `validation_rule_version`
- `date`
- `weekday`
- `provider`
- `instrument`
- `quote_side`
- `timeframe`
- `source_filename`
- `source_file_size_bytes`
- `source_checksum_algorithm`
- `source_checksum`
- `file_status`
- `quality_status`
- `quality_reasons`
- row counts, active counts, inactive-placeholder counts, timestamp range fields, duplicate/out-of-order counts, gap counts, invalid numeric/OHLC/volume counts

Additional provenance to consider before broad ASK acquisition:

- acquisition run identifier or local acquisition timestamp, if available from downloader logs or a new side-specific acquisition manifest
- requested source URL or URL template identity, without embedding secrets
- downloader software revision and dirty-state marker for acquisition runs
- source-side lineage linking raw CSV -> side manifest -> side linked report -> paired reconciliation artifact
- side linked `quality_tier` values carried forward explicitly; paired artifacts must not recompute side tiers from manifest status alone because linked quality also depends on linkage and session reconciliation

Quality populations remain separate by side:

- `strict_valid`
- `warning_review`
- `calendar_only`
- `excluded_unusable`

For ordinary side-specific linked reports, a row's quality tier is based only on that side's raw file, manifest assessment, session calculation, and source linkage.

## BID/ASK Reconciliation Artifact

Spread work needs a dedicated paired artifact. It should read side-specific BID and ASK provenance products and raw/source rows, then write a separate reconciliation CSV. It must not modify BID or ASK raw files, side-specific manifests, or ordinary linked reports.

Proposed artifact scope:

- one row per expected minute timestamp for the requested date range, or one row per available timestamp plus explicit missing-side rows; choose one and document it before implementation
- exact timestamp pairing only for the first implementation
- close-price spread as the initial field, with any OHLC spread extensions treated as a later decision
- candle-level spread fields are diagnostics only; one-minute BID and ASK OHLC candles do not prove simultaneous executable quotes inside the minute
- source identity for both sides either repeated per row or captured in a companion daily/source section; prefer daily companion rows only if the CSV contract remains simple and testable

Minimum proposed columns:

```text
pair_schema_version
validation_rule_version
date
timestamp_utc
provider
instrument
timeframe
bid_source_filename
bid_source_checksum_algorithm
bid_source_checksum
bid_manifest_quality_status
bid_manifest_quality_reasons
bid_quality_tier
ask_source_filename
ask_source_checksum_algorithm
ask_source_checksum
ask_manifest_quality_status
ask_manifest_quality_reasons
ask_quality_tier
bid_open
bid_high
bid_low
bid_close
bid_volume
ask_open
ask_high
ask_low
ask_close
ask_volume
spread_open
spread_high
spread_low
spread_close
pair_quality_status
pair_quality_reasons
```

Minimum user-requested fields are covered by `timestamp_utc`, `bid_close`, `ask_close`, `spread_close`, `bid_manifest_quality_status`/`bid_quality_tier`, `ask_manifest_quality_status`/`ask_quality_tier`, and `pair_quality_status`.

Recommended pair states:

- `strict_valid_pair`: both sides are strict-valid for the date, exact timestamp is present once on each side, numeric values are valid, and all spread fields are positive and within documented sanity bounds.
- `warning_review_pair`: both sides are pairable, but one or both sides are warning-review, a spread sanity warning exists, or market-closed/flat-zero-volume context requires review.
- `missing_bid`: ASK timestamp exists or is expected, but BID is absent.
- `missing_ask`: BID timestamp exists or is expected, but ASK is absent.
- `timestamp_mismatch`: row-level pairing cannot be trusted because duplicate/out-of-order/off-minute timestamps or date mismatches prevent exact one-to-one matching.
- `invalid_spread`: spread is negative, non-numeric, structurally impossible, or violates a hard exclusion threshold.
- `excluded`: one or both side-level observations are calendar-only or excluded-unusable, source identity is unavailable/changed, or another non-pairable condition applies.

Pair reason codes should be deterministic and machine-readable. Initial candidates:

```text
MISSING_BID
MISSING_ASK
BID_DUPLICATE_TIMESTAMP
ASK_DUPLICATE_TIMESTAMP
BID_INVALID_TIMESTAMP
ASK_INVALID_TIMESTAMP
TIMESTAMP_MISMATCH
BID_SIDE_NOT_STRICT_VALID
ASK_SIDE_NOT_STRICT_VALID
BID_SIDE_WARNING_REVIEW
ASK_SIDE_WARNING_REVIEW
BID_SIDE_EXCLUDED_UNUSABLE
ASK_SIDE_EXCLUDED_UNUSABLE
BID_SIDE_CALENDAR_ONLY
ASK_SIDE_CALENDAR_ONLY
NEGATIVE_SPREAD
ZERO_SPREAD
EXTREME_SPREAD
MARKET_CLOSED_PLACEHOLDER
SOURCE_IDENTITY_UNAVAILABLE
SOURCE_IDENTITY_CHANGED
```

Use current Lab style by keeping lower-case status values and upper-case reason codes.

## Alignment Rules

- Pairing rule: exact `timestamp_utc` string match after both side files pass strict timestamp parsing. Do not pair by nearest timestamp in the first implementation.
- Timestamp format: `YYYY-MM-DD HH:MM:SS`, UTC, zero-padded, minute-aligned, matching existing `data_quality.py` rules.
- Duplicate handling: any duplicate timestamp on either side prevents `strict_valid_pair` for that timestamp. Duplicate timestamps should produce `timestamp_mismatch` or `excluded` depending on whether row identity remains recoverable.
- Missing-side handling: emit explicit `missing_bid` or `missing_ask`; do not drop missing-side minutes silently.
- Differing row counts: summarize at date level and express row-level missing-side states. Differing counts are not automatically invalid if all differences are market-closed placeholders or expected gaps, but they prevent headline strict-pair coverage until reviewed.
- Market-closed placeholders: flat zero-volume placeholders should not be treated as executable spread evidence. If both sides are placeholders at the same timestamp, classify as `warning_review_pair` or `excluded` according to the date-level side quality and active-filter policy. If one side is placeholder and the other active, require review.
- Flat/zero-volume considerations: preserve existing edge-placeholder filtering for side-specific reports. For paired minute artifacts, keep enough row-level information to identify whether a spread row came from active candles or placeholder rows.
- Negative spread: always `invalid_spread`.
- Zero spread: not automatically impossible for all data vendors, but should be `warning_review_pair` at minimum until provider semantics prove it is acceptable; repeated zero spreads require escalation before use in execution-realistic testing.
- Extreme spread: define an explicit threshold before implementation. Until threshold is documented, classify detected outliers as `warning_review_pair`, not strict-valid.
- Quality combination: pair quality is the minimum/conservative combination of both sides plus row-level spread checks. Strict pair requires both sides to be strict-valid and row-level pair checks clean. Warning on either side prevents strict pair. Calendar-only or excluded-unusable on either side prevents spread use.

## Affected Components

Likely unchanged for the first implementation:

- Existing inherited raw BID files under `data_raw/`.
- Existing generated BID manifests/reports under `reports/`.
- Existing legacy BID report filenames and their current comparability.
- `candle_filters.py`.
- `session_tools.py`.
- `research_observations.py` core identity/compatibility contract, unless adding convenience filters.
- `historical_baseline_report.py` if it continues reading one side-specific linked report at a time.

Should become side-aware:

- `data_downloader.py` quote-side validation and explicit CLI/config behavior.
- `data_quality.py` source contract metadata.
- `data_manifest.py` source filename builder, manifest metadata, and new side-aware output naming while preserving legacy BID naming.
- `session_report.py` raw path builder and new side-aware output naming while preserving legacy BID naming.
- `linked_observation_report.py` side-specific source contract and new side-aware output naming while preserving legacy BID naming.
- Test fixtures in `tests/fixture_helpers.py`.
- Docs: `README.md`, `docs/DATA_QUALITY_MANIFEST.md`, `docs/CURRENT_STATE.md`, `docs/ROADMAP.md`, `docs/WORKFLOW.md`, `docs/DECISIONS.md`, and `docs/RESEARCH_FINDINGS.md` when implementation begins.

New modules/artifacts to introduce:

- `quote_sides.py` or `source_contracts.py` for quote-side validation and immutable per-run `SourceContract` helpers.
- `bid_ask_reconciliation.py` for explicit paired artifacts.
- `docs/BID_ASK_RECONCILIATION.md` if the paired artifact contract becomes large enough to document separately.
- Side-specific report outputs for ASK, using names that include `ASK`.

## Compatibility Plan

- Default behavior remains BID-compatible until explicitly invoked otherwise.
- Existing BID raw filenames remain `XAUUSD_YYYY-MM-DD_1min_BID_UTC.csv`.
- Existing side-omitted BID report filenames remain readable and reproducible for the current v0.11 milestone.
- New ASK outputs must include `ASK` in filenames or be generated into a clearly side-specific location.
- Ordinary manifests and linked reports must contain one quote side only. Mixed-side ordinary reports should be rejected until an explicit mixed contract exists.
- `research_observations.py` should continue treating `quote_side` as part of identity and compatibility. Same-date BID and ASK observations are separate observations, not duplicates. Its current compatibility behavior should remain unchanged unless a separate paired/mixed loader contract is deliberately introduced.
- Historical BID findings remain comparable only to outputs generated under the same legacy BID contract or an explicitly documented compatible successor.

Migration risks:

- Accidentally changing default BID output filenames would break report comparability.
- Adding ASK to config without downstream side-aware contracts would create untrusted data.
- Allowing mixed side ordinary reports could silently pool BID and ASK observations.
- Changing manifest/linkage schema versions without migration notes could invalidate existing report loaders.
- Treating warning-review ASK rows as equivalent to strict-valid BID rows would overstate evidence quality.

## Tests Required

Minimum test suite before ASK acquisition is trusted:

- BID-only legacy compatibility: existing BID filename builders, manifest output path, linked report output path, chart title, and loader compatibility remain unchanged.
- Quote-side validation: accepts only `BID` and `ASK`; rejects blank, lowercase, mixed-case, and unknown values.
- Downloader URL/path generation: `BID_candles_min_1.bi5` and `ASK_candles_min_1.bi5`; raw filenames include the requested side.
- ASK-side manifesting: synthetic ASK CSV creates manifest rows with `quote_side = ASK`, ASK source filename, stable checksums, and existing structural quality fields.
- Side-specific ordinary reports: ASK runs read ASK files and write ASK-named reports; BID legacy runs remain unchanged.
- Linked-report side contract: intentional ASK linked runs do not trigger `QUOTE_SIDE_MISMATCH`; incorrect manifest/source side does trigger a mismatch.
- Research-observation identity: same date/provider/instrument/timeframe with BID and ASK remain distinct, and mixed ordinary report populations are rejected or explicitly isolated.
- Exact BID/ASK pairing: one BID and one ASK row with the same timestamp produces `strict_valid_pair` when both sides are strict-valid and spread is positive.
- Missing side: missing BID produces `missing_bid`; missing ASK produces `missing_ask`; neither is silently dropped.
- Mismatched timestamps: off-minute/date-mismatched or non-overlapping timestamps prevent strict pairing.
- Duplicate timestamps: duplicates on either side prevent strict pairing and produce deterministic reason codes.
- Invalid/negative spread: negative spread is `invalid_spread`; zero spread is warning or excluded according to the documented threshold; extreme spread is warning until thresholds are approved.
- Quality-tier mismatch: strict+warning becomes `warning_review_pair`; strict+calendar-only or strict+excluded becomes `excluded` for spread use.
- Market-closed placeholder behavior: both-side placeholders and one-side placeholder cases are explicitly classified and cannot be mistaken for executable active spread evidence.
- Source identity: paired artifact preserves or links to both side source filenames and checksums.

## Unresolved Decisions

- Whether side-specific output naming should be mandatory for BID after a future major version, or whether legacy BID names remain the default indefinitely.
- Whether the first paired artifact should be one row per expected calendar minute or one row per union of observed side timestamps plus explicit missing states.
- Whether OHLC spread fields should exist at all before their semantics are justified. The first implementation should be close-spread-only unless OHLC spread diagnostics are separately approved.
- Exact threshold for `EXTREME_SPREAD`.
- Whether zero spread is warning-only or excluded after provider semantics are verified.
- Whether acquisition timestamp belongs in the manifest schema, a separate acquisition log, or both.
- Whether ASK session reports have research value before paired BID/ASK reconciliation, or whether they should remain provenance-only.

## Reviewer Findings

Independent review recommended revision before implementation. The reviewer agreed the hybrid architecture is sound and not unnecessarily complex for the risk, but requested tighter guardrails:

- Replace mutable/global quote-side assumptions with an explicit immutable per-run `SourceContract`.
- Make legacy side-omitted report names BID-only and reject ASK in legacy naming mode.
- Preserve `research_observations.py` compatibility behavior unless a separate paired/mixed loader is deliberately introduced.
- Carry both side manifest statuses and linked `quality_tier` values into paired artifacts; do not recompute side quality from manifest status alone.
- Treat candle-derived spread fields as diagnostics, not proof of simultaneous executable spread.
- Prefer a close-spread-only first paired artifact unless OHLC spread semantics are separately justified.

These changes have been incorporated into this architecture document.

## Recommended Next Bounded Mission

Implement the smallest side-aware infrastructure slice without downloading ASK data:

1. Add quote-side validation and immutable per-run `SourceContract` helpers.
2. Add side-aware filename/path builders while preserving legacy BID defaults and rejecting ASK in legacy side-omitted naming mode.
3. Add synthetic tests for BID legacy compatibility and ASK manifest/source-contract behavior.
4. Do not acquire ASK data or regenerate broad reports in that mission.

After that passes review, request YELLOW approval for a small ASK acquisition pilot date range.

## Escalation Assessment

No RED boundary is involved in this design mission.

YELLOW escalation is required before substantial ASK data acquisition, broad report regeneration, major schema migration, package installation, high-resource computation, or a methodology change that would affect prior BID comparability.
