# Platforms: Where the Manager Runs, Where Workers Run

One manager is authoritative: it holds the board's lease, it alone merges, and every worker on every platform reports to it.
Workers run wherever the parity table and the slots say: Claude locally or in the cloud, Codex, Copilot, or remote hosts.
The same card, the same gates, and the same report schema apply on every platform.

## Parity is live

The Parity table maps tiers to a model and effort per platform; the Slots table says how many workers each platform may run, which tiers it takes, and what it can do.
The board template ships both as defaults, and the owner's approval of the plan accepts them, so setup does not ask about them.
A real example of an owner's mapping when Codex budget grew: "Luna max for Sonnet work (high), Terra xhigh for Sonnet xhigh, Sol xhigh for Opus", with a Codex slot of at most four Luna plus two Terra (or one Terra and one Sol) at a time.
The lead tier (Opus; Codex Sol, `gpt-6.1-sol`) is the default for every lead role, including project initiation and planning.
The frontier tier (Fable; Codex Astra, `gpt-6-astra`) is used only when the owner explicitly asks, for long-horizon jobs or planning the owner names, or when the approved plan's routing lists a frontier trigger.

Models get renamed, new products ship, and quotas move, so:

- The owner edits Parity and Slots (or answers a question that the manager records with `decide <text> --by owner`); the manager never edits them.
- The manager asks the parity question only on a mismatch: a model id a platform refuses, a platform that exists but has no Parity column, a slot whose quota is near its end, or a capability a card needs that no slot has.
  It never asks routinely at setup or at a checkpoint.
- Ask it as a structured question: "Update the parity to <proposal> (Recommended) / Add <platform> as a slot with Max <n> / Keep the current parity".
- Adding a platform means adding a Parity column and a Slots row; `check` warns when a slot names a platform with no column.

### Capabilities (the Can and Needs columns)

Free-form tokens; keep a short shared vocabulary in the plan, for example `gui`, `browser`, `computer-use`, `gpu`, `gpu:<host>`, `macos`, `network`.
A step is placed only on a slot that can do everything it needs.
Computer use and visible graphical user interface (GUI) runs act on the owner's machine: they stay with the manager's own host, need the owner's announced consent each time, and are never delegated to another platform.

## Where the manager runs

| Host | How it ticks | How it asks the owner | Notes |
| --- | --- | --- | --- |
| Claude Code (recommended) | the start prompt prefixed with `/loop ` and no interval; the manager ends each tick by scheduling its next wake | a structured question tool; a notification to reach the owner away from the terminal | workers run in the background so a completion wakes the manager early; mechanics below |
| Codex, interactive | the owner keeps one session open; a scheduler sends "Run one manager tick" into it with `codex queue --thread <session> --message ... --resume`, where the installed version has `codex queue` | `request_user_input` when the session lists it, else plain text; see "Codex mechanics" | verify one manual tick before scheduling; the lease stops a queued tick from overlapping a running one |
| Codex, headless | a scheduler (cron, launchd, a systemd timer) runs `codex exec -m <model id> -s workspace-write -c sandbox_workspace_write.network_access=true -C <repo> "<start prompt>"` once per tick; add the `writable_roots` setting from "Codex worker" when the manager runs in a linked worktree, or use `-s danger-full-access` | none in `codex exec`: questions go to the board and a notification | a headless manager needs network access (`gh`, pushes) and write access to the repository (the board, commits); workers must be detached and write report files, because nothing wakes a headless manager early |
| Copilot command-line interface (CLI) | interactive session ticked by the owner, or a non-interactive prompt run per tick from a scheduler; verify the flags with `copilot --help` on the installed version | `ask_user` when enabled (disabled by `--no-ask-user`); verify the same way | same rules as headless Codex when non-interactive; not yet verified on a live install |
| A cloud scheduled agent | one tick per run against a board kept on a pushed branch | board and notification only | the lease and the board's commits must go through the branch; use only when the owner wants the manager off their machines |

Whatever the host, record every question on the board first; the host's question tool is the fast path, not the record.

### Claude Code mechanics

- Start: prefix the plan's start prompt with `/loop ` and give no interval, so the loop paces itself.
- Wake: end each tick by scheduling the next wake with ScheduleWakeup; its delay is clamped to 60-3600 seconds, so a 30-minute cadence is 1800 and a 60-minute cadence is 3600.
  ScheduleWakeup with `stop: true` ends the dynamic loop; use it when the board is `done` or `paused`.
- Refused tick: schedule one wake at the lease expiry the refusal prints, and do nothing else.
- Questions: AskUserQuestion, up to four questions per call with two to four options each, one marked recommended.
- Notifications: PushNotification, to reach the owner away from the terminal.
- Waits: Monitor with a time limit, never an unbounded poll.
- Workers: the Agent tool with `run_in_background: true`; SendMessage continues a live worker.

### Codex mechanics

- Questions: `request_user_input` works only on the root thread of an interactive session, never in `codex exec`.
  It takes one to three short questions with two or three choices each.
  It is offered only when the tool is listed for the session: in Plan collaboration mode, or with the `default_mode_request_user_input` feature, which is "under development" and off by default in Codex 0.167.0.
  Otherwise Codex asks in plain text in the session; the board record stays.
