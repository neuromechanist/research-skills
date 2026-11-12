# Escalation, Advisors, and Owner Questions

Judgment leaves the manager by three routes: the lead (design and cards), the advisor (a one-off read-only consult), and the owner (decisions only the owner can make).
Each route has mechanical triggers, so a literal manager knows when to use it.

## Triggers

| Trigger | Route |
| --- | --- |
| A step past twice its timebox, or two failed approaches | advisor (lead tier) |
| A security, data-integrity, concurrency, or authorization invariant is in play | advisor (lead tier), before any fix |
| A contested review finding (implementer and reviewer disagree) | advisor (lead tier) |
| A red gate on the integration branch | advisor (lead tier); stop merging into it |
| The same gate step flaky twice in seven days | lead: a diagnosis card |
| A PR that relaxes a gate's assertion | lead; never merge it on the manager's authority |
| An owner answer that contradicts a card's assumption | lead: correct the card before dispatch |
| A projected budget overrun (remaining work x measured median / free slots > time left) | owner: apply the plan's next drop rule only if pre-authorized, otherwise ask |
| The lead tier cannot decide, or the same item looped three times, or a long-horizon question (strategy, priorities across the whole plan) | advisor (frontier tier) |
| A decision only the owner can make (scope, dates, money, outward actions, a merge the host refused, parity or budget changes) | owner question |

## The advisor

The lead tier first (Opus; Codex Sol), the frontier tier (Fable; Codex Astra) only by the ladder above, as the board's Parity table maps them. `spend <board> "Advisor consults"` before each one.

### Brief (one file, under 600 words)

```text
You are an independent advisor (read-only). Do not edit, commit, or run anything that changes state.
State: <what is true now, with numbers and links: board status, the step, the PR, the failing gate>.
Questions (at most three): <exact questions>.
Read: <paths and PRs, in order>.
Constraints: <decided policies that stand; budgets; dates>.
Verify facts yourself and say where this brief is wrong.
Answer in under 1,200 words, in the format below.
```

### Output format

1. `VERDICT:` one line (for a design: SOUND, SOUND WITH CHANGES, UNSOUND; for a stuck step: the recommended path).
2. Findings table: id, severity (blocker, major, minor, note), finding, concrete fix.
3. Ranked recommendations.
4. Top three risks.
5. Decisions for the owner, as structured questions with a recommended option.
6. Not verified by the advisor.

The manager records the verdict and the ranked recommendations with `decide`, posts them on the PR when a PR is involved, sends card changes to the lead, and turns the owner decisions into board questions.
It does not act on a recommendation that changes the plan, a card, or a gate until the lead or owner accepts it.

## Owner questions

### Format

Every question has: an ID, the question in one sentence, two to four options (one marked `(Recommended)`, each with a one-line reason in the question text or the session message), the default (`none` unless the owner pre-authorized defaults for this class), the time it is needed by, and what waits on it.

```bash
python3 <skill>/scripts/manager_board.py ask <board> Q7 \
  --question "Codex quota is at 80 percent with 9 steps left; how should the remaining cards run?" \
  --options "Open a Copilot slot with Max 2 (Recommended) / Keep Claude and Codex and slow down / Raise the Codex budget" \
  --default none --needed-by 2026-11-14T17:00 --step E2.1
```

### Asking

1. Record it on the board (above). The board is the record on every host.
2. If the owner is in an interactive session, ask with the host's structured question tool, batching related questions (Claude Code AskUserQuestion, up to four; Codex `request_user_input`, one to three, interactive root thread only; Copilot CLI `ask_user`).
3. Otherwise send one notification (Claude Code PushNotification where available) naming the question IDs and what waits, and keep working on independent steps.
4. When an answer arrives (session, board page, or `answer`), act on it, `decide` it with "by owner", and set the question `closed`. `archive` clears closed questions from the board.

Never answer for the owner. Never treat silence as an answer.
A default applies at its deadline only for a question class the owner pre-authorized in the plan (for example "an escalation's stated default applies at its deadline"); the manager sets the question `defaulted`, logs it, and says so in the next notification.

## Notifications

Notify only for: an owner question asked, a step that waits on the owner, a gate or milestone the plan names, a checkpoint digest, a visible GUI run about to start (with its stop file), or the manager itself late or stopped.
At most one notification per event class per day, except a visible run, which is announced every time.

A checkpoint digest has five lines: what merged since the last checkpoint, the critical-path item and its date, idle capacity, budget used against limits, and the decisions waiting (question IDs).

## Denied permissions and refused merges

A permission prompt the owner denied, or a merge the host's auto mode refused, is information, not an obstacle.
Do not retry it, do not route it through another agent, and do not look for a different command that does the same thing.
Set the step to `owner`, ask a question that names the exact command and why it is needed, and continue with other steps.
