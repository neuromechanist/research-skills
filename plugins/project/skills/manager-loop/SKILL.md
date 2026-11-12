---
name: manager-loop
description: "Use this skill when the user asks to \"run the plan hands-off\", \"act as the project manager\", \"act as the research manager\", \"manage this plan in a loop\", \"start a manager loop\", \"run one tick\", \"drive the epic with a manager agent\", \"run agent waves\", \"dispatch cards to Claude and Codex\", \"set up parity between Claude and Codex\", \"show me the board\", \"serve the board\", or for any multi-day plan that a manager agent executes by dispatching workers, verifying each step's goal, reviewing, merging, and escalating to an advisor or the owner. Covers the plan pack, the tick, waves versus slots, budgets, cross-platform parity, structured owner questions, and the Markdown board with its live HTML view."
---

# Manager Loop

A lead-tier model writes the plan; a mechanical manager runs it, tick by tick, for hours or days.
The manager dispatches self-contained cards, verifies each step's goal by observing evidence, runs reviews, merges, keeps the board, and asks the owner only through structured questions.
Judgment goes up a ladder (lead, advisor, owner); it never happens in the manager.
Invoke sibling skills through the host's own skill mechanism.

## When to use

| Work | Use |
| --- | --- |
| One change, one PR | `project:engineering-loop` |
| A phased feature where the owner approves each phase | `project:epic-dev` |
| Parallel agents inside one session | `project:agent-fanout` |
| A plan of many steps and PRs, run hands-off by a manager that ticks | This skill; it uses the three above for each step |

Before the loop, the plan exists and the owner approved it (`project:implementation-planning`).
If it does not, stop and plan first.

## Roles

| Role | Default tier | Does | Never |
| --- | --- | --- | --- |
| Owner | person | approves the plan, and with it the defaults for Parity, Slots, budgets, and merge authority; answers questions; takes outward actions | |
| Lead | lead tier; frontier tier only when the owner asks, for long-horizon planning the owner names, or a frontier trigger the approved plan lists | writes the plan pack and cards, completes outline cards at checkpoints, decides design and contested findings | dispatch, merge |
| Manager | worker or worker-hard tier | runs the tick: dispatch, verify, review, merge, board, questions, proposals | design, product code, change the plan, a card, or a gate |
| Advisor | lead tier; frontier tier on the same conditions as for the lead | one read-only consult per escalation, from a brief | edit anything |
| Implementer | by the card's tier and the parity table | one card, one branch, one PR | merge, change scope |
| Reviewer | `project:pr-review-toolkit`, a different model family from the implementer when possible | | edit |

Tier names map to models in the board's Parity table; this skill names no model.
The lead tier is the default for every lead role, including project initiation and planning.
The lead and the manager may be one agent only when the owner says so; that agent then records every judgment call with `decide`.

## Setup (once, before the first tick)

1. **Plan pack.** The lead writes it per `references/plan-pack.md`: the plan with a goal and a literal acceptance gate per step, the manager's runbook, one card per step, the slot and collision rules (or the named waves), and the checkpoints and risks.
2. **Pack review.** An executability reviewer (worker tier) and a design reviewer (lead tier) read the pack, plus a domain reviewer where it applies; every finding gets a disposition before the loop starts.
   Run `manager_board.py card` on every card the first dispatches will use (README.md preambles are skipped); each must pass.
3. **Board.** `manager_board.py init .context/<plan>/board.md --title ... --plan ... --repo ... --branch ...`, then add the steps and waves.
   The script lives in this skill's `scripts/` directory; call it by absolute path with `python3` (standard library only).
4. **Defaults and owner approval.**
   The defaults are the board template's Parity, Slots, and Budget, the plan's merge authority, and "no question takes a default answer".
   The owner's approval of the plan accepts them, including the budget limits that `project:agent-fanout`'s cap asks the user to approve, per wave and per day.
   Ask only about what has no default (for example the notification channel when the host has none), in one batch of structured questions (see "Owner questions").
5. **Start.** Run the plan's start prompt on the host's self-paced loop with no interval, as `references/platforms.md` says for each host.
   Optional: `manager_board.py serve <board>` in a detached shell for the owner's live view.

## The tick

Run in order; each tick is complete on its own because the board carries all state.

1. `date`. Then `manager_board.py tick <board> --manager <id>`; the first tick of a session adds `--state running`.
   The manager id is stable per manager, `<host>-<model>` (for example `mba-claude-sonnet`), never per session, so restarts and headless ticks of the same manager keep the lease.
   If the tick is refused because another manager holds the lease, schedule one wake at the lease expiry the refusal prints and do nothing else.
2. **First tick of a session only:** reconcile the board with the world.
   For each step in `active` or `review`, read its PR and worktree; the PR and the worktree are right, the board is corrected and the correction logged.
   A step with no live worker is dispatched again with the line "This card was started earlier. Continue from the worktree: run `git status` and `git log --oneline -10` first."