- Model ids (read from `~/.codex/models_cache.json`; re-check on the installed version): `gpt-6-astra` (frontier, Fable level), `gpt-6.1-sol` (lead, Opus level), `gpt-6.1-terra` (worker-hard), `gpt-6-luna` (worker and reviewer).
- Headless ticks: nothing wakes the manager early, so workers are detached and write report files; a refused tick ends the run, and the scheduler's next run retries.

### Copilot CLI mechanics

- Questions: the `ask_user` tool when it is enabled; `--no-ask-user` turns it off for non-interactive runs.
- Both come from GitHub's changelog and documentation; Copilot CLI is not installed on the machine where this skill was checked, so verify every Copilot flag and tool with `copilot --help` on the installed version.
- A non-interactive tick is a prompt run from a scheduler, with the same rules as a headless Codex manager.

## Dispatching workers

### Claude Code subagent (local)

Agent tool with the card's tier mapped through Parity (`model`, and effort where the host exposes it), a role name (`impl-E1-2`), `run_in_background: true`, and an isolated worktree.
Fix rounds go to the same agent with SendMessage when it is alive; otherwise a fresh agent gets the continuation line, the pull request (PR) number, and the decided findings.
Close the agent when its step merges.

### Codex worker

```bash
codex exec -m <model id> -c model_reasoning_effort=<effort> \
  -s workspace-write \
  -c 'sandbox_workspace_write.writable_roots=["<main repo>/.git/worktrees/<worktree name>"]' \
  -c sandbox_workspace_write.network_access=true \
  -C <worktree> --json -o <evidence>/codex-last-message.md \
  --output-schema <skill>/assets/report.schema.json \
  "<preamble + card + live facts>" \
  > <evidence>/codex-events.jsonl 2> <evidence>/codex-stderr.log
```

`<skill>` is this skill's absolute directory; `assets/report.schema.json` is the worker report schema (see `plan-pack.md`).
A worker in a linked worktree needs the two `-c` settings (reproduced).
Under `-s workspace-write` alone it cannot commit: git writes `index.lock` in `<main repo>/.git/worktrees/<worktree name>` (the directory `git -C <worktree> rev-parse --git-dir` prints), which is outside the writable roots.
It also has no network, so `git push`, `gh`, and installs fail.

Run it in the background (or detached for long cards), one evidence directory per card and round.
Right after it starts, confirm the model and effort from the worker's own session record, not the newest file: the first event (`thread.started`) gives its thread id; its rollout under `~/.codex/sessions/<yyyy>/<mm>/<dd>/rollout-*-<thread id>.jsonl` must name the card's worktree as `cwd` and show the expected model and reasoning effort.
Anything else: stop it and dispatch again.
Write the thread id, model, and effort on the board's Agents row.
Prefer `workspace-write` with those settings; use `-s danger-full-access` only when a gate needs more, and then the preamble's rules are the only barrier.
A fix round is a new `codex exec` in the same worktree with the continuation line, the PR number, and the decided findings.

### Copilot CLI worker

This recipe is not yet verified on a live install; verify the flags and the session-log location with `copilot --help` on the installed version.
The shape of a non-interactive run, in the card's worktree, with its final output captured as the report:

```bash
copilot -p "<preamble + card + live facts>" --model <model id> --no-ask-user \
  > <evidence>/copilot-last-message.md 2> <evidence>/copilot-stderr.log
```

Add the permission flags the card's gates need (file writes, shell, network) once verified.
Verify the model from its session log the same way as for Codex before trusting the report.

### Cloud workers (Claude Code on the web, Codex cloud, Copilot coding agent)

Start them from a branch or an issue that carries the card, through whatever dispatch the owner has enabled; they report through the PR only.
The manager verifies the PR exactly as for a local worker.
They never get computer use or secrets, and the manager does not assume it can message them mid-run.

### Remote hosts (workstations, clusters, pods)

An operator worker runs the registered commands mechanically and interprets nothing.
Jobs are detached with stage markers, heartbeat files, and a terminal marker (see `project:engineering-loop`'s `background-jobs.md`); one block runs on one host from one pinned commit.
Check that a graphics processing unit (GPU) is free of foreign processes before launching.
For RunPod use `ml-training:runpod`.

## Handing a card from one platform to another

The fixes stay on the original platform unless one of these holds:

1. the review round reports a Critical finding, or three or more accepted findings graded Important or higher;
2. a finding needs a design decision that leaves judgment to the implementer (the lead decides this, not the manager);
3. a fix round did not close its findings;
4. the same defect kind comes back after it was sent back once (a test that cannot fail, a stop condition passed, a computed value given as measured, a PR body replaced);
5. the fix needs evidence or decisions the card, the PR, and the findings do not carry (the lead decides).

Then: stop the first worker before the second starts, so two writers never share a worktree.
The new worker uses the same worktree, branch, and PR, and its brief says:

```text
The pull request is #N; do not open another.
Extend its body, never replace it.
```

It gets every earlier round's report and the decided findings.
The review round count does not restart.
Log each handover with the condition that triggered it.

## Quota and cost

When a platform's quota runs low, the manager asks the parity question with the alternatives; it does not move work by itself.
On a usage limit, write the board, the done and next items, and the reset time; wait once for the reset, then resume from the board.
