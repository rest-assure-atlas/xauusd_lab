# Current State

Verified committed milestone: **v0.11**.

XAUUSD Lab is a Python research project for studying XAU/USD, meaning gold priced in US dollars. The current repository focuses on downloading Dukascopy one-minute BID data, exploring daily data, charting candles, applying configurable research-session windows, producing multi-day session research reports, creating data quality manifests for raw CSV provenance and validation, producing a separate non-canonical linked observation report, loading linked reports through an internal quality-aware research access layer, creating a first descriptive historical baseline from an existing linked observation CSV, and producing a narrow structural diagnostic for internal flat zero-volume runs.

## Repository Structure

Current tracked source and documentation files:

```text
AGENTS.md
CHANGELOG.md
README.md
candle_filters.py
chart.py
config.json
data_manifest.py
data_quality.py
data_downloader.py
explorer.py
historical_baseline_report.py
internal_flat_zero_volume_diagnostic.py
linked_observation_report.py
research_observations.py
requirements.txt
session_report.py
session_tools.py
sessions.json
tests/
reports/.gitkeep
docs/
```

Local generated or ignored folders may include:

```text
data_raw/
logs/
reports/
__pycache__/
tests/__pycache__/
```

The local `data_raw/` folder may contain ignored downloaded XAUUSD CSV files on a development machine. Those CSV files are not included in a fresh Git clone, and the automated tests do not require them.

## Python Files

`data_downloader.py` downloads Dukascopy XAU/USD one-minute BID `.bi5` files, decompresses them, converts them into CSV rows, saves them in `data_raw/`, skips existing files, retries temporary failures, and logs failed downloads after all retries fail. It supports command-line date arguments and no-argument config-file mode.

`data_quality.py` provides pure raw CSV validation and classification logic. It records readable file provenance, validates the expected source contract, counts row-level defects, checks internal timestamp gaps and UTC day-boundary coverage, reuses shared edge-placeholder filtering, and returns deterministic manifest fields without modifying raw files.

`data_manifest.py` creates one data quality and provenance row per requested calendar date. It supports inclusive date ranges, optional `--data-dir`, deterministic output under `reports/`, and terminal summaries whose file-status and quality-status counts reconcile to the requested date count.

`linked_observation_report.py` creates one non-canonical provenance-linked observation row per requested calendar date. It reads each expected raw file into verified bytes, runs the existing manifest assessment and existing session-calculation logic from those same bytes, re-checks source identity after processing, and writes a separate linked report under `reports/` without changing the v0.10 session-report or v0.11 manifest schemas.

`research_observations.py` loads existing linked observation report CSVs through
`research_observation_contract_v1`. It validates linked schema version and
contract compatibility, preserves original row strings and source report path
provenance, keeps blank values unavailable, provides named quality-tier
populations, and supports compatible multi-month loading without reading raw
data, generating outputs, or changing producer schemas.

`historical_baseline_report.py` reads one existing linked observation report CSV and writes a descriptive baseline report under `reports/`. It reports coverage, numeric availability, and daily/Tokyo/London/New York range summaries without reading raw data, regenerating producer outputs, or making strategy, prediction, execution, or profitability claims.

`internal_flat_zero_volume_diagnostic.py` reads one existing data quality manifest, one existing linked observation report, and corresponding raw CSV files to write one structural diagnostic row per internal flat zero-volume run. It locates run start/end timestamps, counts run rows, counts Tokyo/London/New York session overlaps, counts rows outside configured sessions, and copies linked daily/session range context without changing raw data, filtering behaviour, warning policy, existing schemas, or historical-baseline behaviour.

`explorer.py` loads one daily CSV from `data_raw/` and prints daily statistics. With `--sessions`, it also prints Tokyo, London, and New York research-session statistics. It uses active candles only, after excluding leading and trailing inactive placeholder rows.

`chart.py` loads one daily CSV from `data_raw/` and displays a candlestick chart. It supports light mode, `--dark`, `--sessions`, hover OHLC labels, crosshair lines, active-time x-axis limits, and candle-based y-axis scaling.

`candle_filters.py` provides shared logic for detecting flat zero-volume placeholder candles and removing only contiguous inactive placeholder rows at the beginning or end of a candle list.

`session_tools.py` loads session definitions from `sessions.json`, converts local session windows to UTC with `zoneinfo`, selects candles using start-inclusive and end-exclusive windows, and calculates session statistics.

`session_report.py` processes an inclusive date range of downloaded daily CSV files and writes one research-ready CSV row per requested date into `reports/`.

## JSON Configuration

`config.json` controls the downloader's no-argument mode:

```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "symbol": "XAUUSD",
  "price_side": "BID",
  "timeframe": "min_1"
}
```

`sessions.json` defines configurable research-session windows. Current defaults are:

- Tokyo: `Asia/Tokyo`, 09:00-18:00 local time
- London: `Europe/London`, 08:00-17:00 local time
- New York: `America/New_York`, 08:00-17:00 local time

These local times are converted to UTC for the selected date using Python's `zoneinfo` support.

## Supported Commands

Download using `config.json`:

```powershell
python data_downloader.py
```

Download one day:

