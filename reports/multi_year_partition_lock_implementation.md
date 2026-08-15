# Multi-Year Partition Lock Implementation

Date: 2026-08-11
Status: partition-lock/access-log preparation complete
Preserved prior gate: READY_FOR_PARTITION_LOCK_AND_ACCESS_LOG_PREPARATION_ONLY
Implementation readiness result: READY_FOR_BOUNDED_MULTIYEAR_ACQUISITION pending separate explicit acquisition approval

## Scope

This implementation only operationalizes the approved multi-year partition plan.
It did not acquire market data, inspect future-holdout distributions, run
execution-cost validation on new years, run strategy research, alter raw
evidence, or change the approved partition roles.

## Partition Manifest

- 2024: `CONSUMED_DEVELOPMENT`
- 2010: `EXPANSION_SHAKEDOWN`
- 2011-2014: `EXECUTION_COST_CLEAN_VALIDATION`
- 2015-2019: `FUTURE_STRATEGY_DEVELOPMENT`
- 2020-2022: `FUTURE_WALK_FORWARD_VALIDATION`
- 2023: `FINAL_UNTOUCHED_HOLDOUT`
- 2025: `FINAL_UNTOUCHED_HOLDOUT`

Fallback final holdout order is preserved as: 2023, 2022, 2021. Fallback use
requires a recorded substitution reason and must not occur silently.

## Access Policy

The helper module `partition_lock.py` classifies access requests as
`ALLOWED`, `TECHNICAL_METADATA_ONLY`, `REQUIRES_RELEASE_APPROVAL`, or
`PROHIBITED_PRE_RELEASE`.

Final untouched holdouts remain locked before release. Pre-release access allows
only the coarse technical metadata already approved by policy:

- annual requested-day count
- annual file-existence status
- checksum presence/status
- source identity status
- terminal completion status
- coarse schema-validity status

Pre-release final-holdout access rejects spread summaries, quality
distributions, per-day/per-month row counts, descriptive statistics, charts,
anomaly lists, strategy outputs, execution-cost outputs, and exploratory
inspection.

## Access Log

`reports/holdout_access_log.csv` now has the operational v1 header. No fake
historical entries were added. The helper can append access attempts with
timestamp, requester, mission ID, partition/year, artifact path, requested
operation, fields/operations inspected, distributional-content flag, access
class, approval/rejection, approved gate/work order, approval reference, reason,
artifacts touched, partition clean before/after, consumption status after
access, and holdout status before/after.

## Release Rule

Final holdouts cannot be released automatically. A release requires an explicit
human approval reference, purpose, and policy/model/strategy version. Release
events are recorded in the lock artifact and, when an access-log path is
provided, durably appended to the CSV log with no distributional inspection.
The release marks the holdout consumed for that approved purpose.

## Frozen Execution-Cost Candidate

Candidate: `execution_cost_tail_rule_v1_candidate`

- rolling 30-calendar-day lookback
- monthly recalibration
- active `strict_valid_pair` only
- p99.5
- minimum 1,000 prior strict-valid observations
- prospective-only information set
- no warning-review baseline use
- reproducibility identifier: `sha256:a9523047484a546ffb67008fd47b538eaf90c6c0b359fbe0f8cf9b1b0f30b8c6`

The candidate was recorded exactly as a frozen candidate for future clean
multi-year validation. It was not retuned.

## Strategy Protocol Placeholder

Serious strategy discovery remains `BLOCKED` until a separate
strategy-research protocol gate exists. This implementation does not design,
test, rank, or optimize strategies.

## Independent Critic Outcome

The read-only critic found material issues in the first implementation:
gate wording could be read as acquisition permission, the access log omitted
approved leakage-control fields, final-holdout releases were not durably
access-logged by the helper, and operation labels needed basic normalization.
The implementation was tightened before final reporting.

## Final Gate

`READY_FOR_BOUNDED_MULTIYEAR_ACQUISITION`

This gate permits only a later, separately approved bounded acquisition mission.
It does not itself authorize acquisition.
