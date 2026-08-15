# Active Spread Tail Audit: 2024 full year

Scope: descriptive audit of active/non-placeholder rows only from the completed full-year bid/ask reconciliation and spread characterization outputs. Thresholds are preserved as requested: active p99 >= 0.620000, plus separate >= 1.000000 and >= 2.000000 inspections. No raw data was modified or acquired, and no methodology, schema, session definition, policy, strategy, or profitability work was changed or started.

## Sources and validation
- Source reconciliation: `/workspace/XAUUSD_Lab/reports/bid_ask_reconciliation_2024-01-01_to_2024-12-31.csv`
- Existing spread outputs checked: `spread_characterization_2024-01-01_to_2024-12-31_full_year_summary.csv`, `spread_characterization_2024-01-01_to_2024-12-31_tail_context.csv`, and report markdown.
- Source SHA-256: `79284720351511a68b9c8a819540f0265c5fa814a90ad281b6bf54a3d04be0d8`
- Row accounting: total 527040; active/non-placeholder 355891; placeholders 171149; active + placeholders = total: True.
- Existing spread characterization cross-check: non-placeholder p99 count expected 3561 at threshold 0.620000; recomputed 3561. >=1.0 expected 511; recomputed 511. >=2.0 expected 86; recomputed 86.

## Tail population
- Active p99 rows: 3561
- strict_valid vs warning_review: strict_valid_pair 868, warning_review_pair 2693
- 19-date warning-overlap contribution: p99 640 (17.97%); >=1.0 89 (17.42%); >=2.0 2 (2.33%).

## Concentration evidence
- Top 5 dates: 1827/3561 (51.31%) | 2024-12-12=607, 2024-12-11=581, 2024-12-26=243, 2024-12-30=224, 2024-12-13=172
- Top 10 dates: 2212/3561 (62.12%) | 2024-12-12=607, 2024-12-11=581, 2024-12-26=243, 2024-12-30=224, 2024-12-13=172, 2024-12-24=93, 2024-12-23=80, 2024-05-22=77, 2024-12-27=74, 2024-12-31=61
- >=1.0 top 5 dates: 345/511 (67.51%) | 2024-12-11=199, 2024-12-12=81, 2024-01-25=26, 2024-02-18=23, 2024-12-25=16
- >=2.0 top 5 dates: 80/86 (93.02%) | 2024-12-11=62, 2024-02-18=12, 2024-01-25=3, 2024-12-12=2, 2024-04-05=1
- Session distribution: tokyo=1051 (29.51%), outside_configured_sessions=878 (24.66%), london=645 (18.11%), new_york=508 (14.27%), london+new_york=351 (9.86%), tokyo+london=128 (3.59%)
- UTC-hour top 8: 23:00=491 (13.79%), 22:00=387 (10.87%), 12:00=246 (6.91%), 06:00=187 (5.25%), 13:00=177 (4.97%), 20:00=150 (4.21%), 01:00=145 (4.07%), 09:00=144 (4.04%)

## Major clusters
- 2024-12-11 04:32-06:07 UTC: 96 consecutive active p99 rows
- 2024-12-12 08:25-08:57 UTC: 33 consecutive active p99 rows
- 2024-12-25 23:28-23:59 UTC: 32 consecutive active p99 rows
- 2024-02-18 23:25-23:56 UTC: 32 consecutive active p99 rows
- 2024-12-12 05:52-06:19 UTC: 28 consecutive active p99 rows
- 2024-12-11 07:04-07:31 UTC: 28 consecutive active p99 rows
- 2024-12-11 06:09-06:36 UTC: 28 consecutive active p99 rows
- 2024-12-11 06:38-07:01 UTC: 24 consecutive active p99 rows
- Date breadth: 267 dates have at least one p99 row; 38 dates have >=10 p99 rows; 80 dates have exactly one p99 row.

## Interpretation
The active p99 tail is mixed: not purely distributed and not warning-driven. The top 10 dates contribute a material but minority share, while the largest absolute-spread subset is cluster-heavy. Warning-review rows are the majority of p99 rows, but the 19 cautionary session-overlap dates contribute only a minority of p99 rows and very little of the >=2.0 subset.

## Descriptive implications
Downstream execution-cost research should preserve strict_valid and warning_review labels, run sensitivity slices for the warning-review population, and treat the active p99 tail as a separate descriptive cost-regime input before any execution realism or strategy/profitability interpretation.

## Machine-readable summary
| metric | value |
| --- | --- |
| active_p99_rows | 3561 |
| strict_valid_pair_p99 | 868 |
| warning_review_pair_p99 | 2693 |
| top5_date_rows | 1827 |
| top10_date_rows | 2212 |
| ge1_rows | 511 |
| ge2_rows | 86 |
| warning19_p99_rows | 640 |
| warning19_ge1_rows | 89 |
| warning19_ge2_rows | 2 |
| p99_dates | 267 |
| p99_dates_ge10_rows | 38 |
| p99_dates_singleton | 80 |