```powershell
python data_downloader.py 2024-01-02
```

Download a date range, including both dates:

```powershell
python data_downloader.py 2024-01-02 2024-01-31
```

Explore one day:

```powershell
python explorer.py 2024-01-26
```

Explore one day with session statistics:

```powershell
python explorer.py 2024-01-26 --sessions
```

Chart one day:

```powershell
python chart.py 2024-01-26
```

Chart one day in dark mode:

```powershell
python chart.py 2024-01-26 --dark
```

Chart one day with research-session overlays:

```powershell
python chart.py 2024-01-26 --sessions
```

Chart one day with dark mode and research-session overlays:

```powershell
python chart.py 2024-01-26 --dark --sessions
```

Create a multi-day session report:

```powershell
python session_report.py 2024-01-01 2024-01-31
```

Create a data quality and provenance manifest:

```powershell
python data_manifest.py 2024-01-01 2024-01-31
```

Create a manifest from an explicit raw data folder:

```powershell
python data_manifest.py 2024-01-01 2024-01-31 --data-dir data_raw
```

Create a provenance-linked daily/session observation report:

```powershell
python linked_observation_report.py 2024-01-01 2024-01-31
```

Create a linked report from an explicit raw data folder:

```powershell
python linked_observation_report.py 2024-01-01 2024-01-31 --data-dir data_raw
```

Create a descriptive historical baseline from one existing linked report:

```powershell
python historical_baseline_report.py reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
```

Create an internal flat zero-volume diagnostic from existing manifest, linked,
and raw CSV files:

```powershell
python internal_flat_zero_volume_diagnostic.py reports/data_manifest_2024-01-01_to_2024-01-31.csv reports/linked_observation_report_2024-01-01_to_2024-01-31.csv --data-dir data_raw
```

Run the full automated test suite:

```powershell
python -m unittest discover -s tests
```

## Dependencies

External dependencies from `requirements.txt`:

- `matplotlib>=3.8,<4`
- `tzdata>=2024.1`

`matplotlib` is used by `chart.py`. `tzdata` provides IANA timezone data on Windows for `zoneinfo`.

## Data, Logs, Reports, And Tests

Raw downloaded CSV files are saved in `data_raw/` with filenames like:

```text
data_raw/XAUUSD_2024-01-26_1min_BID_UTC.csv
```

Raw CSV files are source records. They are not edited by analysis, charting, or reporting tools.

Downloader failures are logged to:

```text
logs/failed_downloads.txt
```

Generated reports are saved in `reports/` with filenames like:

```text
reports/session_report_2024-01-01_to_2024-01-31.csv
reports/data_manifest_2024-01-01_to_2024-01-31.csv
reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
reports/historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv
reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv
```

`reports/.gitkeep` keeps the report folder present in Git. Generated report CSV files are ignored.

Tests live in `tests/`. The automated tests use deterministic synthetic CSV fixtures created in temporary folders, so the suite does not require downloaded raw CSV files in `data_raw/`.

## Git Treatment Of Generated Files

`.gitignore` ignores:

- `data_raw/*.csv`
- `logs/`
- `reports/*`, except `reports/.gitkeep`
- `__pycache__/`
- `*.pyc`

Source code, tests, documentation, JSON configuration, and `requirements.txt` are not ignored.

## Automated Test Status

The current automated test suite contains 152 tests and currently completes
successfully with:

```powershell
python -m unittest discover -s tests
```

In the bundled Codex runtime used during April validation, Matplotlib was not
available. The latest environment-specific result was:

```text
Bundled Codex runtime:
152 tests run
149 passed
3 skipped
0 failures
0 errors
Runtime: 8.647 seconds
Matplotlib unavailable in that runtime
```

The latest completed application milestone is v0.11.

## Recent Manually Verified Behaviour

The January 2024 session report command has been verified locally:

```powershell
python session_report.py 2024-01-01 2024-01-31
```

Observed summary:

```text
Session report complete.
Requested dates: 31
Completed dates: 27
Missing files: 0
No active candle dates: 4
Failed dates: 0
Output path: C:\Users\Lenovo\Documents\XAUUSD_Lab\reports\session_report_2024-01-01_to_2024-01-31.csv
```

The January 2024 data manifest command has also been verified locally:

```powershell
python data_manifest.py 2024-01-01 2024-01-31 --data-dir data_raw
```

Observed summary:

```text
Data manifest complete.
Requested dates: 31
Processed files: 27
Missing files: 0
Empty files: 0
Parse failures: 0
No-active-candle files: 4
Valid dates: 9
Warning dates: 18
Invalid dates: 0
Not-assessed dates: 4
Output path: C:\Users\Lenovo\Documents\XAUUSD_Lab\reports\data_manifest_2024-01-01_to_2024-01-31.csv
```

Manual January 2024 manifest observations:

