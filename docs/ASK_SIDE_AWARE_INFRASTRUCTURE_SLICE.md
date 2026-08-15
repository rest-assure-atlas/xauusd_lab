# ASK Side-Aware Infrastructure Slice

Date: 2026-08-07

Mission: implement the smallest side-aware infrastructure slice required before ASK onboarding, without downloading ASK data, regenerating broad reports, implementing BID/ASK reconciliation, or changing spread methodology.

## Evidence Classification

`confirmed`: the project now has explicit quote-side validation, an immutable minimal `SourceContract`, and side-aware filename/report-name helpers covered by synthetic tests.

`promising`: this slice supports a future ASK provenance implementation path while preserving legacy BID behavior.

`not complete`: ASK data support is not complete. No ASK data was downloaded, no ASK manifest was generated from real data, no BID/ASK reconciliation exists, and spread-aware or execution-realistic testing is not ready.

## Files Changed

- `source_contracts.py`: added supported quote-side validation, immutable `SourceContract`, raw CSV filename helper, and report filename helper.
- `data_manifest.py`: threaded optional `SourceContract` through source filename/path, manifest row metadata, manifest output path, and manifest creation while preserving default BID behavior.
- `session_report.py`: threaded optional `SourceContract` through raw CSV path, report output path, one-day processing, and session-report creation while preserving default BID behavior.
- `tests/test_source_contracts.py`: added focused synthetic coverage for side validation, legacy compatibility, side-aware paths, ASK rejection in legacy naming mode, immutability, and side identity.
- `docs/ASK_SIDE_AWARE_INFRASTRUCTURE_SLICE.md`: this implementation note.

## Behavior Introduced

- Supported quote sides are exactly `BID` and `ASK`.
- Invalid, blank, lowercase, mixed-case, or unknown quote sides are rejected.
- `SourceContract` is frozen and carries only current source identity fields: provider, instrument, quote side, and timeframe.
- Raw CSV filenames are built as `XAUUSD_YYYY-MM-DD_1min_{QUOTE_SIDE}_UTC.csv`.
- Existing legacy BID report names remain side-omitted by default.
- ASK is rejected before row processing when a legacy side-omitted report name would be produced.
- Side-aware report names are available by passing `legacy_side_omitted=False`, for example `data_manifest_ASK_2024-01-01_to_2024-01-31.csv` and `session_report_ASK_2024-01-01_to_2024-01-31.csv`.

## Compatibility Guarantees

- Existing calls to `data_manifest.build_source_filename(day)` still return `XAUUSD_YYYY-MM-DD_1min_BID_UTC.csv`.
- Existing calls to `data_manifest.build_manifest_path(start, end)` still return `data_manifest_YYYY-MM-DD_to_YYYY-MM-DD.csv`.
- Existing calls to `session_report.build_csv_path(day)` still target BID raw filenames.
- Existing calls to `session_report.build_report_path(start, end)` still return `session_report_YYYY-MM-DD_to_YYYY-MM-DD.csv`.
- `research_observations.py` quote-side compatibility behavior was not modified.
- Inherited BID raw files and existing generated BID reports were not altered.

## Tests Added

`tests/test_source_contracts.py` covers:

- BID legacy compatibility.
- Valid BID side.
- Valid ASK side.
- Invalid quote side rejection.
- ASK rejection under legacy side-omitted naming.
- Side-aware BID filename/path generation.
- Side-aware ASK filename/path generation.
- Synthetic ASK manifest creation with ASK output naming and ASK row identity.
- Synthetic ASK session-report creation with ASK output naming.
- `SourceContract` immutability.
- `SourceContract` side identity in manifest rows.

## Tests Run

Initial environment checks:

- `python -m pytest ...` could not run because `python` was not available.
- `python3 -m pytest ...` could not run because `pytest` was not installed. No package installation was performed.
- `python3 -m unittest ...` without the repo test `PYTHONPATH` failed to import existing `fixture_helpers`; this was an invocation issue, not a project regression.

Successful tests:

```text
PYTHONPATH=/workspace/XAUUSD_Lab/tests:/workspace/XAUUSD_Lab python3 -m unittest tests.test_source_contracts tests.test_data_manifest tests.test_session_report tests.test_linked_observation_report tests.test_research_observations
```

Result: `Ran 85 tests ... OK`.

```text
PYTHONPATH=/workspace/XAUUSD_Lab/tests:/workspace/XAUUSD_Lab python3 -m unittest discover -s tests -p 'test_*.py'
```

Result: `Ran 161 tests ... OK (skipped=3)`. The skipped tests were associated with unavailable matplotlib; no package installation was performed.

## Unresolved Work

- Downloader CLI/config behavior is not yet fully side-aware beyond existing config support.
- `data_quality.py` still exposes legacy BID source constants for existing callers.
- `linked_observation_report.py` was out of scope for this infrastructure-slice mission and was later addressed by `ASK_SIDE_AWARE_LINKED_OBSERVATION.md`.
- Existing CLI entry points still use legacy BID defaults; explicit ASK CLI flows are not yet designed.
- Real ASK acquisition has not been attempted.
- ASK manifests/reports from real files have not been generated.
- BID/ASK reconciliation and spread validation are not implemented.
- OHLC spread semantics remain unresolved and should not be inferred.

## Reviewer Findings

Independent review initially recommended revision before approval. The reviewer found that session-report generation was not yet side-aware beyond helper functions, manifest ASK legacy-name rejection happened after row processing, and tests were too helper-level for the claimed slice.

Revisions made after review:

- `session_report.process_one_day()` and `session_report.create_session_report()` now accept a `SourceContract` and side-specific naming flag.
- `data_manifest.create_data_manifest()` validates the output path before row/file assessment, so ASK legacy side-omitted naming is rejected immediately.
- Tests now include synthetic ASK manifest creation and synthetic ASK session-report creation with side-specific output names.
- The unresolved-work section now records that linked observations, explicit CLI flows, real ASK data, and BID/ASK reconciliation remain out of scope.

## Recommended Next Bounded Mission

See `ASK_SIDE_AWARE_LINKED_OBSERVATION.md` for the follow-on linked-observation side-awareness mission. The next bounded mission should audit downstream linked-report consumers for mixed-side rejection or side-filtering while preserving legacy BID behavior. Do not download ASK data or implement BID/ASK reconciliation in that mission.
