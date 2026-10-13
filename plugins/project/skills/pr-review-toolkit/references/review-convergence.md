# Review Convergence

One PR gets at most two review rounds, then it merges.
Every workflow that reviews a PR follows this file.

## Rounds

| Round | Runs when | Scope | Reviewers |
| --- | --- | --- | --- |
| 1. Full | Always | Whole PR diff | Panel per `review-panel-protocol.md`; one reviewer for docs-only PRs, PRs under 50 changed lines, and final epic or release PRs (integration scope only) |
| 2. Delta | Round 1 was substantial (below) | Fix commits only | One reviewer |
| 3 | Never, unless the user asks | - | - |

## Round 1: triage every finding

Give each finding exactly one outcome:

- **fix**: accepted, including suggestions;
- **reject**: false positive or intended design, with a one-sentence reason in the PR;
- **issue**: about code this PR did not touch; file a follow-up issue and link it.

Resolve accepted findings before merge.
Never merge to fix them in a follow-up PR or the next release.

## Where fixes go

Round 1 was **substantial** if any is true
(judge rules 2, 3, and 5 from the planned fix; if unsure, write the fixes locally off the PR head first, then choose):

1. an accepted finding is Critical;
2. the fixes change more than 150 non-test, non-doc lines;
3. the fixes change a public contract (API, CLI flag, schema, config or file format, migration);
4. the fixes touch authorization, encryption, data integrity, or concurrency;
5. the fixes replace the PR's approach instead of patching it.

| Round 1 result | Fixes go to | Round 2 |
| --- | --- | --- |
| Not substantial | Commits on the PR branch | No. The driver checks each finding is resolved. |
| Substantial, fix is small (only rule 1 or 4) | Commits on the PR branch | Yes, on those commits |
| Substantial, fix is large (rule 2, 3, or 5) | A fix PR whose base is the PR branch | Yes, on the fix PR; then merge it into the PR branch |

A review-fix PR always targets the original PR's head branch, never the integration branch directly.
Never re-review the whole PR.

## Release PRs (head is a protected branch)

When the PR's head branch blocks direct pushes (for example a `develop` to `main` release PR):

- Round 1 uses one integration-scoped reviewer; the feature PRs were already reviewed.
- All fixes from a round go in ONE fix PR into the head branch, never one PR per finding.
- Open the release PR only when it is ready to merge, and merge it promptly; every push to the head branch re-runs its CI.

## Round 2: delta only

Brief one reviewer with the fix diff (`git diff <round-1 head>..HEAD` or the fix PR),
the round-1 findings with their outcomes, and this instruction:
"Report only Critical or Important defects that the fixes introduce or fail to resolve.
Do not re-flag rejected findings or code outside the fix diff."

Fix round-2 findings with commits on the branch the reviewed diff lives on (the fix PR's branch, if there is one), or reject or file them as issues.
The driver verifies each round-2 fix against its finding by running its repro or test.
Do not review again.

## Merge gate

Merge when the round-1 report (and the round-2 report, if round 2 runs) is in, every finding has an outcome, no accepted Critical is open, and CI is green on the final head.
An accepted Critical that cannot be fixed in scope goes to the user.
Never merge while a review is still running.
Routine PRs (single-PR work, epic phases) merge without asking the user.
The final epic merge and any merge with a failing required check need user approval.

## CI cost

Commit fixes atomically, then push once per round, so CI runs once per round.
Run review while CI runs; do not wait for CI before starting round 1.
Changelog and doc updates ride in the PR they describe; never open a PR only to patch a changelog.
