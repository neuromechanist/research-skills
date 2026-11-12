# The Plan Pack

What the lead writes before the first tick, so that a mechanical manager can run the plan without reconstructing intent.
Distilled from three long-running loops: a research rebuttal (six days, a Sonnet manager and a persistent Opus science lead), an application track (84 cards, about 75 merged PRs in three days, Claude and Codex slots), and a web product (waves of at most three implementers driven by a project manager).

## Layout

```text
.context/plans/<name>/
  plan.md          the plan (or a link to it), with section 0 for the manager
  runbook.md       the manager's tick and event handlers (optional when the plan's section 0 is enough)
  cards/README.md  the shared worker preamble and common rules
  cards/<ID>.md    one self-contained card per step
  queue.md         slot lists and the Collisions table (when slots are used)
  checkpoints.md   scheduled lead reviews and their triggers
  risks.md         pre-registered risks
  board.md         state (manager_board.py init)
  board-log.md     Decisions and Log, append-only
```

## The plan

Every step has: an ID, a one-sentence goal, a literal acceptance gate (commands and thresholds, set before any result is seen), dependencies, the files it owns, the host it runs on, and a tier (not a model).
A step the lead cannot specify yet is an `outline`; it is completed at a named checkpoint and is never dispatched before.

Section 0 of the plan, "How the manager uses this plan", holds:

1. The start prompt (below) and the pacing rule.
2. The tick, or a pointer to the runbook.
3. Precedence: the owner's later instructions override the plan and are logged with `decide`; the repository's `AGENTS.md` overrides the plan except where the plan names an explicit exception.
4. Merge authority: which PRs the manager may merge after the merge gate (usually every step PR into the integration branch), and which it never merges (releases, deploying repositories, anything outward).
5. The question classes that may take a default at their deadline (none unless listed).
6. Routing: any frontier trigger the plan lists (for example "frontier tier when the lead tier cannot decide, or after three loops"); with none listed, the frontier tier is used only when the owner asks.

### Start prompt template

```text
/loop You are the manager of <project> <track>. Run one tick of the runbook at <absolute path to runbook.md>, exactly as written, using the project:manager-loop skill. The state is the board beside it: <absolute path to board.md>. Do not write product code. Do not change the plan, a card, a gate, the parity, or a budget limit. When the runbook says to stop or to ask, or does not cover what you see, record it on the board, ask the owner with a structured question, and stop that thread of work.
```

No interval: the manager paces itself (30 minutes while workers run, 60 while it waits on people; a worker's completion wakes it sooner).

## The runbook

Short sections the manager can follow literally:

- What to read: every tick, `status` and the events it points to; at a session's first tick, the runbook, the queue, the checkpoints, and the risks, once; never the whole log or large evidence.
- The tools table: how to dispatch on each platform, how to message a running worker, how to notify, how to ask, how to wake (see `platforms.md`).
- First tick, the tick, and one section per event: a report arrives, a review returns, a check fails, a gate fails, a timebox expires, a worker goes silent, an owner answer arrives, a date arrives, a checkpoint is due.
- What you must never do (start from the skill's "Never" list and add the project's own).

## Cards

A card is dispatched verbatim, with only live facts added (the integration tip, a baseline path and checksum, open PRs) copied from the board at dispatch time, never from an earlier prompt.
Start from `assets/card-template.md`.
`manager_board.py card cards/<ID>.md` refuses a card that is an outline, misses a required section, has an empty section, names no literal command in Acceptance or Gates, or holds a placeholder such as TBD.

Required sections: Goal, Scope, Acceptance, Gates, Stop conditions, Report.
Recommended: Context (what to read first), Decided design ("Settled: ...; the implementer may choose: ..."), Timebox ("L, 2 days; escalate at 4 days or two failed approaches").

### The worker preamble (cards/README.md)

Every card is sent after the same preamble:

- One card, one branch, one PR, in the worktree named on the card. Absolute paths.
- Only the manager merges. Push once per review round. Never force-push or rebase a pushed branch.
- Stay inside Scope; anything else goes in the report as a patch note for its owner.
- Run every gate yourself and quote its output; a computed value is never reported as measured.
- Stop and report on any stop condition, or when the card seems wrong.
- No computer use, no visible GUI runs, no secrets.
- The final message is the report, in the card's schema.

### The report schema (at most 25 lines)

PR number and head SHA; gates run, with their quoted last lines; evidence paths; revert checks per fix; deviations from the card; questions for the lead; patch notes for other owners.
Codex workers can return it against a JSON schema with `codex exec --output-schema`.

## Slots and collisions (the default)

`queue.md` lists, per slot, the cards in priority order with each card's entry condition.
The board's Steps table carries the same order: `status` dispatches the first ready step that fits a free slot.
A Collisions table names every pair of cards that could touch the same files, with the rule:

| Pair | Shared | Rule |
| --- | --- | --- |
| W3.1, W3.5 | the launch agent's unit | W3.5 after W3.1 merges |
| W2.4, W2.22 | the window classes | may run together; the second to merge takes the base in and reruns its gate |

Encode "after" rules as `Depends` on the board so `status` enforces them.

## Named waves (when the plan chooses them)

A wave is a standalone unit: named members, its own agent budget, an exit gate, and an owner checkpoint when it closes.
Use one when the members are independent modules with disjoint files and the owner wants to look at each batch, or when a workflow script drives each batch end to end.
Do not use one for steps that share files or a serialized resource, for sequential dependencies, or when review or lead attention is the bottleneck.

| Wave | Goal | Agents | State | Exit gate |
| --- | --- | --- | --- | --- |
| W1 | conversation basics | 15 | active | E1.1, E3.1, E5.3 merged and verified on the staging site |
| W2 | per-dataset history | 15 | planned | E1.2, E1.3, E4.1 merged |

Inside an active wave, steps still flow through slots: a member starts when its slot frees, not when the whole wave can start.

### Sizing a wave's budget

`members x (1 implementer + round-1 panel size + 1 delta reviewer + expected fix dispatches) + 1 advisor`

Three members with a two-reviewer panel and one fix dispatch each: 3 x (1 + 2 + 1 + 1) + 1 = 16.
Eight members with a three-reviewer panel: about 50, which needs explicit owner approval; split the wave instead.
The owner approves the wave and daily limits with the plan; that approval is what `agent-fanout`'s cap asks for.

## Checkpoints and risks

Checkpoints are scheduled lead reviews (for example after each wave, weekly, or when a trigger fires).
The lead reads only what the checkpoint row lists, completes the outline cards that are due, updates risks, and produces one docs PR with a note of at most one page.
The manager runs the anticipation pass at each checkpoint; the parity question waits for a mismatch (see the skill).

Each risk is pre-registered with an observation, a date by which it is read, what happens if it reads bad, and who decides.
A decision date is not a deadline for the work; it is the day on which nobody may keep hoping.

## Reviewing the pack before the loop

Three lenses, each a fresh agent, every finding with a disposition in the plan's appendix:

1. Executability (worker tier): could a literal manager run this? Missing gates, circular dependencies, ownership collisions, missing escalation defaults.
2. Design (lead tier or advisor): is the approach sound and the scope right?
3. Domain (for research: an area-chair style reviewer; for products: a user-facing reviewer).

Then `manager_board.py check` on the board and `card` on the first cards of every slot list.
