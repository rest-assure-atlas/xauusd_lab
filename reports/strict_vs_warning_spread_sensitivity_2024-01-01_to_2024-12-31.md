# Strict vs Warning Spread Sensitivity, 2024 Full Year

Scope: descriptive sensitivity only. Source is `/workspace/XAUUSD_Lab/reports/bid_ask_reconciliation_2024-01-01_to_2024-12-31.csv`. Rows are active/non-placeholder only; raw data, classifications, methodology, schemas, session definitions, and research policy were not changed. Detailed grouping output is in `/workspace/XAUUSD_Lab/reports/strict_vs_warning_spread_sensitivity_2024-01-01_to_2024-12-31_detail.csv`.

## Population Summary
|population|active_rows|p95|p99|max|count>=0.620000|count>=1.000000|count>=2.000000|share>=0.620000|share>=1.000000|share>=2.000000|
|---|---|---|---|---|---|---|---|---|---|---|
|strict_valid_pair|70165|0.521000|0.632000|4.204000|868|70|2|0.012371|0.000998|0.000029|
|warning_review_pair|285726|0.477000|0.610000|5.981000|2693|441|84|0.009425|0.001543|0.000294|

## Top Dates by Population p99-Row Count
|population|date|p99_row_count|active_rows|date_p99|date_max|
|---|---|---|---|---|---|
|strict_valid_pair|2024-12-13|116|1320|0.701000|1.940000|
|strict_valid_pair|2024-12-24|78|1124|0.844000|1.054000|
|strict_valid_pair|2024-12-25|55|60|1.940000|1.940000|
|strict_valid_pair|2024-12-27|51|1320|0.657810|0.744000|
|strict_valid_pair|2024-04-14|46|120|1.045860|1.200000|
|warning_review_pair|2024-12-12|639|1369|1.406680|2.744000|
|warning_review_pair|2024-12-11|602|1377|3.758720|5.120000|
|warning_review_pair|2024-12-26|286|1375|0.804800|1.980000|
|warning_review_pair|2024-12-30|252|1380|0.747630|1.380000|
|warning_review_pair|2024-05-22|114|1378|0.662000|1.440000|

## Top UTC Hours by Population p99-Row Count
|population|utc_hour|p99_row_count|active_rows|hour_p99|hour_max|
|---|---|---|---|---|---|
|strict_valid_pair|23|174|3179|0.929980|1.940000|
|strict_valid_pair|22|129|2040|0.838830|1.200000|
|strict_valid_pair|18|48|3044|0.670000|1.054000|
|strict_valid_pair|12|44|3060|0.648820|4.204000|
|strict_valid_pair|20|39|2939|0.704000|2.810000|
|warning_review_pair|23|324|12276|0.731750|5.981000|
|warning_review_pair|22|253|8084|0.744510|1.980000|
|warning_review_pair|12|202|12480|0.660000|3.954000|
|warning_review_pair|06|159|12480|0.642000|4.560000|
|warning_review_pair|05|154|12479|0.624660|5.120000|

## Configured Sessions
|population|session|active_rows|p95|p99|max|count>=0.620000|count>=1.000000|count>=2.000000|share>=0.620000|share>=1.000000|share>=2.000000|
|---|---|---|---|---|---|---|---|---|---|---|---|
|strict_valid_pair|London|27540|0.501050|0.607000|4.204000|213|13|1|0.007734|0.000472|0.000036|
|strict_valid_pair|New York|27206|0.497000|0.627000|4.204000|297|39|2|0.010917|0.001434|0.000074|
|strict_valid_pair|Tokyo|27540|0.507000|0.597000|0.750000|157|0|0|0.005701|0.000000|0.000000|
|warning_review_pair|London|112319|0.450000|0.600000|3.954000|911|66|6|0.008111|0.000588|0.000053|
|warning_review_pair|New York|111253|0.450000|0.571000|3.954000|649|86|7|0.005834|0.000773|0.000063|
|warning_review_pair|Tokyo|112294|0.470000|0.610000|5.120000|1022|234|59|0.009101|0.002084|0.000525|

## Excluding Warning Top 5 Extreme Dates
Excluded dates: 2024-05-22, 2024-12-11, 2024-12-12, 2024-12-26, 2024-12-30.

|population|active_rows_after_exclusion|p95|p99|max|count>=0.620000|count>=1.000000|count>=2.000000|share>=0.620000|share>=1.000000|share>=2.000000|
|---|---|---|---|---|---|---|---|---|---|---|
|strict_valid_pair|70165|0.521000|0.632000|4.204000|868|70|2|0.012371|0.000998|0.000029|
|warning_review_pair|278847|0.460000|0.550000|5.981000|961|156|20|0.003446|0.000559|0.000072|

Warning_review remains materially wider after excluding these dates: no (p99 ratio before 0.97x, after 0.87x).

Strict_valid concentrated event clusters: limited; top 5 dates contain 346/704 (49.1%) of strict_valid p99 rows.

Warning_review concentration: top 5 dates contain 1893/2946 (64.3%) of warning_review p99 rows.

Conclusion classification: event-cluster driven.
