# Strand Collection Procedure (Phase 1)

One collector builds the corpus for one strand, from that strand's brief alone.
The orchestrating session runs one collector per strand in parallel and keeps synthesis for Phase 2.
This procedure is the collector's contract on every host: a bundled agent, a configured Codex or Copilot agent, or the orchestrating session itself when no agent is available.

## Inputs

- **Strand name** (required): `<strand>`, matching the brief file name and the folder the collector writes.
- **Brief path** (required): `_briefs/strand-<name>.md`, written from [brief-template.md](brief-template.md).
- **Collection root** (required): usually `research/collection/`; the collector writes only under `<root>/<strand>/`.
- **Schema**: [paper-card-schema.md](paper-card-schema.md), or the local copy at `<root>/_schema/paper-card.md` when the project has one.
- **License rules**: [license-rules.md](license-rules.md).
- **Existing entries**: anything already under `<root>/<strand>/` from an earlier run; extend it, do not rebuild it.

The brief is the whole task.
Do not read other strands' folders, the synthesis directory, or direction papers, and do not ask the orchestrator for its reasoning about the review.

## Steps

1. Read the brief, the schema, and the license rules in full before collecting anything.
2. List the existing entries in the strand folder and their slugs, so new entries do not duplicate them.
3. Mine the brief's seed material first. Each imported entry sets `imported_from: <relative path>` in `card.md`.
4. Search category by category, breadth first, with `opencite:opencite` (canonical search for foundations, sorted search for recent work, the citation graph for gaps). Stop a category when it meets the brief's threshold and further results stop adding distinct work.
5. For each entry, create `<root>/<strand>/<slug>/` with:
   - `card.md` from the schema, with `strand: <strand>` and a relevance grade calibrated to the schema's anchors;
   - `source.md` (always): a PDF-to-markdown extraction, or the canonical README or docs page for a tool, dataset, or standard;
   - `meta.json` with provenance (Digital Object Identifier (DOI) or URL, `retrieved_at`, license, `redistribution_ok`, `pdf_status`, and `pdf_sha256` when a PDF is archived);
   - `source.pdf` only when `redistribution_ok` is true under the license rules.
6. Append each entry's BibTeX from `opencite` to `<root>/<strand>/<strand>.bib`, keeping the key consistent with the slug, and add a one-line entry under the right category in `<root>/<strand>/INDEX.md`.
7. Check the brief's acceptance criteria and report against them.

## Rules

- **No invention.** Every card describes a source the collector retrieved. A DOI, author list, year, venue, or finding that could not be verified is left blank and listed in the report, never filled from memory.
- **Collection only.** Cards summarize one source each. No cross-entry comparison, ranking, or synthesis prose; that is Phase 2.
- **Stay in scope.** Skip the brief's out-of-scope topics even when results are strong; list notable skips in the report so the orchestrator can decide on a new strand.
- **Respect licenses.** When the license is unclear, treat the PDF as not redistributable and record why in `meta.json.notes`.
- **Write only in the strand folder.** Do not touch the brief, the schema, or other strands.

## Report

Return a short report:

1. Entries added and updated, per category, against the brief's thresholds.
2. Acceptance criteria as a checklist, each marked met or not met.
3. Failed retrievals (`pdf_status: not-available`) and unverifiable fields.
4. Out-of-scope or adjacent work worth a new strand, one line each.
