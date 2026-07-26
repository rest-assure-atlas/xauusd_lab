# Durable Decisions

This document records architectural and research decisions that should be preserved unless the user explicitly approves a change.

## Data Source And Time

- The current market data source is Dukascopy XAU/USD one-minute BID data.
- Timestamps are stored and processed internally in UTC.
- Local timezones are used only when explicitly displaying or defining session windows.
- Python `zoneinfo` is used for timezone conversion, with local timezone definitions rather than fixed UTC offsets.

## Raw Data

- Raw downloaded CSV files are immutable source records.
- Do not edit raw CSV files in `data_raw/`.
- Cleaning, filtering, transformation, and derived calculations happen outside the raw layer.
- Inactive leading and trailing market-closed placeholder candles are excluded in analysis and display rather than deleted from raw files.
- Do not classify every isolated flat zero-volume candle as market closed.
- Do not interpolate genuine market closures.
- Do not splice unrelated providers' prices into Dukascopy closures.

## warning_treatment_v1 Research Treatment

Decision status: approved.

Decision date: 2026-07-26.

Problem governed: how descriptive research should treat observations classified
as `warning_review`, including observations whose manifest reason includes
`INTERNAL_FLAT_ZERO_VOLUME`, after the January through March 2024 validation
evidence showed broad recurring warning-review coverage.

This is an analysis-treatment decision only. It does not change raw data, active
filtering, manifest classifications, quality tiers, linked-report schemas,
baseline calculations, diagnostic calculations, session definitions, or current
source-code behaviour.

Adopted rules:

- Primary or headline numeric results must use `strict_valid` observations only.
- Every primary numeric result must report its strict-valid observation count.
- Small strict-valid samples must be reported honestly and must not justify
  weakening the quality rule.
- `warning_review` observations may appear only in separately labelled
  descriptive analysis or `warning-review sensitivity analysis`.
- Warning-review results must remain separate from strict-valid results, report
  available observation counts, report warning-reason counts, remain traceable
  to the provenance-linked source report, and include diagnostic context when a
  diagnostic exists.
- `strict_valid` and `warning_review` observations must not be pooled into
  headline counts, headline range summaries, primary averages, primary medians,
  primary distributions, primary hypothesis-test samples, or other primary
  research results.
- A combined count may be shown only as clearly labelled coverage, not as a
  quality-homogeneous research sample.
- `calendar_only` and `excluded_unusable` observations remain coverage records
  for the current daily/session range research and do not enter numeric range
  summaries unless a future approved contract says otherwise.
- Blank or unavailable numeric values must remain unavailable and must not be
  converted to zero to simplify analysis.
- Treatment is observation-level in this version. A daily observation classified
  `warning_review` remains warning-review as a whole.
- Diagnostic session overlap may be reported descriptively, but it does not prove
  that a non-overlapped session field is unaffected, that an overlapped session
  field is invalid, that a run outside configured sessions is irrelevant to
  daily values, or that any calculated field is harmless or reliable.
- Analyses using warning-review observations must preserve an auditable path to
  the source linked report, linked-report schema version, manifest schema
  version, validation-rule identity, active-filter rule identity,
  session-definition checksum, software revision, quality tier, warning reason,
  and explicit warning-reason combination where present.
- When a corresponding diagnostic exists, warning-review analysis must also be
  traceable to affected date, run count, total affected rows, maximum run length,
  configured-session overlap rows, and outside-configured-session rows.
- If multiple warning reasons appear later, report each reason separately,
  preserve explicit combinations, and do not collapse all warnings into one
  undifferentiated category.
- An analysis must remain explicitly inconclusive when the strict-valid sample is
  inadequate for the stated question, the result depends on prohibited pooling,
  required provenance cannot be verified, schema or rule compatibility cannot be
  established, required warning reasons are missing, a required diagnostic is
  unavailable, a conclusion would depend on an unapproved severity threshold, or
  the result would require an unsupported causal or harmlessness interpretation.

Rejected or postponed alternatives:

- Strict-only primary results are required, but total exclusion of all
  warning-review observations from every descriptive analysis is not the default.
- Separate warning-review reporting is permitted.
- Bounded warning-review sensitivity analysis is permitted when labelled as
  secondary to strict-valid primary results.
- Pooling strict-valid and warning-review observations is rejected for primary or
  headline research results.
- Diagnostic eligibility thresholds based on run length, run count, timing, or
  session overlap are postponed. Future thresholds require a separate approved
  specification and version change.
- Severity categories such as low, medium, high, minor, major, safe, unsafe, or
  harmless are not adopted in this version.
- Field-level primary eligibility is postponed. Diagnostic overlap fields remain
  descriptive context, not permission to promote selected fields to strict-valid
  treatment.

