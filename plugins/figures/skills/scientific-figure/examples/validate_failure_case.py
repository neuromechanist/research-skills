"""Self-contained test fixture for validate_fonts.py.

Constructs synthetic SVGs that cover the validator's edge cases and asserts the
expected outcomes. Encodes the verification claims from PR #40 so they can be
re-run without manual source edits.

    uv run --with lxml python validate_failure_case.py

Exit 0 if every assertion passes, 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
from validate_fonts import validate  # type: ignore[import-not-found]  # noqa: E402  (after sys.path setup)


# In an mm-based viewBox (width="100mm" / viewBox 100), 1 user unit is 1 mm, so a bare
# font-size of N is N mm = N * 72/25.4 pt (~2.835 pt per unit). In a pt-based viewBox
# (matplotlib's export), 1 user unit is 1 pt, so the factor is 1.0. An explicit unit on
# the font-size is absolute and is NOT scaled by the viewBox.
_MM = '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
_PT = '<svg xmlns="http://www.w3.org/2000/svg" width="200pt" height="100pt" viewBox="0 0 200 100">'

# (label, svg body, journal, expected_issue_count, expected_checked_count, expected_skipped_count)
CASES: list[tuple[str, str, str, int, int, int]] = [
    (
        "bare mm font-size below minimum fails (3mm x scale 0.5 = 4.25pt < Nature 5pt)",
        _MM + '<g transform="scale(0.5)"><text x="10" y="20" font-size="3">tiny</text></g></svg>',
        "nature", 1, 1, 0,
    ),
    (
        "bare mm font-size passes (2mm = 5.7pt >= Nature 5pt)",
        _MM + '<text x="10" y="20" font-size="2">ok</text></svg>',
        "nature", 0, 1, 0,
    ),
    (
        "explicit pt is absolute, NOT scaled by the mm viewBox (4pt < Nature 5pt fails)",
        _MM + '<text x="10" y="20" font-size="4pt">abs</text></svg>',
        "nature", 1, 1, 0,
    ),
    (
        "explicit pt passes (7pt >= Nature 5pt)",
        _MM + '<text x="10" y="20" font-size="7pt">abs</text></svg>',
        "nature", 0, 1, 0,
    ),
    (
        "explicit mm unit converts to pt (1.5mm = 4.25pt < Nature 5pt fails)",
        _MM + '<text x="10" y="20" font-size="1.5mm">mm</text></svg>',
        "nature", 1, 1, 0,
    ),
    (
        "pt-based (matplotlib) viewBox is unaffected: bare 4 = 4pt < Nature 5pt fails",
        _PT + '<text x="10" y="20" font-size="4">mpl</text></svg>',
        "nature", 1, 1, 0,
    ),
    (
        "pt-based (matplotlib) viewBox passes: bare 7 = 7pt >= Nature 5pt",
        _PT + '<text x="10" y="20" font-size="7">mpl</text></svg>',
        "nature", 0, 1, 0,
    ),
    (
        "transform scale composes with the viewBox factor (4mm x scale 0.3 = 3.4pt fails)",
        _MM + '<g transform="scale(0.3)"><text x="10" y="20" font-size="4">scaled</text></g></svg>',
        "nature", 1, 1, 0,
    ),
    (
        "negative scale (mirrored panel) does not produce false positives (3mm = 8.5pt)",
        _MM + '<g transform="scale(-1, 1)"><text x="10" y="20" font-size="3">mirror</text></g></svg>',
        "nature", 0, 1, 0,
    ),
    (
        "matrix scale magnitude is honored (4mm at matrix scale 0.5 = 5.7pt passes)",
        _MM + '<g transform="matrix(0.354 0.354 -0.354 0.354 0 0)">'
        '<text x="10" y="20" font-size="4">rot</text></g></svg>',
        "nature", 0, 1, 0,
    ),
    (
        "tspan bare mm font-size is checked (1mm = 2.8pt < Nature 5pt fails)",
        _MM + '<g transform="scale(0.5)"><text x="10" y="20"><tspan font-size="2">tspan</tspan></text></g></svg>',
        "nature", 1, 1, 0,
    ),
    (
        "style= attribute with an explicit mm unit is absolute (1.5mm = 4.25pt fails)",
        _MM + '<text x="10" y="20" style="font-size: 1.5mm">styled</text></svg>',
        "nature", 1, 1, 0,
    ),
    (
        "explicit pt inside a scaled group is scaled by the transform, not the viewBox (10pt x 0.4 = 4pt fails)",
        _MM + '<g transform="scale(0.4)"><text x="10" y="20" font-size="10pt">abs</text></g></svg>',
        "nature", 1, 1, 0,
    ),
    (
        "text with no font-size at all is counted as skipped, not silently passed",
        _MM + '<text x="10" y="20">unsized</text></svg>',
        "nature", 0, 0, 1,
    ),
]


def run() -> int:
    failures = 0
    with TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        for i, (label, body, journal, exp_issues, exp_checked, exp_skipped) in enumerate(CASES):
            svg_path = tmp / f"case_{i}.svg"
            svg_path.write_text(body)
            report = validate(svg_path, journal)
            issues = report["issue_count"]
            checked = report["checked_count"]
            skipped = report["skipped_count"]
            ok = issues == exp_issues and checked == exp_checked and skipped == exp_skipped
            status = "PASS" if ok else "FAIL"
            print(
                f"[{status}] {label}: issues={issues} (exp {exp_issues}), "
                f"checked={checked} (exp {exp_checked}), skipped={skipped} (exp {exp_skipped})"
            )
            if not ok:
                failures += 1

    print()
    print(f"{len(CASES) - failures}/{len(CASES)} cases passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
