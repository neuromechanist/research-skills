"""Filesystem and live-server tests for the manager-loop board helper.

Every test runs the real script as a subprocess against a real board file; the
server test starts the real HTTP server on a free localhost port.
"""

import importlib.util
import json
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "project" / "skills" / "manager-loop"
SCRIPT = SKILL / "scripts" / "manager_board.py"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"{args} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}"
        )
    return result


def status(board: Path) -> dict:
    return json.loads(run("status", str(board), "--json").stdout)


@pytest.fixture
def board(tmp_path: Path) -> Path:
    path = tmp_path / "plan" / "board.md"
    run(
        "init",
        str(path),
        "--title",
        "Demo plan",
        "--plan",
        "plan.md",
        "--repo",
        "acme/widget",
        "--branch",
        "develop",
    )
    return path


def add_step(board: Path, sid: str, *values: str) -> None:
    run("set", str(board), "steps", sid, f"Title=Step {sid}", *values, "--new")


def test_init_writes_valid_board_and_log(board: Path):
    assert board.exists()
    assert (board.parent / "board-log.md").exists()
    assert "board OK" in run("check", str(board)).stdout
    assert run("init", str(board), "--title", "again", check=False).returncode == 2


def test_dispatch_respects_dependencies_tiers_needs_and_capacity(board: Path):
    run("set", str(board), "slots", "codex", "Max=1")
    run("set", str(board), "slots", "claude-sonnet", "Max=1")
    add_step(board, "S1", "Tier=worker", "State=done")
    add_step(board, "S2", "Tier=worker", "State=todo", "Depends=S1")
    add_step(board, "S3", "Tier=worker", "State=todo", "Needs=browser")
    add_step(board, "S4", "Tier=worker", "State=todo", "Depends=S3")
    add_step(board, "S5", "Tier=lead", "State=todo")
    add_step(board, "S6", "Tier=worker", "State=todo")

    data = status(board)
    plan = {d["step"]: d for d in data["dispatch"]}
    # S2 is first in table order and fits claude-sonnet first; S3 needs a browser,
    # which codex cannot do, and claude-sonnet is then full.
    assert plan["S2"]["slot"] == "claude-sonnet"
    assert plan["S2"]["model"] == "Sonnet high"
    assert "S4" not in plan  # waits on S3
    assert plan["S5"] == {"step": "S5", "slot": "claude-opus", "model": "Opus xhigh"}
    assert plan["S6"]["slot"] == "codex"
    assert plan["S6"]["model"] == "gpt-6-luna max"
    unplaced = {u["step"]: u["reason"] for u in data["unplaced"]}
    assert unplaced["S3"] == "fitting slots are full"
    lanes = {s["id"]: s["lane"] for s in data["steps"]}
    assert lanes["S4"] == "todo" and lanes["S2"] == "ready" and lanes["S1"] == "done"


def test_waves_gate_readiness(board: Path):
    run(
        "set",
        str(board),
        "waves",
        "W1",
        "Goal=first",
        "Agents=10",
        "State=active",
        "Exit gate=merged",
        "--new",
    )
    run(
        "set",
        str(board),
        "waves",
        "W2",
        "Goal=second",
        "Agents=10",
        "State=planned",
        "Exit gate=merged",
        "--new",
    )
    add_step(board, "A", "Wave=W1", "State=todo")
    add_step(board, "B", "Wave=W2", "State=todo")
    data = status(board)
    ready = {s["id"]: s["ready"] for s in data["steps"]}
    assert ready == {"A": True, "B": False}
    wave = next(w for w in data["waves"] if w["id"] == "W1")
    assert (wave["done"], wave["total"]) == (0, 1)


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (["State=doing"], "is not one of"),
        (["State=todo", "Depends=NOPE"], "depends on unknown step"),
        (["State=todo", "Slot=ghost"], "is not in ## Slots"),
        (["State=todo", "Next=" + "x" * 300], "limit 240"),
        (["State=todo", "Timebox=soon"], "cannot read Timebox"),
    ],
)
def test_invalid_changes_are_refused_and_board_is_unchanged(
    board: Path, values, message
):
    before = board.read_text()
    result = run(
        "set", str(board), "steps", "S1", "Title=x", *values, "--new", check=False
    )
    assert result.returncode == 2
    assert message in result.stderr
    assert board.read_text() == before