Rationale:

- The January through March 2024 evidence shows recurring warning-review
  coverage, but it does not establish cause or equivalence with strict-valid
  observations.
- The existing historical baseline already uses strict-valid observations as the
  headline numeric baseline and reports warning-review observations separately.
- The provenance-linked report preserves quality tier and reason fields, and the
  diagnostic provides descriptive run context for internal flat zero-volume
  warnings.
- Preserving separation keeps the research auditable while still allowing
  descriptive sensitivity checks.

Consequences:

- Future descriptive analyses must state which population each numeric result
  uses.
- Warning-review sensitivity results must be labelled secondary and must retain
  warning-reason and diagnostic context.
- Outputs from `session_report.py`, `explorer.py`, and `chart.py` use edge
  filtering but are not independently quality-tier-aware. They must not be
  presented as quality-screened research evidence unless linked back to the
  applicable manifest or provenance-linked assessment.
- `historical_baseline_report.py` already follows the core strict-versus-warning
  separation, and no source-code change is part of this decision.

Explicit non-goals:

- Do not infer the cause of `INTERNAL_FLAT_ZERO_VOLUME`.
- Do not classify any warning as harmless, expected market behaviour, market
  closure, provider outage, corruption, or reliable.
- Do not establish universal XAU/USD behaviour, statistical significance,
  support or resistance, a setup or signal, prediction, trading edge,
  profitability, or execution realism.

Future version triggers:

- A new warning reason requires a decision on whether `warning_treatment_v1`
  still applies.
- Any numeric threshold, severity label, field-level eligibility rule, pooling
  rule, or causal interpretation requires a separate approved specification and
  a new treatment-rule version.
- A future source, session-definition, schema, validation-rule, or diagnostic
  contract change requires compatibility review before reusing this treatment
  decision.

## research_observation_contract_v1 Linked-Report Access

Decision status: approved.

Decision date: 2026-07-26.

Problem governed: how future internal analyses should load existing
linked-observation CSV reports without duplicating compatibility checks or
silently mixing quality populations.

This interface is internal and linked-report-only. It wraps existing schema-v1
linked reports and is not a canonical dataset, a new report producer, or a
replacement for existing producers. The producers remain authoritative and
unchanged, and report schemas do not change.

Adopted rules:

- The proposed research observation unit is one linked-report row for one
  requested UTC date under one compatible source contract.
- Observation identity is `date`, `provider`, `instrument`, `quote_side`, and
  `timeframe`.
- The loader validates linked schema version, source contract, manifest schema,
  validation rule, active-filter rule, and session-definition checksum
  compatibility.
- `strict_valid`, `warning_review`, `calendar_only`, and `excluded_unusable`
  remain separate populations.
- No silent strict-valid plus warning-review pooling is provided.
- Blank values remain unavailable and are not converted to zero.
- Field availability is independent of observation quality tier; a strict-valid
  or warning-review observation may still contain blank session fields.
- Compatible mixed `software_revision` values are allowed when the schema,
  source, validation, filtering, and session-definition contracts match.
- Manifest and diagnostic attachment are deferred.

Consequences:

- Future analysis code can use named quality-tier selectors instead of ad hoc
  CSV filtering.
- Row values remain the original CSV strings, with source linked-report path and
  row software revision preserved as provenance.
- Manifest detail lookup, diagnostic run lookup, baseline integration, raw-data
  access, and research calculations require separate approval.

## Session Research

- Session definitions come from `sessions.json`.
- Tokyo, London, and New York sessions are configurable research windows rather than universal exchange sessions.
- Daylight-saving conversion must use `zoneinfo` and the configured local timezone definitions.
- Session candle selection is start-inclusive and end-exclusive.
- Session windows can overlap, so one candle may belong to more than one session.
- Because sessions overlap, future claims such as "one session broke another session's range" require a precise, non-ambiguous definition before implementation.

## Shared Logic

- Shared filtering logic belongs in `candle_filters.py`.
- Shared session loading, timezone conversion, selection, and statistics logic belongs in `session_tools.py`.
- Tools should reuse shared modules instead of duplicating calculations.
- Python should stay readable and beginner-friendly.

## Generated Files

- Generated reports are ignored by Git.
- Downloaded raw CSV files, logs, caches, and temporary artifacts should not be committed.

## Research And Trading Claims

- Current BID-only research is not sufficient for realistic strategy profitability claims.
- Future execution-aware testing must account for ASK data, spread, commission, slippage, latency, and execution assumptions.
- Findings should eventually be validated against another suitable data source and the intended live broker.
- The project is a research platform, not evidence of a profitable trading system.