- Saturdays 2024-01-06, 2024-01-13, 2024-01-20, and 2024-01-27 were `no_active_candles` and `not_assessed`, each with 1440 leading inactive rows.
- Fridays 2024-01-05, 2024-01-12, 2024-01-19, and 2024-01-26 were `processed` and `valid`, each with 120 trailing inactive rows and active data through 21:59 UTC.
- Sundays 2024-01-07, 2024-01-14, 2024-01-21, and 2024-01-28 were `processed` and `valid`, each with 1380 leading inactive rows and active data from 23:00 UTC.
- 2024-01-01 was `processed` and `valid`, with 1380 leading inactive rows and active data from 23:00 UTC.
- 2024-01-15 was `processed` with `warning` quality because of `INTERNAL_FLAT_ZERO_VOLUME`.
- The 18 warning dates in the January sample were warnings for `INTERNAL_FLAT_ZERO_VOLUME`.
- The January sample had complete 00:00 through 23:59 UTC timestamp coverage for every existing raw file, so no rows received `PARTIAL_DAY_COVERAGE`.

These are structural observations only. They do not prove market closure, provider failure, or tradability.

## February 2024 Pipeline Validation

The February 2024 single-month pipeline has been manually validated for the
inclusive date range 2024-02-01 through 2024-02-29.

Verified February 2024 counts:

```text
Requested dates: 29
Raw files: 29
Manifest processed: 25
Manifest no_active_candles: 4
Manifest valid: 5
Manifest warning: 20
Manifest not_assessed: 4

Linked strict_valid: 5
Linked warning_review: 20
Linked calendar_only: 4
Linked excluded/unusable: 0

Diagnostic warning dates: 20
Diagnostic runs: 29
Diagnostic run rows: 1,192
```

All 29 February raw CSV files were present with 1,440 data rows each. February
29 was present, processed, and classified as `warning_review` with
`INTERNAL_FLAT_ZERO_VOLUME`.

The standalone February manifest, linked observation report, historical
baseline, internal-flat diagnostic, and raw-source checksums reconciled. The
baseline kept `strict_valid` and `warning_review` numeric summaries separate,
and `calendar_only` values remained unavailable rather than being treated as
zero.

Seven February dates contained multiple separate diagnostic runs:

```text
2024-02-06: 3 runs
2024-02-12: 2 runs
2024-02-14: 2 runs
2024-02-18: 2 runs
2024-02-19: 2 runs
2024-02-27: 2 runs
2024-02-29: 3 runs
```

The February diagnostic command was accidentally executed twice. Verification
showed deterministic replacement of the same output path, identical content,
no appended rows, no duplicate report artifact, and no raw-file mutation.

No saved January before-hash snapshot was available for direct January
before/after proof. Implementation inspection showed the February commands were
date-bounded to February output paths and February raw filenames, but that is
not equivalent to direct January hash evidence.

February is one additional bounded descriptive month only. January and February
must not be treated as establishing normal XAU/USD behaviour. `strict_valid`
and `warning_review` observations must remain separate. The February outputs do
not support strategy, support/resistance, signal, prediction, edge,
profitability, execution, or causal conclusions. `INTERNAL_FLAT_ZERO_VOLUME`
remains an unresolved warning and has not been proven harmless or assigned a
market or provider cause.

## March 2024 Pipeline Validation

The March 2024 single-month pipeline has been manually validated for the
inclusive date range 2024-03-01 through 2024-03-31.

Verified March 2024 counts:

```text
Requested dates: 31
Raw files: 31
Manifest processed: 25
Manifest no_active_candles: 6
Manifest valid: 9
Manifest warning: 16
Manifest not_assessed: 6

Linked strict_valid: 9
Linked warning_review: 16
Linked calendar_only: 6
Linked excluded/unusable: 0

Diagnostic warning dates: 16
Diagnostic runs: 23
Diagnostic run rows: 909
```

All 31 March raw CSV files were present exactly once with the expected
filenames, header, 1,440 data rows, and 97,962 bytes per file. The final raw
inventory covered March 1 through March 31 with no duplicate, temporary,
partial, or unexpected March files. A first downloader attempt logged a
2024-03-09 network timeout; a bounded retry saved the March 9 raw file with
1,440 rows, and the retry reported 31 successful or skipped days and 0 failed
days. The historical failure-log entry was left unchanged as generated evidence.

The March manifest wrote 31 rows with schema version `1` and validation rule
`raw_data_quality_v1`. File-status counts were 25 `processed` and 6
`no_active_candles`; quality-status counts were 9 `valid`, 16 `warning`, and 6
`not_assessed`. The reason distribution was 16
`INTERNAL_FLAT_ZERO_VOLUME`, 6 `NO_ACTIVE_CANDLES`, and 9 blank reason rows.
March 31 was present, processed, valid, and linked as `strict_valid`.

The March linked observation report wrote 31 rows with linked schema version
`1`, active-filter rule `edge_flat_zero_volume_v1`, session-definition checksum
`30f6099c9cd51c206e03ba3ac96f43287ec2a62528d97de591118e73a6ec681a`, and
software revision `a6233fa3375be6871ee225c3382e0ba3c02d9a1d`. Linkage-status
counts were 25 `linked` and 6 `calendar_only`; linkage reasons were blank for
all rows. Raw file sizes and SHA-256 checksums matched between the raw files,
the standalone manifest, and the linked report. Calendar-only range values
remained unavailable rather than being treated as zero.

