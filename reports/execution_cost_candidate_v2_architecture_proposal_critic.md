# Independent Critic Review: Execution-Cost Candidate v2 Architecture Proposal

## Scope

Read-only independent critic review of:

- `reports/execution_cost_candidate_v2_architecture_proposal.md`
- `reports/execution_cost_candidate_v2_architecture_proposal.json`
- Necessary 2024 development, 2011-2014 validation/diagnostic, and partition-lock context

No files were modified by the critic.

## Verdict

No blocking defects found. Accept for Director review.

## Key Checks Passed

- Scope is explicitly design-only in both Markdown and JSON.
- `execution_cost_tail_rule_v1_candidate` is retired and preserved as failed evidence, not advanced or silently modified.
- No candidate performance calculation, parameter optimization, backtest, strategy research, 2015+ inspection/acquisition, or 2023/2025 holdout access is claimed.
- The two v1 weaknesses are explicitly addressed: 11990 unavailable rows from sparse 30-day strict-valid history, and coverage instability led by 2011-08 undercoverage.
- Exactly three architectures are proposed.
- Each architecture covers threshold estimate, update cadence, sparse-history handling, regime/tail response, allowed prospective data, leakage safeguards, strengths/risks, complexity, parameters to freeze, and structural versus tunable choices.
- Recommendation of Architecture B is methodological, not based on retrospective performance optimization.
- Partition plan treats 2024 as consumed, 2011-2014 as burned, 2015-2019 and 2020-2022 as gated future use, and 2023/2025 as final untouched holdouts.

## Non-Blocking Caveats

- Architecture A's optional deterministic interim update and guard trigger need especially tight freeze language later, since they could become hidden tuning knobs.
- Architecture C's "reserve for later if simple mechanisms fail under clean testing" path should be handled carefully: any such clean-testing evidence would become consumed for that design generation.
- The v2 JSON references `execution_cost_model_spec.json` and `post_corroboration_execution_cost_evidence_policy.json` as additional source evidence; these were not inspected by the critic because the review task constrained necessary source context.

## Recommended Gate

`DESIGN_PROPOSAL_ACCEPT_FOR_DIRECTOR_REVIEW_EXECUTION_COST_CANDIDATE_V2`
