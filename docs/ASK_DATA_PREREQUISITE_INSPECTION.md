# ASK Data Prerequisite Inspection

Date: 2026-08-07

Mission: determine what is required to add trustworthy ASK-data support before any spread-aware or execution-realistic strategy testing is attempted.

This is an inspection/design artifact for the experimental OpenClaw copy. It does not implement ASK support, download ASK data, regenerate reports, alter inherited raw BID evidence, or establish execution realism.

## Evidence Classification

`invalid due to data or methodology` for any attempted spread-aware or execution-realistic testing using the current BID-only pipeline.

`promising` as a bounded data/provenance prerequisite direction: ASK acquisition and BID/ASK alignment appear feasible to investigate, but implementation requires explicit side-aware provenance design and validation gates.

ASK support should be treated as a new data/provenance milestone, not as strategy evidence, profitability evidence, or execution-realism evidence.

## Facts Directly Observed

- Current application version is documented as `v0.11`.
- Current confirmed data/provenance checkpoint is complete January-December 2024 Dukascopy XAUUSD one-minute BID linked-observation coverage in ignored local outputs.
- Current docs repeatedly state the evidence is BID-only and that ASK remains a prerequisite before spread-aware or execution-aware testing.
- `data_downloader.py` defaults to `SYMBOL = "XAUUSD"`, `PRICE_SIDE = "BID"`, and `TIMEFRAME = "min_1"`.
- `config.json` currently sets `"price_side": "BID"`.
- `data_downloader.py` can read `price_side` from `config.json` and uses `PRICE_SIDE` in the Dukascopy URL and output filename.
- Command-line date mode in `data_downloader.py` does not load `config.json`, so it keeps the module default `BID`.
- Downloader output filename shape is `XAUUSD_YYYY-MM-DD_1min_{PRICE_SIDE}_UTC.csv`.
- `data_quality.py` source contract constants are `PROVIDER = "Dukascopy"`, `INSTRUMENT = "XAUUSD"`, `QUOTE_SIDE = "BID"`, and `TIMEFRAME = "1min"`.
- `data_manifest.py` imports `QUOTE_SIDE` from `data_quality` and builds expected filenames as `XAUUSD_YYYY-MM-DD_1min_BID_UTC.csv`.
- `session_report.py`, `explorer.py`, and chart-facing tests use BID-specific filename/title assumptions.
- `linked_observation_report.py` imports `QUOTE_SIDE` from `data_quality`, compares manifest `quote_side` against it, and emits `QUOTE_SIDE_MISMATCH` for mismatches.
- `research_observations.py` includes `quote_side` in observation identity and compatibility fields, which helps prevent silent BID/ASK mixing once source contracts exist.
- Existing linked reports include `quote_side`, source filename, source file size, checksum, manifest schema version, validation rule version, active filter identity, session definition checksum, and software revision.
- Existing tests encode BID-only behavior in fixture filename helpers, manifest filename expectations, linked-report source contract checks, research-observation fixtures, chart title expectations, and baseline fixtures.
- `docs/DECISIONS.md` says current BID-only research is not sufficient for realistic strategy profitability claims and future execution-aware testing must account for ASK data, spread, commission, slippage, latency, and execution assumptions.

## BID-Only Assumptions Found

### Downloader And Config

- Default quote side is hard-coded as `BID`.
- Config can override `price_side`, but only no-argument config mode applies it.
- The URL builder uses `{PRICE_SIDE}_candles_{TIMEFRAME}.bi5`; this suggests the same Dukascopy path pattern may support `ASK`, but this mission did not perform external acquisition or provider verification.
- Output filenames include quote side, which is a useful existing convention.

### Raw Filename And Manifest Contract

- `data_manifest.build_source_filename(day)` always expects `XAUUSD_YYYY-MM-DD_1min_BID_UTC.csv`.
- Manifest metadata always records `quote_side` from `data_quality.QUOTE_SIDE`, currently `BID`.
- `docs/DATA_QUALITY_MANIFEST.md` defines the source contract as one-minute BID quote files.
- An ASK file placed in `data_raw/` would not be picked up by the current manifest path builder unless code is changed.

### Data Quality

- Structural validation rules are mostly side-neutral at the CSV level: headers, timestamps, OHLC consistency, volume, gaps, checksums, edge placeholders, and internal flat zero-volume warnings.
- The source contract is not side-neutral because `QUOTE_SIDE` is a module constant and documentation says BID.
- ASK quality cannot inherit BID validity; it needs independent assessment and provenance.

### Reports And Linked Observations

- `session_report.py`, `explorer.py`, and `chart.py` build BID raw paths using `PRICE_SIDE = "BID"`.
- `linked_observation_report.py` is side-aware in output columns but BID-bound through imported constants and expected filenames.
- `research_observations.py` treats `quote_side` as an identity and compatibility dimension, which is compatible with future side-separated reports.
- `historical_baseline_report.py` requires `quote_side` but does not itself create side-aware source contracts.

### Tests

- `tests/fixture_helpers.py` returns BID production filenames.
- `tests/test_data_manifest.py` asserts exact BID filename contracts.
- `tests/test_linked_observation_report.py` verifies quote-side mismatch behavior by changing manifest `quote_side` to `ASK`.
- `tests/test_research_observations.py` uses BID fixtures and rejects incompatible `quote_side` across loaded reports.
- `tests/test_chart.py` expects a BID chart title.

## ASK Prerequisites

Before ASK support is trustworthy, the project needs:

