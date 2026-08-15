# ASK Downstream Consumer Audit

Date: 2026-08-08

Mission: audit and minimally harden downstream XAUUSD_Lab consumers for quote-side identity before any real ASK acquisition.

This mission did not download ASK data, modify inherited BID raw evidence, regenerate broad historical reports, implement BID/ASK reconciliation, change spread methodology, install packages, or claim execution realism/profitability.

## Components Audited

| Component | Inputs consumed | Quote-side handling | Classification | Action |
| --- | --- | --- | --- | --- |
| `historical_baseline_report.py` | One existing linked-observation CSV | Required `quote_side` column was present, but rows from one malformed linked report could previously switch source identity across dates and still be pooled into one baseline | needs mixed-side rejection | Hardened validation to require one provider/instrument/quote_side/timeframe population per input report and to reject unsupported quote-side values |
| `research_observations.py` | One or more linked-observation CSVs | `quote_side` is already part of row identity and compatibility metadata; mixed side/provider/instrument/timeframe reports are rejected | already safe | Left unchanged |
| `explorer.py` | One raw CSV path derived from date | Hard-coded legacy `BID` raw filename and user-facing BID semantics | BID-only by design for now | Left unchanged; it has no ASK mode and cannot silently choose ASK by argument |
| `chart.py` | One raw CSV path derived from date | Hard-coded legacy `BID` raw filename and BID chart title | BID-only by design for now | Left unchanged; it has no ASK mode and cannot silently choose ASK by argument |
| Relevant diagnostics/tests | Linked reports, raw BID paths, helper fixtures | Diagnostics inspected only where linked/raw paths are consumed; no new mixed-side aggregation path found in this mission scope | not relevant or already covered by linked-report contracts | No diagnostic code changes |

## Files Changed

- `historical_baseline_report.py`
- `tests/test_historical_baseline_report.py`
- `docs/ASK_DOWNSTREAM_CONSUMER_AUDIT.md`

Existing side-aware files from previous missions remain part of the working tree but were not broadly refactored by this mission.

## Safeguards Added

- `historical_baseline_report.validate_linked_report_rows()` now validates `quote_side` with the shared `source_contracts.validate_quote_side()` helper.
- Historical baseline generation now rejects unsupported quote sides instead of treating them as ordinary labels.
- Historical baseline generation now records the first linked row's provider, instrument, quote side, and timeframe as the expected source identity for the report.
- Any later row in the same linked report with a different provider, instrument, quote side, or timeframe raises a clear `ValueError` before baseline metrics are calculated.
- Historical baseline output rows now carry `provider`, `instrument`, `quote_side`, and `timeframe` so a baseline artifact remains side-identifiable even if the source linked report was renamed.
- Baseline output naming remains derived from the input linked-report stem, so side-aware ASK linked-report filenames naturally produce side-aware baseline filenames.

## Compatibility Guarantees

- Legacy BID linked reports with side-omitted names remain accepted.
- Existing BID baseline output naming remains unchanged.
- Historical baseline schema is extended with source identity columns; metric semantics and quality population calculations remain unchanged.
- Existing strict-valid, warning-review, calendar-only, and excluded-unusable quality populations remain separate.
- `research_observations.py` remains unchanged because it already rejects incompatible `quote_side` values through compatibility metadata.
- `explorer.py` and `chart.py` remain legacy BID-only raw-data tools; they do not claim or accept ASK support.

## Tests

Added focused synthetic tests in `tests/test_historical_baseline_report.py` for:

- explicit ASK linked-report baseline acceptance
- ASK side-aware baseline output naming via source linked-report stem
- mixed BID/ASK rows rejected before population pooling
- provider mismatch rejected
- instrument mismatch rejected
- timeframe mismatch rejected
- unknown quote side rejected
- source identity preserved in every baseline metric row

Existing tests continue to cover legacy BID baseline behavior, quality-tier separation, research-observation compatibility, linked-report side awareness, and BID-only chart/explorer path helpers.

## Test Results

Focused relevant subset:

- `test_historical_baseline_report.py`: ran 21, OK
- `test_research_observations.py`: ran 19, OK
- `test_linked_observation_report.py`: ran 47, OK
- `test_session_report.py`: ran 8, OK
- `test_chart.py`: ran 0, OK, skipped 1 existing matplotlib-dependent class
- `test_market_closed_placeholders.py`: ran 4, OK, skipped 1 existing matplotlib-dependent test

Initial direct-file unittest invocation was invalid for repo-local fixture imports and failed with `ModuleNotFoundError: fixture_helpers`; it was rerun with unittest discovery patterns.

Full unittest discovery:

- Ran 176 tests
- OK
- skipped 3 existing matplotlib-dependent chart tests

No packages were installed.

## Reviewer Findings

The independent reviewer found one medium issue: baseline validation rejected mixed side identity, but baseline CSV rows did not carry provider, instrument, quote side, or timeframe. An ASK linked report renamed to a generic filename could therefore produce a baseline artifact whose rows did not explicitly identify ASK.

Revision made: added source identity columns to the baseline schema and every emitted baseline metric row, then added a focused test proving ASK source identity survives in the output rows. No other code-level blockers were found. The reviewer agreed `research_observations.py` was safe to leave unchanged and that `explorer.py`/`chart.py` can remain BID-only in this bounded mission.

## Components Intentionally Left BID-Only

- `explorer.py`: BID-only raw-file explorer for current inherited data.
- `chart.py`: BID-only raw-file chart viewer for current inherited data.

These should become explicitly side-aware only if ASK raw inspection/charting becomes part of an approved mission. Until then, they do not accept ASK arguments and do not generate side-aware reports.

## Remaining BID-Only Assumptions

- CLI entry points for raw-data viewing remain BID-oriented.
- Downstream chart/explorer titles and path helpers remain BID-specific.
- Diagnostics may still be BID-oriented unless they consume side-aware linked reports through the hardened contracts.
- No paired BID/ASK artifact exists.
- No ASK acquisition path has been run.

## Tiny Real ASK Pilot Readiness

The pipeline is technically closer to a tiny real ASK pilot because ordinary side-specific linked reports and the historical baseline consumer now reject silent mixed-side pooling. However, a pilot should still be treated as a provenance/data-quality exercise only. It should use a tiny date range, side-aware output naming, and no spread or strategy conclusions.

## Evidence Classification

`confirmed`: downstream linked-report consumers audited in this mission either already preserve quote-side identity, remain explicitly BID-only, or now reject mixed source identity before pooling.

`confirmed`: historical baseline generation is now hardened against mixed provider/instrument/quote_side/timeframe rows in one linked-report input and preserves that source identity in every baseline metric row.

`promising`: the current safeguards are sufficient to justify considering a tiny ASK provenance pilot after final reviewer approval and explicit mission scoping.

`not complete`: ASK support is not complete. No real ASK data was downloaded, no BID/ASK pairing exists, no spread-awareness or execution realism is established, and no profitability evidence is implied.

## Recommended Next Mission

Run a tiny ASK provenance pilot for a narrowly bounded date range only after confirming acquisition prerequisites: generate ASK raw files, ASK manifest, ASK session report, ASK linked-observation report, and optional ASK historical baseline with side-aware filenames, then compare provenance completeness without BID/ASK reconciliation or spread claims.
