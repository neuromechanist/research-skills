# Seam Review (lens `seam`)

The `seam` lens reviews a set of already-reviewed pull requests (PRs) as one unit, at the moment they integrate.
It answers three questions: are the stated goals met end to end, do the records (changelog, versions, docs) tell the truth about what landed, and did anything fall between the PRs.

It is not a line-level review.
Every PR in scope was reviewed on its own; do not repeat that work.
Every claim cites a `file:line`, commit, PR, or issue that the reviewer observed in this run.

## Modes

| Mode | Runs when | Unit under review | Base and head |
| --- | --- | --- | --- |
| `epic` | All phase PRs are merged into the epic branch, before the final epic PR merges or the epic issue closes | The epic: its issue, phase sub-issues, and phase PRs | integration branch and epic branch |
| `promotion` | Before an integration branch merges into a release branch (for example `dev` or `develop` to `main`) | Every PR merged into the head branch since the last promotion | release branch and integration branch |
| `delta` | Round 2, after seam fixes | The fix diff and the matrix rows and findings it touches | round-1 head and current head |

`seam` is never part of `all`.
It runs only when requested by name or by a workflow at one of the two moments above.
A single PR with no sibling PRs has no seams; use the other lenses.

## Inputs

The dispatcher passes:

- `mode`: `epic`, `promotion`, or `delta`.
- `epic`: the epic issue number, and the epic branch and integration branch (from `.claude/epic.local.md` when it exists).
- `promotion`: the base (release) and head (integration) refs, and the last promotion tag or commit.
  When it is omitted, derive it in step 1 and state the derived value in the report.
- Optional: the final PR number, the plan or plan-pack path that holds acceptance gates, and the integration test command.
- `delta`: the round-1 report, each finding's outcome, and the round-1 head commit.

Never pass the authoring rationale.
If a required input is missing and cannot be derived, ask once; do not guess the scope.

## Reviewer briefing

Dispatch exactly one integration-scoped reviewer, fresh context, read-only: Claude Opus at `medium` effort or Codex Luna (`gpt-6-luna`) at `max`.
Do not dispatch the per-PR panel for this lens.
A user-supplied model, effort, or inline choice overrides the default.
With no subagent surface, the session runs this file inline.

The brief contains the inputs above, this file's path, and this instruction:
"Every PR in scope has already been reviewed.
Do not re-review their diffs.
Report only goal-level gaps, cross-PR seams, false records, and unresolved follow-ups.
Cite evidence you observed for every claim, and stop at ten findings, most severe first."

The lead (Claude Opus or Codex Sol at `xhigh`; the session driver delegates to it) reproduces every Critical finding and every `unmet` row, then owns the verdict.
The reviewer proposes a verdict; it never merges, pushes, comments, or closes issues.

## Procedure

### 1. Build the scope manifest

List every PR in scope with its number, title, merge commit, the issues it closes, and whether a review record exists.
Fetch first (`git fetch origin --tags --prune`) and use `origin/` refs.

`epic` mode:

```bash
gh issue view {epic_issue} --json title,body,state,comments
gh api 'repos/{owner}/{repo}/issues/{epic_issue}/sub_issues' --jq '.[] | [.number, .state, .title] | @tsv'
gh pr list --base {epic_branch} --state merged --limit 200 \
  --json number,title,body,mergeCommit,mergedAt,closingIssuesReferences
git log --first-parent --format='%h %s' origin/{integration_branch}..origin/{epic_branch}
git diff --stat origin/{integration_branch}...origin/{epic_branch}
```

Leave `{owner}` and `{repo}` literal; `gh api` fills them from the current repository.
Read each phase sub-issue body (`gh issue view N --json title,body,state,comments`) and the state file's notes.

`promotion` mode:

```bash
git describe --tags --abbrev=0 origin/{base}              # last release tag
git merge-base origin/{base} origin/{head}                # last promotion, when promotions are regular merges
git log --first-parent --format='%h %s' {last_promotion}..origin/{head}
gh pr list --base {head} --state merged --limit 200 --search "merged:>={date of last promotion}" \
  --json number,title,body,mergeCommit,mergedAt,closingIssuesReferences
git diff --stat {last_promotion}..origin/{head}
```