def test_dependency_cycle_is_reported(board: Path):
    add_step(board, "A", "State=todo")
    add_step(board, "B", "State=todo", "Depends=A")
    result = run("set", str(board), "steps", "A", "Depends=B", check=False)
    assert result.returncode == 2
    assert "dependency cycle" in result.stderr


def test_hand_edit_errors_are_caught_by_check(board: Path):
    text = board.read_text().replace(
        "|---|---|---|---|---|---|---|---|---|---|---|---|\n",
        "|---|---|---|---|---|---|---|---|---|---|---|---|\n| S1 | broken row |\n",
    )
    board.write_text(text)
    result = run("check", str(board), check=False)
    assert result.returncode == 1
    assert "cells, header has 12" in result.stdout


def test_board_line_limit(board: Path):
    board.write_text(board.read_text() + "\n## Notes\n\n" + "line\n" * 300)
    result = run("check", str(board), check=False)
    assert result.returncode == 1
    assert "limit 300" in result.stdout


def test_pipe_in_cell_round_trips(board: Path):
    add_step(board, "S1", "State=todo", "Next=choose a | b")
    assert "choose a \\| b" in board.read_text()
    step = next(s for s in status(board)["steps"] if s["id"] == "S1")
    assert step["Next"] == "choose a | b"


def test_active_step_gets_started_stamp(board: Path):
    add_step(board, "S1", "State=todo")
    run("set", str(board), "steps", "S1", "State=active", "Slot=claude-sonnet")
    step = next(s for s in status(board)["steps"] if s["id"] == "S1")
    assert datetime.fromisoformat(step["Started"]).date() == datetime.now().date()


def test_timebox_flags(board: Path):
    started = (datetime.now().astimezone() - timedelta(hours=5)).isoformat(
        timespec="minutes"
    )
    add_step(
        board,
        "S1",
        "State=active",
        "Slot=claude-sonnet",
        f"Started={started}",
        "Timebox=2h",
    )
    add_step(
        board,
        "S2",
        "State=active",
        "Slot=claude-sonnet",
        f"Started={started}",
        "Timebox=4h",
    )
    states = {s["id"]: s["timebox_state"] for s in status(board)["steps"]}
    assert states == {"S1": "twice", "S2": "over"}
    assert "past twice its timebox" in run("status", str(board)).stdout


def test_lease_blocks_a_second_manager(board: Path):
    run(
        "tick",
        str(board),
        "--manager",
        "claude@mac",
        "--next",
        "30m",
        "--state",
        "running",
    )
    result = run(
        "tick", str(board), "--manager", "codex@mac", "--next", "30m", check=False
    )
    assert result.returncode == 2
    assert "another manager is live" in result.stderr
    run(
        "tick", str(board), "--manager", "claude@mac", "--next", "30m"
    )  # the holder may tick again
    run("tick", str(board), "--manager", "codex@mac", "--next", "30m", "--take-over")
    assert status(board)["heartbeat"]["manager"] == "codex@mac"


def test_spend_refuses_to_pass_a_limit(board: Path):
    run("spend", str(board), "Advisor consults", "3")
    result = run("spend", str(board), "Advisor consults", check=False)
    assert result.returncode == 2
    assert "Stop and ask the owner" in result.stderr
    run("spend", str(board), "Advisor consults", "--over")
    item = next(b for b in status(board)["budget"] if b["Item"] == "Advisor consults")
    assert item["used"] == 4


