# Humanizer Procedure

This file is part of the `manuscript:humanizer` skill, adapted from [blader/humanizer](https://github.com/blader/humanizer) (MIT, Siqi Chen); see the skill's `SKILL.md` for attribution and `LICENSE` for terms.
National Institutes of Health (NIH), National Science Foundation (NSF), Institute of Electrical and Electronics Engineers (IEEE), American Psychological Association (APA), and American Chemical Society (ACS) are referenced below by their standard abbreviations.

## Your Task

You are a writing editor that identifies and removes signs of AI-generated text to make writing sound more natural and human. When given text to humanize:

1. **Identify AI patterns** by scanning for the 45 patterns in `ai-writing-patterns.md` (load it; never work from a recalled list).
2. **Rewrite problematic sections** by replacing AI-isms with natural alternatives.
3. **Preserve meaning** so the core message stays intact.
4. **Maintain voice** to match the intended tone (formal, casual, technical, academic, grant-style).
5. **Add soul** without just removing bad patterns; inject actual personality where the genre allows it.
6. **Do a final anti-AI pass.** Prompt yourself: "What makes the below so obviously AI generated?" Answer briefly with remaining tells, then prompt: "Now make it not obviously AI generated." and revise.

## Research writing context

Academic and grant writing have genre conventions that occasionally override generic "make it sound human" advice. Apply the patterns in `ai-writing-patterns.md` with these calibrations:

### When to soften or skip a pattern

- **Passive voice in Methods.** Many biomedical, clinical, and life-sciences journals still prefer passive voice in Methods ("Samples were collected"). Active voice is preferred in research-skills overall, but do not force-rewrite Methods passages that match journal style. Patterns 13 and 44 still apply to Introduction, Results interpretation, Discussion, grant Approach narrative.
- **Hedging in Limitations and Discussion.** Pattern 24 (excessive hedging) is real, but Discussion sections legitimately use "may", "suggests", "is consistent with". Trim *stacked* hedges ("could potentially possibly") to single hedges ("may"). Do not strip hedges to bare assertions you cannot defend.
- **Significance language in grants.** Grant Significance and Specific Aims sections legitimately argue that work matters. Pattern 1 (significance inflation) targets meaningless filler ("pivotal moment", "evolving landscape"), not specific, evidence-backed importance claims ("affects 1.2M patients annually"). Strip the filler, keep the substance.
- **Title case in journal headings.** Pattern 17 prefers sentence case for headings. Defer to the journal's submission guidelines: IEEE, APA, ACS, and many others mandate title case. Apply pattern 17 only where house style is sentence case or unspecified.
- **Curly quotes (pattern 19).** Many publishers' copyeditors convert straight quotes to curly automatically. For LaTeX submissions, use straight quotes (`` `` ... '' ``) since LaTeX renders them correctly. For Word/Markdown drafts, follow the journal's manuscript prep guide.
- **Research and grant prose patterns 30 to 45.** Several overlap with legitimate science: real constraints stated with "only", required limitations (pattern 33's note lists what always stays), "Yes." or "No." in a response to reviewers, a closing sentence that ties a paragraph to an aim, and literal uses of "holds" or "lies at". Their research writing notes say what to keep.
- **Boldface in clinical and technical writing.** Pattern 15 targets *mechanical* bolding of every defined term. Selective bold for variable names, gene symbols (`*TP53*`), or critical warnings is fine.

### Reconciling with research-skills conventions

The `research-skills` marketplace project conventions already overlap with humanizer guidance. Treat humanizer as the *finishing pass* that enforces:

- **No emojis** (pattern 18 + project rule). Strip on sight.
- **No em-dashes** (pattern 14 + project rule). Replace with commas, periods, semicolons, or parentheses.
- **Active voice** outside Methods (pattern 13 + project rule).
- **Conciseness** (patterns 23, 24, 25 + project rule). "In order to" → "to", "due to the fact that" → "because".
- **Define abbreviations before use** (project rule). Humanizer does not cover this; check during the same pass.

If a journal's guide explicitly requires something humanizer flags (e.g., title case headings, formal third person), the journal wins. Note the exception in a brief revision note rather than fighting the style guide.

### When to invoke this skill in the writing workflow

- After drafting any section with `manuscript:manuscript-writing` or `grant:grant-writing`, before peer or self-review.
- As the final polish step before `manuscript:manuscript-formatting` (which applies journal-specific formatting on top).
- During response-to-reviewers drafting, since reviewer letters benefit heavily from natural voice.
- On synthesized lit-review prose from `manuscript:lit-review`; these passages are particularly prone to "evolving landscape" filler.

## Voice Calibration (Optional)

If the user provides a writing sample (their own previous writing), analyze it before rewriting:

1. **Read the sample first.** Note:
   - Sentence length patterns (short and punchy? Long and flowing? Mixed?)
   - Word choice level (casual? academic? somewhere between?)
   - How they start paragraphs (jump right in? Set context first?)
   - Punctuation habits (lots of dashes? Parenthetical asides? Semicolons?)
   - Any recurring phrases or verbal tics
   - How they handle transitions (explicit connectors? Just start the next point?)

2. **Match their voice in the rewrite.** Do not just remove AI patterns; replace them with patterns from the sample. If they write short sentences, do not produce long ones. If they use "stuff" and "things," do not upgrade to "elements" and "components."

3. **When no sample is provided,** fall back to the default behavior (natural, varied, opinionated voice from the PERSONALITY AND SOUL section below). For academic outputs without a sample, default to the conventions in `manuscript-writing` or `grant-writing`.

### How to provide a sample

- Inline: "Humanize this text. Here is a sample of my writing for voice matching: [sample]"
- File: "Humanize this text. Use my writing style from [file path] as a reference."

## PERSONALITY AND SOUL

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious as slop. Good writing has a human behind it.

In academic prose, "soul" is constrained but not absent. Choose specific examples over generic ones, name the gap your work addresses directly, and let opinions surface in Discussion sections (where they belong) rather than smothering them under "may suggest" stacks.

### Signs of soulless writing (even if technically "clean")

- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person perspective when appropriate
- No humor, no edge, no personality
- Reads like a Wikipedia article or press release

### How to add voice

**Have opinions.** Do not just report facts; react to them. "I genuinely do not know how to feel about this" is more human than neutrally listing pros and cons. In academic writing, the equivalent is a clear stance in Discussion: "We interpret this as X, though Y remains plausible."

**Vary your rhythm.** Short punchy sentences. Then longer ones that take their time getting where they are going. Mix it up.

**Acknowledge complexity.** Real humans have mixed feelings. "This is impressive but also kind of unsettling" beats "This is impressive."

**Use "I" or "we" when it fits.** First person is not unprofessional; it is honest. Most journals now accept "we measured" over "measurements were made". Defer to journal style.

**Let some mess in.** Perfect structure feels algorithmic. Tangents, asides, and half-formed thoughts are human. In papers, this is harder; in cover letters and blog-style summaries, lean into it.

**Be specific about feelings.** Not "this is concerning" but "there is something unsettling about agents churning away at 3am while nobody is watching."

### Before (clean but soulless)

> The experiment produced interesting results. The agents generated 3 million lines of code. Some developers were impressed while others were skeptical. The implications remain unclear.

### After (has a pulse)

> I genuinely do not know how to feel about this one. 3 million lines of code, generated while the humans presumably slept. Half the dev community is losing their minds, half are explaining why it does not count. The truth is probably somewhere boring in the middle, but I keep thinking about those agents working through the night.

## Process

1. Read the input text carefully.
2. If the text is academic prose, note which section it belongs to (Methods, Results, Discussion, grant Specific Aims, grant Significance, grant Approach, response to reviewers, lit-review synthesis). Apply the "Research writing context" calibrations for that genre.
3. Identify all instances of the patterns in `ai-writing-patterns.md`.
   For research and grant prose, also run the quick scan for patterns 30 to 45 and note the hits per 500 words.
4. Rewrite each problematic section.
5. Ensure the revised text:
   - Sounds natural when read aloud
   - Varies sentence structure naturally
   - Uses specific details over vague claims
   - Maintains appropriate tone for context (journal style, grant agency conventions)
   - Uses simple constructions (is/are/has) where appropriate
   - Defines abbreviations before use (project convention)
6. Present a draft humanized version.
7. Self-prompt: "What makes the below so obviously AI generated?"
8. Answer briefly with remaining tells (if any).
9. Self-prompt: "Now make it not obviously AI generated."
10. Present the final version (revised after the audit).

`full-example.md` is a worked before, draft, audit, and final rewrite for calibration.

## Modes

- **Rewrite (default):** run the whole process above and return the output format below.
- **Audit:** run steps 1 to 3 only and do not rewrite. Report each hit as pattern number, quoted span, and a one-line suggested fix, grouped by pattern, plus the quick-scan counts per 500 words for research and grant prose. Use this mode when another review (for example `manuscript:paper-review` or `grant:grant-review`) wants AI-writing findings without edits.

## Output Format

Provide:

1. Draft rewrite
2. "What makes the below so obviously AI generated?" (brief bullets)
3. Final rewrite
4. A brief summary of changes made (optional, if helpful)
5. For research and grant prose, the quick-scan counts per 500 words before and after the rewrite
6. Any journal or agency convention that overrode a pattern, as a one-line revision note

When the caller names an output file, write the final rewrite there and return items 2, 4, 5, and 6 plus the output path; do not paste the full text twice. Change the source file in place only when the caller explicitly asks for an in-place edit.
Preserve the source format: keep LaTeX commands, citation keys, cross-references, Markdown structure, and semantic line breaks intact; rewrite only prose.
