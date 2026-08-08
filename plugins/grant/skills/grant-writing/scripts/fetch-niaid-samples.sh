#!/usr/bin/env bash
#
# fetch-niaid-samples.sh
#
# Downloads the NIAID small-business sample applications and summary statements
# listed in niaid-samples.txt, and optionally converts each PDF to markdown.
#
# The samples are copyrighted by the awardees and licensed for nonprofit
# educational use only, provided the material remains unchanged and the
# principal investigators, awardee organizations, and NIH NIAID are credited.
# They are therefore fetched on demand rather than redistributed with this
# plugin. Keep the downloaded files out of version control.
#
# Usage:
#   ./fetch-niaid-samples.sh [-o OUTPUT_DIR] [-m] [-l] [LABEL ...]
#
#   -o, --output-dir DIR   Where to write files (default: ./niaid-samples)
#   -m, --markdown         Also convert each PDF to markdown via opencite
#   -l, --list             Print the manifest and exit, downloading nothing
#   -h, --help             Print this help and exit
#   LABEL ...              Optional label filters; substring match, case
#                          insensitive (for example: MacLeod R44)
#
# Examples:
#   ./fetch-niaid-samples.sh                       # all 18 files, PDFs only
#   ./fetch-niaid-samples.sh -m MacLeod Brooks     # two PIs, with markdown
#   ./fetch-niaid-samples.sh -o ~/niaid -m         # custom directory
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="${SCRIPT_DIR}/niaid-samples.txt"
BASE_URL="https://www.niaid.nih.gov/sites/default/files"
INDEX_URL="https://www.niaid.nih.gov/grants-contracts/sample-applications"

# niaid.nih.gov answers a default curl user agent with HTTP 403. A browser
# user agent plus a Referer from the index page is what gets through.
USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

OUT_DIR="./niaid-samples"
CONVERT=0
LIST_ONLY=0
FILTERS=()

usage() {
    sed -n '2,28p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

# niaid.nih.gov redirects a missing or renamed file to a "page not found" node
# that answers HTTP 200 with an HTML body, so curl -f cannot see the failure and
# writes the error page to the .pdf path. Every download is therefore checked
# for the PDF magic bytes, and so is every cached file, since an error page
# saved by an earlier run would otherwise be trusted forever.
is_pdf() {
    [[ -s "$1" ]] || return 1
    [[ "$(head -c 5 "$1" 2>/dev/null)" == "%PDF-" ]]
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output-dir)
            [[ $# -ge 2 ]] || { echo "error: $1 needs a directory" >&2; exit 2; }
            OUT_DIR="$2"
            shift 2
            ;;
        -m|--markdown)
            CONVERT=1
            shift
            ;;
        -l|--list)
            LIST_ONLY=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo "error: unknown option $1" >&2
            usage >&2
            exit 2
            ;;
        *)
            FILTERS+=("$1")
            shift
            ;;
    esac
done

[[ -f "$MANIFEST" ]] || { echo "error: manifest not found at $MANIFEST" >&2; exit 1; }

matches_filter() {
    local label_lc
    label_lc="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
    [[ ${#FILTERS[@]} -eq 0 ]] && return 0
    local f f_lc
    for f in "${FILTERS[@]}"; do
        f_lc="$(printf '%s' "$f" | tr '[:upper:]' '[:lower:]')"
        [[ "$label_lc" == *"$f_lc"* ]] && return 0
    done
    return 1
}

if [[ $LIST_ONLY -eq 1 ]]; then
    printf '%-45s %s\n' "LABEL" "URL"
    # `|| [[ -n "$label" ]]` keeps the last entry when the manifest has no
    # trailing newline; a bare `read` would drop it silently.
    while IFS='|' read -r label filename || [[ -n "$label" ]]; do
        [[ -z "${label// }" || "$label" == \#* ]] && continue
        matches_filter "$label" || continue
        printf '%-45s %s/%s\n' "$label" "$BASE_URL" "$filename"
    done < "$MANIFEST"
    exit 0
fi

if [[ $CONVERT -eq 1 ]] && ! command -v uvx >/dev/null 2>&1; then
    echo "error: --markdown needs uvx (install uv: https://docs.astral.sh/uv/)" >&2
    exit 1
fi

mkdir -p "$OUT_DIR/pdf"
[[ $CONVERT -eq 1 ]] && mkdir -p "$OUT_DIR/markdown"

downloaded=0
converted=0
failed=0

while IFS='|' read -r label filename || [[ -n "$label" ]]; do
    [[ -z "${label// }" || "$label" == \#* ]] && continue
    matches_filter "$label" || continue

    pdf="$OUT_DIR/pdf/${label}.pdf"
    if is_pdf "$pdf"; then
        echo "have  ${label}.pdf"
    else
        [[ -e "$pdf" ]] && echo "  discarding ${label}.pdf, not a PDF" >&2 && rm -f "$pdf"
        echo "fetch ${label}.pdf"
        if curl -fsSL \
            --retry 3 --retry-delay 2 --connect-timeout 20 \
            -A "$USER_AGENT" \
            -H "Referer: ${INDEX_URL}" \
            -o "$pdf" \
            "${BASE_URL}/${filename}"; then
            if is_pdf "$pdf"; then
                downloaded=$((downloaded + 1))
            else
                echo "  not a PDF, the server returned an error page: ${BASE_URL}/${filename}" >&2
                echo "  the file may have been renamed or withdrawn; check ${INDEX_URL}" >&2
                rm -f "$pdf"
                failed=$((failed + 1))
                continue
            fi
        else
            echo "  failed: ${BASE_URL}/${filename}" >&2
            rm -f "$pdf"
            failed=$((failed + 1))
            continue
        fi
    fi

    [[ $CONVERT -eq 1 ]] || continue

    md="$OUT_DIR/markdown/${label}.md"
    if [[ -s "$md" ]]; then
        echo "have  ${label}.md"
        continue
    fi
    echo "convert ${label}.md"
    # opencite defaults to the Mistral converter, which fails without
    # MISTRAL_API_KEY, so markitdown is selected explicitly.
    if uvx --from 'opencite[pdf]' --with 'markitdown[pdf]' \
        opencite convert "$pdf" --converter markitdown -o "$md" >/dev/null; then
        converted=$((converted + 1))
    else
        echo "  conversion failed for ${label}" >&2
        rm -f "$md"
        failed=$((failed + 1))
    fi
done < "$MANIFEST"

echo
echo "downloaded ${downloaded} PDF(s), converted ${converted} file(s), ${failed} failure(s) into ${OUT_DIR}"
echo "These files are copyrighted by the awardees; nonprofit educational use only,"
echo "unchanged, crediting the principal investigators, awardee organizations, and NIH NIAID."
echo "Do not commit them to a public repository."

# Exit non-zero when anything failed, so a caller or CI notices rather than
# reading the summary line as success.
[[ $failed -eq 0 ]]