def test_daily_budget_resets_on_first_tick_of_a_day(board: Path):
    run("spend", str(board), "Agents today", "7")
    run("spend", str(board), "Advisor consults", "2")
    yesterday = (datetime.now().astimezone() - timedelta(days=1)).isoformat(
        timespec="minutes"
    )
    run("set", str(board), "now", "Last tick", f"Value={yesterday}")
    run("tick", str(board), "--manager", "m1", "--next", "30m")
    budget = {b["Item"]: b["used"] for b in status(board)["budget"]}
    assert budget["Agents today"] == 0
    assert budget["Advisor consults"] == 2  # Resets: never
    log = (board.parent / "board-log.md").read_text()
    assert "budget reset (daily): Agents today was 7" in log


def test_question_lifecycle(board: Path):
    result = run(
        "ask",
        str(board),
        "Q1",
        "--question",
        "Open a slot?",
        "--options",
        "Yes (Recommended) / No",
        "--default",
        "Maybe",
        check=False,
    )
    assert result.returncode == 2 and "not one of the options" in result.stderr
    run(
        "ask",
        str(board),
        "Q1",
        "--question",
        "Open a slot?",
        "--options",
        "Yes (Recommended) / No",
        "--default",
        "none",
        "--needed-by",
        "2000-01-01T00:00",
    )
    data = status(board)
    question = data["questions"][0]
    assert question["overdue"] is True and question["has_default"] is False
    assert any(item["kind"] == "question" for item in data["needs_you"])
    assert "no default: keep waiting" in run("status", str(board)).stdout

    too_long = run("answer", str(board), "Q1", "y" * 201, check=False)
    assert too_long.returncode == 2
    run("answer", str(board), "Q1", "Yes")
    question = status(board)["questions"][0]
    assert question["state"] == "answered" and question["Answer"].startswith(
        "Yes (owner, "
    )
    again = run("answer", str(board), "Q1", "No", check=False)
    assert again.returncode == 2 and "not open" in again.stderr


def test_one_proposal_per_tick_and_archive(board: Path):
    run("tick", str(board), "--manager", "m1", "--next", "30m")
    run("propose", str(board), "Run the docs review", "--why", "the plan names it")
    second = run("propose", str(board), "Another idea", "--why", "x", check=False)
    assert second.returncode == 2 and "at most one per tick" in second.stderr

    run(
        "ask",
        str(board),
        "Q1",
        "--question",
        "Ship?",
        "--options",
        "Yes (Recommended) / No",
    )
    run("set", str(board), "questions", "Q1", "State=closed", "Answer=Yes")
    run("set", str(board), "proposals", "P1", "State=accepted")
    assert "archived 2 rows" in run("archive", str(board)).stdout
    data = status(board)
    assert data["questions"] == [] and data["proposals"] == []
    log = (board.parent / "board-log.md").read_text()
    assert (
        "archived question Q1 closed" in log and "archived proposal P1 accepted" in log
    )


def test_history_is_append_only(board: Path):
    run(
        "decide",
        str(board),
        "Codex slot opened",
        "--by",
        "owner",
        "--reason",
        "more budget",
    )
    run("log", str(board), "E1 merged as #12")
    result = run("set", str(board), "log", "x", "Event=y", check=False)
    assert result.returncode == 2 and "append-only" in result.stderr
    data = status(board)
    assert data["decisions"][-1]["Decision"] == "Codex slot opened"
    assert data["log"][-1]["Event"] == "E1 merged as #12"


def test_parity_platform_mismatch_warns(board: Path):
    run(
        "set",
        str(board),
        "slots",
        "gemini",
        "Platform=Gemini",
        "Tiers=worker",
        "Max=1",
        "--new",
    )
    warnings = status(board)["warnings"]
    assert any("has no ## Parity column" in w for w in warnings)


