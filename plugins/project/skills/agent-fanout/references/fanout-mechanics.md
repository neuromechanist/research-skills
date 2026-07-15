# Fan-Out Mechanics: The Plumbing

Concrete, tool-by-tool instructions for spawning, addressing, and supervising
agents. Written for a model that has never done this before. Skip to your
tool's section; the concepts transfer.

## Concepts (all tools)

- **Subagent (one-shot)**: spawned with a prompt, runs, returns one final
  message, ends. Use for bounded questions and single deliverables.
- **Teammate (named, persistent)**: spawned with a name, stays addressable.
  You can send follow-up work, corrections, and stand-down messages without
  respawning. Use for anything with revision rounds (implementers, recurring
  scouts).
- **The final message is the deliverable.** Instruct every agent that its last
  message must contain the full report or result. Subagents are often blocked
  from writing report files, and an "idle" or "completed" notification does
  NOT mean the report arrived. If an agent goes idle without delivering, nudge
  it (template in `fanout-prompts.md`).
- **Isolation**: agents that edit code in parallel must not share a working
  tree. One git worktree per implementer (commands below). Read-only agents
  need no isolation.

## Claude Code

**Spawn** with the Agent tool. Parameters that matter:

- `prompt`: the full brief (see `fanout-prompts.md`; never a bare task line).
- `subagent_type`: `Explore` for read-only search, `Plan` for architecture
  plans, `general-purpose` for implementation, or a plugin agent such as
  `project:pr-review-toolkit` for reviews.
- `model`: use Fable/Opus (or inherit a strongest-tier session) for macro
  architecture, Sonnet for approved-plan implementation and routine review.
  A phase-plan elaborator may use Sonnet only when every architecture decision
  is already fixed; otherwise it inherits the lead model.
- `name`: set a role-descriptive name (`engine-scout`, `fix-661`,
  `phase2-reviewer`) whenever you may need to follow up. A transcript that
  reads "engine-scout reported X" stays legible.
- Spawn all independent agents of a wave in ONE message (parallel tool calls).

**Address later** with `SendMessage({to: "<name>", message: ...})`: follow-up
tasks to a live scout, revision rounds to an implementer, corrections,
stand-downs. Prefer messaging the same agent over respawning; it keeps context.

**Track** with the task tools: `TaskCreate` one task per work item (one per
issue/PR), `TaskUpdate` with `owner` when assigning, `addBlockedBy` to encode
ordering ("start after #662 lands"). The task board, not the conversation, is
the swarm's source of truth. Mark a task completed only when its own stated
criterion is met (usually merged, not PR-opened).

**Background shell work**: use `run_in_background` Bash for watch-then-act
chains, e.g. wait for CI then merge then clean up in one call:

```bash
gh pr checks 235 --watch --fail-fast >/dev/null 2>&1 \
  && gh pr merge 235 --merge --delete-branch \
  && git -C /abs/path/repo pull --ff-only
```

**Completion semantics**: you are notified when agents finish. Duplicated
idle/completion notifications happen; verify against what you already
received and acknowledge duplicates explicitly ("confirmed duplicate, nothing
further needed") rather than redoing work.

After harvesting a final report, stop/remove the agent unless it has a named
recurring role and a concrete next task. Do not retain completed agents merely
because they might be useful later.

## OpenAI Codex

Current Codex clients support native subagents and personal or project custom
agents. Put standalone TOML agent files under `~/.codex/agents/` (personal) or
`.codex/agents/` (project). Each file requires `name`, `description`, and
`developer_instructions`; it may also set `model`, `model_reasoning_effort`,
`sandbox_mode`, MCP servers, and skills.

Route roles explicitly when the current account exposes the aliases:

- lead/architect/observer/synthesizer: `gpt-5.6-sol`;
- bounded phase-plan elaborator: `gpt-5.6-terra`;
- detailed implementation, focused tests, routine review, validation:
  `gpt-5.6-luna`.

Use the built-in `explorer` for bounded read-heavy mapping and `worker` for
execution when custom role files are unnecessary. Use `/agent` in the CLI, or
the corresponding agent controls in the app/IDE, to inspect, steer, stop, and
close threads. After collecting a report, close the thread unless the plan
names an immediate follow-up.

If the spawn surface does not expose a per-call model choice, select a custom
agent whose TOML pins the intended model. If the exact alias is unavailable,
preserve the role class: strongest lead, intermediate elaborator, clear-task
worker. This plugin ships opt-in `phase-planner.toml` (Terra) and
`implementation-worker.toml` (Luna) under `agents/templates/`; copy them to the
Codex user or project agent directory before use.

## GitHub Copilot CLI

Copilot personal agents live under `~/.copilot/agents/`; project agents live
under `.github/agents/`. Set the optional `model` frontmatter field only when
the selected Copilot environment exposes a stable model identifier. Otherwise
use the strongest/balanced/worker capability classes from the main skill. Use
`/agent` to inspect and switch agents, and remove completed one-off agents when
their reports are incorporated. The plugin exposes matching `phase-planner`
and `implementation-worker` agent profiles through its native Copilot manifest.

## Tools without native subagents

Two options:

1. **Configured agents**: copy or adapt the plugin's agent templates into the
   current tool's user or project agent directory.
2. **Sequential fresh contexts**: run each role's prompt from
   `fanout-prompts.md` as its own fresh session or context, in dependency
   order: explorers first, then planner, then implementers (one per worktree,
   still isolated via git worktrees), then reviewers. You lose wall-clock
   parallelism but keep the two properties that matter: fresh eyes per role
   and scoped briefs. Record each role's report in a file under `.context/`
   so the next role can read it.

The budget still applies: count the total role-runs before starting; 10-20
per task is the routine budget, 40 the hard cap (see the skill's Hard limits
section).

## Git worktree isolation (all tools)

One worktree per implementer, cut fresh from the integration branch. Paste
these literal commands into the implementer's brief; never leave naming to the
agent when several run concurrently:

```bash
git -C /abs/path/repo fetch origin develop
git -C /abs/path/repo worktree add ../repo-issue-N -b fix/issue-N-<slug> origin/develop
# Work ONLY inside /abs/path/repo-issue-N. Use absolute paths.
```

Cleanup after merge (never force-remove a dirty worktree without approval):

```bash
git -C /abs/path/repo worktree remove ../repo-issue-N
git -C /abs/path/repo branch -d fix/issue-N-<slug>
```

## Long-running jobs spawned by agents

Any job over ~10 minutes (benchmark, training, batch) must be detached so it
survives session compaction: `nohup ./job.sh > /tmp/job.log 2>&1 & disown`,
then watch the log (not the shell). Details and job-script requirements are in
the engineering-loop skill's `references/background-jobs.md`.

## Sizing worked example

Task: review a platform with 6 subsystems, verify findings, fix confirmed
bugs. Worst case: 6 reviewers x up to 8 findings each = 48 potential
verifications. That exceeds the 40-agent cap before implementers exist, so cut
before launching: cap findings at 5 per reviewer in the prompt, verify with 1
vote instead of 3 (6 + 30 = 36), or batch verification after deduplication
(usually collapses 48 raw findings to 15-20 unique). Then add implementers one
wave later, reusing the budget freed by completed agents only if the user has
approved continuing.