- A documented ASK source contract: provider, instrument, quote side, timeframe, timezone, filename convention, expected columns, price scale, and Dukascopy URL pattern.
- A decision on whether modules should be generalized with a `quote_side` parameter or whether BID and ASK should remain separate side-specific pipelines with a later paired-spread layer.
- A side-aware manifest contract or an explicit separate ASK manifest contract and versioning plan.
- Side-aware raw path builders that do not silently treat ASK as BID or BID as ASK.
- Independent ASK raw validation with source file size and checksum provenance.
- Clear rules for dates where BID is valid but ASK is missing, warning, or invalid, and vice versa.
- A paired BID/ASK reconciliation artifact before any spread derivation.
- Explicit treatment of quality populations: `strict_valid`, `warning_review`, `calendar_only`, and `excluded_unusable` must remain separate by side and in any paired artifact.

## Alignment And Spread Risks

Spread derivation is not just `ASK - BID` at the daily report level. Risks include:

- Missing one side for a date or minute.
- Different timestamp coverage by side.
- Duplicate or out-of-order timestamps by side.
- Different warning/invalid populations by side.
- Side-specific provider outages or flat zero-volume periods.
- Negative, zero, crossed, or extreme spread values.
- One-minute OHLC candles not proving simultaneous tradable bid/ask quotes within the minute.
- Session overlap and active-candle filtering potentially differing by side.
- Commission, slippage, latency, order type, and broker execution rules remaining undefined.

A spread-aware layer should preserve both source checksums and side-specific quality status, then compute only on explicitly aligned timestamp intersections or another documented pairing rule.

## Missing Information

- No external verification was performed to prove Dukascopy ASK availability or exact semantics for XAUUSD one-minute candle files.
- No ASK sample was downloaded or inspected.
- No decision exists yet on side-aware schema versioning.
- No paired BID/ASK artifact schema exists.
- No execution model exists for spread, commission, slippage, latency, order type, or broker assumptions.

## Proposed Minimal Implementation Sequence

1. Architecture decision: choose side-aware generalization versus separate BID/ASK pipelines plus a paired-spread layer.
2. Document an ASK source contract and update durable decisions without claiming execution realism.
3. Refactor filename/source-contract helpers to accept explicit `quote_side` while preserving existing BID outputs.
4. Add tests proving current BID filename, manifest, linked-report, and loader behavior remains unchanged.
5. Add downloader URL/output filename tests for both `BID` and `ASK`; decide command-line/config behavior so quote side is explicit and predictable.
6. Add ASK manifest/data-quality tests using synthetic ASK-shaped CSV files.
7. Add side-specific session/linked-report tests, including no `QUOTE_SIDE_MISMATCH` for intentional ASK runs.
8. Add research-observation compatibility tests proving same-date BID and ASK observations remain distinct and cannot be silently pooled.
9. Run a bounded ASK acquisition/provenance pilot on a small date range only after approval for data acquisition.
10. Design a paired BID/ASK reconciliation report with timestamp alignment, side-specific quality, checksum preservation, and spread sanity metrics.
11. Only after paired provenance is reviewed, consider a bounded spread analysis. Do not call it execution-realistic until execution assumptions are separately specified.

## Required Tests

- Downloader URL and filename generation for `BID` and `ASK`.
- Config and command-line behavior for quote side.
- Manifest source filename and metadata for ASK.
- Data-quality validation of ASK files with the same structural rules as BID.
- Missing-side tests: ASK missing must not imply BID missing, and BID missing must not imply ASK missing.
- Session report path/metadata tests for ASK, if side-specific session reports are retained.
- Linked report tests for ASK rows, side-specific source filename/checksum, and expected quote-side matching.
- Research observation tests proving BID and ASK same-date rows are distinct identities.
- Compatibility tests deciding whether mixed BID+ASK linked reports are intentionally allowed or intentionally rejected.
- Paired-spread tests for timestamp alignment, missing-side exclusion, negative/zero spread flags, extreme spread summaries, and provenance links to both source files.
- Regression tests proving existing BID outputs remain unchanged after side-aware refactoring.

## Reviewer Findings

Independent review agreed with the main inspection:

- Current pipeline is explicitly BID-only across downloader defaults, manifest, session report, linked report, loader contracts, docs, and tests.
- Adding ASK only at the downloader/config level would create data that downstream provenance tools cannot verify correctly.
- ASK support should be a new data/provenance milestone, not an execution-realistic milestone.
- Spread derivation requires paired BID/ASK provenance and alignment checks before any spread report.
- Implementation should be blocked only for spread-aware or execution-realistic testing. A narrow ASK provenance implementation can proceed after an architecture decision on schema/layout.

## Recommendation For Next Bounded Mission

Next mission should be an architecture decision and minimal design spec:

**Decide and document the side-aware provenance architecture for ASK onboarding.**

The decision should answer:

- Generalize existing modules with explicit `quote_side`, or create separate ASK pipeline entry points?
- One quote side per manifest/linked report, or mixed side reports with compatibility rules?
- Where should paired BID/ASK reconciliation artifacts live and what schema fields are required?
- What small ASK pilot date range should be used after data acquisition is approved?

After that decision, a small implementation mission can add side-aware helpers and tests while preserving existing BID behavior.

## Escalation Needed

YELLOW escalation is needed before substantial ASK data acquisition, schema changes that affect comparability, or broad report regeneration.

RED boundaries were not encountered. No broker credentials, live execution, external publishing, authoritative repository access, or real-money trading were involved.
