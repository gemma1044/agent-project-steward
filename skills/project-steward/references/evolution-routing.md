# Evolution routing

When a steward needs a new or corrected rule, record the failure, root cause, evidence, validation and privacy review first. Then decide its destination.

## Local: update `references/local/`

Choose `local` when the rule depends on this repository's architecture, commands, data model, deployment path, product policy, team agreement, private system, naming convention, or current worktree state. Local rules are immediately useful here and remain always owned by this repository.

## Upstream candidate: notify the portfolio steward

Choose `upstream_candidate` only when the rule describes a reusable Agent Stud mechanism with no repository-specific names, paths, identifiers, credentials, quotas, or business examples. Include enough evidence to show that it is not an isolated mistake. The portfolio steward reviews it before changing the public core.

## Tie-breaker

If uncertain, choose `local` first. Promoting a proven local rule later is safe; prematurely universalizing it makes unrelated repositories harder to operate.
