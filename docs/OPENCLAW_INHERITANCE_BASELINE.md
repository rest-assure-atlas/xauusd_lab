# OpenClaw Inheritance Baseline

Date/time of inheritance: 2026-08-07T16:19:48+00:00

This baseline records the inherited state of the OpenClaw experimental copy at `/workspace/XAUUSD_Lab`. This is not the authoritative XAUUSD_Lab project.

## Git State

- Branch: `main`
- HEAD: `c117949b1b3f85537328d0b326b262cf099c1598`
- HEAD message: `Document full-year 2024 open-to-close finding`

Current Git status at inheritance:

```text
## main...origin/main
 M .gitignore
 M README.md
?? CODEX_HANDOVER.md
```

`README.md` and `.gitignore` appear to have line-ending-only changes: normal Git diff lists both files, while `git diff --ignore-space-at-eol` shows no substantive content differences for them.

`CODEX_HANDOVER.md` is untracked and appears to be an intentional handover artifact.

No unfinished code implementation was identified during read-only inspection. No tracked Python, JSON, requirements, or test files were modified, and no untracked non-documentation implementation files were observed.

## Data And Evidence Status

The inherited ignored evidence appears to contain a full-year 2024 Dukascopy XAUUSD one-minute BID dataset:

- Raw data files matching `data_raw/XAUUSD_2024-??-??_1min_BID_UTC.csv`: 366
- First raw file: `XAUUSD_2024-01-01_1min_BID_UTC.csv`
- Last raw file: `XAUUSD_2024-12-31_1min_BID_UTC.csv`

Report family counts under `reports/`:

- `data_manifest_2024-*.csv`: 12
- `linked_observation_report_2024-*.csv`: 12
- `historical_baseline_linked_observation_report_2024-*.csv`: 12
- `internal_flat_zero_volume_diagnostic_2024-*.csv`: 12
- `session_report_2024-*.csv`: 12

Standalone full-month `session_report` files for February and March 2024 were not observed. The visible standalone session reports include January and April through December full-month files, plus additional January short/single-day reports.

`logs/failed_downloads.txt` exists.

## Research Caution

This project is research software and evidence management, not a live trading or profitability system. Do not infer profitability, execution realism, trading edge, or future performance from historical findings, generated reports, or backtest-like results alone.
