# License-Aware Archival Rules

The lit-review corpus must be redistributable. PDFs are committed only when the license permits. Markdown extractions are typically committed under research-note fair use.

## The single source of truth

`meta.json.redistribution_ok` (boolean) is the authoritative flag. Every other rule derives from it.

| `redistribution_ok` | `source.pdf` allowed in repo? | `source.md` allowed in repo? |
|---|---|---|
| `true`  | yes; populate `pdf_sha256`         | yes |
| `false` | no; `pdf_path: null`, `pdf_sha256: null` | yes; flag uncertainty in `notes` if extraction is borderline |

## License vocabulary and redistribution mapping

| `pdf_license` value | `redistribution_ok` |
|---|---|
| `CC-BY`, `CC-BY-2.0`, `CC-BY-3.0`, `CC-BY-4.0` | true |
| `CC0` | true |
| `CC-BY-NC` | true (research use; document non-commercial in `notes`) |
| `preprint-cc-arxiv`, `preprint-cc-biorxiv`, `preprint-cc-osf` | true |
| `author-accepted-manuscript` | true; document the institutional repository in `notes` |
| `publisher-paywall` | false |
| `publisher-paywall (<journal>); university repository copy archived` | true (the AAM is what is archived; document in `notes`) |
| `not-applicable` | true (no PDF; tool/dataset card) |
| `unknown` | false (default deny) |

When in doubt, default to `false`. Re-archiving is cheap; takedown notices are not.

## Source preference order

For each entry, prefer in order:

1. **Open-access publisher copy** (CC-BY journal, eLife, PLOS, Frontiers).
2. **Preprint** (arXiv, bioRxiv, OSF). Note the relationship to the published version in `notes`.
3. **Author Accepted Manuscript** in an institutional repository.
4. **Markdown extraction only**, no PDF (paywalled with no preprint).

If the only available copy is paywalled with no preprint or AAM, set `pdf_status: not-redistributable`, `pdf_path: null`, and store the markdown extraction.

## Markdown extractions of paywalled papers

Storing a markdown extraction (text only, no figures, no original layout) of a paywalled paper is generally accepted under research-note fair use across US, EU, and UK academic norms. However:

- Document the source in `meta.json.notes`: "extracted from paywalled <journal> PDF, used as research notes only".
- Do not commit the original PDF.
- Do not reproduce figures from the paywalled paper. Reference them by figure number and citation.
- If the rights holder requests removal, comply. Track such requests in a top-level `LICENSE-NOTES.md` if they accumulate.
- For papers under aggressive paywalls (e.g. publisher with active anti-circumvention enforcement), consider linking to the publisher landing page and citing without storing the markdown.

## Storage rules summary

- **Open-access PDF available**: commit `source.pdf` and `source.md`. `redistribution_ok: true`. Populate `pdf_sha256`.
- **Preprint available, no published OA**: commit the preprint as `source.pdf` and `source.md`. Note the relationship in `notes`.
- **AAM in institutional repository**: commit the AAM as `source.pdf` and `source.md`. Document the repository URL in `notes`.
- **Paywalled with no OA / preprint / AAM**: do NOT commit PDF. Commit `source.md`. `redistribution_ok: false`.
- **Tool / dataset / standard with no paper**: snapshot README or canonical landing as `source.md`. `pdf_status: not-applicable`. `redistribution_ok: true` (READMEs are typically permissively licensed; document in `notes`).
- **Failed download**: set `pdf_status: not-available`. Document failure mode (Cloudflare, broken DOI, reCAPTCHA, etc.) in `notes`. Re-attempt later.

## CI rule

Recommended invariant for the corpus repository (enforce in CI):

> If `meta.json.redistribution_ok == false`, then no `source.pdf` file may exist in the entry folder.

A simple shell check:

```bash
for entry in research/collection/*/*/; do
  redistribution_ok=$(jq -r '.redistribution_ok' "$entry/meta.json" 2>/dev/null)
  if [[ "$redistribution_ok" == "false" && -f "$entry/source.pdf" ]]; then
    echo "VIOLATION: $entry has source.pdf but redistribution_ok=false"
    exit 1
  fi
done
```

Add this to the pre-commit hook or CI workflow if the corpus is on GitHub.

## When a license changes

Open-access publishers occasionally re-license content. Preprint servers do not. If a previously open-access journal becomes paywalled retroactively for old content (rare), the existing committed PDFs are protected by the license active at retrieval time. Document `retrieved_at` in `meta.json` so the licensing context is preserved.

## When in doubt

Ask the rights holder (publisher, repository, author). If the answer is unclear, store the markdown only and set `redistribution_ok: false`.