3. `manager_board.py status <board>`: the needs-you list, the dispatch plan, timeboxes, questions, budget.
4. **Collect events:** worker reports, open PRs and their checks, owner answers (board and session), dates due.
5. **Handle events in this order:** owner answers, worker reports, reviews, failed checks or gates, merge conflicts, timeboxes and silent workers, dates and questions due, a checkpoint due.
   Limits and next actions come from `project:engineering-loop`'s `references/unblock-rules.md`; apply them literally.
   - An answered question: act on it, record it with `decide <text> --by owner`, set the question `closed`.
   - A report: verify by observation (below), then start the review while continuous integration (CI) runs; do not wait for CI.
   - A review: give every finding an outcome per `project:pr-review-toolkit`'s `references/review-convergence.md`; at most two rounds.
   - A check failing because of the diff: two fix attempts, then escalate to the advisor with the failing log.
   - CI failing without the diff (it fails on the base, on infrastructure, or flakily): one rerun (`gh run rerun <id> --failed`), then file an issue with the log and continue.
   - A merge conflict: the branch's worker merges the base into the branch and reruns the gates; never a rebase, never a force-push.
   - A silent worker, an implementer at 45 minutes without commits or messages or a reviewer at 20 minutes: nudge once, then redispatch with an inventory of its files and commits (the manager hands the card to a worker and never takes it over).
   - A step past twice its timebox: escalate to the advisor.
   - A date or question due: ask it now, with a recommendation.
   - A checkpoint due: the checkpoint items under "Contribute".
   - Merge when the merge gate passes and the board's authority allows it.
     The merge gate: every review report is in with each finding resolved, no accepted Critical is open, and `gh pr checks N` is green on the final head (every check, not only required ones).
     A merge the host refuses (a refused permission or an automated policy denial) is not retried or worked around: set the step to `owner` and ask.
6. **Fill free slots** from the dispatch plan in `status` (it already applies dependencies, open waves, tiers, needs, and slot limits).
   For each: `card` check, `spend <board> "Agents today"` (and `spend <board> "Agents this wave"` only when the step belongs to a wave), dispatch the card verbatim plus live facts copied from the board now, then `set` the step `active` with its slot and add its agent row.
7. **Contribute** with the closed checklist below; at most one proposal per tick.
8. **Ask** the owner if an event needs it (below).
9. **Write and wake.** `log` one line per event; commit the board locally (push only at checkpoints, with `[skip ci]` when no CI reads it); `tick <board> --next 30m` while workers run, `--next 60m` while waiting on people; then schedule the wake with the host's self-paced loop (`references/platforms.md`).

## Verify by observation

A worker's "done" is not evidence. Check, in order, and stop at the first failure:

1. The PR's head and base equal the report (`gh pr view N --json headRefOid,baseRefName`).
2. The diff stays inside the card's Scope (`gh pr diff N --name-only`).
3. The card's acceptance gate was run on the final head: run its literal command yourself, or read the quoted hook or run record the card names.
4. Every fix has a revert check or a test that fails without it.
5. Deviations from the card are listed and each is triaged (accept, send back, or ask the lead).

Green checks on the final head belong to the merge gate (tick step 5), not to this list.

Send back, inside the current round: a value stated as measured that was computed, a stop condition the worker passed, a test that cannot fail, a PR body replaced instead of extended.

## Waves or slots

Slots are the default: a step starts when its dependencies are merged and a fitting slot is free.
Apply in order:

1. A step that shares a file with an in-flight step, needs a serialized resource (one GPU, one VM, one simulator), or has an unmerged dependency runs by slots, never in a wave.
2. When review or lead attention is the bottleneck (reviews waited longer than one tick), use slots.
3. Otherwise a wave runs only if the plan names it, with its members, budget, exit gate, and an owner checkpoint. The manager never forms a wave itself.

On the board, a step whose wave is not `active` is not ready; the manager sets the next wave `active` only after the current wave's exit gate passes and the checkpoint is recorded.
Wave budget = members x (1 implementer + round-1 panel size + 1 delta reviewer + expected fix dispatches) + 1 advisor.
Opening a wave (`set Waves <id> State=active`) resets every Budget row whose Resets is `wave` to 0 and logs it; step 6 spends the wave budget only for a step that belongs to a wave.
Details and examples: `references/plan-pack.md`.

## Budgets

The board's Budget table holds limits the owner approved; Slots hold concurrency.
`spend` refuses to pass a limit: at a limit, stop dispatching and ask.
Daily rows reset on the first tick of a day; wave rows reset automatically when a wave opens, and the reset is logged.
Compute budgets (GPU hours, cloud dollars) carry the plan's overrun trigger and its ordered drop rules; never drop anything on the plan's never-drop list.

## Parity and platforms

