# Unblock Rules

Every wait has a limit and a next action.
When a limit is hit, take the action; do not wait again, re-ask, or restart the step.

| Situation | Limit | Then |
| --- | --- | --- |
| CI running | 30 min (run `gh pr checks N --watch --fail-fast` in the background; check it at 30 min) | Check `gh run list`; if runs are queued, not failing, report it and continue other work. |
| CI job running past twice its usual time | - | It is hung: `gh run cancel <id>`, rerun once, and file an issue to add `timeout-minutes` if missing. |
| CI never starts | 5 min | Conflict (`gh pr view N --json mergeable`): merge the base in. No workflow matches (base branch, path filter, `[skip ci]`): run the local gates and note it in the PR; if a required check stays pending, ask the user. |
| CI fails because of the diff | 2 fix attempts | Escalate to Opus or Sol with the failing log; if still red, hand off. |
| CI fails without the diff (fails on base, infra, flaky) | 1 rerun (`gh run rerun <id> --failed`) | File an issue with the log, note it in the PR, continue. Merging past a failing required check needs the user. |
| Reviewer silent | 20 min | Proceed with the reports received; run a missing high-risk lens inline. |
| Implementer silent | 45 min without commits or messages | Nudge once; then take over or respawn with an inventory of its files. |
| Merge conflict with base | - | Merge or rebase base, rerun gates. Logic changed while resolving counts as the delta round; if round 2 already ran, the driver verifies the resolution itself. |
| Same command keeps failing | 2 retries, each with a changed approach | Record the blocker in the state file or PR, move to the next independent task. |
| Usage or rate limit | 1 wait for the reset | Write done and next steps to the state file or PR first, then resume from it. |
| Tool or permission denied | 0 retries of the same call | Take another route; if none exists, ask once. |
| Ambiguous instruction | - | Pick the conservative reading, state it in one line, continue. |
| Question for the user | - | Batch questions into one message; continue independent work while waiting. |

**Hand off** means: post the failing command and log on the PR, tell the user, stop that item, and continue other work.

Besides the asks a workflow defines for its own state (for example, corrupt epic state), ask the user only for:

- plan approval;
- an accepted Critical that cannot be fixed in scope (it needs changes outside the PR, or still fails after two attempts and escalation);
- irreversible or external actions (production deploy, publishing, force-push to a shared branch, deleting branches you did not create);
- a denied permission with no other route;
- merging past a failing or pending required check;
- the final epic merge.

Never poll without a timeout. Never end a turn idle while independent work remains.
