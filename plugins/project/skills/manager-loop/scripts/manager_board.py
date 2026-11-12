#!/usr/bin/env python3
"""Read, check, update, render, and serve a manager-loop board.

The board is one Markdown file (``board.md``) and it is the only source of truth
for the loop's current state. History lives beside it in ``board-log.md``
(Decisions and Log, append-only). Every command parses those files; nothing
derived is stored. The HTML view, the status summary, and the dispatch plan are
computed from the Markdown each time they are asked for.

Standard library only, so the same script runs under Claude Code, Codex, and
Copilot CLI hosts without installing anything.
"""

from __future__ import annotations

import argparse
import contextlib
import html
import json
import os
import re
import secrets
import stat
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast
from urllib.parse import unquote

try:
    import fcntl

    HAVE_FLOCK = True
except ImportError:  # Windows has no fcntl; writes then say so
    HAVE_FLOCK = False

DESCRIPTION = "Read, check, update, render, and serve a manager-loop board (board.md)."
SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_MD = SKILL_DIR / "assets" / "board-template.md"
TEMPLATE_LOG = SKILL_DIR / "assets" / "board-log-template.md"
TEMPLATE_HTML = SKILL_DIR / "assets" / "board.html"

# Default headers, used when a command has to create a missing section.
# Parity is open-ended: its first column is Tier, its last is Notes, and every
# column between is a platform the owner has added (Claude, Codex, Copilot, ...).
SCHEMA: dict[str, list[str]] = {
    "now": ["Key", "Value"],
    "parity": ["Tier", "Claude", "Codex", "Copilot", "Notes"],
    "slots": ["Slot", "Platform", "Tiers", "Max", "Can", "Notes"],
    "budget": ["Item", "Limit", "Used", "Resets", "Notes"],
    "waves": ["Wave", "Goal", "Agents", "State", "Exit gate"],
    "steps": [
        "ID",
        "Title",
        "Wave",
        "Tier",
        "Needs",
        "Slot",
        "State",
        "Depends",
        "PR",
        "Started",
        "Timebox",
        "Next",
    ],
    "questions": [
        "ID",
        "Step",
        "Question",
        "Options",
        "Default",
        "Needed by",
        "State",
        "Answer",
    ],
    "proposals": ["ID", "Time", "Proposal", "Why", "State"],
    "agents": ["Agent", "Role", "Slot", "Model", "Step", "Started", "State"],
}
HISTORY_SCHEMA: dict[str, list[str]] = {
    "decisions": ["Time", "Decision", "By", "Reason"],
    "log": ["Time", "Event"],
}
SECTION_ORDER = list(SCHEMA)
HISTORY_ORDER = list(HISTORY_SCHEMA)
TITLES = {
    "now": "Now",
    "parity": "Parity",
    "slots": "Slots",
    "budget": "Budget",
    "waves": "Waves",
    "steps": "Steps",
    "questions": "Questions",
    "proposals": "Proposals",
    "agents": "Agents",
    "decisions": "Decisions",
    "log": "Log",
}

STEP_STATES = (
    "outline",
    "todo",
    "active",
    "review",
    "blocked",
    "owner",
    "done",
    "dropped",
)
IN_FLIGHT = ("active", "review")
WAVE_STATES = ("planned", "active", "done", "hold")
QUESTION_STATES = ("open", "answered", "closed", "defaulted")
PROPOSAL_STATES = ("open", "accepted", "rejected", "withdrawn")
RESETS = ("never", "daily", "wave")
EMPTY = {"", "-", "none", "n/a"}
MAX_BOARD_LINES = 300
MAX_CELL_CHARS = 240
MAX_ANSWER_CHARS = 200
LATE_GRACE = timedelta(minutes=10)
RELEASING_STATES = ("paused", "stopped", "done")  # a manager in these holds no lease
LOCK_WAIT = 10.0  # seconds to wait for another writer before giving up
HISTORY_TAIL = 20
CARD_SECTIONS = ("Goal", "Scope", "Acceptance", "Gates", "Stop conditions", "Report")
CARD_PLACEHOLDER = re.compile(
    r"\b(TBD|TODO|FIXME)\b|\?\?\?|\[fill[^\]]*\]", re.IGNORECASE
)
ANGLE_PLACEHOLDER = re.compile(
    r"<[A-Za-z][^<>]*>"
)  # template slots such as <title>, outside code


class BoardError(Exception):
    """A board that cannot be parsed or a command that cannot be applied."""


# ---------------------------------------------------------------------------
# Parsing


@dataclass
class Table:
    header: list[str]
    rows: list[dict[str, str]]
    row_lines: list[int]  # 0-based line index of each row in the file
    header_line: int
    end_line: int  # one past the table's last line

    def column(self, name: str) -> str | None:
        wanted = name.strip().lower()
        for col in self.header:
            if col.strip().lower() == wanted:
                return col
        return None


@dataclass
class Section:
    key: str
    title: str
    start: int  # line index of the "## " heading
    end: int  # one past the section's last line
    table: Table | None = None
    text: str = ""


@dataclass
class Board:
    title: str
    lines: list[str]
    sections: dict[str, Section] = field(default_factory=dict)
    extra: list[Section] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def table(self, key: str) -> Table | None:
        section = self.sections.get(key)
        return section.table if section else None

    def rows(self, key: str) -> list[dict[str, str]]:
        table = self.table(key)
        return table.rows if table else []

    def now(self) -> dict[str, str]:
        return {
            row.get("Key", "").strip(): row.get("Value", "").strip()
            for row in self.rows("now")
        }


def split_cells(line: str) -> list[str]:
    """Split one Markdown table line into cells, honoring ``\\|`` escapes."""
    body = line.strip()
    body = body.removeprefix("|")
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    cells: list[str] = []
    current: list[str] = []
    i = 0
    while i < len(body):
        char = body[i]
        if char == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            current.append("|")
            i += 2
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        i += 1
    cells.append("".join(current).strip())
    return cells


def escape_cell(value: str) -> str:
    text = " ".join(str(value).split())
    return text.replace("|", "\\|")


def format_row(cells: list[str]) -> str:
    return "| " + " | ".join(escape_cell(c) for c in cells) + " |"


def format_separator(header: list[str]) -> str:
    return "|" + "|".join("---" for _ in header) + "|"


SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def section_key(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


FENCE_OPEN = re.compile(r"^\s*(?:(`{3,})[^`]*|(~{3,}).*)$")


def inert_lines(lines: list[str]) -> list[bool]:
    """Mark lines inside a fenced code block or an HTML comment.

    Inert lines are never headings and never start or continue a table.
    One classifier serves every parser here, so they agree on what is prose.
    """
    mask: list[bool] = []
    fence = ""
    in_comment = False
    for line in lines:
        if in_comment:
            mask.append(True)
            in_comment = "-->" not in line
            continue
        if fence:
            mask.append(True)
            body = line.strip()
            if body and set(body) == {fence[0]} and len(body) >= len(fence):
                fence = ""
            continue
        opened = FENCE_OPEN.match(line)
        if opened:
            fence = opened.group(1) or opened.group(2)
            mask.append(True)
            continue
        if line.lstrip().startswith("<!--"):
            mask.append(True)
            in_comment = "-->" not in line.lstrip()[4:]
            continue
        mask.append(False)
    return mask


def parse_table(
    lines: list[str],
    start: int,
    end: int,
    where: str,
    errors: list[str],
    inert: list[bool],
) -> Table | None:
    def is_row(index: int) -> bool:
        return not inert[index] and lines[index].lstrip().startswith("|")

    i = start
    while i < end and not is_row(i):
        i += 1
    if i >= end:
        return None
    header_line = i
    header = split_cells(lines[i])
    if i + 1 >= end or inert[i + 1] or not SEPARATOR.match(lines[i + 1]):
        errors.append(
            f"{where}: line {i + 2}: table header is not followed by a |---| separator"
        )
        return None
    names: set[str] = set()
    for col in header:
        if col.strip().lower() in names:
            errors.append(f"{where}: duplicate column {col!r}")
        names.add(col.strip().lower())
    rows: list[dict[str, str]] = []
    row_lines: list[int] = []
    j = i + 2
    while j < end and is_row(j):
        cells = split_cells(lines[j])
        if len(cells) != len(header):
            errors.append(
                f"{where}: line {j + 1}: {len(cells)} cells, header has {len(header)}"
                " (escape a literal | as \\|)"
            )
            cells = (cells + [""] * len(header))[: len(header)]
        rows.append(dict(zip(header, cells, strict=True)))
        row_lines.append(j)
        j += 1
    return Table(
        header=header,
        rows=rows,
        row_lines=row_lines,
        header_line=header_line,
        end_line=j,
    )


def parse_board(text: str, known: dict[str, list[str]] | None = None) -> Board:
    known = SCHEMA if known is None else known
    lines = text.splitlines()
    inert = inert_lines(lines)
    title = ""
    headings: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        if inert[idx]:
            continue
        if not title and line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            headings.append((idx, line[3:].strip()))
    board = Board(title=title, lines=lines)
    for n, (idx, heading) in enumerate(headings):
        end = headings[n + 1][0] if n + 1 < len(headings) else len(lines)
        key = section_key(heading)
        section = Section(key=key, title=heading, start=idx, end=end)
        section.table = parse_table(
            lines, idx + 1, end, f"## {heading}", board.errors, inert
        )
        section.text = "\n".join(lines[idx + 1 : end]).strip()
        if key in known:
            if key in board.sections:
                board.errors.append(f"## {heading}: duplicate section")
            board.sections[key] = section
        else:
            board.extra.append(section)
    return board


def parse_history(text: str) -> Board:
    return parse_board(text, HISTORY_SCHEMA)


# ---------------------------------------------------------------------------
# Values


def is_empty(value: str | None) -> bool:
    return value is None or value.strip().lower() in EMPTY


def split_list(value: str | None) -> list[str]:
    if value is None or is_empty(value):
        return []
    return [item.strip() for item in re.split(r"[,;]", value) if item.strip()]


def split_options(value: str | None) -> list[str]:
    if value is None or is_empty(value):
        return []
    return [item.strip() for item in value.split(" / ") if item.strip()]


def option_name(option: str) -> str:
    return re.sub(r"\s*\(recommended\)\s*$", "", option, flags=re.IGNORECASE).strip()


def plain_id(value: str) -> str:
    """Strip Markdown decoration from an id cell: links, backticks, bold."""
    text = value.strip()
    match = re.fullmatch(r"\[([^\]]+)\]\([^)]*\)", text)
    if match:
        text = match.group(1)
    return text.strip("`* ")


def first_number(value: str | None) -> float | None:
    if value is None or is_empty(value):
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
    return float(match.group(0)) if match else None


def local_now() -> datetime:
    return datetime.now().astimezone()


def stamp(moment: datetime | None = None) -> str:
    return (moment or local_now()).isoformat(timespec="minutes")


def parse_time(value: str | None) -> datetime | None:
    if value is None or is_empty(value):
        return None
    text = value.strip().strip("`")
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.astimezone()
    return moment


DURATION_TOKEN = re.compile(r"(\d+(?:\.\d+)?)\s*([smhd])")
DURATION_FULL = re.compile(r"(?:\d+(?:\.\d+)?\s*[smhd]\s*)+")
DURATION_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def parse_duration(value: str) -> timedelta:
    """Read ``30m``, ``1h30m``, ``2d``, or a bare number of minutes; nothing else."""
    text = value.strip().lower()
    if re.fullmatch(r"\d+", text):
        return timedelta(minutes=int(text))
    if not DURATION_FULL.fullmatch(text):
        raise BoardError(
            f"cannot read duration {value!r}; use forms like 30m, 2h, 1h30m, 2d"
            " (a bare number is minutes)"
        )
    return timedelta(
        seconds=sum(
            float(amount) * DURATION_SECONDS[unit]
            for amount, unit in DURATION_TOKEN.findall(text)
        )
    )


def try_duration(value: str | None) -> timedelta | None:
    if value is None or is_empty(value):
        return None
    try:
        return parse_duration(value)
    except BoardError:
        return None


def history_path(board_path: Path) -> Path:
    return board_path.with_name(f"{board_path.stem}-log{board_path.suffix}")


def platforms(board: Board) -> list[str]:
    table = board.table("parity")
    if not table:
        return []
    return [c for c in table.header[1:] if c.strip().lower() != "notes"]


# ---------------------------------------------------------------------------
# Validation and derived state


def id_column(board: Board, key: str) -> str:
    """The column that names a row: the table's first header, whatever it is called."""
    table = board.table(key)
    return table.header[0] if table and table.header else SCHEMA[key][0]


def row_id(board: Board, key: str, row: dict[str, str]) -> str:
    return plain_id(row.get(id_column(board, key), ""))


def step_index(board: Board) -> dict[str, dict[str, str]]:
    return {
        sid: row for row in board.rows("steps") if (sid := row_id(board, "steps", row))
    }


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for dep in graph.get(node, []):
            if dep not in graph:
                continue
            if state.get(dep) == 1:
                return stack[stack.index(dep) :] + [dep]
            if state.get(dep) is None:
                found = visit(dep)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in graph:
        if state.get(node) is None:
            found = visit(node)
            if found:
                return found
    return None


def check_states(
    board: Board, key: str, allowed: tuple[str, ...], errors: list[str]
) -> None:
    seen: set[str] = set()
    id_col = id_column(board, key)
    for row in board.rows(key):
        rid = row_id(board, key, row)
        if rid in seen:
            errors.append(f"## {TITLES[key]}: duplicate {id_col} {rid}")
        seen.add(rid)
        state = row.get("State", "").strip().lower()
        if state not in allowed:
            errors.append(
                f"## {TITLES[key]}: {rid}: state {state!r} is not one of {', '.join(allowed)}"
            )


def validate(board: Board) -> tuple[list[str], list[str]]:
    errors = list(board.errors)
    warnings: list[str] = []
    if "steps" not in board.sections or board.table("steps") is None:
        errors.append("## Steps: missing section or table")
        return errors, warnings

    if len(board.lines) > MAX_BOARD_LINES:
        errors.append(
            f"board has {len(board.lines)} lines (limit {MAX_BOARD_LINES}); it holds state only:"
            " move history to the log, specs to cards, and run `archive`"
        )
    for key, section in board.sections.items():
        if not section.table:
            continue
        first = section.table.header[0]
        for row in section.table.rows:
            rid = plain_id(row.get(first, ""))
            for col, value in row.items():
                if len(value) > MAX_CELL_CHARS:
                    errors.append(
                        f"## {TITLES.get(key, key)}: row {rid!r}: {col!r} has {len(value)} characters"
                        f" (limit {MAX_CELL_CHARS}); put detail in the card or the log"
                    )

    steps_table = board.table("steps")
    if steps_table and steps_table.column("State") is None:
        errors.append("## Steps: missing column 'State'")
    seen: set[str] = set()
    graph: dict[str, list[str]] = {}
    slots = {plain_id(r.get("Slot", "")) for r in board.rows("slots")}
    waves = {plain_id(r.get("Wave", "")) for r in board.rows("waves")}
    tiers = {plain_id(r.get("Tier", "")) for r in board.rows("parity")}
    for row in board.rows("steps"):
        sid = row_id(board, "steps", row)
        if not sid:
            errors.append("## Steps: a row has an empty ID")
            continue
        if sid in seen:
            errors.append(f"## Steps: duplicate ID {sid}")
        seen.add(sid)
        graph[sid] = [plain_id(d) for d in split_list(row.get("Depends"))]
        state = row.get("State", "").strip().lower()
        if state not in STEP_STATES:
            errors.append(
                f"## Steps: {sid}: state {state!r} is not one of {', '.join(STEP_STATES)}"
            )
        slot = plain_id(row.get("Slot", ""))
        if board.rows("slots") and not is_empty(slot) and slot not in slots:
            errors.append(f"## Steps: {sid}: slot {slot!r} is not in ## Slots")
        if state in IN_FLIGHT and board.rows("slots") and is_empty(slot):
            warnings.append(f"## Steps: {sid} is {state} but has no slot")
        wave = plain_id(row.get("Wave", ""))
        if board.rows("waves") and not is_empty(wave) and wave not in waves:
            errors.append(f"## Steps: {sid}: wave {wave!r} is not in ## Waves")
        tier = plain_id(row.get("Tier", ""))
        if board.rows("parity") and not is_empty(tier) and tier not in tiers:
            warnings.append(f"## Steps: {sid}: tier {tier!r} is not in ## Parity")
        if not is_empty(row.get("Started")) and parse_time(row.get("Started")) is None:
            errors.append(
                f"## Steps: {sid}: cannot read Started {row.get('Started')!r}"
            )
        if (
            not is_empty(row.get("Timebox"))
            and try_duration(row.get("Timebox")) is None
        ):
            errors.append(
                f"## Steps: {sid}: cannot read Timebox {row.get('Timebox')!r} (use 4h, 2d)"
            )
    for sid, deps in graph.items():
        for dep in deps:
            if dep not in graph:
                errors.append(f"## Steps: {sid} depends on unknown step {dep}")
    cycle = find_cycle(graph)
    if cycle:
        errors.append("## Steps: dependency cycle " + " -> ".join(cycle))

    known_platforms = {p.lower() for p in platforms(board)}
    for row in board.rows("slots"):
        name = plain_id(row.get("Slot", ""))
        if first_number(row.get("Max")) is None:
            errors.append(
                f"## Slots: {name}: Max {row.get('Max', '')!r} is not a number"
            )
        platform = row.get("Platform", "").strip().lower()
        if known_platforms and platform and platform not in known_platforms:
            warnings.append(
                f"## Slots: {name}: platform {row.get('Platform')!r} has no ## Parity column;"
                " ask the owner to add it"
            )
        for tier in split_list(row.get("Tiers")):
            if tiers and plain_id(tier) not in tiers:
                warnings.append(f"## Slots: {name}: tier {tier!r} is not in ## Parity")

    check_states(board, "waves", WAVE_STATES, errors)
    check_states(board, "questions", QUESTION_STATES, errors)
    check_states(board, "proposals", PROPOSAL_STATES, errors)
    for row in board.rows("questions"):
        qid = row_id(board, "questions", row)
        if (
            not is_empty(row.get("Needed by"))
            and parse_time(row.get("Needed by")) is None
        ):
            errors.append(
                f"## Questions: {qid}: cannot read 'Needed by' {row.get('Needed by')!r}"
            )
        options = split_options(row.get("Options"))
        state = row.get("State", "").strip().lower()
        if (
            state == "open"
            and options
            and not any("(recommended)" in o.lower() for o in options)
        ):
            warnings.append(f"## Questions: {qid}: no option is marked (Recommended)")

    now = board.now()
    for key in ("Last tick", "Next tick"):
        if not is_empty(now.get(key)) and parse_time(now.get(key)) is None:
            errors.append(f"## Now: cannot read {key!r} {now.get(key)!r}")

    for row in board.rows("budget"):
        item = row.get("Item", "")
        limit, used = first_number(row.get("Limit")), first_number(row.get("Used"))
        if limit is not None and used is not None and used > limit:
            warnings.append(
                f"## Budget: {item}: used {used:g} is over the limit {limit:g}"
            )
        resets = row.get("Resets", "never").strip().lower() or "never"
        if "Resets" in row and resets not in RESETS:
            errors.append(
                f"## Budget: {item}: Resets {resets!r} is not one of {', '.join(RESETS)}"
            )
    return errors, warnings


def lane_of(state: str, ready: bool) -> str:
    if state in ("outline", "todo"):
        return "ready" if ready else "todo"
    if state in ("blocked", "owner"):
        return "attention"
    return state  # active, review, done, dropped


def analyze(
    board: Board, history: Board | None = None, now: datetime | None = None
) -> dict:
    """Everything the status command and the HTML view need, computed from the board."""
    now = now or local_now()
    errors, warnings = validate(board)
    steps = step_index(board)
    wave_rows = {plain_id(r.get("Wave", "")): r for r in board.rows("waves")}
    parity = {plain_id(r.get("Tier", "")): r for r in board.rows("parity")}

    slots: list[dict[str, Any]] = []
    for row in board.rows("slots"):
        name = plain_id(row.get("Slot", ""))
        slots.append(
            {
                **row,
                "name": name,
                "max": int(first_number(row.get("Max")) or 0),
                "tiers": [plain_id(t) for t in split_list(row.get("Tiers"))],
                "can": [c.lower() for c in split_list(row.get("Can"))],
                "platform": row.get("Platform", "").strip(),
            }
        )
    slot_by_name = {s["name"]: s for s in slots}

    out_steps: list[dict[str, Any]] = []
    for sid, row in steps.items():
        state = row.get("State", "").strip().lower()
        deps = [plain_id(d) for d in split_list(row.get("Depends"))]
        unmet = [
            d
            for d in deps
            if steps.get(d, {}).get("State", "").strip().lower() != "done"
        ]
        wave = plain_id(row.get("Wave", ""))
        wave_state = (
            wave_rows.get(wave, {}).get("State", "").strip().lower() if wave else ""
        )
        wave_open = not wave or not wave_rows or wave_state == "active"
        ready = state == "todo" and not unmet and wave_open
        started = parse_time(row.get("Started"))
        box = try_duration(row.get("Timebox"))
        timebox = ""
        if started and box and state in IN_FLIGHT:
            if now > started + 2 * box:
                timebox = "twice"
            elif now > started + box:
                timebox = "over"
        tier = plain_id(row.get("Tier", ""))
        slot = slot_by_name.get(plain_id(row.get("Slot", "")))
        model = ""
        if slot and tier in parity:
            column = next(
                (c for c in parity[tier] if c.lower() == slot["platform"].lower()), None
            )
            model = parity[tier].get(column, "") if column else ""
        out_steps.append(
            {
                **row,
                "id": sid,
                "state": state,
                "lane": lane_of(state, ready),
                "ready": ready,
                "unmet": unmet,
                "wave_open": wave_open,
                "needs": split_list(row.get("Needs")),
                "timebox_state": timebox,
                "model": model,
            }
        )

    # Slot use and a greedy dispatch plan in table order (the order is the priority).
    for slot in slots:
        slot["holding"] = [
            s["id"]
            for s in out_steps
            if s["state"] in IN_FLIGHT and plain_id(s.get("Slot", "")) == slot["name"]
        ]
        slot["free"] = max(slot["max"] - len(slot["holding"]), 0)
    free: dict[str, int] = {s["name"]: s["free"] for s in slots}
    dispatch: list[dict[str, str]] = []
    unplaced: list[dict[str, str]] = []
    for step in out_steps:
        if not step["ready"]:
            continue
        if not slots:
            dispatch.append({"step": step["id"], "slot": "", "model": ""})
            continue
        tier = plain_id(step.get("Tier", ""))
        needs = {n.lower() for n in step["needs"]}
        fitting = [
            s
            for s in slots
            if (not s["tiers"] or is_empty(tier) or tier in s["tiers"])
            and needs <= set(s["can"])
        ]
        target = next((s for s in fitting if free[s["name"]] > 0), None)
        if target:
            free[target["name"]] -= 1
            model = ""
            if tier in parity:
                column = next(
                    (
                        c
                        for c in parity[tier]
                        if c.lower() == target["platform"].lower()
                    ),
                    None,
                )
                model = parity[tier].get(column, "") if column else ""
            dispatch.append(
                {"step": step["id"], "slot": target["name"], "model": model}
            )
        else:
            reason = (
                "no slot takes this tier and these needs"
                if not fitting
                else "fitting slots are full"
            )
            unplaced.append({"step": step["id"], "reason": reason})
    idle = [name for name, n in free.items() if n > 0]
    for slot in slots:
        if len(slot["holding"]) > slot["max"]:
            warnings.append(f"## Slots: {slot['name']} holds more steps than its Max")

    waves: list[dict[str, Any]] = []
    for wid, row in wave_rows.items():
        members = [s for s in out_steps if plain_id(s.get("Wave", "")) == wid]
        live = [s for s in members if s["state"] != "dropped"]
        waves.append(
            {
                **row,
                "id": wid,
                "state": row.get("State", "").strip().lower(),
                "total": len(live),
                "done": sum(1 for s in live if s["state"] == "done"),
                "steps": [s["id"] for s in members],
            }
        )

    questions: list[dict[str, Any]] = []
    for row in board.rows("questions"):
        state = row.get("State", "").strip().lower()
        needed = parse_time(row.get("Needed by"))
        questions.append(
            {
                **row,
                "id": row_id(board, "questions", row),
                "state": state,
                "options": split_options(row.get("Options")),
                "overdue": bool(state == "open" and needed and needed < now),
                "has_default": not is_empty(row.get("Default")),
                "needed_by": needed.isoformat() if needed else "",
            }
        )

    budget: list[dict[str, Any]] = []
    for row in board.rows("budget"):
        limit, used = first_number(row.get("Limit")), first_number(row.get("Used"))
        ratio = (used / limit) if (limit and used is not None) else None
        budget.append({**row, "limit": limit, "used": used, "ratio": ratio})

    info = board.now()
    last, nxt = parse_time(info.get("Last tick")), parse_time(info.get("Next tick"))
    running = info.get("State", "").strip().lower() == "running"
    late = bool(nxt and running and now > nxt + LATE_GRACE)

    needs_you: list[dict[str, str]] = []
    if late:
        needs_you.append(
            {
                "kind": "late",
                "text": "the manager missed its wake; check that the loop is alive",
            }
        )
    for q in questions:
        if q["state"] == "open":
            needs_you.append(
                {"kind": "question", "id": q["id"], "text": q.get("Question", "")}
            )
    for s in out_steps:
        if s["state"] == "owner":
            needs_you.append(
                {
                    "kind": "step",
                    "id": s["id"],
                    "text": s.get("Next", "") or s.get("Title", ""),
                }
            )
    proposals = [
        {**p, "id": row_id(board, "proposals", p)} for p in board.rows("proposals")
    ]
    for p in proposals:
        if p.get("State", "").strip().lower() == "open":
            needs_you.append(
                {"kind": "proposal", "id": p["id"], "text": p.get("Proposal", "")}
            )

    decisions = history.rows("decisions")[-HISTORY_TAIL:] if history else []
    log = history.rows("log")[-HISTORY_TAIL:] if history else []
    return {
        "title": board.title,
        "generated": now.isoformat(timespec="seconds"),
        "now": info,
        "heartbeat": {
            "manager": info.get("Manager id", ""),
            "last": last.isoformat() if last else "",
            "next": nxt.isoformat() if nxt else "",
            "late": late,
        },
        "platforms": platforms(board),
        "parity": board.rows("parity"),
        "slots": slots,
        "budget": budget,
        "waves": waves,
        "steps": out_steps,
        "dispatch": dispatch,
        "unplaced": unplaced,
        "idle_slots": idle,
        "questions": questions,
        "proposals": proposals,
        "agents": board.rows("agents"),
        "needs_you": needs_you,
        "decisions": decisions,
        "log": log,
        "extra": [{"title": s.title, "text": s.text} for s in board.extra],
        "errors": errors,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Writing


_HELD = threading.local()


@contextlib.contextmanager
def board_lock(path: Path):
    """Hold the one lock for the board's directory (the board and its log share it).

    The lock is re-entrant within a thread, so a command can hold it across
    both files. It is an ``flock`` on the directory itself, so it never depends
    on a temporary directory and a crashed writer cannot leave it stuck.
    """
    if not HAVE_FLOCK:
        raise BoardError("manager_board.py needs a POSIX system (macOS, Linux, or WSL)")
    directory = str(path.resolve().parent)
    held: set[str] = _HELD.__dict__.setdefault("dirs", set())
    if directory in held:
        yield
        return
    fd = os.open(directory, os.O_RDONLY)
    try:
        deadline = time.monotonic() + LOCK_WAIT
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise BoardError("board is locked by another writer") from None
                time.sleep(0.05)
        held.add(directory)
        try:
            yield
        finally:
            held.discard(directory)
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_atomic(path: Path, text: str) -> None:
    """Replace a file in one step, keeping its permissions and any symlink to it."""
    target = Path(os.path.realpath(path))
    try:
        mode: int | None = stat.S_IMODE(target.stat().st_mode)
    except FileNotFoundError:
        mode = None
    tmp = target.with_name(f".{target.name}.{secrets.token_hex(6)}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        if mode is not None:
            os.chmod(tmp, mode)
        os.replace(tmp, target)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        raise


def resolve_section(key: str) -> str:
    wanted = section_key(key)
    for name, title in TITLES.items():
        if wanted in (name, title.lower()):
            return name
    raise BoardError(
        f"unknown section {key!r}; choose from: {', '.join(TITLES.values())}"
    )


def ensure_section(
    lines: list[str], key: str, schema: dict[str, list[str]]
) -> list[str]:
    """Append a missing standard section (heading and empty table) in canonical order."""
    board = parse_board("\n".join(lines), schema)
    header = schema[key]
    table_block = [format_row(header), format_separator(header)]
    if key in board.sections and board.sections[key].table is not None:
        return lines
    if key in board.sections:  # heading without a table: add the table under it
        at = board.sections[key].start + 1
        return lines[:at] + [""] + table_block + lines[at:]
    order = list(schema)
    later = [
        board.sections[k].start
        for k in order[order.index(key) + 1 :]
        if k in board.sections
    ]
    at = min(later) if later else len(lines)
    block = [f"## {TITLES[key]}", "", *table_block, ""]
    if at > 0 and lines[at - 1].strip():
        block.insert(0, "")
    return lines[:at] + block + lines[at:]


def apply_row(
    text: str,
    key: str,
    row_key: str | None,
    values: dict[str, str],
    create: bool,
    schema: dict[str, list[str]] | None = None,
) -> str:
    """Update the row whose first cell is ``row_key`` or, with ``create``, append a row."""
    schema = SCHEMA if schema is None else schema
    lines = text.splitlines()
    if create:
        lines = ensure_section(lines, key, schema)
    board = parse_board("\n".join(lines), schema)
    if board.errors:
        raise BoardError("fix the file before writing: " + "; ".join(board.errors))
    table = board.table(key)
    if table is None:
        raise BoardError(
            f"## {TITLES[key]}: no table (use --new to create the section)"
        )
    columns = {}
    for name, value in values.items():
        col = table.column(name)
        if col is None:
            raise BoardError(
                f"## {TITLES[key]}: no column {name!r}; columns are {', '.join(table.header)}"
            )
        columns[col] = value
    first = table.header[0]
    match = None
    if row_key is not None:
        for idx, row in enumerate(table.rows):
            if plain_id(row.get(first, "")) == plain_id(row_key):
                match = idx
                break
    if match is not None:
        if create:
            raise BoardError(f"## {TITLES[key]}: a row {row_key!r} already exists")
        row = dict(table.rows[match])
        row.update(columns)
        lines[table.row_lines[match]] = format_row(
            [row.get(col, "") for col in table.header]
        )
    else:
        if not create:
            raise BoardError(
                f"## {TITLES[key]}: no row {row_key!r} (use --new to append one)"
            )
        row = {col: "" for col in table.header}
        if row_key is not None:
            row[first] = row_key
        row.update(columns)
        lines.insert(
            table.end_line, format_row([row.get(col, "") for col in table.header])
        )
    return "\n".join(lines) + "\n"


def remove_rows(text: str, key: str, ids: set[str]) -> str:
    board = parse_board(text)
    table = board.table(key)
    if not table or not ids:
        return text
    first = table.header[0]
    drop = {
        line
        for row, line in zip(table.rows, table.row_lines, strict=True)
        if plain_id(row[first]) in ids
    }
    return (
        "\n".join(line for i, line in enumerate(text.splitlines()) if i not in drop)
        + "\n"
    )


def normalize_error(error: str) -> str:
    """An error without its counts, so a board that grew is still the same error."""
    return re.sub(r"\d+ (lines|characters)", r"N \1", error)


def read_board(path: Path) -> str:
    if not path.exists():
        raise BoardError(f"{path}: no such board")
    return read_utf8(path)


def history_text(board_path: Path) -> str:
    """The log's text (or a fresh log), refusing a log with parse errors."""
    path = history_path(board_path)
    if path.exists():
        text = read_utf8(path)
        errors = parse_history(text).errors
        if errors:
            raise BoardError(
                f"{path.name}: the log has errors; fix it before writing: "
                + "; ".join(errors)
            )
        return text
    title = parse_board(read_utf8(board_path)).title if board_path.exists() else "Board"
    return read_utf8(TEMPLATE_LOG).replace("__TITLE__", title)


def add_history(text: str, entries: list[tuple[str, dict[str, str]]]) -> str:
    for key, values in entries:
        text = apply_row(text, key, None, values, create=True, schema=HISTORY_SCHEMA)
    return text


def mutate(
    path: Path, change: Callable[[str], str], events: list[str] | None = None
) -> None:
    """Apply ``change`` to the board under the lock.

    A board that already has parse errors is not written. Validation errors
    that existed before the change do not block it; only new ones do. Pass a
    list as ``events`` when the change also logs: the log is checked before
    anything changes, the lines ``change`` appends to the list are written to
    the log first, and the board is written last, so a failure never loses a row.
    """
    with board_lock(path):
        text = read_board(path)
        before = parse_board(text)
        if before.errors:
            raise BoardError("fix the file before writing: " + "; ".join(before.errors))
        known = {normalize_error(e) for e in validate(before)[0]}
        log = history_text(path) if events is not None else None
        new = change(text)
        fresh = [
            e for e in validate(parse_board(new))[0] if normalize_error(e) not in known
        ]
        if fresh:
            raise BoardError(
                "the change would leave the board invalid: " + "; ".join(fresh)
            )
        if log is not None and events:
            when = stamp()
            rows = [("log", {"Time": when, "Event": event}) for event in events]
            write_atomic(history_path(path), add_history(log, rows))
        if new != text:
            write_atomic(path, new)


def append_history(board_path: Path, key: str, values: dict[str, str]) -> None:
    with board_lock(board_path):
        text = add_history(history_text(board_path), [(key, values)])
        write_atomic(history_path(board_path), text)


def load_history(board_path: Path) -> Board | None:
    path = history_path(board_path)
    return parse_history(read_utf8(path)) if path.exists() else None


def record_answer(path: Path, qid: str, answer: str, by: str) -> None:
    answer = " ".join(answer.split())
    if not answer:
        raise BoardError("empty answer")
    if len(answer) > MAX_ANSWER_CHARS:
        raise BoardError(
            f"answer is {len(answer)} characters (limit {MAX_ANSWER_CHARS}); reply in the session"
        )

    def change(text: str) -> str:
        board = parse_board(text)
        row = next(
            (
                r
                for r in board.rows("questions")
                if row_id(board, "questions", r) == plain_id(qid)
            ),
            None,
        )
        if row is None:
            raise BoardError(f"no question {qid!r}")
        if row.get("State", "").strip().lower() != "open":
            raise BoardError(f"question {qid} is {row.get('State')}, not open")
        return apply_row(
            text,
            "questions",
            qid,
            {"Answer": f"{answer} ({by}, {stamp()})", "State": "answered"},
            create=False,
        )

    mutate(path, change)


# ---------------------------------------------------------------------------
# Rendering and serving


def render_html(data: dict, mode: str, token: str = "") -> str:
    template = read_utf8(TEMPLATE_HTML)
    # Escape every "<" (so no "</script>" or "<!--" survives) and the two line
    # separators JavaScript treats as newlines; the result is still valid JSON.
    payload = (
        json.dumps(data, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    return (
        template.replace("__BOARD_TITLE__", html.escape(data.get("title") or "Board"))
        .replace("__BOARD_MODE__", mode)
        .replace("__BOARD_TOKEN__", token)
        .replace("__BOARD_DATA__", payload)
    )


def load(path: Path) -> Board:
    return parse_board(read_board(path))


def snapshot(path: Path) -> dict:
    return analyze(load(path), load_history(path))


class BoardServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], board_path: Path, token: str):
        super().__init__(address, BoardHandler)
        self.board_path = board_path
        self.token = token


class BoardHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        del format, args

    @property
    def board_server(self) -> BoardServer:
        return cast(BoardServer, self.server)

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").strip().lower()
        if host.startswith("["):
            host = host[1:].split("]", 1)[0]
        else:
            host = host.rsplit(":", 1)[0]
        bound = str(self.board_server.server_address[0]).lower()
        return host in {"127.0.0.1", "localhost", "::1"} or host == bound

    def _linked_markdown(self, route: str) -> Path | None:
        """A card or plan linked from the board: a .md file inside the board's folder, read-only."""
        if not route.endswith(".md"):
            return None
        root = self.board_server.board_path.parent.resolve()
        target = (root / unquote(route).lstrip("/")).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            return None
        return target

    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: dict) -> None:
        self._send(
            status,
            json.dumps(data, ensure_ascii=False).encode(),
            "application/json; charset=utf-8",
        )

    def do_GET(self) -> None:
        if not self._host_ok():
            return self._send(HTTPStatus.FORBIDDEN, b"forbidden host", "text/plain")
        route = self.path.split("?", 1)[0]
        path = self.board_server.board_path
        try:
            if route in ("/", "/index.html"):
                page = render_html(snapshot(path), "live", self.board_server.token)
                return self._send(
                    HTTPStatus.OK, page.encode(), "text/html; charset=utf-8"
                )
            if route == "/board.json":
                return self._json(HTTPStatus.OK, snapshot(path))
            if route == "/board.md":
                return self._send(
                    HTTPStatus.OK, path.read_bytes(), "text/plain; charset=utf-8"
                )
            linked = self._linked_markdown(route)
            if linked is not None:
                return self._send(
                    HTTPStatus.OK, linked.read_bytes(), "text/plain; charset=utf-8"
                )
        except (BoardError, OSError) as exc:
            return self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
        return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain")

    def do_POST(self) -> None:
        if not self._host_ok():
            return self._send(HTTPStatus.FORBIDDEN, b"forbidden host", "text/plain")
        if self.path.split("?", 1)[0] != "/answer":
            return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain")
        if not secrets.compare_digest(
            self.headers.get("X-Board-Token", ""), self.board_server.token
        ):
            return self._json(
                HTTPStatus.FORBIDDEN, {"error": "bad token; reload the page"}
            )
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 16_000)
            body = json.loads(self.rfile.read(length) or b"{}")
            record_answer(
                self.board_server.board_path,
                str(body.get("id", "")),
                str(body.get("answer", "")),
                "owner",
            )
        except (ValueError, BoardError) as exc:
            return self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        return self._json(HTTPStatus.OK, {"ok": True})


# ---------------------------------------------------------------------------
# Cards


def check_card(text: str) -> list[str]:
    """Problems that make a card unfit to dispatch verbatim."""
    problems: list[str] = []
    headings: dict[str, str] = {}
    current = None
    buffer: list[str] = []
    lines = text.splitlines()
    inert = inert_lines(lines)
    for line, skip in zip(lines, inert, strict=True):
        match = None if skip else re.match(r"^#{2,3}\s+(.+?)\s*$", line)
        if match:
            if current:
                headings[current] = "\n".join(buffer).strip()
            current, buffer = match.group(1).strip().lower(), []
        elif current:
            buffer.append(line)
    if current:
        headings[current] = "\n".join(buffer).strip()
    status = re.search(
        r"^\s*(?:\*\*)?Status:?(?:\*\*)?:?\s*(\S+)", text, re.MULTILINE | re.IGNORECASE
    )
    if status and status.group(1).strip("`*.").lower() == "outline":
        problems.append("status is outline: the lead completes it before dispatch")
    for name in CARD_SECTIONS:
        body = headings.get(name.lower())
        if body is None:
            problems.append(f"missing section '## {name}'")
        elif not body:
            problems.append(f"section '## {name}' is empty")
    for name in ("acceptance", "gates"):
        body = headings.get(name, "")
        if body and "`" not in body:
            problems.append(
                f"'## {name.title()}' names no literal command (wrap commands in backticks)"
            )
    for n, (line, skip) in enumerate(zip(lines, inert, strict=True), 1):
        prose = re.sub(r"`[^`]*`", "", line)
        if not skip and (
            CARD_PLACEHOLDER.search(prose) or ANGLE_PLACEHOLDER.search(prose)
        ):
            problems.append(f"line {n}: unresolved placeholder: {line.strip()[:80]}")
    return problems


# ---------------------------------------------------------------------------
# Commands


def parse_assignments(items: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise BoardError(f"expected Column=value, got {item!r}")
        name, value = item.split("=", 1)
        values[name.strip()] = value.strip()
    return values


def print_problems(errors: list[str], warnings: list[str]) -> None:
    for line in errors:
        print(f"ERROR {line}")
    for line in warnings:
        print(f"WARN  {line}")


def cmd_init(args) -> int:
    path = Path(args.board)
    if path.exists() and not args.force:
        raise BoardError(f"{path} exists; pass --force to overwrite")
    replacements = {
        "__TITLE__": args.title,
        "__PLAN__": args.plan or "-",
        "__REPO__": args.repo or "-",
        "__BRANCH__": args.branch or "-",
        "__CREATED__": stamp(),
    }
    text = read_utf8(TEMPLATE_MD)
    for old, new in replacements.items():
        text = text.replace(old, new)
    errors, _ = validate(parse_board(text))
    if errors:
        raise BoardError("template produced an invalid board: " + "; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    log = history_path(path)
    with board_lock(path):
        write_atomic(path, text)
        kept = log.exists()  # history is never overwritten, even with --force
        if not kept:
            write_atomic(log, read_utf8(TEMPLATE_LOG).replace("__TITLE__", args.title))
    print(f"wrote {path}" + (f"; kept existing {log}" if kept else f" and {log}"))
    return 0


def cmd_check(args) -> int:
    path = Path(args.board)
    errors, warnings = validate(load(path))
    history = load_history(path)
    if history and history.errors:
        errors += [f"{history_path(path).name}: {e}" for e in history.errors]
    print_problems(errors, warnings)
    if not errors:
        print("board OK" + (f" ({len(warnings)} warnings)" if warnings else ""))
    return 1 if errors else 0


def human_delta(moment: str, now: datetime) -> str:
    when = parse_time(moment)
    if not when:
        return "never"
    minutes = int((now - when).total_seconds() // 60)
    if minutes >= 0:
        return f"{minutes} min ago" if minutes < 120 else f"{minutes // 60} h ago"
    minutes = -minutes
    return f"in {minutes} min" if minutes < 120 else f"in {minutes // 60} h"


def cmd_status(args) -> int:
    now = local_now()
    path = Path(args.board)
    data = analyze(load(path), load_history(path), now)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 1 if data["errors"] else 0
    info, beat = data["now"], data["heartbeat"]
    print(
        f"{data['title']}  [{info.get('State', '?')}]  manager {beat['manager'] or '-'}"
    )
    late = "  LATE" if beat["late"] else ""
    print(
        f"tick: last {human_delta(beat['last'], now)}, next {human_delta(beat['next'], now)}{late}"
    )
    for item in data["needs_you"][:5]:
        ident = f" {item['id']}" if item.get("id") else ""
        print(f"needs you: {item['kind']}{ident}: {item['text']}")
    if len(data["needs_you"]) > 5:
        print(f"needs you: {len(data['needs_you']) - 5} more")
    counts: dict[str, int] = {}
    for step in data["steps"]:
        counts[step["lane"]] = counts.get(step["lane"], 0) + 1
    order = ["todo", "ready", "active", "review", "attention", "done", "dropped"]
    print(
        "steps: "
        + ", ".join(f"{lane} {counts[lane]}" for lane in order if lane in counts)
    )
    for slot in data["slots"]:
        holding = ", ".join(slot["holding"]) or "-"
        print(
            f"slot {slot['name']} ({slot['platform']}): {len(slot['holding'])}/{slot['max']} ({holding})"
        )
    for d in data["dispatch"]:
        model = f" as {d['model']}" if d.get("model") else ""
        print(f"dispatch: {d['step']} -> {d['slot'] or '?'}{model}")
    for item in data["unplaced"]:
        print(f"waiting: {item['step']} ({item['reason']})")
    if data["idle_slots"] and not data["dispatch"]:
        print(
            "idle capacity: "
            + ", ".join(data["idle_slots"])
            + " (nothing ready; one proposal or one question)"
        )
    for step in data["steps"]:
        if step["timebox_state"] == "twice":
            print(
                f"timebox: {step['id']} is past twice its timebox (escalate to the advisor)"
            )
        elif step["timebox_state"] == "over":
            print(f"timebox: {step['id']} is past its timebox")
    for wave in data["waves"]:
        print(
            f"wave {wave['id']}: {wave['state']}, {wave['done']}/{wave['total']} done"
        )
    for q in data["questions"]:
        if q["state"] == "open" and q["overdue"]:
            action = (
                "apply its default and log it"
                if q["has_default"]
                else "no default: keep waiting, notify again"
            )
            print(f"question {q['id']} OVERDUE: {action}")
        elif q["state"] == "answered":
            print(
                f"question {q['id']} answered: {q.get('Answer', '')} (act on it, log it, close it)"
            )
    for item in data["budget"]:
        if item["ratio"] is not None and item["ratio"] >= 0.8:
            print(f"budget {item.get('Item', '')}: {item['used']:g}/{item['limit']:g}")
    for step in data["steps"]:
        if step["lane"] == "attention":
            print(f"{step['state']}: {step['id']} {step.get('Next', '')}".rstrip())
    print_problems(data["errors"], data["warnings"])
    return 1 if data["errors"] else 0


def cmd_set(args) -> int:
    key = resolve_section(args.section)
    if key in HISTORY_SCHEMA:
        raise BoardError(
            f"## {TITLES[key]} is append-only; use the `{'decide' if key == 'decisions' else 'log'}` command"
        )
    values = parse_assignments(args.values)
    events: list[str] = []

    def row_state(parsed: Board, section: str) -> tuple[Table | None, dict[str, str]]:
        table = parsed.table(section)
        rows = table.rows if table else []
        current = next(
            (r for r in rows if row_id(parsed, section, r) == plain_id(args.key)), {}
        )
        return table, current

    def change(text: str) -> str:
        stamped = dict(values)
        parsed = parse_board(text)
        table, current = row_state(parsed, key)
        if (
            key == "steps"
            and stamped.get("State", "").lower() == "active"
            and table
            and table.column("Started")
            and is_empty(current.get("Started"))
            and "Started" not in stamped
        ):
            stamped["Started"] = stamp()
        opening = (
            key == "waves"
            and stamped.get("State", "").strip().lower() == "active"
            and current.get("State", "").strip().lower() != "active"
        )
        text = apply_row(text, key, args.key, stamped, create=args.new)
        if opening:  # a wave opening zeroes the budgets that reset per wave
            for item in parse_board(text).rows("budget"):
                used = first_number(item.get("Used"))
                if item.get("Resets", "").strip().lower() == "wave" and used:
                    name = item.get("Item", "")
                    text = apply_row(text, "budget", name, {"Used": "0"}, create=False)
                    events.append(
                        f"budget reset (wave {args.key} opened): {name} was {item.get('Used', '')}"
                    )
        return text

    # Only opening a wave can log, so only then must the log be checked first.
    logs = key == "waves" and values.get("State", "").strip().lower() == "active"
    mutate(Path(args.board), change, events if logs else None)
    print(f"{'added' if args.new else 'updated'} {TITLES[key]} {args.key}")
    return 0


def cmd_tick(args) -> int:
    path = Path(args.board)
    moment = local_now()
    events: list[str] = []
    released = (args.state or "").strip().lower() in RELEASING_STATES

    def change(text: str) -> str:
        board = parse_board(text)
        info = board.now()
        holder = info.get("Manager id", "")
        nxt = parse_time(info.get("Next tick"))
        if (
            args.manager
            and not is_empty(holder)
            and holder != args.manager
            and nxt
            and moment <= nxt + LATE_GRACE
            and not args.take_over
        ):
            raise BoardError(
                f"manager {holder!r} holds this board and another manager is live."
                " Stop here. Use --take-over only after confirming that manager has stopped."
                f" The lease expires at {stamp(nxt + LATE_GRACE)}"
            )
        values = {"Last tick": stamp(moment)}
        if args.manager:
            values["Manager id"] = args.manager
        wake = parse_duration(args.next) if args.next is not None else None
        if wake is not None:
            values["Next tick"] = stamp(moment + wake)
        if args.state:
            values["State"] = args.state
            if released:
                values["Next tick"] = "-"  # no pending wake, so no lease
        for name, value in values.items():
            exists = any(
                r.get("Key", "").strip() == name for r in parse_board(text).rows("now")
            )
            text = apply_row(text, "now", name, {"Value": value}, create=not exists)
        last = parse_time(info.get("Last tick"))
        if last and last.astimezone().date() != moment.date():
            for row in parse_board(text).rows("budget"):
                if row.get("Resets", "").strip().lower() == "daily" and first_number(
                    row.get("Used")
                ) not in (None, 0):
                    text = apply_row(
                        text, "budget", row.get("Item", ""), {"Used": "0"}, create=False
                    )
                    events.append(
                        f"budget reset (daily): {row.get('Item', '')} was {row.get('Used', '')}"
                    )
        if args.note:
            events.append(args.note)
        return text

    mutate(path, change, events)
    if released:
        after = f", state {args.state}, lease released"
    else:
        after = f", next in {args.next}" if args.next else ""
    print(f"tick {stamp(moment)}{after}")
    return 0


def cmd_spend(args) -> int:
    def change(text: str) -> str:
        row = next(
            (
                r
                for r in parse_board(text).rows("budget")
                if r.get("Item", "").strip() == args.item.strip()
            ),
            None,
        )
        if row is None:
            raise BoardError(f"## Budget: no row {args.item!r}")
        limit, used = first_number(row.get("Limit")), first_number(row.get("Used")) or 0
        total = used + args.amount
        if limit is not None and total > limit and not args.over:
            raise BoardError(
                f"## Budget: {args.item} would be {total:g} of {limit:g}. Stop and ask the owner;"
                " pass --over only with the owner's approval"
            )
        return apply_row(
            text, "budget", args.item, {"Used": f"{total:g}"}, create=False
        )

    mutate(Path(args.board), change)
    print(f"spent {args.amount:g} on {args.item}")
    return 0


def cmd_log(args) -> int:
    append_history(Path(args.board), "log", {"Time": stamp(), "Event": args.event})
    print("logged")
    return 0


def cmd_decide(args) -> int:
    values = {
        "Time": stamp(),
        "Decision": args.decision,
        "By": args.by,
        "Reason": args.reason or "",
    }
    append_history(Path(args.board), "decisions", values)
    print("decision recorded")
    return 0


def cmd_ask(args) -> int:
    options = split_options(args.options)
    default = args.default or "none"
    if (
        not is_empty(default)
        and options
        and default.strip() not in [option_name(o) for o in options] + options
    ):
        raise BoardError(f"default {default!r} is not one of the options")
    if args.needed_by and parse_time(args.needed_by) is None:
        raise BoardError(
            f"cannot read --needed-by {args.needed_by!r}; use ISO form, e.g. 2026-11-14T17:00"
        )
    values = {
        "Step": args.step or "-",
        "Question": args.question,
        "Options": " / ".join(options),
        "Default": default,
        "Needed by": args.needed_by or "-",
        "State": "open",
        "Answer": "",
    }
    mutate(
        Path(args.board),
        lambda text: apply_row(text, "questions", args.id, values, create=True),
    )
    print(f"question {args.id} recorded")
    return 0


def cmd_answer(args) -> int:
    record_answer(Path(args.board), args.id, args.answer, args.by)
    print(f"question {args.id} answered")
    return 0


PROPOSAL_LOGGED = re.compile(r"(?:archived )?proposal P(\d+)\b")
PROPOSAL_OPENED = re.compile(r"proposal P\d+ opened\b")


def cmd_propose(args) -> int:
    path = Path(args.board)
    created: list[str] = []
    events: list[str] = []

    def change(text: str) -> str:
        board = parse_board(text)
        history = load_history(path)
        log_rows = history.rows("log") if history else []
        last = parse_time(board.now().get("Last tick"))
        rows = board.rows("proposals")
        opened = [parse_time(r.get("Time")) for r in rows] + [
            parse_time(r.get("Time"))
            for r in log_rows
            if PROPOSAL_OPENED.match(r.get("Event", ""))
        ]
        if last and any(t is not None and t >= last for t in opened):
            raise BoardError(
                "a proposal was already made this tick; at most one per tick"
            )
        if any(
            r.get("State", "").strip().lower() == "open"
            and r.get("Proposal", "") == args.proposal
            for r in rows
        ):
            raise BoardError(
                "this proposal is already open; do not repeat it unless the facts changed"
            )
        numbers = [
            int(m.group(1))
            for r in rows
            if (m := re.fullmatch(r"P(\d+)", row_id(board, "proposals", r)))
        ] + [
            int(m.group(1))
            for r in log_rows
            if (m := PROPOSAL_LOGGED.match(r.get("Event", "")))
        ]
        pid = f"P{max(numbers, default=0) + 1}"
        created.append(pid)
        events.append(f"proposal {pid} opened: {args.proposal}")
        values = {
            "Time": stamp(),
            "Proposal": args.proposal,
            "Why": args.why,
            "State": "open",
        }
        return apply_row(text, "proposals", pid, values, create=True)

    mutate(path, change, events)
    print(f"proposal {created[0]} recorded")
    return 0


def cmd_archive(args) -> int:
    """Move settled questions and proposals from the board to the log."""
    path = Path(args.board)
    events: list[str] = []

    def change(text: str) -> str:
        board = parse_board(text)
        q_ids: set[str] = set()
        p_ids: set[str] = set()
        for r in board.rows("questions"):
            rid = row_id(board, "questions", r)
            if r.get("State", "").strip().lower() in ("closed", "defaulted"):
                q_ids.add(rid)
                events.append(
                    f"archived question {rid} {r.get('State')}: {r.get('Question')} -> {r.get('Answer')}"
                )
        for r in board.rows("proposals"):
            rid = row_id(board, "proposals", r)
            if r.get("State", "").strip().lower() in (
                "accepted",
                "rejected",
                "withdrawn",
            ):
                p_ids.add(rid)
                events.append(
                    f"archived proposal {rid} {r.get('State')}: {r.get('Proposal')}"
                )
        return remove_rows(remove_rows(text, "questions", q_ids), "proposals", p_ids)

    mutate(path, change, events)
    print(f"archived {len(events)} rows")
    return 0


def cmd_card(args) -> int:
    failed = 0
    for name in args.cards:
        problems = check_card(read_utf8(Path(name)))
        for problem in problems:
            print(f"ERROR {name}: {problem}")
        if not problems:
            print(f"{name}: ready to dispatch")
        failed += bool(problems)
    return 1 if failed else 0


def cmd_render(args) -> int:
    path = Path(args.board)
    out = Path(args.output) if args.output else path.with_suffix(".html")
    write_atomic(out, render_html(snapshot(path), "snapshot"))
    print(f"wrote {out}")
    return 0


def cmd_serve(args) -> int:
    path = Path(args.board).resolve()
    load(path)
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        print(
            f"WARNING: serving on {args.host}; anyone who can reach it can read the board",
            file=sys.stderr,
        )
    server = BoardServer((args.host, args.port), path, secrets.token_urlsafe(24))
    host, port = server.server_address[:2]
    shown = "localhost" if host in ("127.0.0.1", "::1") else host
    print(f"board: http://{shown}:{port}/  (Ctrl-C to stop)", flush=True)
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()
    server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, func, help_text: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_text, description=help_text)
        p.set_defaults(func=func)
        return p

    p = add("init", cmd_init, "write a new board and its log from the templates")
    p.add_argument("board")
    p.add_argument("--title", required=True)
    p.add_argument("--plan")
    p.add_argument("--repo")
    p.add_argument("--branch", help="integration branch")
    p.add_argument("--force", action="store_true")

    p = add("check", cmd_check, "parse and validate; exit 1 on errors")
    p.add_argument("board")

    p = add(
        "status",
        cmd_status,
        "heartbeat, needs-you, slots, dispatch plan, timeboxes, waves, questions, budget",
    )
    p.add_argument("board")
    p.add_argument("--json", action="store_true")

    p = add(
        "set", cmd_set, "update one row of a board table (or append one with --new)"
    )
    p.add_argument("board")
    p.add_argument(
        "section",
        help="Now, Parity, Slots, Budget, Waves, Steps, Questions, Proposals, Agents",
    )
    p.add_argument("key", help="the row's first cell, e.g. a step ID")
    p.add_argument("values", nargs="+", help="Column=value pairs")
    p.add_argument(
        "--new", action="store_true", help="append a new row instead of updating"
    )

    p = add(
        "tick",
        cmd_tick,
        "record the heartbeat, hold the manager lease, reset daily budgets",
    )
    p.add_argument("board")
    p.add_argument(
        "--manager", help="this manager's id (host, model, session); holds the lease"
    )
    p.add_argument("--next", help="time to the next wake, e.g. 30m or 1h")
    p.add_argument("--state", help="manager state: running, paused, stopped, done")
    p.add_argument("--note", help="also append this line to the log")
    p.add_argument(
        "--take-over",
        action="store_true",
        help="take the lease from a manager confirmed stopped",
    )

    p = add("spend", cmd_spend, "add to a budget's Used; refuses to pass its Limit")
    p.add_argument("board")
    p.add_argument("item")
    p.add_argument("amount", nargs="?", type=float, default=1.0)
    p.add_argument(
        "--over", action="store_true", help="the owner approved going over the limit"
    )

    p = add("log", cmd_log, "append a line to the log")
    p.add_argument("board")
    p.add_argument("event")

    p = add("decide", cmd_decide, "append a decision to the log's Decisions table")
    p.add_argument("board")
    p.add_argument("decision")
    p.add_argument("--by", required=True)
    p.add_argument("--reason")

    p = add("ask", cmd_ask, "record an owner question on the board")
    p.add_argument("board")
    p.add_argument("id")
    p.add_argument("--question", required=True)
    p.add_argument("--options", default="", help='"Option A (Recommended) / Option B"')
    p.add_argument(
        "--default",
        help="option applied at the deadline (only if pre-authorized), or none",
    )
    p.add_argument("--needed-by", help="ISO time, e.g. 2026-11-14T17:00")
    p.add_argument("--step")

    p = add("answer", cmd_answer, "record an answer to an open question")
    p.add_argument("board")
    p.add_argument("id")
    p.add_argument("answer")
    p.add_argument("--by", default="owner")

    p = add(
        "propose",
        cmd_propose,
        "record one proposal for the lead or owner (at most one per tick)",
    )
    p.add_argument("board")
    p.add_argument("proposal")
    p.add_argument("--why", required=True)

    p = add("archive", cmd_archive, "move settled questions and proposals to the log")
    p.add_argument("board")

    p = add(
        "card", cmd_card, "check that cards are complete enough to dispatch verbatim"
    )
    p.add_argument("cards", nargs="+")

    p = add("render", cmd_render, "write a static HTML snapshot")
    p.add_argument("board")
    p.add_argument("-o", "--output")

    p = add("serve", cmd_serve, "serve the live board page on localhost")
    p.add_argument("board")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--host", default="127.0.0.1")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (BoardError, OSError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