The March historical baseline used
`linked_observation_report_2024-03-01_to_2024-03-31.csv` as its source and read
31 linked rows. Coverage counts reconciled with the linked report, and
`strict_valid` and `warning_review` numeric summaries remained separate.

March descriptive range summaries:

```text
Group           Field            Count  Min     Median  Mean    Max
strict_valid    daily_range      9      3.710   12.420  19.669  49.300
strict_valid    tokyo_range      4      9.490   11.575  14.033  23.490
strict_valid    london_range     4      16.180  26.575  28.070  42.950
strict_valid    new_york_range   4      12.150  28.461  27.948  42.720
warning_review  daily_range      16     14.230  26.350  30.299  73.400
warning_review  tokyo_range      16     4.940   11.569  11.752  19.910
warning_review  london_range     16     10.900  20.165  22.967  45.421
warning_review  new_york_range   16     8.990   18.942  22.673  42.471
```

The March internal-flat diagnostic was required because the manifest contained
`INTERNAL_FLAT_ZERO_VOLUME`. Diagnostic affected dates matched the 16 manifest
warning dates exactly:

```text
2024-03-04
2024-03-05
2024-03-06
2024-03-07
2024-03-08
2024-03-11
2024-03-12
2024-03-13
2024-03-14
2024-03-18
2024-03-19
2024-03-20
2024-03-21
2024-03-25
2024-03-26
2024-03-27
```

The diagnostic produced 23 runs and 909 run rows. Run lengths were 7 one-row
runs, 1 two-row run, and 15 sixty-row runs. Six dates had multiple runs:

```text
2024-03-06: 2 runs
2024-03-11: 2 runs
2024-03-14: 2 runs
2024-03-19: 2 runs
2024-03-21: 3 runs
2024-03-26: 2 runs
```

Run starts were distributed across UTC hours 03, 04, 20, 21, 22, and 23. The
earliest run start was 2024-03-04 22:00:00 and the latest run start was
2024-03-27 21:00:00. Diagnostic overlap totals were 3 Tokyo rows, 0 London
rows, 1 New York row, and 905 outside-configured-session rows; these reconciled
to 909 total run rows. A raw-file reconstruction matched the diagnostic rows,
including run boundaries, run lengths, and configured-session overlap counts.

Before March generation, a deterministic hash snapshot was stored outside the
repository at
`C:\Users\Lenovo\AppData\Local\Temp\xauusd_lab_jan_feb_hashes_before_march_20260726_124831.csv`.
After March generation, the same January and February inventory was recalculated
and all 69 files matched exactly: 31 January raw files, 29 February raw files, 5
January report CSVs, and 4 February report CSVs. No January or February file
changed, disappeared, or appeared unexpectedly.

January, February, and March use compatible manifest, linked, baseline,
diagnostic, active-filter, validation-rule, and session-definition contracts.
The linked-report software revisions differ by month, but the compared schema
and rule identities remain compatible.

Three-month coverage checkpoint:

```text
Month  Days  Raw  Processed  No-active  Valid  Warning  Not assessed  Strict  Warning review  Calendar only  Excluded  Warning dates  Runs  Run rows
Jan    31    31   27         4          9      18       4             9       18              4              0         18/31          20    1,232
Feb    29    29   25         4          5      20       4             5       20              4              0         20/29          29    1,192
Mar    31    31   25         6          9      16       6             9       16              6              0         16/31          23    909
```

Across the three validated months, `INTERNAL_FLAT_ZERO_VOLUME` recurred as the
only manifest warning reason: 18 January warning dates, 20 February warning
dates, and 16 March warning dates. Warning-date proportions were 18/31
(58.1%), 20/29 (69.0%), and 16/31 (51.6%). Runs per warning date were 20/18
(1.11), 29/20 (1.45), and 23/16 (1.44), so fragmentation increased from
January to February and stayed similar in March rather than moving in one
steady direction.

The recurring descriptive pattern is broad warning-review coverage, many runs
near 60 rows, repeated late-UTC timing, and most diagnostic rows outside the
configured Tokyo/London/New York windows. February and March both showed more
multi-run dates and more one-row fragments than January. The 210-row diagnostic
outlier appeared in January and February but not March. March added a two-row
run and had materially fewer total diagnostic run rows than January or February.

After March, the next bounded milestone should be a focused
`INTERNAL_FLAT_ZERO_VOLUME` warning-treatment specification before broader
monthly expansion. This is not a final treatment rule and does not assign a
reason to the warning. The specification should preserve uncertainty, keep
`strict_valid` and `warning_review` observations separate, and define how future
descriptive research may include, exclude, label, or bracket warning-review
observations using the already generated January through March evidence.

March remains one additional bounded descriptive month only. January,
February, and March must not be treated as a universal market baseline.

## April 2024 Pipeline Validation

The April 2024 single-month pipeline has been manually validated for Dukascopy
XAUUSD one-minute BID data in UTC, covering 2024-04-01 through 2024-04-30.
This was a pipeline-validation and data/provenance-readiness milestone only,
not a market finding. `warning_treatment_v1` and
`research_observation_contract_v1` were preserved.

