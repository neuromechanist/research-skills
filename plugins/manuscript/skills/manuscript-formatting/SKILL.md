---
name: manuscript-formatting
description: "Use this skill for \"format manuscript\", \"prepare for submission\", \"journal formatting\", \"LaTeX template\", \"submission checklist\", \"format references\", \"BibTeX\", \"author guidelines\", \"page limits\", \"format for Nature\", \"format for IEEE\", or when the user wants to format a manuscript for journal submission."
version: 0.3.0
---

# Manuscript Formatting and Submission Preparation

Format manuscripts to meet journal-specific requirements and prepare submission packages.

## When to Use

- Formatting a manuscript for a specific journal
- Preparing a submission package (cover letter, figures, supplementary)
- Converting between formats (Word to LaTeX, markdown to LaTeX)
- Checking compliance with author guidelines
- Managing references and BibTeX

## Common Journal Formats

### IEEE
- **Template:** IEEEtran class
- **Columns:** Two-column
- **References:** Numbered, [1] style
- **Figures:** Fit within column or span both columns
- **Page limit:** Varies (typically 6-8 for conference, 12-14 for journal)

```latex
\documentclass[journal]{IEEEtran}
\usepackage{cite}
\usepackage{amsmath}
\usepackage{graphicx}
```

### Nature/Science
- **Format:** Single column, specific heading hierarchy
- **References:** Superscript numbered
- **Word limit:** ~3000-5000 words (main text)
- **Figures:** Max 6-8, submitted as separate files
- **Methods:** Often separate section with no word limit

### PNAS
- **Template:** pnas-new class
- **Columns:** Two-column in print, single for review
- **Word limit:** ~4500 words
- **References:** Numbered
- **Significance statement:** Required, 120 words max

### PLoS ONE
- **Format:** No specific template required
- **References:** Numbered, Vancouver style
- **No length restriction**
- **Data availability:** Statement required

### Elsevier
- **Template:** elsarticle class
- **Multiple formats:** preprint, review, final
```latex
\documentclass[preprint,12pt]{elsarticle}
```

## LaTeX Essentials

### Document Structure
```latex
\documentclass[options]{class}
\usepackage{packages}

\title{Title}
\author{Authors}

\begin{document}
\maketitle
\begin{abstract}
\end{abstract}

\section{Introduction}
\section{Methods}
\section{Results}
\section{Discussion}

\bibliography{references}
\end{document}
```

### BibTeX Management

```bibtex
@article{smith2024,
  author  = {Smith, John and Doe, Jane},
  title   = {Title of the Paper},
  journal = {Journal Name},
  year    = {2024},
  volume  = {10},
  pages   = {1--15},
  doi     = {10.1000/example}
}
```

Common BibTeX styles:
- `plain` - numbered, sorted alphabetically
- `unsrt` - numbered, order of citation
- `ieeetr` - IEEE transactions style
- `apalike` - APA-like author-year

### Cross-references
```latex
\label{fig:results}   % Label a figure
\ref{fig:results}     % Reference by number
Figure~\ref{fig:results}  % Standard format
```

## Submission Checklist

### Before Submission
- [ ] Manuscript formatted per journal template
- [ ] Title page: title, authors, affiliations, corresponding author, ORCID
- [ ] Abstract within word limit
- [ ] Keywords provided (if required)
- [ ] Main text within page/word limit
- [ ] Figures as separate high-resolution files (typically 300+ DPI)
- [ ] Figure captions in a separate list
- [ ] Tables formatted per journal style
- [ ] References complete and consistently formatted
- [ ] Supplementary materials prepared separately
- [ ] Cover letter drafted (run `manuscript:humanizer` on it; cover letters are particularly prone to AI-tell phrasing)
- [ ] `manuscript:humanizer` natural-writing pass applied to all narrative sections, *then* journal house style (title case, citation format, etc.) re-applied where it overrides humanizer defaults
- [ ] Conflict of interest statement
- [ ] Data availability statement
- [ ] Ethics approval statement (if applicable)
- [ ] Author contributions (CRediT format if required)
- [ ] Suggested reviewers (if required)

### Cover Letter Template

```
Dear Editor,

We submit our manuscript titled "{TITLE}" for consideration
in {JOURNAL}.

{1-2 sentences: what the study did and found}

{1-2 sentences: why this matters to the journal's readership}

{1 sentence: confirmation of originality and no concurrent submission}

We suggest the following reviewers:
1. {Name, Affiliation, Email}
2. {Name, Affiliation, Email}

Sincerely,
{Corresponding Author}
```

## Format Conversion

### Markdown to LaTeX
```bash
pandoc manuscript.md -o manuscript.tex --template=journal-template.tex --bibliography=refs.bib --citeproc
```

### Word to LaTeX
```bash
pandoc manuscript.docx -o manuscript.tex --extract-media=figures/
```

### LaTeX to Word (for journals requiring .docx)
```bash
pandoc manuscript.tex -o manuscript.docx --bibliography=refs.bib --citeproc
```

## Semantic Line Breaks

Semantic line breaks put each substantial unit of thought on its own source
line, so a small prose edit produces a small, reviewable diff. The
[SemBr specification](https://sembr.org/) requires that this formatting not
alter the rendered document. The [`sembr` CLI](https://pypi.org/project/sembr/)
supports Markdown, plain text, and LaTeX and can be installed portably with
`uv tool install sembr`.

Raw SemBr output is reasonable for ordinary Markdown after review. Do not
trust raw output on LaTeX: line breaks can change comment scope or corrupt
commands and escape sequences. Use the bundled safety wrapper for LaTeX:

```bash
uv run python plugins/manuscript/skills/manuscript-formatting/scripts/semantic_breaks.py \
  manuscript.tex manuscript-semantic.tex \
  --compile-command latexmk -pdf -interaction=nonstopmode \
  -outdir {build_dir} {source}
```

The wrapper performs these gates before writing the destination:

1. It replaces `\\begin{verbatim}...\\end{verbatim}` blocks and full-line `%`
   comments with atomic placeholders, then restores them after SemBr.
2. It aligns whitespace-delimited tokens with Python's
   `difflib.SequenceMatcher`. If any token content diverges, it restores the
   original paragraph containing that divergence; whitespace-only changes in
   other paragraphs remain available as semantic breaks. A whitespace-collapsed
   string comparison alone is unsafe because it misses `%` comment truncation.
3. When `--compile-command` is supplied, it compiles the original and guarded
   versions separately, runs `pdftotext` on both PDFs, and refuses to write the
   result unless the extracted bytes are identical. The compiler command must
   use `{source}` for its input and route generated files into `{build_dir}`;
   arguments after `--compile-command` are consumed by the wrapper.

Inspect the resulting diff and keep the compiled-output check in the workflow;
matching extracted text is a safety gate, not a substitute for reviewing the
source and the rendered PDF.

## Additional Resources

- Reference: [references/journal-requirements.md](references/journal-requirements.md) - Detailed requirements for major journals
- Reference: [references/latex-troubleshooting.md](references/latex-troubleshooting.md) - Common LaTeX issues and fixes
