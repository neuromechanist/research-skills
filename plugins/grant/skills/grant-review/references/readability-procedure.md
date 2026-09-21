# Grant Readability Review Procedure

This is a prose-only pass that runs before a merit review when the caller selects
`readability` mode. It is deliberately independent from NIH/NSF scoring: do not
assign scores, assess significance, or infer whether the proposal should be
funded. The purpose is to make the existing argument easier for a panelist to
follow without expanding the page count.

## 1. Establish the review scope

Read the proposal from a fresh context. Record the proposal path and the
available format. For a PDF, use page and section anchors and inspect the visual
line wrapping. For Markdown or LaTeX, use section and source-line anchors. Do
not rely on authoring rationale, previous reviews, or unstated domain context.

## 2. Check clarity patterns

Report only findings that affect first-read comprehension:

- sentences spanning roughly 2-3 typeset lines, especially when they chain
  independent claims;
- run-on clauses joined by repeated `and`, `but`, or `so`;
- `it`, `its`, `this`, or `that` with a distant or ambiguous referent;
- sentence-initial `And`, `But`, or `Nor`, rhetorical inversions, or negative
  framing that makes the literal claim harder to parse;
- names, groups, technical terms, or abbreviations used before introduction to
  a panelist outside the author's subfield;
- gratuitous self-undermining such as "we make no claim" when the evidence can
  be stated directly. Preserve substantive limitations, uncertainty, risks, and
  alternatives; those are not readability defects.

When the caller requests the optional **conciseness hunt**, also flag redundant
restatement, throat-clearing lead-ins, stacked intensifiers, and facts repeated
beyond their second appearance. A conciseness rewrite must be strictly shorter
while preserving every number, citation, qualification, and required element.

## 3. Write actionable findings

Every finding must include:

1. a severity (`Critical`, `Important`, or `Suggested`);
2. a page/section/source-line anchor;
3. the smallest quoted excerpt needed to locate the issue;
4. a length-neutral rewrite, unless this is a conciseness finding, in which case
   the rewrite must be shorter;
5. one sentence explaining the comprehension cost.

Do not rewrite a passage merely to express a stylistic preference. Preserve the
author's scientific meaning, numbers, citations, caveats, and technical terms.

## 4. Return the readability report

Use this structure:

```text
# Readability Review

## Scope
- Proposal: ...
- Mode: readability [plus optional conciseness hunt]
- Input coverage: ...

## Findings
### [Severity] [anchor] -- short title
- Original: "..."
- Rewrite: "..."
- Why: ...

## No finding
...
```

If no actionable clarity issue remains, say so explicitly and note any pages or
sections that could not be assessed. Do not append merit scores, an overall
impact score, strengths/weaknesses, or an NIH/NSF funding recommendation.