Acquisition completed with 30 local ignored April raw CSV files, one for each
requested date. Each file contained 1,440 rows and was 97,962 bytes. Failed
dates were 0. No April failure entry was added to the existing downloader
failure log, although the downloader touched that log's timestamp during
current initialisation behaviour. The timestamp touch alone is not evidence of
an April failure or raw-data change. Raw and generated CSV files remain ignored
local artifacts, not committed repository content.

A pre/post SHA-256 protection check covered 91 January-March raw CSVs and 15
January-March generated reports. It found no changed, missing, or unexpectedly
appearing protected files, and the temporary snapshot file was stored outside
the repository and removed afterward.

The existing pipeline successfully produced the April manifest, session report,
linked observation report, historical baseline, and internal flat zero-volume
diagnostic. The linked report retained one row per requested April date, zero
duplicate dates, zero linked/session calculation mismatches, and the
Dukascopy/XAUUSD/BID/1min provider contract. No source, schema, configuration,
dependency, or quality-treatment change was required.

Linked quality tiers were `8 strict_valid`, `18 warning_review`,
`4 calendar_only`, and `0 excluded_unusable`. `INTERNAL_FLAT_ZERO_VOLUME`
affected 18 warning-review observations, and four observations were
`calendar_only` because they had no active candles. The warning cause remains
unresolved; no harmlessness, severity, provider-outage, closure, corruption,
or causal interpretation was made. The session report is not independently
quality-tier aware and was not used alone for a research conclusion.

April alone loaded successfully through
`research_observations.load_linked_reports(...)`: chronological ordering and
contract validation passed, no duplicate identity was detected, and
calendar-only `daily_range` remained unavailable. January through April loaded
successfully together with 121 observations: `31 strict_valid`,
`72 warning_review`, `18 calendar_only`, and `0 excluded_unusable`.
Chronological and compatibility validation passed, and no loader expansion was
required.

The April historical baseline command was rerun as the bounded determinism
check and produced identical SHA-256 content before and after. This
determinism check applied only to that baseline output, not every producer.

The April validation run reported `152 run`, `149 passed`, `3 skipped`, `0
failures`, `0 errors`, and `8.647 seconds`. The three skips were
Matplotlib-dependent chart-display tests in that runtime and are not counted
as passed tests.

April is data/provenance-ready for a later bounded descriptive research
extension under `warning_treatment_v1`, subject to its 18 warning-review
observations, four calendar-only observations, and separate Director approval
of any research extension. No April research extension has yet been approved,
and the next research question remains unselected.

## warning_treatment_v1 Research Contract

`warning_treatment_v1` is the approved research-treatment contract for
`warning_review` observations after the January through March 2024 validation
evidence. It is a documentation and research-governance decision only. It does
not change raw data, filtering, manifest classifications, quality tiers, linked
schemas, baseline calculations, diagnostics, session definitions, or current
source-code behaviour.

Primary or headline numeric results must use `strict_valid` observations only
and must report the strict-valid observation count for every numeric result.
Small strict-valid samples must be reported honestly and must not be used as a
reason to weaken the quality rule.

`warning_review` observations may be used only in separately labelled
descriptive analysis or `warning-review sensitivity analysis`. Warning-review
results must remain separate from strict-valid results, report available
observation counts and warning-reason counts, remain traceable to the
provenance-linked source report, and include diagnostic context when a diagnostic
exists.

`strict_valid` and `warning_review` observations must not be pooled into primary
or headline research results. Combined counts may be shown only as clearly
labelled coverage, not as a quality-homogeneous research sample. `calendar_only`
and `excluded_unusable` observations remain coverage records for the current
daily/session range research. Blank or unavailable numeric values remain
unavailable and are not converted to zero.

The treatment is observation-level in this version. A daily observation
classified `warning_review` remains warning-review as a whole. Diagnostic
session overlap can be reported descriptively, but it does not prove that a
non-overlapped field is unaffected, that an overlapped field is invalid, that a
run outside configured sessions is irrelevant to daily values, or that any field
is harmless or reliable. Field-level eligibility and diagnostic thresholds are
postponed until a separately approved specification.

`historical_baseline_report.py` already follows the core strict-versus-warning
separation. The provenance-linked report preserves quality tier and warning
reason fields, and the diagnostic supplies descriptive warning context.
`session_report.py`, `explorer.py`, and `chart.py` use edge filtering but are
not independently quality-tier-aware, so their outputs must not be presented as
quality-screened research evidence unless linked back to the applicable manifest
or provenance-linked assessment.

`warning_treatment_v1` does not establish the cause of
`INTERNAL_FLAT_ZERO_VOLUME`, harmlessness, expected market behaviour, market
closure, provider outage, corruption, universal XAU/USD behaviour, statistical
significance, support or resistance, a setup or signal, prediction, trading
edge, profitability, or execution realism.

The first six bounded descriptive questions under `warning_treatment_v1` are
complete and recorded in [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md). For
January through April 2024 Dukascopy XAUUSD one-minute BID linked observations,
the extended daily-range finding showed higher warning-review sensitivity
median and mean values than strict-valid median and mean values in each
validated month. April strict-valid median, mean, and maximum were `25.977`,
`36.707`, and `97.630`; April warning-review sensitivity median and mean were
`40.305` and `40.896`. April extended the finding without material revision,
but broader daily-range distribution comparisons remain statistic-specific:
monthly maxima were mixed between quality tiers. No loader expansion was
required for that extension. See [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md)
for detailed evidence.

