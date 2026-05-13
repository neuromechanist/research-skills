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
from validate_fonts import validate  # type: ignore[import-not-found]


# (label, svg body, journal, expected_issue_count, expected_checked_count, expected_skipped_count)
CASES: list[tuple[str, str, str, int, int, int]] = [
    (
        "scaled tiny text fails Nature 5pt",
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
        '<g transform="scale(0.5)"><text x="10" y="20" font-size="8">tiny</text></g></svg>',
        "nature",
        1, 1, 0,
    ),
    (
        "scaled larger text passes Nature 5pt",
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
        '<g transform="scale(0.5)"><text x="10" y="20" font-size="14">ok</text></g></svg>',
        "nature",
        0, 1, 0,
    ),
    (
        "root-level 12pt passes Nature 5pt",
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
        '<text x="10" y="20" font-size="12">root</text></svg>',
        "nature",
        0, 1, 0,
    ),
    (
        "boundary: 12pt source x scale 0.5 = 6pt effective passes Science 6pt",
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
        '<g transform="scale(0.5)"><text x="10" y="20" font-size="12">boundary</text></g></svg>',
        "science",
        0, 1, 0,
    ),
    (
        "negative scale (mirrored panel) does not produce false positives",
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
        '<g transform="scale(-1, 1)"><text x="10" y="20" font-size="12">mirrored</text></g></svg>',
        "nature",
        0, 1, 0,
    ),
    (
        "matrix rotation+scale: 45deg rotation at scale 0.5 -> effective 6pt at 12pt source passes Science 6pt",
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
        '<g transform="matrix(0.354 0.354 -0.354 0.354 0 0)">'
        '<text x="10" y="20" font-size="12">rot</text></g></svg>',
        "science",
        0, 1, 0,
    ),
    (
        "tspan font-size is checked, not just text",
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
        '<g transform="scale(0.5)"><text x="10" y="20"><tspan font-size="8">tspan</tspan></text></g></svg>',
        "nature",
        1, 1, 0,
    ),
    (
        "text with no font-size at all is counted as skipped, not silently passed",
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
        '<text x="10" y="20">unsized</text></svg>',
        "nature",
        0, 0, 1,
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