def test_card_check(tmp_path: Path):
    template = SKILL / "assets" / "card-template.md"
    result = run("card", str(template), check=False)
    assert result.returncode == 1
    assert "unresolved placeholder" in result.stdout

    card = tmp_path / "E1.md"
    card.write_text(
        "# Card E1: Store v3\n\nStatus: ready\n\n## Goal\nStore keeps 30 conversations.\n\n"
        "## Scope\n`frontend/store.js`\n\n## Acceptance\n`bun frontend/test-store.js` passes; `Vec<String>` is fine in code.\n\n"
        "## Gates\n`bun run biome check`\n\n## Stop conditions\nA design question.\n\n## Report\nPR and gates.\n"
    )
    assert "ready to dispatch" in run("card", str(card)).stdout

    card.write_text(card.read_text().replace("Status: ready", "Status: outline"))
    assert "status is outline" in run("card", str(card), check=False).stdout


def embedded_data(page: str) -> dict:
    match = re.search(
        r'<script id="board-data" type="application/json">(.*?)</script>',
        page,
        re.DOTALL,
    )
    assert match, "no board-data block"
    return json.loads(match.group(1))


def test_card_check_ignores_fenced_and_commented_lines(tmp_path: Path):
    card = tmp_path / "E2.md"
    card.write_text(
        "# Card E2: Store v3\n\nStatus: ready\n\n<!-- TODO <fill in later> -->\n\n"
        "## Goal\nStore keeps 30 conversations.\n\n~~~\nTODO <title>\n## Scope\n~~~\n\n"
        "## Scope\n`frontend/store.js`\n\n## Acceptance\n`bun test` passes.\n\n"
        "## Gates\n`bun run biome check`\n\n## Stop conditions\nA design question.\n\n"
        "## Report\nPR and gates.\n",
        encoding="utf-8",
    )
    assert "ready to dispatch" in run("card", str(card)).stdout


def test_render_embeds_json_that_cannot_break_out(board: Path, tmp_path: Path):
    breakout = "</script><script>alert(1)</script>"
    add_step(board, "S1", "State=todo", f"Next={breakout}", "Title=a <!-- note")
    out = tmp_path / "snap.html"
    run("render", str(board), "-o", str(out))
    page = out.read_text(encoding="utf-8")
    assert page.count("</script>") == 2  # the data block and the app script only
    assert "<!-- note" not in page.split('id="board-data"', 1)[1].split("</script>")[0]
    steps = {s["id"]: s for s in embedded_data(page)["steps"]}
    assert steps["S1"]["Next"] == breakout
    assert steps["S1"]["Title"] == "a <!-- note"
    assert 'content="snapshot"' in page


