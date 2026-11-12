# The Board

`board.md` is the loop's state and its single source of truth.
`board-log.md`, beside it, is the history (Decisions and Log), append-only.
Everything else (the HTML view, the status summary, the dispatch plan) is computed from the Markdown on demand; nothing derived is stored.

Two failure modes shaped this format.
Status files that also held history grew past 150 KB, with cells of several thousand characters, and in-place edits started to fail silently.
A board that every tick reads in full spends the manager's context on the past.
So the board holds state only, within hard limits, and history goes to the log.

## Sections

| Section | Owner | Columns | Notes |
| --- | --- | --- | --- |
| Now | manager | Key, Value | Plan, Repo, Integration branch, Manager id, State, Cadence, Last tick, Next tick, Stop when |
| Parity | owner | Tier, one column per platform, Notes | add a platform by adding a column; see `platforms.md` |
| Slots | owner | Slot, Platform, Tiers, Max, Can, Notes | Platform names a Parity column; Can lists capabilities |
| Budget | owner sets Limit; manager updates Used | Item, Limit, Used, Resets, Notes | Resets: never, daily, or wave |
| Waves | lead, then manager sets State | Wave, Goal, Agents, State, Exit gate | optional; states planned, active, done, hold; setting a wave `active` resets the wave budgets |
| Steps | manager | ID, Title, Wave, Tier, Needs, Slot, State, Depends, PR, Started, Timebox, Next | table order is dispatch priority |
| Questions | manager asks; owner answers | ID, Step, Question, Options, Default, Needed by, State, Answer | states open, answered, closed, defaulted |
| Proposals | manager | ID, Time, Proposal, Why, State | states open, accepted, rejected, withdrawn |
| Agents | manager | Agent, Role, Slot, Model, Step, Started, State | ids needed to message or resume a worker |

Other `##` sections are kept and shown as text; use them sparingly.

### Step states

`outline` (not dispatchable until the lead completes the card), `todo`, `active`, `review`, `blocked` (say on what in Next), `owner` (waits on the owner), `done`, `dropped`.
A step is ready when it is `todo`, every step in Depends is `done`, and its wave (if the board has waves) is `active`.

### Waves and budgets

Setting a wave's State to `active` (`set Waves <id> State=active`) resets every Budget row whose Resets is `wave` to 0 and logs the reset, so the new wave starts with its full wave budget.
A step spends the wave budget only when it belongs to a wave.

### Values

- Lists (Depends, Needs, Tiers, Can) are comma-separated.
- Options are separated by ` / `; mark one with `(Recommended)`.
- Times are written year-month-day, `T`, hour:minute (`2026-11-14T17:00`), optionally with a numeric offset; the helper writes local time with its offset.
- Timebox is a duration (`4h`, `2d`); `status` flags a step past its timebox and past twice its timebox.
- Titles may link to the card: `[Store v3](cards/E1.1.md)`.
- A literal `|` in a cell is written `\|`.

## Limits

`check` fails a board over 300 lines or with a cell over 240 characters.
Detail belongs in the card, the PR, or the log.
`archive` moves settled questions and proposals to the log; done steps stay as the board's Done lane.

## The dispatch plan

`status` walks ready steps in table order and puts each on the first slot that has room, accepts the step's tier, and can do everything the step needs.
It prints the model the slot runs for that tier (from Parity), the steps that cannot be placed and why, and idle slots when nothing is ready.

## The lease

`tick --manager <id>` records the manager's id and its next wake.
The id is stable per manager, `<host>-<model>` (for example `mba-claude-sonnet`), never per session, so a restart or a headless tick of the same manager keeps the lease.
A second manager calling `tick` with a different id before that wake (plus ten minutes) is refused, which prevents double dispatch and double merge when a scheduled tick overlaps a live session.
The refusal prints the lease expiry; the refused manager schedules one wake at that time and does nothing else.
The first tick of a session passes `--state running`.
`tick --state paused`, `stopped`, or `done` clears Next tick and releases the lease, and `status` reports the manager as late only while State is `running`.
Handing over to a different manager: the old one runs `tick --state paused` first.
`--take-over` is only for a manager confirmed stopped; log why (`--note`).

## Writing

The helper is the normal writer: every write takes a lock, re-reads the file, applies one change, validates the result, and replaces the file atomically; an invalid result is refused and the file is left as it was.
The lock is on the board's directory, so it holds across sandboxes; it is POSIX-only (macOS, Linux, Windows Subsystem for Linux).
The owner may hand-edit Parity, Slots, and Budget limits; anyone who hand-edits runs `check` afterward.
Workers never write the board; they report to the manager.

## Commits

Commit the board and its log locally each tick (`docs: board, <what changed>`).
Push them only at checkpoints and milestones, on a docs branch or the integration branch as the plan says, with `[skip ci]` when no CI job reads them.
Never commit the HTML snapshot; it is regenerated.

## The live page

```bash
nohup python3 <skill>/scripts/manager_board.py serve <board.md> --port 8765 > /tmp/board-serve.log 2>&1 & disown
```

- Binds `127.0.0.1` by default; requests with any other Host header are refused, so other web pages cannot read it through DNS rebinding.
- The page re-reads the board every 5 seconds and redraws only when something changed.
- Answer buttons post to `/answer` with a per-run token embedded in the page; an answer is recorded only for an open question, at most 200 characters, through the same locked write as the helper.
- It serves the board, its JSON, and `.md` files inside the board's folder (cards, the plan pack), read-only; nothing else.
- To view it from another machine, use an SSH tunnel (`ssh -L 8765:127.0.0.1:8765 <host>`), not `--host 0.0.0.0`.
- `render` writes a static snapshot (`board.html`) for sharing a moment in time; its answer buttons are disabled.

The board can carry paths, hashes, and answers. Do not publish it or the snapshot unless the owner asks.