The daily-extrema UTC-hour frequency finding now covers January-April.
January-March strict-valid recorded daily-high modal hour was `23` in each
month, but April adds a material qualification with high modal hour `22`
containing `4/8` observations. April strict-valid recorded daily-low modal hour
was also `22` with `4/8` observations, matching March but not January or
February. April warning-review sensitivity had high modal hour `22` with
`4/18` observations and low modal hour `01` with `5/18` observations; the
warning-review hour distributions were more dispersed. The daily-extrema
ordering finding now covers January-April. January-March strict-valid
observations had a `low_before_high` majority in each month, but April reversed
that balance with `6/8` `high_before_low`. April warning-review sensitivity had
`7/18` `high_before_low` and `11/18` `low_before_high`. April therefore adds a
material qualification; no eligible January-April observation had both extrema
in the same recorded minute, and April repeated-extremum handling changed no
category. Repeated-extremum sensitivity changed no April UTC-hour category. No
loader expansion was required. All three extrema-timing findings now extend
through April. The next proposed phase is May-December 2024 batch acquisition
with monthly validation, subject to separate Director approval. See
[RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md) for detailed evidence.

The daily close-location finding showed that strict-valid closes were more
often in the lower half of the recorded daily range in January and more often
in the upper half in February and March. The separately labelled warning-review
sensitivity population had the same monthly lower-half or upper-half category
majority in each corresponding month, though medians and category percentages
differed by month. The daily open-to-close finding showed that January and
February strict-valid observations had more below-open dates, while March
strict-valid observations had more above-open dates. The warning-review
sensitivity population had more above-open dates in all three months, and the
quality-tier comparison was mixed by month. Open-to-close classification is
distinct from close location within the daily range. The elapsed-time
between-daily-extrema finding now covers January-April. April strict-valid
minimum, median, mean, and maximum absolute gaps were `1`, `129`, `283`, and
`940` minutes; April warning-review sensitivity values were `53`, `572`,
`622.556`, and `1,262` minutes. Warning-review medians were higher than
strict-valid medians in all four months, and April extended the finding without
material revision. The sole April repeated-extremum observation changed no gap
statistic. This elapsed-separation result is distinct from extrema ordering and
extrema clock-hour frequency. The loader-backed executions using
`research_observation_contract_v1` succeeded without loader expansion. No
production code, schema, filtering, classification, raw data, report artifact,
dependency, loader, or producer change was made. No pooled
strict-valid/warning-review result was produced. The daily-range,
daily-extrema ordering, and elapsed-extrema separation findings currently
extend through April. The next research task has not yet been selected.

## research_observation_contract_v1 Linked-Report Loader

`research_observations.py` now provides the internal linked-report research
loader for `research_observation_contract_v1`.

The loader reads existing schema-v1 linked observation report CSVs and validates
the proposed research observation unit identity, linked schema version, source
contract, manifest schema, validation-rule identity, active-filter identity, and
session-definition checksum. It rejects duplicate identities within or across
loaded reports and orders observations chronologically after validation.

The public access functions are `load_linked_report(path)` and
`load_linked_reports(paths)`. They return a small collection with generic
iteration, observation count, contract metadata, source report paths, exact
population counts, and named selectors for `strict_valid`, `warning_review`,
`calendar_only`, `excluded_unusable`, and coverage-only observations.

The loader preserves original CSV field values as strings, preserves the source
linked-report path and row `software_revision` as provenance, keeps blank values
unavailable, and does not treat quality tier as field-level eligibility.
Compatible mixed software revisions are allowed when the schema, source,
validation, filtering, and session-definition contracts match.

Manifest attachment, diagnostic attachment, baseline integration, raw-data
access, report generation, report regeneration, research calculations, charts,
and user-interface work remain deferred. Existing producers and report schemas
are unchanged, and no analysis has been implied to have migrated to the loader.

## v0.11 Data Quality Manifest Behaviour

`data_manifest.py` creates one CSV row per requested calendar date.

Each row includes:

- source contract metadata and expected filename
- readable source file size and SHA-256 checksum
- file status and quality status
- stable machine-readable reason codes
- row counts, edge inactive counts, internal inactive counts, timestamp continuity metrics, day-boundary coverage metrics, and row-level defect counts

File statuses are:

- `missing_file`
- `empty_file`
- `parse_failed`
- `no_active_candles`
- `processed`

Quality statuses are:

- `valid`
- `warning`
- `invalid`
- `not_assessed`

Manifest timestamps must match `YYYY-MM-DD HH:MM:SS` exactly. Fractional-second timestamp text is invalid, while non-zero whole seconds are parseable but counted as off-minute timestamps. `first_timestamp_utc` and `last_timestamp_utc` are chronological minimum and maximum parsed timestamps when invalid timestamps do not prevent reliable bounds.

See [DATA_QUALITY_MANIFEST.md](DATA_QUALITY_MANIFEST.md) for the full contract.

## v0.10 Session Report Behaviour

