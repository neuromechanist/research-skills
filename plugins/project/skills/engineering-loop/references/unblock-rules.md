# Unblock Rules

Every wait has a limit and a next action.
When a limit is hit, take the action; do not wait again, re-ask, or restart the step.

| Situation | Limit | Then |
| --- | --- | --- |
| CI running | 30 min (`gh pr checks N --watch --fail-fast` under a 30-min tool timeout) | Check `gh run list`; if runs are queued, not failing, report it and continue other work. |
| CI job running past twice its usual time | - | It is hung: `gh run cancel <id>`, rerun once, and file an issue to add `timeout-minutes` if missing. |
| CI fails because of the diff | 2 fix attempts | Escalate to Opus or Sol with the failing log; if still red, hand off. |
| CI fails without the diff (fails on base, infra, flaky) | 1 rerun (`gh run rerun <id> --failed`) | File an issue with the log, note it in the PR, continue. Merging past a failing required check needs the user. |
| Reviewer silent | 20 min | Proceed with the reports received; run a missing high-risk lens inline. |
| Implementer silent | 45 min without commits or messages | Nudge once; then take over or respawn with an inventory of its files. |
| Merge conflict with base | - | Merge or rebase base, rerun gates. Logic changed while resolving counts as the delta round. |
| Same command keeps failing | 2 retries, each with a changed approach | Record the blocker in the state file or PR, move to the next independent task. |
| Usage or rate limit | 1 wait for the reset | Write done and next steps to the state file or PR first, then resume from it. |
| Tool or permission denied | 0 retries of the same call | Take another route, or ask once. |
| Ambiguous instruction | - | Pick the conservative reading, state it in one line, continue. |
| Question for the user | - | Batch questions into one message; continue independent work while waiting. |

Ask the user only for: plan approval, irreversible or external actions
(production deploy, publishing, force-push to a shared branch, deleting branches you did not create),
merging past a failing required check, and the final epic merge.

Never poll without a timeout. Never end a turn idle while independent work remains.
