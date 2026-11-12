# __TITLE__

<!--
manager-loop board: state only, history goes to the -log file beside it, specs to the plan and cards.
Write through the helper (manager_board.py set, tick, ask, propose, spend) and run `check` after any hand edit.
The owner owns Parity, Slots, and Budget limits: the manager proposes changes there, never makes them.
These are the defaults; the owner's approval of the plan accepts them.
Step states: outline (not dispatchable), todo, active, review, blocked, owner (waits on the owner), done, dropped.
In Steps and Questions, the first column holds each row's identifier (ID); in Steps, PR holds the pull request (PR) number.
-->

## Now

| Key | Value |
|---|---|
| Plan | __PLAN__ |
| Repo | __REPO__ |
| Integration branch | __BRANCH__ |
| Manager id | - |
| State | paused |
| Cadence | 30m with workers running, 60m waiting on people |
| Last tick | - |
| Next tick | - |
| Stop when | every step done, or all remaining work waits on the owner |
| Created | __CREATED__ |

## Parity

| Tier | Claude | Codex | Copilot | Notes |
|---|---|---|---|---|
| worker | Sonnet high | gpt-6-luna max | balanced coding model | routine cards from a detailed plan |
| worker-hard | Sonnet xhigh | gpt-6.1-terra xhigh | balanced reasoning model | protocol, concurrency, security, contract work |
| lead | Opus xhigh | gpt-6.1-sol xhigh | strong reasoning model | default for planning, design, first-level advice |
| frontier | Fable | gpt-6-astra xhigh | strongest model | only when the owner asks, for long-horizon planning, or a frontier trigger the plan lists |
| reviewer | Sonnet high | gpt-6-luna max | balanced coding model | a different model family from the implementer when possible |

## Slots

| Slot | Platform | Tiers | Max | Can | Notes |
|---|---|---|---|---|---|
| claude-sonnet | Claude | worker, worker-hard | 3 | gui, browser | graphical user interface (GUI) or computer use only with the owner's announced consent |
| claude-opus | Claude | lead | 1 | gui, browser | |
| codex | Codex | worker, worker-hard, lead | 0 | | owner opens this slot; never computer use or visible runs |

## Budget

| Item | Limit | Used | Resets | Notes |
|---|---|---|---|---|
| Agents today | 40 | 0 | daily | implementers, reviewers, advisors spawned; the plan approval covers this limit |
| Agents this wave | 15 | 0 | wave | items x (1 + review panel + 1 delta + fix rounds) + 1 advisor |
| Advisor consults | 3 | 0 | never | lead tier; frontier only when the owner or the plan says |

## Waves

| Wave | Goal | Agents | State | Exit gate |
|---|---|---|---|---|

## Steps

| ID | Title | Wave | Tier | Needs | Slot | State | Depends | PR | Started | Timebox | Next |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Questions

| ID | Step | Question | Options | Default | Needed by | State | Answer |
|---|---|---|---|---|---|---|---|

## Proposals

| ID | Time | Proposal | Why | State |
|---|---|---|---|---|

## Agents

| Agent | Role | Slot | Model | Step | Started | State |
|---|---|---|---|---|---|---|