`session_report.py` creates one CSV row per requested calendar date.

Each row includes:

- date, weekday, and status
- daily OHLC, range, and high/low times
- total CSV row count
- active candle count
- inactive placeholder count
- Tokyo, London, and New York session OHLC, range, high/low times, and active candle count

Statuses mean:

- `complete`: the daily CSV exists, active candles were found, and daily/session statistics were calculated.
- `missing_file`: the expected daily CSV file was not found.
- `no_active_candles`: the daily CSV exists, but no active candles remained after removing leading/trailing inactive placeholders.
- `failed`: the file existed but processing failed because of a handled read, parse, data, or file error.

Verified January 2024 result:

- 31 requested dates
- 27 complete dates
- 4 no-active-candle Saturdays
- 0 missing files
- 0 failed dates

## Linked Observation Report Behaviour

`linked_observation_report.py` creates one separate non-canonical linked row per
requested calendar date. It is a provenance-linking and reconciliation artifact,
not a replacement for the v0.10 session report or the v0.11 data quality
manifest.

The physical linkage inside the controlled operation is the requested `date`.
The logical observation identity is:

```text
date + provider + instrument + quote_side + timeframe
```

Source filename, file size, checksum, rule identities, software revision, and
linked schema version are provenance and validation fields rather than join
keys.

For each existing raw file, the linked report:

1. derives the expected raw filename;
2. reads the raw file into bytes;
3. records file size and SHA-256 checksum for those bytes;
4. runs the existing manifest assessment from those same bytes;
5. runs the existing session-calculation logic from those same bytes;
6. re-reads the source identity afterward and flags source mutation.

The tool does not accept arbitrary pre-existing session-report or manifest CSVs
as provenance-linked evidence.

Quality tiers are:

- `strict_valid`: session status is `complete`, manifest file status is
  `processed`, manifest quality status is `valid`, and no linkage contradiction
  exists.
- `warning_review`: session status is `complete`, manifest file status is
  `processed`, manifest quality status is `warning`, and no linkage
  contradiction exists. Individual manifest reason codes are retained and the
  row is excluded from the strict-valid subset by default.
- `excluded_unusable`: invalid quality states, processing failures,
  source-contract failures, source identity changes, or linkage contradictions.
- `calendar_only`: missing-file or no-active-candle calendar rows with no
  linkage contradiction.

Linked schema version `1` uses this exact column order:

```text
linked_schema_version
date
weekday
provider
instrument
quote_side
timeframe
source_filename
source_file_size_bytes
source_checksum_algorithm
source_checksum
manifest_schema_version
validation_rule_version
active_filter_rule_identity
session_definition_checksum
software_revision
session_status
manifest_file_status
manifest_quality_status
manifest_quality_reasons
linkage_status
linkage_reasons
quality_tier
manifest_total_row_count
manifest_active_row_count
session_total_csv_rows
session_active_candle_count
session_inactive_placeholder_count
daily_open
daily_high
daily_low
daily_close
daily_range
time_of_daily_high_utc
time_of_daily_low_utc
tokyo_open
tokyo_high
tokyo_low
tokyo_close
tokyo_range
tokyo_time_of_high_utc
tokyo_time_of_low_utc
tokyo_active_candle_count
london_open
london_high
london_low
london_close
london_range
london_time_of_high_utc
london_time_of_low_utc
london_active_candle_count
new_york_open
new_york_high
new_york_low
new_york_close
new_york_range
new_york_time_of_high_utc
new_york_time_of_low_utc
new_york_active_candle_count
```

Linked status values are:

- `linked`
- `calendar_only`
- `contradiction`
- `source_changed`
- `source_unavailable`

Linkage reason codes are machine-readable and separated by semicolons:

```text
DATE_COVERAGE_MISMATCH
DUPLICATE_DATE
PROVIDER_MISMATCH
INSTRUMENT_MISMATCH
QUOTE_SIDE_MISMATCH
TIMEFRAME_MISMATCH
SOURCE_FILENAME_MISMATCH
SOURCE_SIZE_MISMATCH
SOURCE_CHECKSUM_MISMATCH
SOURCE_CHECKSUM_UNAVAILABLE
SOURCE_IDENTITY_CHANGED
ROW_COUNT_MISMATCH
ACTIVE_COUNT_MISMATCH
STATUS_DISAGREEMENT
SESSION_VALUES_WITH_MANIFEST_FAILURE
MANIFEST_PROCESSED_SESSION_FAILED
```

Rule and run identity fields are:

- `manifest_schema_version`: existing manifest schema version.
- `validation_rule_version`: existing manifest validation-rule version.
- `active_filter_rule_identity`: current edge flat zero-volume active-filter
  identity, without changing filter behaviour.
- `session_definition_checksum`: deterministic SHA-256 checksum of the parsed
  session definitions.
- `software_revision`: full Git commit when the working tree is clean; the same
  commit with `-dirty` when tracked changes or non-ignored untracked files are
  present; otherwise `unknown`. The `-dirty` suffix identifies the base commit
  and warns that uncommitted changes were present. It does not uniquely identify
  the exact uncommitted code state.
- `linked_schema_version`: linked report schema version.

