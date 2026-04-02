# LaTeX Troubleshooting

## Common Errors

### "Undefined control sequence"
**Cause:** Using a command without loading the required package.
```latex
% Fix: Add the missing package
\usepackage{amsmath}    % For \text, \boldsymbol, etc.
\usepackage{graphicx}   % For \includegraphics
\usepackage{hyperref}   % For \url, \href
```

### "Missing $ inserted"
**Cause:** Using math symbols outside math mode.
```latex
% Wrong:
The value is 2.5 x 10^3
% Correct:
The value is $2.5 \times 10^3$
```

### "Float(s) lost"
**Cause:** Float placed inside a restricted environment.
```latex
% Wrong: figure inside multicols
\begin{multicols}{2}
  \begin{figure}[h]  % Will be lost
  \end{figure}
\end{multicols}

% Fix: Use figure* or place outside multicols
```

### "Too many unprocessed floats"
**Cause:** Too many figures/tables without enough text.
```latex
% Fix: Add float placement hints
\begin{figure}[htbp]  % try here, top, bottom, page
% Or force placement
\usepackage{float}
\begin{figure}[H]  % Force HERE
```

### "Overfull \hbox"
**Cause:** Content too wide for the column.
```latex
% For long URLs:
\usepackage[hyphens]{url}

% For tables:
\resizebox{\columnwidth}{!}{%
  \begin{tabular}{...}
  \end{tabular}
}

% For equations:
\begin{equation}
\resizebox{.9\columnwidth}{!}{$long equation$}
\end{equation}
```

## BibTeX Issues

### References not showing
1. Compile order: pdflatex -> bibtex -> pdflatex -> pdflatex
2. Check .bib file is in the right location
3. Check `\bibliography{filename}` matches (no .bib extension)
4. Check `\bibliographystyle{style}` is present

### Author names wrong
```bibtex
% Corporate author:
author = {{World Health Organization}},  % Double braces

% Multiple authors:
author = {Smith, John and Doe, Jane and {van der Berg}, Peter},

% Accented characters:
author = {M{\"u}ller, Hans and Caf{\'{e}}, Jean},
```

### Title capitalization lost
```bibtex
% BibTeX lowercases titles by default. Protect with braces:
title = {A Study of {BIDS} Format in {EEG} Research},
```

## Figure Best Practices

### Vector vs Raster
- Use PDF/EPS for plots, diagrams, charts (vector, infinitely scalable)
- Use PNG for photographs, screenshots (raster, fixed resolution)
- Never use JPEG for figures with text or lines (compression artifacts)

### Including figures
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\columnwidth]{figures/result.pdf}
  \caption{Description of the figure.}
  \label{fig:result}
\end{figure}

% Multi-panel
\begin{figure*}[htbp]  % Span both columns
  \centering
  \includegraphics[width=\textwidth]{figures/panels.pdf}
  \caption{(A) First panel. (B) Second panel.}
  \label{fig:panels}
\end{figure*}
```

## Useful Packages

```latex
\usepackage{amsmath}      % Math environments
\usepackage{amssymb}      % Math symbols
\usepackage{graphicx}     % Figure inclusion
\usepackage{booktabs}     % Professional tables (\toprule, \midrule)
\usepackage{hyperref}     % Clickable references
\usepackage{cleveref}     % Smart cross-references (\cref)
\usepackage{siunitx}      % SI units and number formatting
\usepackage{natbib}       % Author-year citations
\usepackage{xcolor}       % Color text (for tracked changes)
\usepackage{soul}          % Highlighting
\usepackage{lineno}       % Line numbers (for review)
```
