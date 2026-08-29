% nsfproposal.cls — LaTeX class for NSF proposal documents
%
% Encodes the PAPPG format requirements (NSF 24-1 Ch. II.C,
% https://www.nsf.gov/policies/pappg/24-1/ch-2-proposal-preparation):
%   - Margins: at least 1 inch in ALL directions; nothing in the margins.
%     Applies to every uploaded section, including supplementary documents.
%   - Fonts: Arial (NOT Arial Narrow), Courier New, or Palatino Linotype at
%     10 pt or larger; Times New Roman at 11 pt or larger; Computer Modern at
%     11 pt or larger. Smaller than 10 pt allowed only in formulas, figures,
%     tables, captions, and Symbol-font special characters.
%   - Line spacing: no more than 6 lines of text per vertical inch
%     (10 pt type on 12 pt leading is exactly 6 lines/inch; do not tighten).
%   - Paper: US letter; single-column strongly encouraged.
%   - No page numbers (Research.gov paginates the assembled proposal).
%
% Class options:
%   10pt (default) - Arial at 10 pt, the smallest permitted size (max space)
%   11pt           - Arial at 11 pt
%
% Commands:
%   \doctitle{...}  - centered bold document title (12 pt)
%
% Usage: \documentclass[10pt]{nsfproposal}
% Add document-specific packages (natbib, graphicx, ...) in the preamble.

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nsfproposal}[2026/08/29 NSF proposal formatting per PAPPG]

\newcommand{\nsf@ptsize}{10pt}
\DeclareOption{10pt}{\renewcommand{\nsf@ptsize}{10pt}}
\DeclareOption{11pt}{\renewcommand{\nsf@ptsize}{11pt}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[\nsf@ptsize,letterpaper]{article}

% PAPPG: margins at least 1 inch in all directions
\RequirePackage[margin=1in,letterpaper]{geometry}

% Arial font (helvet is the LaTeX substitute, metrically identical)
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

% Leading: article defaults (10/12, 11/13.6) satisfy the 6-lines-per-inch cap.
% Never reduce \baselineskip below 12 pt.

% No page numbers; Research.gov paginates
\pagenumbering{gobble}

% Paragraphs: no indent, 4 pt spacing (house style)
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt plus 1pt}
\hyphenpenalty=5000
\tolerance=1000
\emergencystretch=3em

% Captions: small but >= permitted minimum only for captions (PAPPG allows <10 pt here);
% keep 8 pt for space, bold labels
\RequirePackage{caption}
\DeclareCaptionFont{eightp}{\fontsize{8pt}{10pt}\selectfont}
\captionsetup{font=eightp, labelfont={eightp,bf}, skip=4pt}

\RequirePackage{xcolor}
\RequirePackage{titlesec}

% Section headers: body size + 1 pt, bold, unnumbered, tight spacing
\titleformat{\section}{\fontsize{12pt}{14pt}\selectfont\bfseries}{}{0pt}{}
\titlespacing*{\section}{0pt}{8pt}{2pt}
\titleformat{\subsection}{\bfseries}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{6pt}{1pt}
\titleformat{\subsubsection}{\itshape\bfseries}{}{0pt}{}
\titlespacing*{\subsubsection}{0pt}{4pt}{1pt}
\setcounter{secnumdepth}{0}

% Centered bold 12 pt document title
\newcommand{\doctitle}[1]{%
  \begin{center}%
    {\fontsize{12pt}{14pt}\selectfont\bfseries #1}%
  \end{center}%
  \vspace{2pt}%
}

\endinput