The implementation validates the current expected session names, generated
prefixes, calculation fields, and column order. A separate session-report schema
version and stable session identifiers remain deferred.

## Historical Baseline Report Behaviour

`historical_baseline_report.py` reads one existing linked observation report CSV
path directly:

```powershell
python historical_baseline_report.py reports/linked_observation_report_2024-01-01_to_2024-01-31.csv
```

For that command, the output path is:

```text
reports/historical_baseline_linked_observation_report_2024-01-01_to_2024-01-31.csv
```

The tool validates the linked schema version, required baseline columns,
duplicate dates, `quality_tier`, and required identity/status fields before
building metrics. It does not read raw data, regenerate linked reports,
regenerate session reports, regenerate manifests, download data, or mutate
existing source files.

Baseline schema version `1` uses this exact column order:

```text
baseline_schema_version
source_report
metric_section
metric_name
observation_group
reason_code
field_name
count
min
median
mean
max
notes
```

The baseline report includes:

- coverage counts by quality tier, linkage status, session status, manifest file
  status, manifest quality status, manifest quality reasons, and linkage
  reasons;
- numeric availability counts for `daily_range`, `tokyo_range`, `london_range`,
  and `new_york_range`;
- descriptive range summaries for `daily_range`, `tokyo_range`, `london_range`,
  and `new_york_range`.

Strict-valid observations are the headline numeric baseline. Warning-review
observations are reported separately and split by manifest warning reason code
where available. Calendar-only and excluded/unusable rows appear in coverage and
availability counts but are excluded from numeric range summaries. Blank session
range values are unavailable values, not zeroes.

The baseline is descriptive only. It is not a strategy, signal generator,
backtest, prediction system, profitability analysis, support/resistance tool, or
execution model.

## Internal Flat Zero-Volume Diagnostic Behaviour

`internal_flat_zero_volume_diagnostic.py` reads one existing data quality
manifest path, one existing linked observation report path, and raw CSV files
from a selected data directory:

```powershell
python internal_flat_zero_volume_diagnostic.py reports/data_manifest_2024-01-01_to_2024-01-31.csv reports/linked_observation_report_2024-01-01_to_2024-01-31.csv --data-dir data_raw
```

For that command, the output path is:

```text
reports/internal_flat_zero_volume_diagnostic_2024-01-01_to_2024-01-31.csv
```

The tool validates that the manifest and linked report cover the same dates in
the same order. It reads raw CSV files only for manifest rows whose
`quality_reasons` include `INTERNAL_FLAT_ZERO_VOLUME`.

In current software terms, an internal flat zero-volume row is a numeric-valid
row where `volume == 0` and `open == high == low == close`, after contiguous
leading and trailing flat zero-volume placeholders have been excluded by the
active-candle filter. The diagnostic reconstructs contiguous internal runs,
checks that detected run rows reconcile with the manifest
`internal_inactive_row_count`, and writes one row per run.

Diagnostic schema version `1` uses this exact column order:

```text
diagnostic_schema_version
date
weekday
source_filename
manifest_file_status
manifest_quality_status
manifest_quality_reasons
total_row_count
active_row_count
leading_inactive_row_count
trailing_inactive_row_count
internal_inactive_row_count
run_number
run_start_utc
run_end_utc
run_row_count
tokyo_overlap_rows
london_overlap_rows
new_york_overlap_rows
outside_configured_session_rows
linked_quality_tier
linked_session_status
daily_range
tokyo_range
london_range
new_york_range
tokyo_active_candle_count
london_active_candle_count
new_york_active_candle_count
```

The diagnostic does not regenerate manifests, linked reports, session reports,
baselines, charts, downloads, or raw data. It does not infer market closure,
provider outage, corruption, harmlessness, or market meaning. Filtering
behaviour, warning policy, manifest schema, linked-report schema, and
historical-baseline behaviour are unchanged.

## Known Limitations

- The current research data is BID-only and does not include ASK prices or spread.
- The project does not yet model commission, slippage, latency, or execution assumptions.
- There is no backtesting engine yet.
- There is no multi-year downloader orchestration yet.
- `explorer.py`, `chart.py`, and `session_report.py` are currently built around XAUUSD one-minute BID CSV filenames.
- `data_manifest.py` is also built around the current XAUUSD one-minute BID source contract.
- `linked_observation_report.py` is also built around the current XAUUSD one-minute BID source contract and current Tokyo, London, and New York session column contract.
- `historical_baseline_report.py` is built around linked observation report
  schema version `1` and the current daily/Tokyo/London/New York range fields.
- `internal_flat_zero_volume_diagnostic.py` is built around the current manifest,
  linked-report, raw XAUUSD one-minute BID, and Tokyo/London/New York session
  contracts.
- Generated reports are overwritten when the same date range is run again.
- The data quality manifest is structural. It does not repair data or prove why flat zero-volume runs, missing minutes, or day-boundary gaps occurred.
- The linked observation report is non-canonical and does not repair, interpolate,
  or relabel raw data.
- The historical baseline report is descriptive only and does not classify
  warning reasons as harmless.
- Session windows are configurable research windows, not proof of exchange opening hours.
- The current project is a research platform, not evidence of a profitable trading system.
