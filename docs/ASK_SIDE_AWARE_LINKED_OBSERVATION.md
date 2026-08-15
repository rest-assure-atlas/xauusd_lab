# ASK Side-Aware Linked Observation Report

Date: 2026-08-08

Mission: extend side-aware infrastructure into linked-observation report generation without downloading ASK data, regenerating broad reports, implementing BID/ASK reconciliation, or changing spread methodology.

## Evidence Classification

`confirmed`: linked-observation report generation now accepts a per-run `SourceContract`, uses side-aware raw/source filenames and report naming, preserves legacy BID defaults, and rejects ASK under legacy side-omitted output naming.

`confirmed`: synthetic tests cover explicit BID and ASK linked-report contracts, ASK linked-report generation from synthetic rows, ambiguous ASK naming rejection, incompatible source identity detection, and side-specific data-quality population separation.

`not complete`: this is not complete ASK support. No ASK data was downloaded, no real ASK reports were generated, no BID/ASK reconciliation exists, and no spread-aware, execution-realistic, or profitability evidence is established.

## Files Changed

- `linked_observation_report.py`: threaded optional `SourceContract` through linked report path construction, manifest-row construction, source path lookup, source filename expectations, linkage contract checks, row construction, day processing, and report creation.
- `tests/test_linked_observation_report.py`: added focused synthetic coverage for linked-report side awareness and compatibility.
- `docs/ASK_SIDE_AWARE_LINKED_OBSERVATION.md`: this implementation note.

## Implementation Behavior

- Existing calls to `create_linked_observation_report(start_day, end_day, data_dir)` still use the default BID `SourceContract`.
- Existing calls to `build_linked_report_path(start_day, end_day)` still return `linked_observation_report_YYYY-MM-DD_to_YYYY-MM-DD.csv`.
- Explicit ASK runs must pass `legacy_side_omitted=False`, producing `linked_observation_report_ASK_YYYY-MM-DD_to_YYYY-MM-DD.csv`.
- ASK runs in legacy side-omitted naming mode raise `SourceContractError` before row processing.
- Linked rows inherit provider, instrument, quote side, timeframe, source filename, size, and checksum from the side-specific manifest/source assessment path.
- Source-contract mismatch detection now compares manifest/source identity against the supplied `SourceContract`, not the legacy BID constants.
- Side-specific raw file lookup uses `data_manifest.build_source_path(data_dir, day, source_contract)`, so an ASK linked run does not process a legacy BID file with the same date.
- The linked CSV schema was not broadened.

## Compatibility Guarantees

- Legacy BID linked-report naming is unchanged by default.
- Legacy BID linked-report generation remains side-omitted and BID-compatible.
- Existing linked report columns remain unchanged.
- Existing `research_observations.py` quote-side behavior was not modified.
- Existing inherited BID raw files and historical reports were not modified or regenerated.
- Quality tiers remain side-specific for ordinary linked reports; BID file quality does not establish ASK quality.

## Tests Added

`tests/test_linked_observation_report.py` now includes coverage for:

- Legacy BID linked-report path compatibility.
- Explicit BID `SourceContract` linked identity.
- Explicit ASK `SourceContract` linked identity.
- Synthetic ASK linked-report generation with side-specific output naming.
- ASK rejection under ambiguous legacy side-omitted naming.
- Mismatched manifest quote side exclusion.
- Provider, instrument, and timeframe incompatibility exclusion.
- Source identity preservation in linked output.
- Data-quality population separation when an ASK run sees only a legacy BID raw file.

## Tests Run

```text
PYTHONPATH=/workspace/XAUUSD_Lab/tests:/workspace/XAUUSD_Lab python3 -m unittest tests.test_linked_observation_report tests.test_source_contracts
```

Result: `Ran 59 tests ... OK`.

```text
PYTHONPATH=/workspace/XAUUSD_Lab/tests:/workspace/XAUUSD_Lab python3 -m unittest discover -s tests -p 'test_*.py'
```

Result: `Ran 172 tests ... OK (skipped=3)`. The skipped tests are existing matplotlib-dependent chart display tests. No package installation was performed.

## Reviewer Findings

Independent review found no code-level GREEN-scope blocker for linked-observation quote-side awareness.

The reviewer confirmed:

- `SourceContract` propagation is present through filename/path building and row identity.
- ASK linked-report creation reads ASK-named synthetic CSVs, writes ASK-named linked reports, and does not fall back to legacy BID files.
- Manifest quote-side and filename mismatches are excluded as contradictions.
- Legacy BID compatibility is covered.
- Quality-tier behavior remains based on same-side linkage plus manifest/session status, with no evident BID/ASK quality population leakage.
- Existing downstream research observation loading already treats `quote_side` as identity/compatibility.

The only reviewer finding was low-severity documentation drift in the prior `ASK_SIDE_AWARE_INFRASTRUCTURE_SLICE.md` note, which still described linked observations as a future mission. That note was updated to point to this follow-on mission.

## Remaining BID-Only Assumptions

- CLI entry points still use legacy BID defaults; explicit ASK CLI ergonomics are not yet designed.
- `data_quality.py` still exposes legacy source identity constants for callers that have not moved to `SourceContract`.
- `explorer.py`, `chart.py`, and internal diagnostics retain BID-oriented assumptions unless separately refactored.
- `historical_baseline_report.py` has not been audited in this mission for mixed-side input rejection beyond existing `quote_side` columns.
- Downloader URL/config behavior has not been expanded in this mission.

## Unresolved Work Before ASK Acquisition

- Decide whether and how to expose explicit ASK generation through CLIs/config without weakening legacy BID compatibility.
- Audit remaining consumers for mixed-side input handling before using real ASK outputs.
- Add downloader-side URL/path tests for ASK before any substantial ASK acquisition.
- Keep BID and ASK ordinary linked reports separate until a dedicated reconciliation artifact exists.
- Define and test BID/ASK reconciliation separately; do not infer spread or execution realism from side-specific linked reports.

## Recommended Next Bounded Mission

Audit downstream linked-report consumers, especially `historical_baseline_report.py`, `research_observations.py`, `explorer.py`, and `chart.py`, for explicit side-filtering or mixed-side rejection while preserving current legacy BID behavior. Do not download ASK data or implement BID/ASK reconciliation in that mission.
