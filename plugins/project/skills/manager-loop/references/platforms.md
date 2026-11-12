# Platforms: Where the Manager Runs, Where Workers Run

One manager is authoritative: it holds the board's lease, it alone merges, and every worker on every platform reports to it.
Workers run wherever the parity table and the slots say: Claude locally or in the cloud, Codex, Copilot, or remote hosts.
The same card, the same gates, and the same report schema apply on every platform.

## Parity is live

The Parity table maps tiers to a model and effort per platform; the Slots table says how many workers each platform may run, which tiers it takes, and what it can do.
A real example of an owner's mapping when Codex budget grew: "Luna max for Sonnet work (high), Terra xhigh for Sonnet xhigh, Sol xhigh for Opus", with a Codex slot of at most four Luna plus two Terra (or one Terra and one Sol) at a time.
The frontier tier maps the same way: Fable to Astra (`gpt-6-astra`), with Sol (`gpt-6.1-sol`) at the Opus level.

Models get renamed, new products ship, and quotas move, so:

- The owner edits Parity and Slots (or answers a question that the manager records with `decide`). The manager never edits them.
- The manager asks the parity question at setup, at every checkpoint, and on any mismatch: a model id a platform refuses, a platform that exists but has no Parity column, a slot whose quota is near its end, or a capability a card needs that no slot has.
- Ask it as a structured question: "Update the parity to <proposal> (Recommended) / Add <platform> as a slot with Max <n> / Keep the current parity".
- Adding a platform means adding a Parity column and a Slots row; `check` warns when a slot names a platform with no column.

### Capabilities (the Can and Needs columns)

Free-form tokens; keep a short shared vocabulary in the plan, for example `gui`, `browser`, `computer-use`, `gpu`, `gpu:<host>`, `macos`, `network`.
A step is placed only on a slot that can do everything it needs.
Computer use and visible GUI runs act on the owner's machine: they stay with the manager's own host, need the owner's announced consent each time, and are never delegated to another platform.

## Where the manager runs

| Host | How it ticks | How it asks the owner | Notes |
| --- | --- | --- | --- |
| Claude Code (recommended) | `/loop` with no interval; the manager ends each tick by scheduling its next wake (ScheduleWakeup) | AskUserQuestion; PushNotification to reach the owner away from the terminal | dispatch workers with `run_in_background: true` so a completion wakes the manager early; use Monitor with a time limit for waits on CI or jobs |
| Codex, interactive | the owner keeps one session open; a scheduler sends "Run one manager tick" into it with `codex queue --thread <session> --message ... --resume`, where the installed version has `codex queue` | `request_user_input` (one to three short questions; interactive root thread only) | verify one manual tick before scheduling; the lease stops a queued tick from overlapping a running one |
| Codex, headless | a scheduler (cron, launchd, a systemd timer) runs `codex exec -C <repo> "<start prompt>"` once per tick | none in `codex exec`: questions go to the board and a notification | workers must be detached and write report files, because nothing wakes a headless manager early |
| Copilot CLI | interactive session ticked by the owner, or a non-interactive prompt run per tick from a scheduler (check `copilot --help` for the installed flags) | `ask_user` when enabled (it can be disabled with `--no-ask-user`) | same rules as headless Codex when non-interactive |
| A cloud scheduled agent | one tick per run against a board kept on a pushed branch | board and notification only | the lease and the board's commits must go through the branch; use only when the owner wants the manager off their machines |

Whatever the host, record every question on the board first; the host's question tool is the fast path, not the record.

## Dispatching workers

### Claude Code subagent (local)

Agent tool with the card's tier mapped through Parity (`model`, and effort where the host exposes it), a role name (`impl-E1-2`), `run_in_background: true`, and an isolated worktree.
Fix rounds go to the same agent with SendMessage when it is alive; otherwise a fresh agent gets the continuation line, the PR number, and the decided findings.
Close the agent when its step merges.

### Codex worker

```bash
codex exec -m <model id> -c model_reasoning_effort=<effort> -s workspace-write \
  -C <worktree> --json -o <evidence>/codex-last-message.md \
  --output-schema <plan>/report.schema.json \
  "<preamble + card + live facts>" \
  > <evidence>/codex-events.jsonl 2> <evidence>/codex-stderr.log
```

Run it in the background (or detached for long cards), one evidence directory per card and round.
Right after it starts, confirm the model and effort from the worker's own session record, not the newest file: the first event (`thread.started`) gives its thread id; its rollout under `~/.codex/sessions/<yyyy>/<mm>/<dd>/rollout-*-<thread id>.jsonl` must name the card's worktree as `cwd` and show the expected model and reasoning effort.
Anything else: stop it and dispatch again. Write the thread id, model, and effort on the board's Agents row.
Prefer `workspace-write`; use `danger-full-access` only when a gate needs it, and then the preamble's rules are the only barrier.
A fix round is a new `codex exec` in the same worktree with the continuation line, the PR number, and the decided findings.

### Copilot CLI worker

Run the preamble and card through Copilot's non-interactive prompt mode with the model flag of the installed version, in the card's worktree; capture its final message as the report.
Verify the model from its session log the same way before trusting the report.

### Cloud workers (Claude Code on the web, Codex cloud, Copilot coding agent)

Start them from a branch or an issue that carries the card, through whatever dispatch the owner has enabled; they report through the PR only.
The manager verifies the PR exactly as for a local worker.
They never get computer use or secrets, and the manager does not assume it can message them mid-run.

### Remote hosts (GPU workstations, clusters, pods)

An operator worker runs the registered commands mechanically and interprets nothing.
Jobs are detached with stage markers, heartbeat files, and a terminal marker (see `project:engineering-loop`'s `background-jobs.md`); one block runs on one host from one pinned commit.
Check that a GPU is free of foreign processes before launching. For RunPod use `ml-training:runpod`.

## Handing a card from one platform to another

The fixes stay on the original platform unless one of these holds:

1. the review round reports a Critical finding, or three or more accepted findings graded Important or higher;
2. a finding needs a design decision that leaves judgment to the implementer (the lead decides this, not the manager);
3. a fix round did not close its findings;
4. the same defect kind comes back after it was sent back once (a test that cannot fail, a stop condition passed, a computed value given as measured, a PR body replaced);
5. the fix needs evidence or decisions the card, the PR, and the findings do not carry (the lead decides).

Then: stop the first worker before the second starts, so two writers never share a worktree; the new worker uses the same worktree, branch, and PR ("The pull request is #N; do not open another. Extend its body, never replace it."); it gets every earlier round's report and the decided findings.
The review round count does not restart.
Log each handover with the condition that triggered it.

## Quota and cost

When a platform's quota runs low, the manager asks the parity question with the alternatives; it does not move work by itself.
On a usage limit, write the board, the done and next items, and the reset time; wait once for the reset, then resume from the board.
