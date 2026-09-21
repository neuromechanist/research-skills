#!/usr/bin/env python3
"""Apply SemBr with conservative guards for source files.

The external ``sembr`` command is intentionally kept separate from this
wrapper. This script protects LaTeX regions whose line breaks are meaningful,
checks whitespace-delimited token alignment, and optionally verifies the
compiled output before replacing the requested destination.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterable, Sequence
from pathlib import Path

VERBATIM_RE = re.compile(
    r"(?ms)(?:^|\r?\n)[ \t]*\\begin\{verbatim\}.*?^[ \t]*\\end\{verbatim\}[ \t]*(?:\r\n|\n|$)"
)
COMMENT_RE = re.compile(r"(?m)(?:^|\r?\n)[ \t]*%[^\r\n]*(?:\r\n|\n|$)")
VERBATIM_MARKER_RE = re.compile(r"\\(?P<kind>begin|end)\{verbatim\}")
PARAGRAPH_SEPARATOR_RE = re.compile(r"(\r?\n[ \t]*\r?\n+)")


def _line_ending(text: str) -> str:
    if text.endswith("\r\n"):
        return "\r\n"
    if text.endswith("\n"):
        return "\n"
    return ""


def _next_placeholder(source: str, index: int) -> tuple[str, int]:
    while True:
        token = f"SEMBRPROTECTEDTOKEN{index:04d}"
        if token not in source:
            return token, index + 1
        index += 1


def protect_latex_regions(source: str) -> tuple[str, dict[str, str]]:
    """Replace verbatim blocks and full-line comments with atomic tokens.

    The replacement keeps the protected region's line ending so SemBr still
    sees a line-oriented document. A malformed verbatim pair is rejected
    rather than passed through to a formatter that could corrupt it.
    """

    depth = 0
    for marker in VERBATIM_MARKER_RE.finditer(source):
        if marker.group("kind") == "begin":
            depth += 1
        elif depth == 0:
            raise ValueError("unmatched \\begin{verbatim} or \\end{verbatim} block")
        else:
            depth -= 1
    if depth:
        raise ValueError("unmatched \\begin{verbatim} or \\end{verbatim} block")

    regions: list[tuple[int, int]] = [
        (match.start(), match.end()) for match in VERBATIM_RE.finditer(source)
    ]
    for match in COMMENT_RE.finditer(source):
        if not any(start < match.end() and match.start() < end for start, end in regions):
            regions.append((match.start(), match.end()))
    regions.sort()

    protected: dict[str, str] = {}
    chunks: list[str] = []
    cursor = 0
    placeholder_index = 1
    for start, end in regions:
        if start < cursor:
            continue
        raw = source[start:end]
        token, placeholder_index = _next_placeholder(source, placeholder_index)
        protected[token] = raw
        chunks.append(source[cursor:start])
        chunks.append(token)
        chunks.append(_line_ending(raw))
        cursor = end
    chunks.append(source[cursor:])
    return "".join(chunks), protected


def restore_latex_regions(source: str, protected: dict[str, str]) -> str:
    """Restore protected regions and reject missing or duplicated tokens."""

    restored = source
    for token, raw in protected.items():
        count = restored.count(token)
        if count != 1:
            raise ValueError(
                f"protected token {token} occurred {count} times after SemBr"
            )
        start = restored.index(token)
        end = start + len(token)
        if _line_ending(raw):
            generated_whitespace = re.match(
                r"[ \t]*(?:(?:\r\n|\n)[ \t]*)*", restored[end:]
            )
            if generated_whitespace:
                end += generated_whitespace.end()
        restored = restored[:start] + raw + restored[end:]
    return restored


def _token_alignment(original: str, candidate: str) -> list[tuple[str, int, int, int, int]]:
    return difflib.SequenceMatcher(
        None, original.split(), candidate.split(), autojunk=False
    ).get_opcodes()


def _same_tokens(original: str, candidate: str) -> bool:
    return all(tag == "equal" for tag, *_ in _token_alignment(original, candidate))


def _paragraph_parts(source: str) -> list[str]:
    return PARAGRAPH_SEPARATOR_RE.split(source)


def restore_changed_spans(original: str, candidate: str) -> str:
    """Keep candidate breaks only in spans whose tokens remain identical.

    SemBr should change whitespace, not source content. When token alignment
    reports a replacement, insertion, or deletion, the smallest practical
    source span here is the paragraph containing that divergence. That
    conservative rollback prevents a comment-truncation or LaTeX-escape bug
    from surviving while retaining valid semantic breaks in other paragraphs.
    If paragraph boundaries themselves diverge, the complete original is
    returned because there is no safe one-to-one span mapping.
    """

    original_parts = _paragraph_parts(original)
    candidate_parts = _paragraph_parts(candidate)
    if len(original_parts) != len(candidate_parts):
        return original

    content_changed = False
    content_matches: list[bool] = []
    for index in range(0, len(original_parts), 2):
        same = _same_tokens(original_parts[index], candidate_parts[index])
        content_matches.append(same)
        content_changed = content_changed or not same

    if not content_changed:
        return candidate

    restored: list[str] = []
    content_index = 0
    for index, (original_part, candidate_part) in enumerate(
        zip(original_parts, candidate_parts)
    ):
        if index % 2 == 1:
            # A changed content span owns its surrounding separator too.
            restored.append(original_part)
            continue
        if content_matches[content_index]:
            restored.append(candidate_part)
        else:
            restored.append(original_part)
        content_index += 1
    return "".join(restored)


def _read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _run_sembr(
    executable: str, input_path: Path, output_path: Path, extra_args: Sequence[str]
) -> None:
    command = [executable, "-i", str(input_path), "-o", str(output_path), *extra_args]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as error:
        raise RuntimeError(f"could not run SemBr: {error}") from error
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"SemBr failed with exit code {result.returncode}: {detail}")


def _format_command(command: Sequence[str], source: Path, build_dir: Path) -> list[str]:
    formatted = [
        token.replace("{source}", str(source)).replace("{build_dir}", str(build_dir))
        for token in command
    ]
    if not any("{source}" in token for token in command):
        formatted.append(str(source))
    return formatted


def _find_pdf(build_dir: Path) -> Path:
    pdfs = sorted(path for path in build_dir.rglob("*.pdf") if path.is_file())
    if len(pdfs) != 1:
        names = ", ".join(str(path.relative_to(build_dir)) for path in pdfs)
        raise RuntimeError(
            f"expected exactly one compiled PDF in {build_dir}, found {len(pdfs)}"
            + (f": {names}" if names else "")
        )
    return pdfs[0]


def _compile_and_extract(
    command: Sequence[str], source: Path, build_dir: Path, pdftotext: str
) -> bytes:
    build_dir.mkdir(parents=True, exist_ok=True)
    formatted = _format_command(command, source, build_dir)
    try:
        result = subprocess.run(
            formatted,
            cwd=source.parent,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise RuntimeError(f"could not run compile command: {error}") from error
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(
            f"compile command failed with exit code {result.returncode}: {detail}"
        )

    pdf = _find_pdf(build_dir)
    try:
        extracted = subprocess.run(
            [pdftotext, str(pdf), "-"],
            check=False,
            capture_output=True,
        )
    except OSError as error:
        raise RuntimeError(f"could not run pdftotext: {error}") from error
    if extracted.returncode:
        detail = extracted.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"pdftotext failed with exit code {extracted.returncode}: {detail}"
        )
    return extracted.stdout


def _compile_gate(
    command: Sequence[str], source: Path, candidate: str, pdftotext: str
) -> None:
    descriptor, candidate_name = tempfile.mkstemp(
        prefix=f".{source.stem}.semantic-",
        suffix=source.suffix,
        dir=source.parent,
    )
    candidate_path = Path(candidate_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(candidate)
        with tempfile.TemporaryDirectory(
            prefix=".semantic-breaks-", dir=source.parent
        ) as temporary_dir:
            root = Path(temporary_dir)
            original_text = _compile_and_extract(
                command, source, root / "original-build", pdftotext
            )
            candidate_text = _compile_and_extract(
                command, candidate_path, root / "candidate-build", pdftotext
            )
            if original_text != candidate_text:
                raise RuntimeError(
                    "compiled pdftotext differs; refusing to write semantic line breaks"
                )
    finally:
        try:
            candidate_path.unlink()
        except FileNotFoundError:
            pass


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply SemBr with LaTeX protection and content-integrity gates."
    )
    parser.add_argument("input", type=Path, help="source file to read")
    parser.add_argument("output", type=Path, help="destination file to write")
    parser.add_argument("--sembr-bin", default="sembr", help="SemBr executable")
    parser.add_argument(
        "--sembr-arg",
        action="append",
        default=[],
        metavar="ARG",
        help="extra argument passed to SemBr; repeat for multiple arguments",
    )
    parser.add_argument(
        "--pdftotext-bin", default="pdftotext", help="pdftotext executable"
    )
    parser.add_argument(
        "--compile-command",
        nargs=argparse.REMAINDER,
        help=(
            "optional compiler command, last argument; use {source} and {build_dir} "
            "placeholders, and route compiler outputs to {build_dir}"
        ),
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        source = args.input.resolve(strict=True)
        destination = args.output.resolve()
        if source == destination:
            raise ValueError("input and output must be different files")
        original = _read_text(source)
        protected, regions = protect_latex_regions(original)
        with tempfile.TemporaryDirectory(prefix="semantic-breaks-") as temporary_dir:
            temporary = Path(temporary_dir)
            protected_path = temporary / source.name
            candidate_path = temporary / f"candidate{source.suffix}"
            _write_atomic(protected_path, protected)
            _run_sembr(args.sembr_bin, protected_path, candidate_path, args.sembr_arg)
            candidate = _read_text(candidate_path)
        guarded = restore_changed_spans(protected, candidate)
        converted = restore_latex_regions(guarded, regions)
        if args.compile_command:
            _compile_gate(args.compile_command, source, converted, args.pdftotext_bin)
        _write_atomic(destination, converted)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