When promotions are squash merges the merge base is stale; use the last release tag's date instead.
Reconcile the two lists: every first-parent commit maps to a PR or is named as a direct push, and every listed PR has a commit in the range.
A direct push to the integration branch is unreviewed work; report it as a finding.

For each PR, collect the review record:

```bash
gh pr view N --json reviews,comments,body
gh api graphql -F owner='{owner}' -F name='{repo}' -F number=N -f query='
  query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){
    pullRequest(number:$number){reviewThreads(first:100){nodes{
      isResolved path line comments(first:1){nodes{body url}}}}}}}'
```

A PR with no review record is a finding ("unreviewed PR #N"); recommend the per-PR lenses for it, and do not review it here.

### 2. Trace goals to evidence

Extract every goal and acceptance criterion, verbatim, from the epic issue, the phase sub-issues, the plan or plan-pack cards (their Acceptance sections), and, in `promotion` mode, the release milestone or the draft release notes.
Number them `G1..Gn` and fill one row each:

| ID | Goal (quoted, with source) | Evidence on the head | How verified | Status |
| --- | --- | --- | --- | --- |
| G1 | "Export supports CSV" (#132 body) | `src/export.py:41`, `tests/test_export.py:12`, PR #135 | ran `uv run pytest tests/test_export.py` | met |

Status is one of:

- `met`: the behavior exists on the head and was observed (a test run, a command, or a read of the code path end to end);
- `partial`: some of the criterion holds; name what is missing;
- `unmet`: no evidence on the head;
- `unverifiable`: the check could not run here; say why and what would settle it;
- `descoped`: the owner dropped it, with a link to the decision.

Rules:

- A closed issue, a merged PR, a ticked checkbox, or a PR description is a claim, not evidence.
- Evidence must be on the current head; a later PR may have removed what an earlier one added.
- A goal that spans phases needs evidence that crosses them: one test or one traced call path through both sides.
- Only the owner descopes a goal; without a linked decision the row is `unmet`.
- Run the integration test command on the head when one exists; report the command and result, or why it did not run.

### 3. Walk the seams

Check each item; record `clean` with the command that showed it, or a finding.

| ID | Seam | How to look |
| --- | --- | --- |
| S1 | Assumed work: a PR says another phase "will" or "already does" something | Search PR bodies, issue bodies, and review threads for "phase", "later", "follow-up", "out of scope", "separate PR"; confirm the other side landed. |
| S2 | Interfaces between PRs: names, signatures, schemas, config keys, file formats, exit codes | For each symbol or key one PR produces and another consumes, read both ends on the head. |
| S3 | Duplicated or conflicting helpers, constants, and defaults | `git diff --stat {base}...{head}` for files added by different PRs; `rg` each new helper name and constant. |
| S4 | Deferred items: `TODO`, `FIXME`, `XXX`, `HACK`, skipped or expected-fail tests, feature flags left off | `git diff {base}...{head} \| rg '^\+.*(TODO\|FIXME\|XXX\|HACK\|skip\|xfail)'` |
| S5 | Merge damage: a later PR's conflict resolution or squash reverted an earlier PR's change | For each file touched by two or more PRs, compare the earlier PR's hunks against the head. |
| S6 | Cross-cutting work no PR owned: docs, tests that cross PRs, manifests, parity across agent or platform surfaces, migrations, continuous integration (CI) configuration | Read the project's rules (`AGENTS.md`, `.rules/`) for required companions to each kind of change, and check each exists. |
| S7 | Dead code from an abandoned approach: unused modules, flags, fixtures, dependencies | `rg` each symbol and dependency added in range for a caller on the head. |
| S8 | Config and manifest drift: values declared in more than one place disagree | Compare every declaration of each version, name, path, and count the range touched. |
| S9 | Half-landed work: one side of a pair merged (writer without reader, flag without code, migration without rollback, command without registration) | From the manifest, pair each PR with the PR its body says it depends on or enables. |

A defect that lives inside one PR's diff and involves no other PR is out of scope.
Report it only when it is Critical, tagged `escaped`.

### 4. Check the records against what landed

Compare each record with the manifest and the head, in both directions.

- **Changelog and release notes:** every entry maps to a PR in scope; every user-visible PR has an entry; no entry describes reverted, descoped, or unmerged work; entries sit under the right version and category.
- **Version:** the bump level matches the largest change in scope (breaking, feature, fix); every file that declares the version agrees; the target tag does not already exist (`git tag -l`); the release date is right.
- **README, `AGENTS.md`, and docs:** each command, flag, path, count, file tree, and default the range touched exists on the head as written; examples run or are marked as not run.
- **Issues:** each issue the range closes is complete per its own criteria; open issues are not described as done; the epic issue's checklist matches the sub-issue states.
- **PR and epic descriptions:** the final PR's summary and phase list match the manifest.

Verify by reading the head or running the command, never from the PR that wrote the record.

### 5. Settle per-PR follow-ups

Collect every deferral from the review records in step 1: findings triaged as `issue`, comments that say "follow-up" or "later", unresolved review threads, and unticked task boxes in PR and issue bodies.
Give each one disposition:

- `done`: fixed in range; cite the commit;
- `tracked`: an open issue exists and the item is outside the goals in step 2; cite the issue;
- `blocking`: it belongs to a goal in step 2; it becomes a finding;
- `stale`: no longer applies; say why in one sentence.

A deferral with no fix and no issue is a finding (Important, or Critical when it belongs to a goal).
An accepted per-PR finding that was never fixed is always a finding.

## Severity and verdict

- **Critical:** a goal is `unmet`; the end-to-end path fails; a record is false in a way users or the release hit (wrong version, changelog claims a missing feature, install path broken); merge damage lost reviewed work.
- **Important:** a `partial` goal; an untracked deferral; an interface mismatch not yet exercised; drift between declarations; cross-cutting work missing.
- **Moderate:** dead code, duplicate helpers, and stale docs with no user-facing error.

| Verdict | Condition |
| --- | --- |
| `ready` | Every goal is `met` or `descoped`; no open Critical or Important finding; records are true; every deferral has a disposition; integration verification passed. |
| `ready-with-fixes` | No Critical; every goal is `met`, `descoped`, or `partial` with a named fix; the Important findings can be fixed on the branch within the convergence rules below. |
| `not-ready` | Any Critical; any `unmet` goal; any `unverifiable` goal the owner has not accepted; or integration verification failed or did not run without an accepted reason. |

The verdict informs the merge decision; it is not approval.
The final epic merge and a promotion still need the user.

## Output additions

Keep the toolkit's findings-first shape and add the seam sections:

```markdown
**Verdict:** ready | ready-with-fixes | not-ready
**Scope:** {mode}, {base}..{head}, {n} PRs (#a, #b, ...), last promotion {ref} (given | derived)

**Findings**
- Critical: [G2 | S5 | records | follow-up] [evidence] Description. Impact. Fix.
- Important: ...
- Moderate: ...

**Goals**
| ID | Goal | Evidence | How verified | Status |

**Seams**
S1 clean (command) | S2 finding 3 | ...

**Records**
Changelog, version, docs, issues: true, or the finding number.

**Follow-ups**
| Source (PR, thread) | Item | Disposition | Evidence |

**Questions**
**Residual Risk**
```

Each finding names its origin (a goal ID, a seam ID, `records`, or `follow-up`) and its evidence.
When the report is posted to GitHub, keep each paragraph and list item on one source line.

## Convergence

The caps in `review-convergence.md` apply: one full round, one delta round, no third round unless the user asks.

Triage every finding as `fix`, `reject`, or `issue`.
An `unmet` or `partial` goal cannot be triaged as `issue`; fix it, or take the descope decision to the owner and link it on the epic issue or release PR.

Where fixes go:

- `epic` mode: commits on the epic branch (the final PR's head); a large fix (more than 150 non-test, non-doc lines, a changed public contract, or a replaced approach) goes in one fix PR based on the epic branch.
- `promotion` mode: one fix PR into the integration branch for the whole round, never one PR per finding, and never a direct push to a protected branch.
- Changelog, version, and doc corrections ride with the fixes; never defer them to after the merge.

Round 2 (`delta`) runs when round 1 had a Critical, an `unmet` goal, or a large fix.
One reviewer rechecks only the fix diff, the matrix rows that were not `met`, and the findings triaged `fix`, then restates the verdict.
Otherwise the driver verifies each fix against its finding and updates the verdict itself.
A `not-ready` verdict after round 2 goes to the user with the open rows; do not review again.