The Parity table maps each tier to a model and effort on every platform; its columns are the platforms the owner uses.
Cards name a tier, not a model; `status` shows which model the chosen slot runs.
Parity is live: models are renamed and new products appear.
The board template's Parity, Slots, and Budget are the defaults, and the owner's approval of the plan accepts them.
The owner owns them and edits them when things change; the manager never edits them.
The manager asks the parity question only on a mismatch (a refused model id, a platform missing from Parity, a quota near its end, a capability no slot has), never routinely at a checkpoint: "update the parity, add this platform as a slot, or keep it?"
Allocate by capability first (GUI, browser, computer use, hardware), then cost and quota.
Computer use and visible GUI runs stay with the manager's host and need the owner's announced consent every time.
Dispatch commands, model checks, handover rules, and every host-specific mechanic (the self-paced loop, questions, notifications, waits) are in `references/platforms.md`.

## Owner questions

Record every question on the board first: `manager_board.py ask <board> Q7 --question <text> --options "A (Recommended) / B" --default none --needed-by <time>`.
Then, if the owner is in an interactive session, ask it with the host's structured question tool, batching a few related questions, each with options, one recommended, the default, and what waits; the batch limits per host are in `references/platforms.md`.
If the host offers no such tool in this session, ask in plain text in the session; the board record stays either way.
If the owner is away, send one notification through the host and keep working on independent steps.
The owner may answer in the session or on the live board page; both land in the board's Questions table.
Never answer for the owner and never treat silence as an answer; a default applies at its deadline only for a question class the owner pre-authorized, and the manager logs that it applied it.

## Escalation

Escalate to the advisor (lead tier) on: a step at twice its timebox, two failed approaches, a security, data-integrity, concurrency, or authorization invariant, a contested review finding, or a red gate on the integration branch.
The flaky gate, a PR that relaxes a gate, an owner answer that contradicts a card, and a projected overrun go to the lead or the owner as `references/escalation.md` says.
Use the frontier tier only when the owner explicitly asks, for a long-horizon job or planning the owner names, or when the approved plan's routing lists a frontier trigger (for example "frontier tier when the lead tier cannot decide, or after three loops").
Use the brief and output format in `references/escalation.md`; `spend` the advisor budget; record the ruling with `decide` and on the PR.
The lead turns a ruling into card changes; the manager never edits a card itself.

## Contribute (closed checklist)

Each tick, after the mechanical work, check these and act only as stated:

1. A slot or GPU idle for two ticks with nothing ready: `propose` the next plan item and the one thing blocking it.
2. A question whose "ask on" date is within two days: ask it now, with a recommendation.
3. A skill or review lens the plan names that has not run on a merged step: run it.
4. The same defect kind twice: ask the lead for a diagnosis card.
5. A mismatch seen in a dispatch (a refused model id, a platform missing from Parity, a quota near its end, a capability no slot has): ask the parity question.

At checkpoints only: an advisor anticipation pass (how will the owner, reviewers, and users react to the current state, and what will they ask next), a budget and capacity projection, and the batched questions; the parity question waits for a mismatch.
Proposals never dispatch until the lead or owner accepts them; one notification per event class per day; never repeat a proposal unless the facts changed.

## The board

`board.md` holds state only and is the single source of truth; `board-log.md` beside it holds Decisions and Log, append-only.
Specs live in the plan and cards.
Write through the helper so limits hold (300 lines, 240 characters per cell); run `check` after any hand edit.

| Command | Use |
| --- | --- |
| `init`, `check`, `status [--json]` | create, validate, read the tick summary |
| `set <section> <key> Col=value [--new]` | update or add a row (Steps, Questions, Proposals, Agents, Waves) |
| `tick --manager <id> [--next 30m] [--state <state>]` | heartbeat and lease; refuses a second live manager; `--state paused`, `stopped`, or `done` clears Next tick and releases the lease |
| `spend <item> [n]`, `ask <id> --question <text>`, `answer`, `propose <text> --why <reason>`, `decide <text> --by <who>`, `log`, `archive` | budgets, questions, proposals, history |
| `card <files>` | refuse to dispatch an incomplete card (files named README.md are skipped) |
| `render`, `serve [--port]` | static snapshot, or the live localhost page with answer buttons |

Format, columns, states, and the server's limits: `references/board.md`.

## Never

- Merge with a red or pending check, an unresolved finding, or a review still running; start a third review round.
- Change a gate's expectation, a card, the plan, the parity, or a budget limit.
- Retry a refused permission, work around an automated policy denial, force-push, or rebase a pushed branch.
- Perform outward actions (deploy, publish, post, contact anyone); hand them to the owner as exact commands.
- Delegate computer use, or start a visible GUI run without an announcement and a stop file.
- Answer for the owner, or act on an assumed answer.
- Read or print secrets.

## Stop and hand off

Stop when every step is `done` or `dropped`, or when everything left waits on the owner: set the board's state to `done` or `paused` with `tick --state`, notify once through the host with what waits, and end the host's loop (`references/platforms.md`).
Handing over to a different manager: the old one runs `tick --state paused` first, and the new one uses `--take-over` only for a manager confirmed stopped, with the reason logged.
When the manager's own context runs long, finish the tick, write the board, and restart the session with the same start prompt and the same manager id; the first-tick reconcile resumes it.
