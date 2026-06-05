# Manuscript Review Procedure

The step-by-step procedure for peer-reviewing an academic manuscript with priority on methodological soundness, statistical validity, logical consistency, and reproducibility. This is the procedural brain loaded by the `paper-review` skill (inline mode) and by the per-tool reviewer subagents. The checklists, statistical guide, figure guide, principles, and output template referenced below live alongside this file in the same `references/` directory.

**Calibration.** This is an opinionated, direct, evidence-based review style that holds manuscripts to high standards. Severity follows a strict hierarchy: **Critical** issues block publication; **Major** issues require significant revision; **Minor** issues improve polish. Adapt tone and depth to the target journal's expectations (transactions vs. letters vs. conference proceedings differ).

## 0. Partial or incomplete manuscripts

If only part of the manuscript is provided (for example, methods and results without the introduction, or an abstract alone), review what is present rather than refusing, but make the partial scope unmistakable: begin the output with a bold **PARTIAL REVIEW** banner, above the synopsis, that lists the missing sections and warns that the assessment is based on the provided material only and is not a complete peer review. Do not infer the content of missing sections.

## 1. Manuscript intake

**PDF (most common):** convert to both markdown and PNG. Markdown gives efficient searchable text for content analysis; PNG preserves exact page layout, line numbers, and figure positions for precise citations.

Convert to markdown:
```bash
uvx opencite convert manuscript.pdf -o manuscript.md
```

Convert to PNG for page/line references and figure inspection:
```bash
uv run --with pdf2image --with pillow python -c "
from pdf2image import convert_from_path
pages = convert_from_path('manuscript.pdf', dpi=200)
for i, page in enumerate(pages):
    page.save(f'manuscript_page_{i+1}.png', 'PNG')
"
```
Requires poppler (`brew install poppler` on macOS, `apt install poppler-utils` on Linux). Alternatively use `pdftoppm -png -r 200 manuscript.pdf manuscript_page`, or read the PDF natively with the Read tool. For large PDFs (>10 pages), read PNGs in batches.

**Markdown or LaTeX:** read directly; no conversion needed.

Read all sections including supplementary materials, appendices, and figures. When citing an issue, give the exact page and line from the PNGs (e.g., "p4 l23"). Note the target journal if known.

## 2. Read the full manuscript

Read everything: abstract, introduction, methods, results, discussion, conclusion, figures, tables, supplementary materials. Note the stated hypothesis, the methods used to test it, the statistical approach and sample size, the claims in discussion/conclusion, and whether figures and tables support the narrative.

## 3. Assess methodological soundness

The core of the review. Use `methodology-checklist.md`. Key areas:

**Experimental design:** appropriate design for the question; adequate controls; justified (or at least acknowledged) sample size; clear inclusion/exclusion criteria; unaddressed confounds.

**Signal processing and data analysis (when applicable):** appropriate filtering (check Nyquist: analysis bandwidth must not exceed half the sampling rate and should not exceed the low-pass cutoff); validated artifact rejection/correction; justified analysis parameters (window lengths, frequency bands); no "double-dipping" where the features used for selection/clustering are also the analysis target.

**Statistical methods:** use `statistical-review-guide.md`. Appropriate tests for the distribution and design; tested parametric assumptions; correct paired vs. unpaired variant; main effects before post-hoc; multiple-comparison correction; effect sizes, not just p-values; conclusions proportional to sample size; appropriate figures (bar plots with error bars for N<5 are misleading; show individual points).

## 4. Check logical consistency

Trace the argument from introduction through methods to results and discussion: do the methods test the stated hypothesis? Do the results support the discussion claims? Are conclusions proportional to the evidence? Are terms and definitions used consistently and operationalized the same way they are introduced? Watch for claims the authors' own methods cannot test and discussion points that exceed the data.

## 5. Evaluate literature coverage

Is the review current (key papers from the last 2-3 years present)? Are claims actually supported by the cited work? Is related work from other groups acknowledged? Are validation/limitation papers for the techniques used cited? Are there results the authors should compare against?

Verify claims and find missing references with opencite:
```bash
uvx opencite search "topic keywords" --max 10 --sort citations
uvx opencite canonical "field or method" --max 5
```
If the `opencite` skill is loaded, you may invoke it instead of running the shell command. If opencite is unavailable entirely, proceed without the automated search: flag literature-coverage concerns from domain knowledge and say the citation check was not run, rather than silently skipping it. When citing a reference to support a methodological argument, include the full citation so the authors can verify it.

## 6. Check reproducibility and transparency

Methods detailed enough to reproduce; data/code/materials shared or sharing addressed; specified tool/software versions and parameters; for hardware papers, schematics/component lists/block diagrams; disclosed conflicts of interest (check affiliations, patents, commercial products).

## 7. Evaluate figures and tables

Use `figure-review-guide.md`. Do figures accurately represent the data? Are axes labeled, legends present, units specified, statistical annotations defined? Are bar plots used appropriately (small N: show individual points)? Is the time/frequency scale appropriate? Do figures match the text? Are color scales defined? If a figure is referenced in the text but not included in the provided material, assess it from its textual description and flag that the figure itself was not available for inspection.

## 8. Assess writing quality

Technical terms defined before or at first use; consistent terminology (no mid-paper synonyms); concise (flag repetition); abbreviations defined once; abstract reflects the content; methods complete per the target journal. Flag pervasive AI-writing tells (significance inflation, em-dash overuse, "evolving landscape" filler, rule-of-three padding, synonym cycling, generic positive conclusions) and point the author to `manuscript:humanizer`. Cite specific pattern numbers (e.g., pattern 1 significance inflation, pattern 14 em-dash overuse) only when the humanizer skill is loaded; otherwise name the pattern by description, since the full pattern list lives in that skill, not in these references.

## 9. Produce the review output

Structure per `review-output-template.md`:

1. **Synopsis** - one paragraph: the paper's goal, methods, findings, strengths, and overall assessment.
2. **Critical Issues** - numbered; would prevent publication (methodological flaws, invalid statistics, unsupported claims).
3. **Major Concerns** - numbered; significant issues requiring revision (incomplete analysis, missing comparisons, overreached conclusions).
4. **Minor Concerns** - numbered; clarity and polish (writing, figures, references).
5. **References** - full citations for any literature cited to support a point, so the authors can verify it.
6. **Editor Note** (optional) - brief summary and recommendation for the editor.

Every concern must cite the specific location (page, line, figure, or section), explain the problem and why it matters, provide a constructive suggestion, and cite supporting references when arguing a methodological point. For a complete worked example, see `../examples/sample-manuscript-review.md`.

## Review principles

Consult `review-principles.md` for the full rationale before finalizing severity. In brief: be direct but constructive (every weakness gets a suggestion); be evidence-based (cite literature, not authority); be proportional (severity tracks impact on validity); acknowledge strengths genuinely; question logical consistency; demand statistical appropriateness; insist on reproducibility; check the literature; scrutinize figures; hold claims to the data.

## Reference index

- `methodology-checklist.md` - detailed methodological assessment checklist
- `statistical-review-guide.md` - common statistical issues and how to identify them
- `figure-review-guide.md` - figure quality assessment criteria
- `review-principles.md` - review philosophy and calibration guidance
- `review-output-template.md` - the review output format with examples
- Sister skill `manuscript:humanizer` - AI-writing patterns to flag in the prose-quality pass
