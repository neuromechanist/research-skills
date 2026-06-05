# Review-subagent pattern (epic #61)

How review and QA surfaces are structured across the marketplace so that a review runs as an **independent, fresh-context subagent** on Claude Code, Codex CLI, and Copilot CLI, while staying installable from a single shared artifact.

## Why

Review validity depends on independence. A reviewer that shares the conversation that produced an artifact is biased toward it: it "remembers" the authoring rationale and quietly defends it. Running the reviewer in a separate context, with only the artifact and the rubric, gives a genuinely independent critique. Subagents also add parallelism (panel review) and keep verbose review output out of the main context.

## Binding constraint

All three CLIs support subagents (2026), but they differ in format and, critically, in packaging:

| Tool | Agent format | Discovery dir | Auto-bundled from an installed plugin? |
|---|---|---|---|
| Claude Code | Markdown + YAML frontmatter | plugin `agents/*.md` | **Yes** |
| Codex CLI | TOML | `~/.codex/agents/` or `.codex/agents/` | No (plugins distribute skills) |
| Copilot CLI | Markdown `.agent.md` | `.github/agents/` or `~/.copilot/agents/` | Not supported / not documented |

Only Claude Code ships agents inside an installed plugin. Therefore the portable, install-time artifact must be the **skill**, and the agents are thin per-tool shells.

## The invariant

For a review/QA surface named `<name>`:

- **`skills/<name>/SKILL.md`, thin dispatch.** Owns the user-facing trigger phrases. Body routes to the right execution path per tool and selects the mode. No rubric content.
- **`skills/<name>/references/`, the brain.** Rubric, criteria, procedure, output templates. Single source of truth. This is the only artifact all three ecosystems bundle on install, so the rubric must live here and nowhere else. (Engine scripts, where applicable, live in `references/` or a sibling `scripts/`.)
- **Per-tool shells, thin.** `agents/<name>.md` (Claude, bundled), `agents/templates/<name>.toml` (Codex), `agents/templates/<name>.agent.md` (Copilot). Each loads `references/` and emits the structured report. The Codex/Copilot templates are opt-in: the user copies them into `.codex/agents/` or `.github/agents/` because those tools do not bundle plugin agents.

## Trigger ownership

The **skill owns the triggers**. Each Claude agent's `description` is scoped to "invoked by the `<name>` skill; not triggered directly" so the skill and agent never compete to match the same natural-language request.

## Dispatch contract

`SKILL.md` selects a branch:

- **Claude Code:** `Task(subagent_type: "<name>", ...)`.
- **Codex CLI:** run the `<name>` subagent (`/agent`) after the template is installed.
- **Copilot CLI:** run the `<name>` agent (`/fleet` for parallel) after the template is installed.
- **Fallback:** no subagent support, or the user wants an interactive in-thread review -> run the procedure inline by following `references/`.

Pass only **framing** to the reviewer (artifact path, type/mechanism, target venue, resubmission status), never the authoring rationale. Independent must not mean blind.

## Mode contract (single vs panel)

- **Single (default):** one reviewer applies the full procedure.
- **Panel (opt-in, user decides each run):** N independent reviewers run in parallel, each scoring from `references/`, then a synthesis/chair pass reconciles them into one output (surface genuine disagreement; do not blindly average). Panel composition is domain-specific (grant: NIH 3-reviewer study section / NSF panel; paper: methods / statistics / novelty lenses).

## Reference implementation

`grant:grant-review` (epic #61, Phase 1) is the canonical implementation: thin `SKILL.md`, brain in `references/` (including the extracted `review-procedure.md`), Claude shell `agents/grant-review.md`, Codex/Copilot templates under `agents/templates/`, single + study-section panel modes, and an inline fallback.

## Rollout

- Phase 1 (#62, done): convention + `grant-review`.
- Phase 2 (#63, done): `paper-review`.
- Phase 3 (#64, done): retrofit existing QA agents `figure-qa` and `grant-figure-qa` to the pattern (thin skill in front, agent demoted to a shell, engine scripts kept).
- Phase 4 (#65): version bumps (patch: grant 0.3.5, manuscript 0.5.1, figures 0.10.2, marketplace 0.15.3), README, cross-phase review.

## Scope boundary (what does NOT get this pattern)

The pattern applies to **context-influenced reviews**: tasks where a fresh, unbiased look has real value because a reviewer sharing the authoring context would be biased (grant review, paper review, figure QA). It does **not** apply to **mechanical validators**, whose checks are deterministic and carry no context-bias risk: `bids-validator` (neuroinformatics), `dependency-auditor`, and `release-prep` (project) stay as plain skills. They are not retrofitted, and no follow-on epic is planned for them. The test: if running the task twice with and without knowledge of how the artifact was produced would change the verdict, it is a review (use the pattern); if not, it is a validator (leave it).
