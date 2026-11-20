---
name: humanizer
description: "Use this skill for \"humanize this text\", \"remove AI tells\", \"make this less AI-sounding\", \"strip AI patterns\", \"de-AI my writing\", \"reduce AI-isms\", \"final natural-writing pass\", \"check for AI vocabulary\", \"em dash overuse\", \"rule of three overuse\", \"AI vocabulary\", \"signs of AI writing\", \"AI tells in grant prose\", \"too much passive voice\", \"ambiguous pronouns\", or when polishing prose (papers, grants, lit reviews, abstracts, cover letters, responses to reviewers) to remove signs of AI-generated text while preserving meaning and discipline-appropriate conventions."
version: 0.4.0
---

# Humanizer: Remove AI Writing Patterns

Routes prose to an **independent, fresh-context editor** that finds and removes signs of AI-generated text while preserving meaning and discipline conventions. This skill is a thin dispatcher: it decides how to run the editor and in which mode. The procedure, the 45-pattern catalog, and the worked example live in `references/` and are loaded by the editor, not duplicated here.

## Attribution

This skill is adapted from the upstream `humanizer` skill at https://github.com/blader/humanizer (v2.5.1) by Siqi Chen, released under the MIT License. The upstream patterns are themselves a distillation of [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup.

**Upstream content (preserved with minor copyedits):** the 29 AI-writing patterns and their before/after examples (`references/ai-writing-patterns.md`); the "Personality and Soul", "Voice Calibration", "Process", and "Output Format" sections (`references/humanizer-procedure.md`); the "Full Example" (`references/full-example.md`); and the closing "Reference" note.

**Additions for the research-skills marketplace:**

- The YAML frontmatter (rewritten in marketplace `description` style with academic-trigger phrases).
- The "Research writing context" section (including the "When to soften or skip a pattern", "Reconciling with research-skills conventions", and "When to invoke this skill in the writing workflow" subsections) and the "Modes" section, in `references/humanizer-procedure.md`.
- The per-pattern "Research writing note" callouts on 15 of the 29 patterns.
- The "Research and grant prose patterns" section (patterns 30 to 45 and the quick scan), drawn from revising AI-assisted grant drafts that had already passed patterns 1 to 29; patterns 44 and 45 come from a PI's line edits of such a draft.
- The fresh-context dispatch in this file and the agent shells that load `references/`.
- The "Cross-references in the research-skills marketplace" section near the end.

The MIT license is preserved in the `LICENSE` file in this skill directory; the additions above are released under MIT as well to keep upstream compatibility.

## Why a fresh-context editor

The session that drafted a text has normalized its own tells: it reads its phrasing as intended, and it is biased toward keeping it. A separate editor sees only the text, the genre, and the venue, which is what a human reader sees. The pattern catalog is also long (about 750 lines), and loading it into the drafting session crowds out the work it is polishing. Pass only **framing** (text or file path, section or genre, target journal or agency, voice sample, mode, output path), never the drafting rationale.

## Modes (caller decides each run)

- **Rewrite (default):** the full process in `references/humanizer-procedure.md`: draft rewrite, AI-tell audit, final rewrite, change summary, and quick-scan counts for research and grant prose.
- **Audit:** report pattern hits with quoted spans and suggested fixes, without rewriting. Use it when a review wants AI-writing findings, or when the user wants to make the edits themselves.
- **Long documents (opt-in split):** for a document over about 3,000 words, run one editor per major section in parallel, passing each the same voice sample and the abbreviations already defined in earlier sections, then read the joined result once for consistent terms and abbreviation definitions.

Edits land in the source file only when the user asks for an in-place edit; otherwise the editor writes to a named output file or returns the text.

## Dispatch

Pick the branch for the current tool. In every branch the editor follows `references/humanizer-procedure.md`.

- **Claude Code:** `Agent(subagent_type: "manuscript:humanizer", ...)` passing the text or file path, genre or section, target venue, voice-sample path if any, mode, and output path. For a split long document, issue one `Agent` call per section in a single message so they run in parallel.
- **Codex CLI:** plugin installation exposes this skill, not a Codex subagent. To use a fresh-context Codex editor, first copy `agents/templates/humanizer.toml` to `~/.codex/agents/` or `.codex/agents/`, then invoke that configured agent if the current Codex surface supports `/agent`. If no Codex subagent is configured or available, use the fallback branch.
- **Copilot CLI:** plugin installation exposes this skill and, through `.github/plugin/plugin.json`, the `.agent.md` editor in `agents/templates/`. Invoke that configured agent when the current Copilot surface supports custom agents. If running outside a plugin install, copy `agents/templates/humanizer.agent.md` to `.github/agents/` or `~/.copilot/agents/`. If no custom agent is available, use the fallback branch.
- **Fallback** (no subagent support, a short passage of a few sentences, or the user wants an interactive in-thread pass): first locate the references (`$CLAUDE_PLUGIN_ROOT/skills/humanizer/references`, else `find . -type d -path '*/skills/humanizer/references' | head -1`); if they cannot be found, stop and tell the user to install the manuscript plugin rather than working from a recalled pattern list. Then follow `references/humanizer-procedure.md` directly in this context.

## The brain (do not duplicate into dispatch or agent shells)

- `references/humanizer-procedure.md` -- the task, research writing calibrations, voice calibration, personality guidance, process, modes, and output format.
- `references/ai-writing-patterns.md` -- the 45 patterns with before/after examples, research writing notes, and the quick scan for patterns 30 to 45.
- `references/full-example.md` -- worked rewrite for calibration.

## Cross-references in the research-skills marketplace

Invoke each installed skill by its fully qualified `<plugin>:<skill>` name through the host's skill-invocation mechanism. Keep host-specific command or tool syntax in the host adapter, not in shared skill instructions.

- `manuscript:manuscript-writing` for paper drafting and section-level guidance. Run humanizer after drafting and before review.
- `manuscript:paper-review` for peer-review feedback. Humanizer is often the right fix for a "writing quality" comment from a reviewer.
- `manuscript:manuscript-formatting` for journal-specific formatting. Run humanizer first; formatting applies house style afterward (title case, citation style, etc.).
- `manuscript:lit-review` for literature-review prose. The synthesized passages from lit-review are particularly prone to "evolving landscape" and "growing body of work" filler.
- `grant:grant-writing` for NIH/NSF proposals. Run humanizer on Specific Aims, Significance, Innovation, and Approach narrative. Pay extra attention to patterns 1 (significance inflation), 4 (promotional language), and 24 (excessive hedging), and to the research and grant prose patterns 30 to 45 with their quick scan; defer to the funding mechanism's formatting for patterns 17 (title case) and 19 (curly quotes).
- `grant:grant-review` for proposal critique. Patterns most relevant to grant prose: 1 (significance inflation), 4 (promotional language), 7 (AI vocabulary), 8 (copula avoidance), 14 (em-dash overuse), 24 (excessive hedging), 25 (generic positive conclusions), and the research and grant prose patterns 30 to 45. These often surface as "writing quality" or "lack of specificity" reviewer comments.

## Reference

This skill is adapted from [blader/humanizer](https://github.com/blader/humanizer) (MIT, Siqi Chen, 2025), which is itself based on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (WikiProject AI Cleanup).

Key insight from Wikipedia: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."
