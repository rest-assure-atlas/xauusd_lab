# Full-Year 2024 Spread Characterization

Scope: descriptive spread characterization only; no raw data, reconciliation logic, schema, quality rule, session definition, warning treatment, research policy, strategy design, execution-cost model, or profitability claim was changed.

## Overall Populations
- full_population: count 527040, placeholder 171149 (0.324736), min/median/mean/p75/p90/p95/p99/max 0.001000/0.410000/0.584784/0.632000/1.110000/1.462000/1.940000/5.981000
- non_placeholder: count 355891, placeholder 0 (0.000000), min/median/mean/p75/p90/p95/p99/max 0.001000/0.380000/0.384377/0.410000/0.447000/0.487000/0.620000/5.981000
- strict_valid_pair: count 70165, placeholder 0 (0.000000), min/median/mean/p75/p90/p95/p99/max 0.001000/0.387000/0.392572/0.420000/0.461000/0.521000/0.632000/4.204000
- warning_review_pair: count 380555, placeholder 94829 (0.249186), min/median/mean/p75/p90/p95/p99/max 0.001000/0.400000/0.531602/0.490000/1.010000/1.291000/1.860000/5.981000
- excluded_calendar_only: count 76320, placeholder 76320 (1.000000), min/median/mean/p75/p90/p95/p99/max 0.307000/0.970000/1.026679/1.192000/1.590000/1.860000/2.810000/2.810000

## Monthly Pattern
- 2024-01: count 44640, median 0.340000, mean 0.467674, p95 1.100000, p99 1.100000, max 2.490000, placeholder share 0.321953
- 2024-02: count 41760, median 0.340000, mean 0.501556, p95 1.191000, p99 1.191000, max 5.981000, placeholder share 0.310153
- 2024-03: count 44640, median 0.351000, mean 0.464162, p95 0.750000, p99 0.750000, max 1.710000, placeholder share 0.380623
- 2024-04: count 43200, median 0.390000, mean 0.708988, p95 2.810000, p99 2.810000, max 2.810000, placeholder share 0.297245
- 2024-05: count 44640, median 0.410000, mean 0.656274, p95 1.720000, p99 1.720000, max 2.107000, placeholder share 0.295184
- 2024-06: count 43200, median 0.417000, mean 0.529088, p95 1.001000, p99 1.001000, max 1.687000, placeholder share 0.361875
- 2024-07: count 44640, median 0.410000, mean 0.634105, p95 1.370000, p99 1.370000, max 3.954000, placeholder share 0.292406
- 2024-08: count 44640, median 0.420000, mean 0.615226, p95 1.590000, p99 1.590000, max 1.980000, placeholder share 0.322581
- 2024-09: count 43200, median 0.421000, mean 0.564693, p95 1.192000, p99 1.192000, max 3.224000, placeholder share 0.329977
- 2024-10: count 44640, median 0.417000, mean 0.571931, p95 1.590000, p99 1.590000, max 2.954000, placeholder share 0.290547
- 2024-11: count 43200, median 0.430000, mean 0.549409, p95 1.051000, p99 1.051000, max 4.204000, placeholder share 0.338611
- 2024-12: count 44640, median 0.487000, mean 0.749358, p95 1.940000, p99 1.940000, max 5.120000, placeholder share 0.355668

## Configured Session Pattern
- London: count 139859, median 0.377000, mean 0.378350, p95 0.461000, p99 0.601000, max 4.204000
- New York: count 138459, median 0.370000, mean 0.374386, p95 0.460000, p99 0.587000, max 4.204000
- Tokyo: count 139834, median 0.387000, mean 0.387330, p95 0.477000, p99 0.604000, max 5.120000

## Tail Context
- full_population p95 >= 1.462000: count 26934, share 0.051104, placeholder 26716, active 218, warning_review 13946, 19-date overlap 12
- full_population p99 >= 1.940000: count 6111, share 0.011595, placeholder 6013, active 98, warning_review 3225, 19-date overlap 2
- full_population absolute_0.500000 >= 0.500000: count 166663, share 0.316225, placeholder 151853, active 14810, warning_review 93003, 19-date overlap 2738
- full_population absolute_1.000000 >= 1.000000: count 76283, share 0.144739, placeholder 75772, active 511, warning_review 40213, 19-date overlap 479
- full_population absolute_2.000000 >= 2.000000: count 3098, share 0.005878, placeholder 3012, active 86, warning_review 1656, 19-date overlap 2
- non_placeholder p95 >= 0.487000: count 18398, share 0.051696, placeholder 0, active 18398, warning_review 12865, 19-date overlap 1291
- non_placeholder p99 >= 0.620000: count 3561, share 0.010006, placeholder 0, active 3561, warning_review 2693, 19-date overlap 640
- non_placeholder absolute_0.500000 >= 0.500000: count 14810, share 0.041614, placeholder 0, active 14810, warning_review 10270, 19-date overlap 1169
- non_placeholder absolute_1.000000 >= 1.000000: count 511, share 0.001436, placeholder 0, active 511, warning_review 441, 19-date overlap 89
- non_placeholder absolute_2.000000 >= 2.000000: count 86, share 0.000242, placeholder 0, active 86, warning_review 84, 19-date overlap 2

## Widest Active-Market Spreads
- 2024-02-18 23:13:00: spread 5.981000, bid-relative bps 29.724941, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW
- 2024-12-11 05:17:00: spread 5.120000, bid-relative bps 19.128567, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW
- 2024-12-11 05:18:00: spread 4.750000, bid-relative bps 17.754255, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW
- 2024-12-11 05:16:00: spread 4.741000, bid-relative bps 17.709369, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW
- 2024-12-11 05:20:00: spread 4.630000, bid-relative bps 17.311550, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW
- 2024-12-11 05:15:00: spread 4.607000, bid-relative bps 17.203471, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW
- 2024-12-11 05:45:00: spread 4.587000, bid-relative bps 17.071305, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW
- 2024-12-11 06:01:00: spread 4.560000, bid-relative bps 16.956306, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW
- 2024-12-11 06:10:00: spread 4.504000, bid-relative bps 16.751291, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW
- 2024-12-11 06:31:00: spread 4.451000, bid-relative bps 16.531449, status warning_review_pair, reasons BID_SIDE_WARNING_REVIEW;ASK_SIDE_WARNING_REVIEW

## Warning Tail Overlap
- Active p99 threshold: 0.620000; active p99 rows 3561, warning_review rows 2693, 19 configured-session-overlap warning-date rows 640.

## Artifacts
- reports/spread_characterization_2024-01-01_to_2024-12-31_full_year_summary.csv
- reports/spread_characterization_2024-01-01_to_2024-12-31_wide_observations.csv
- reports/spread_characterization_2024-01-01_to_2024-12-31_tail_context.csv
- reports/spread_characterization_2024-01-01_to_2024-12-31_report.md
