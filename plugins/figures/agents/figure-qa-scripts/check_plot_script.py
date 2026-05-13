"""Static analysis on a Python plot script (matplotlib / seaborn / plotly / plotnine).

Looks at the source of a script (no execution) and reports:
- Which plotting library is used
- Whether font sizes set in rcParams meet the journal minimum
- Whether savefig uses transparent=True and bbox_inches='tight'
- A library recommendation when the script uses matplotlib but the chart type
  matches a row in the plot-library decision tree

Run from anywhere:

    uv run python check_plot_script.py SCRIPT.py [--journal nature]

Emits a single JSON document on stdout. Exit 0 clean, 1 issues, 2 IO/parse error.

This is deliberately a string-and-AST scan, not a runtime execution. The agent
runs the script separately if it needs to actually render the plot.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


JOURNAL_MIN_PT: dict[str, float] = {
    "nature": 5.0,
    "science": 6.0,
    "cell": 6.0,
    "pnas": 6.0,
    "generic": 5.0,
}

LIBRARY_IMPORTS = {
    "matplotlib": ("matplotlib", "matplotlib.pyplot", "pylab"),
    "seaborn": ("seaborn",),
    "plotly": ("plotly", "plotly.express", "plotly.graph_objects", "plotly.graph_objs"),
    "plotnine": ("plotnine",),
    "ggplot2": ("rpy2",),  # rpy2 + ggplot2
    "pyvista": ("pyvista",),
}


def _detect_libraries(tree: ast.AST) -> list[str]:
    """Walk the AST and return every plotting library detected by import."""
    detected: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for lib, names in LIBRARY_IMPORTS.items():
                    if alias.name in names:
                        detected.add(lib)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for lib, names in LIBRARY_IMPORTS.items():
                    if node.module in names:
                        detected.add(lib)
    return sorted(detected)


def _find_rcparam_font_sizes(tree: ast.AST) -> list[dict[str, Any]]:
    """Find rcParams.update({'font.size': N}) and plt.rcParams['font.size'] = N
    assignments, returning the value(s)."""
    findings = []
    for node in ast.walk(tree):
        # plt.rcParams.update({"font.size": 9})
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "update"
            and node.args
            and isinstance(node.args[0], ast.Dict)
        ):
            for k, v in zip(node.args[0].keys, node.args[0].values):
                if (
                    isinstance(k, ast.Constant)
                    and isinstance(k.value, str)
                    and "font.size" in k.value
                    and isinstance(v, ast.Constant)
                    and isinstance(v.value, (int, float))
                ):
                    findings.append({"key": k.value, "pt": float(v.value)})
        # plt.rcParams["font.size"] = 9
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Subscript)
            and isinstance(node.targets[0].slice, ast.Constant)
            and isinstance(node.targets[0].slice.value, str)
            and "font.size" in node.targets[0].slice.value
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, (int, float))
        ):
            findings.append({"key": node.targets[0].slice.value, "pt": float(node.value.value)})
    return findings


def _savefig_kwargs(tree: ast.AST) -> list[dict[str, Any]]:
    """Find every .savefig(...) call and capture the transparent / bbox_inches kwargs."""
    findings = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "savefig"
        ):
            kwargs = {}
            for kw in node.keywords:
                if kw.arg in ("transparent", "bbox_inches", "dpi", "format"):
                    if isinstance(kw.value, ast.Constant):
                        kwargs[kw.arg] = kw.value.value
            findings.append(kwargs)
    return findings


def _recommend_library(libs: list[str], source: str) -> str | None:
    """If the script uses matplotlib directly for a chart type that has a
    better-defaults library, return a recommendation string."""
    if "matplotlib" not in libs:
        return None
    if any(lib in libs for lib in ("seaborn", "plotnine", "plotly")):
        # Already using a higher-level wrapper alongside matplotlib; no rec.
        return None
    src = source.lower()
    if any(token in src for token in (".boxplot", ".violinplot", ".regplot", "regression", "facet")):
        return (
            "matplotlib used for a statistical plot (box/violin/regression/facet). "
            "Consider seaborn for better defaults and less code."
        )
    if "ggplot" in src or "geom_" in src:
        return (
            "ggplot-style API used via matplotlib. Consider plotnine for the same grammar "
            "without the R bridge."
        )
    return None


def check_plot_script(script_path: Path, journal: str | None) -> dict[str, Any]:
    source = script_path.read_text()
    tree = ast.parse(source, filename=str(script_path))

    libs = _detect_libraries(tree)
    rcparams = _find_rcparam_font_sizes(tree)
    savefigs = _savefig_kwargs(tree)
    rec = _recommend_library(libs, source)

    issues: list[dict[str, Any]] = []
    if journal:
        min_pt = JOURNAL_MIN_PT.get(journal.lower())
        if min_pt is None:
            issues.append({"kind": "unknown_journal", "journal": journal})
        else:
            for r in rcparams:
                if r["pt"] < min_pt:
                    issues.append({
                        "kind": "font_size_below_journal",
                        "key": r["key"],
                        "pt": r["pt"],
                        "minimum_pt": min_pt,
                    })

    for sf in savefigs:
        if "transparent" in sf and sf["transparent"] is False:
            issues.append({
                "kind": "savefig_not_transparent",
                "note": "transparent=True is recommended so the figure composites cleanly on any background.",
            })
        if "bbox_inches" not in sf:
            issues.append({
                "kind": "savefig_missing_bbox_inches",
                "note": "bbox_inches='tight' avoids leftover whitespace around the saved figure.",
            })

    return {
        "input": str(script_path),
        "libraries_detected": libs,
        "rcparam_font_sizes": rcparams,
        "savefig_calls": savefigs,
        "library_recommendation": rec,
        "issues": issues,
        "summary": {"issue_count": len(issues)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Static analysis on a Python plot script.")
    parser.add_argument("script", type=Path, help="Python script to inspect")
    parser.add_argument(
        "--journal",
        choices=["nature", "science", "cell", "pnas", "generic"],
        help="Target journal (sets font-size minimum).",
    )
    args = parser.parse_args(argv)

    if not args.script.exists():
        print(f"error: script not found: {args.script}", file=sys.stderr)
        return 2
    try:
        report = check_plot_script(args.script, args.journal)
    except SyntaxError as exc:
        print(f"error: SyntaxError in '{args.script}': {exc}", file=sys.stderr)
        return 2

    json.dump(report, sys.stdout, indent=2)
    print(file=sys.stdout)
    if report["issues"]:
        print(f"check_plot_script: {len(report['issues'])} issue(s).", file=sys.stderr)
        return 1
    print("check_plot_script: clean.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
