# Atlas Recovery Index: XAUUSD_Lab

Created: 2026-08-13

## Purpose

This file is the recovery entry point for Atlas when determining the current
XAUUSD_Lab research gate. It points to authoritative evidence and precedence
rules; it does not replace the full research history or project documentation.

## Source Precedence

When recovering current XAUUSD_Lab state, prefer:

1. Latest explicit frozen/current gate artifacts.
2. Independent critic or review artifacts for those gates, where applicable.
3. Partition locks, holdout locks, constitutions, and access policies.
4. Candidate validation and failure evidence needed to understand the gate.
5. Older planning/state docs such as `docs/CURRENT_STATE.md` and
   `docs/ROADMAP.md` only as historical/contextual sources when newer artifacts
   supersede them.

Do not use this index to weaken existing project governance. Newer explicit gate
artifacts may supersede this index.

## Current Authoritative Gate

- V1 clean validation over 2011-2014 failed.
- V1 `execution_cost_tail_rule_v1_candidate` is retired from advancement and
  preserved as failed evidence.
- 2011-2014 are burned/not pristine for V2 because they informed V1 validation,
  diagnostics, and the V2 design response.
- V2 Architecture B specification contract is frozen:
  `B_multi_horizon_strict_tail_maximum`.
- Independent critic review completed with no blocking defect.
- 2023 and 2025 remain final untouched holdouts.
- This does not imply V2 implementation, candidate performance testing,
  backtesting, strategy research, or holdout release has occurred.

## Authoritative Artifact Pointers

- `reports/execution_cost_candidate_v2_architecture_b_specification_freeze.md`
- `reports/execution_cost_candidate_v2_architecture_b_specification_freeze_critic.md`
- `reports/execution_cost_tail_rule_v1_candidate_clean_validation_2011_2014.md`
- `reports/execution_cost_tail_rule_v1_candidate_failure_diagnostics_2011_2014.md`
- `reports/multi_year_partition_lock.json`

## Stale-Document Warning

`docs/CURRENT_STATE.md` and `docs/ROADMAP.md` currently predate the later
execution-cost and V2 work. They must not by themselves be treated as the latest
research gate.

Do not modify those files merely to recover current state.

## Recovery Procedure

1. Read this recovery index.
2. Verify the referenced latest gate artifacts still exist.
3. Inspect newer candidate/gate artifacts if timestamps or content indicate this
   index may itself have been superseded.
4. Preserve all holdout, partition, methodology, quality-population, and safety
   restrictions.
5. Recover current state before proposing new research.
