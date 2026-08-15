# CODEX_HANDOVER: XAUUSD_Lab

## What this project does

XAUUSD_Lab is a long-term Python research project for studying XAU/USD, gold priced in U.S. dollars. It downloads Dukascopy one-minute BID data, validates raw CSV provenance, builds daily/session reports, links observations to source data, and records descriptive research findings.

## Current state

Confirmed application milestone: v0.11. The copied local project includes ignored generated/local folders such as `data_raw/`, `reports/`, `logs/`, and `__pycache__/` because the handover was requested with no exclusions.

## Completed work

- Downloader, explorer, charting, session tools, session reports, data manifests, linked observation reports, research observation loader, historical baseline reports, and internal flat zero-volume diagnostics.
- Full January-December 2024 Dukascopy XAUUSD one-minute BID local data/provenance checkpoint is present in ignored local outputs.
- Latest documented finding records the full-year 2024 open-to-close result.

## Latest known working commit

`c117949b1b3f85537328d0b326b262cf099c1598` - `Document full-year 2024 open-to-close finding`

## Outstanding tasks

- Review and preserve the annual data/provenance checkpoint.
- Decide the next bounded research direction.
- Perform a bounded ASK-data prerequisite inspection before execution-realistic testing.
- Continue to keep strict-valid, warning-review, calendar-only, and excluded-unusable populations separate.

## Important technical decisions

- Preserve raw market data unchanged. Never edit downloaded CSV files in `data_raw/`.
- Use UTC internally unless local time is explicitly displayed.
- Keep generated raw CSVs, generated reports, logs, caches, and temporary artifacts out of Git.
- Reuse shared modules such as `candle_filters.py` and `session_tools.py`.
- Add or update tests for behavioral changes.

## Setup and test commands

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

Use small date ranges and existing fixtures during development. Avoid large downloads during ordinary tests.

## Known problems

- Local ignored data and reports are valuable evidence but are not part of a fresh Git clone.
- The project is research software, not an execution or profitability system.
- Some generated outputs are intentionally ignored and must be handled carefully during migration.

## Suggested first prompt for Codex on the new laptop

"Inspect XAUUSD_Lab, read AGENTS.md, README.md, CHANGELOG.md, docs/CURRENT_STATE.md, docs/ROADMAP.md, and git status. Then verify the copied data/provenance checkpoint and recommend the next bounded research task."
