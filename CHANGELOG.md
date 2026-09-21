# Changelog

All notable changes to the Research Skills marketplace are documented here.

## [0.16.3] - 2026-09-20

This release consolidates the changes merged after `v0.15.13`, including the
cross-agent runtime work tracked by issues #87, #97, and #98.

### Added

- **Project plugin 0.9.0:** a read-only `project-preflight` probe for the
  repository, worktree, shell, terminal, GitHub CLI, credentials, and native
  agent capability surfaces.
- **Project plugin 0.9.0:** a bounded fresh-context PR review panel with
  explicit risk grouping, reviewer accounting, fallback behavior, and cleanup
  requirements for Codex, Claude Code, and Copilot-compatible workflows.
- **Project plugin 0.9.0:** tracked, agent-agnostic `.memory/` scaffolding,
  initialization and update-rules integration, and documented boundaries
  between memory, analysis, and binding ADRs.
- **Manuscript plugin 0.6.0:** a conservative semantic-line-break wrapper for
  LaTeX, including protected verbatim/comment regions, token-alignment
  validation, optional compilation, and a byte-identical `pdftotext` gate.
- **ML-training plugin 0.1.0:** RunPod provisioning, image, lifecycle,
  monitoring, GPU-selection, job-execution, and independent fleet fan-out
  workflows.
- A shared figures backend, figure bible, theme validation, multi-panel
  composition, OCR-aware QA, JSON verdicts, editor handoff tooling, and an
  explicit Atlas Cloud icon backend.
- Grant readability review guidance and SBIR/STTR writing and review support.

### Changed

- Claude Code, Codex, and GitHub Copilot marketplace and plugin manifests now
  remain synchronized, with portable skill references and tool-specific agent
  shells kept thin.
- Review and delegation guidance now separates design, observation,
  supervision, synthesis, and implementation responsibilities across the
  supported agent surfaces.
- Figure, grant, manuscript, and project documentation and validation contracts
  were updated to match the shipped workflows.

### Fixed

- Hardened figure backend and QA contracts for malformed responses, exit codes,
  OCR-skipped text, finding actions, panel scaling, and duplicate panel
  lettering.
- Removed unsafe raw-LaTeX semantic line-break behavior that could alter escape
  sequences, split verbatim content, or swallow following content after a `%`
  comment.
- Corrected cross-agent skill dispatch and namespacing paths so the same shared
  capability can be discovered without relying on one tool's private layout.

### Verification

- The repository validation gate passed, including the filesystem-backed test
  suite, manifest and skill checks, shell checks, documentation build, and
  strict link validation.