def load_module():
    spec = importlib.util.spec_from_file_location("manager_board_under_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_escapes_javascript_line_separators():
    module = load_module()
    page = module.render_html(
        {"title": "t", "cell": "a\u2028b\u2029c <!--"}, "snapshot"
    )
    assert "\u2028" not in page and "\u2029" not in page
    assert embedded_data(page)["cell"] == "a\u2028b\u2029c <!--"


def test_fences_and_comments_are_inert(board: Path):
    add_step(board, "S1", "State=todo")
    block = (
        "\n## Notes\n\n```text\n## Steps\n| a | b |\n```\n\n"
        "~~~\n## Questions\n| x | y |\n~~~\n\n"
        "<!--\n## Proposals\n| c | d |\n-->\n"
    )
    board.write_text(board.read_text(encoding="utf-8") + block, encoding="utf-8")
    assert "board OK" in run("check", str(board)).stdout
    assert [s["id"] for s in status(board)["steps"]] == ["S1"]
    add_step(board, "S2", "State=todo")
    assert board.read_text(encoding="utf-8").count("| S2 |") == 1


def test_duplicate_column_is_an_error(board: Path):
    text = board.read_text(encoding="utf-8").replace(
        "| ID | Time | Proposal | Why | State |", "| ID | Time | Time | Why | State |"
    )
    board.write_text(text, encoding="utf-8")
    result = run("check", str(board), check=False)
    assert result.returncode == 1
    assert "duplicate column 'Time'" in result.stdout


def test_first_header_names_the_row(board: Path):
    text = board.read_text(encoding="utf-8")
    text = text.replace("| ID | Step | Question |", "| Ref | Step | Question |")
    text = text.replace("| ID | Time | Proposal |", "| Ref | Time | Proposal |")
    board.write_text(text, encoding="utf-8")
    run("tick", str(board), "--manager", "m1", "--next", "30m")
    run(
        "ask",
        str(board),
        "Q1",
        "--question",
        "Ship?",
        "--options",
        "Yes (Recommended) / No",
    )
    run("answer", str(board), "Q1", "Yes")
    run("set", str(board), "questions", "Q1", "State=closed")
    run("propose", str(board), "Try it", "--why", "cheap")
    run("set", str(board), "proposals", "P1", "State=accepted")
    data = status(board)
    assert data["questions"][0]["id"] == "Q1" and data["proposals"][0]["id"] == "P1"
    assert "archived 2 rows" in run("archive", str(board)).stdout
    log = (board.parent / "board-log.md").read_text(encoding="utf-8")
    assert "archived question Q1 closed" in log and "archived proposal P1" in log


@pytest.mark.parametrize("bad", ["2 months", "3 sprints", "5m30", "soon", ""])
def test_durations_must_match_in_full(board: Path, bad: str):
    before = board.read_text(encoding="utf-8")
    result = run("tick", str(board), "--manager", "m1", "--next", bad, check=False)
    assert result.returncode == 2 and "cannot read duration" in result.stderr
    assert board.read_text(encoding="utf-8") == before


@pytest.mark.parametrize(
    ("good", "minutes"), [("1h30m", 90), ("2d", 2880), ("45", 45), ("1h 15m", 75)]
)
def test_durations_accept_tokens_and_bare_minutes(board: Path, good: str, minutes: int):
    run("tick", str(board), "--manager", "m1", "--next", good)
    beat = status(board)["heartbeat"]
    gap = datetime.fromisoformat(beat["next"]) - datetime.fromisoformat(beat["last"])
    assert gap == timedelta(minutes=minutes)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request(
    url: str, method: str = "GET", body: dict | None = None, headers: dict | None = None
):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.status, res.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode()


def test_live_server(board: Path):
    run(
        "ask",
        str(board),
        "Q1",
        "--question",
        "Ship?",
        "--options",
        "Yes (Recommended) / No",
    )
    (board.parent / "cards").mkdir()
    (board.parent / "cards" / "S1.md").write_text("# S1\n")
    (board.parent.parent / "secret.md").write_text("outside\n")
    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPT), "serve", str(board), "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    base = f"http://127.0.0.1:{port}"
    code, page = 0, ""
    try:
        for _ in range(50):
            try:
                code, page = request(base + "/")
                break
            except urllib.error.URLError:
                time.sleep(0.1)
        else:
            pytest.fail("server did not start")
        assert code == 200 and 'content="live"' in page
        token = page.split('name="board-token" content="', 1)[1].split('"', 1)[0]
        assert len(token) >= 24

        assert request(base + "/board.json", headers={"Host": "evil.example"})[0] == 403
        assert request(base + "/cards/S1.md")[0] == 200
        assert request(base + "/%2e%2e/secret.md")[0] == 404
        assert request(base + "/board-log.md")[0] == 200
        assert request(base + "/../secret.md")[0] == 404

        answer = {"id": "Q1", "answer": "Yes"}
        assert request(base + "/answer", "POST", answer)[0] == 403
        assert (
            request(base + "/answer", "POST", answer, {"X-Board-Token": "wrong"})[0]
            == 403
        )
        code, body = request(base + "/answer", "POST", answer, {"X-Board-Token": token})
        assert code == 200, body
        code, body = request(base + "/answer", "POST", answer, {"X-Board-Token": token})
        assert code == 400 and "not open" in body

        code, body = request(base + "/board.json")
        assert json.loads(body)["questions"][0]["state"] == "answered"
        assert "| answered | Yes (owner, " in board.read_text()
    finally:
        proc.terminate()
        proc.wait(timeout=5)
