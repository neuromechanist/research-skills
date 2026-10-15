#!/usr/bin/env python3
"""PreToolUse guard: refuse destructive shell commands aimed at protected paths.

Written after 2026-08-08, when a Claude Code subagent in auto-approve mode ran
`rm -rf ~` against a real home directory and destroyed the user's Desktop,
shell config, app state and language runtimes. The command reached the shell
because an exploit-shaped test payload was written with backticks inside a
double-quoted argument:

    bun -e "... String.raw`git status && echo ' ; rm -rf ~` ..."

Backticks inside "..." are command substitution. The shell expanded them
*before* bun ever ran. Approval mode was the only thing between that string and
the filesystem, and it was set to auto.

This hook is the layer that should have existed. It is independent of approval
mode: PreToolUse runs before the permission decision, so a deny here holds even
under `--dangerously-skip-permissions`.

Contract
--------
stdin : PreToolUse hook JSON  {tool_name, tool_input:{command}, cwd}
stdout: nothing when allowed; a deny decision (JSON) when blocked
exit  : always 0 — the decision travels in the JSON body

Fails CLOSED. An internal error emits a deny, not a silent allow. A guard that
fails open is a guard that lies about protecting you.
"""

import json
import os
import re
import shlex
import sys

HOME = os.path.expanduser("~")


def _p(path):
    """Normalize an absolute-ish path for comparison (no trailing slash)."""
    path = os.path.normpath(path)
    return path.rstrip("/") or "/"


# Deleting *these exact directories* is refused. Deleting things INSIDE them is
# fine — `rm -rf ~/Documents/git/some-repo/node_modules` is ordinary work.
PROTECTED_EXACT = {
    _p(p)
    for p in (
        "/", "/bin", "/sbin", "/usr", "/usr/bin", "/usr/local", "/usr/share",
        "/etc", "/var", "/opt", "/opt/homebrew", "/opt/local",
        "/Applications", "/System", "/Library", "/private", "/Volumes",
        "/Users", "/home", "/root", "/srv", "/tmp",
        HOME,
        f"{HOME}/Desktop", f"{HOME}/Documents", f"{HOME}/Downloads",
        f"{HOME}/Library", f"{HOME}/Movies", f"{HOME}/Music",
        f"{HOME}/Pictures", f"{HOME}/Public", f"{HOME}/Applications",
        f"{HOME}/Documents/git", f"{HOME}/git", f"{HOME}/src", f"{HOME}/code",
        f"{HOME}/.claude", f"{HOME}/.config", f"{HOME}/.local",
    )
}

# Nothing may be deleted at OR BELOW these. Credential and key material: the
# blast radius of a wrong call is an account compromise, not a rebuild.
PROTECTED_SUBTREE = [
    _p(p)
    for p in (
        f"{HOME}/.ssh", f"{HOME}/.gnupg", f"{HOME}/.password-store",
        f"{HOME}/.aws", f"{HOME}/.kube", f"{HOME}/.docker",
        f"{HOME}/.appstoreconnect", "/System", "/private/etc",
    )
]

# Verbs that remove or overwrite data.
DESTRUCTIVE = {
    "rm", "rmdir", "unlink", "shred", "srm", "trash", "trash-put",
    "mv", "dd", "mkfs", "truncate", "chown", "chmod",
}

# Tokens that separate one command from the next.
SPLIT = re.compile(r"(?:\|\||&&|[;|&\n])")

# Command substitution: `...` and $(...). The 2026-08-08 vector.
SUBST = re.compile(r"`([^`]*)`|\$\(([^)]*)\)", re.DOTALL)

# Wrappers to look through to find the real verb.
WRAPPERS = {"sudo", "doas", "command", "env", "nohup", "time", "xargs", "exec", "builtin"}


def deny(reason):
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def allow():
    sys.exit(0)


def expand(cmd):
    """Resolve ~ and $HOME so `rm -rf ~` and `rm -rf $HOME` compare equal."""
    cmd = re.sub(r"\$\{HOME\}|\$HOME\b", HOME, cmd)
    cmd = re.sub(r"(?<![\w/])~(?=/|\s|$)", HOME, cmd)
    return cmd


def resolve(token, cwd):
    """Turn an argument into an absolute path for comparison."""
    token = token.strip().strip("'\"")
    if not token:
        return None
    # Strip a trailing glob so `rm -rf ~/*` is judged as `~`.
    stripped = re.sub(r"/\*+$", "", token)
    if not stripped.startswith("/"):
        stripped = os.path.join(cwd, stripped)
    return _p(stripped)


def is_git_root(path):
    """A directory holding .git is a whole repository — never a routine delete."""
    try:
        return os.path.isdir(os.path.join(path, ".git")) or os.path.isfile(
            os.path.join(path, ".git")
        )
    except OSError:
        return False


def classify(path, raw):
    """Return a refusal reason for this target, or None if it is acceptable."""
    if path is None:
        return None
    if path in PROTECTED_EXACT:
        return f"`{raw}` resolves to {path}, a protected directory"
    for base in PROTECTED_SUBTREE:
        if path == base or path.startswith(base + "/"):
            return f"`{raw}` is inside {base}, which holds credentials or system state"
    if is_git_root(path):
        return f"`{raw}` resolves to {path}, the root of a git repository"
    return None


def tokens_of(segment):
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def check_segment(segment, cwd):
    toks = tokens_of(segment)
    i = 0
    while i < len(toks) and (toks[i] in WRAPPERS or "=" in toks[i].split("/")[0][:40] and re.match(r"^\w+=", toks[i])):
        i += 1
    if i >= len(toks):
        return
    verb = os.path.basename(toks[i])

    if verb == "find":
        if not re.search(r"-delete\b|-exec\s+rm\b|-execdir\s+rm\b", segment):
            return
        args = toks[i + 1:]
    elif verb == "git":
        # `git clean -xfd` at a repo root wipes every untracked file.
        if len(toks) > i + 1 and toks[i + 1] == "clean" and re.search(r"-\w*[fx]", segment):
            reason = classify(_p(cwd), cwd)
            if reason:
                deny(f"Refusing `git clean` — {reason}.")
        return
    elif verb in DESTRUCTIVE:
        if verb in ("chown", "chmod") and not re.search(r"(^|\s)-\w*R", segment):
            return
        args = toks[i + 1:]
    else:
        return

    recursive = bool(re.search(r"(^|\s)-\w*[rR]", segment)) or verb != "rm"

    saw_path = False
    for a in args:
        if a.startswith("-"):
            continue
        # `rm -rf *` / `.` / `..` executed while sitting in a protected dir.
        if a in ("*", ".", "./", "..", "../"):
            reason = classify(_p(cwd), cwd)
            if reason:
                deny(
                    f"Refusing `{verb} {a}` — the working directory {cwd} is protected."
                )
            saw_path = True
            continue
        target = resolve(a, cwd)
        reason = classify(target, a)
        if reason:
            if not recursive and target and os.path.isdir(target):
                pass  # non-recursive rm on a dir fails anyway
            deny(
                f"Refusing `{verb}` against a protected path: {reason}.\n\n"
                "This guard is independent of approval mode (see "
                "guardrails/deny-destructive-paths.py). If you genuinely intend "
                "this, run it yourself in a terminal."
            )
        saw_path = True
    _ = saw_path


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        allow()  # not our payload to judge

    if payload.get("tool_name") != "Bash":
        allow()

    raw = (payload.get("tool_input") or {}).get("command") or ""
    if not raw.strip():
        allow()

    cwd = payload.get("cwd") or os.getcwd()

    try:
        cmd = expand(raw)

        # 1. Command substitution. This is the vector that caused the incident:
        #    a payload inside backticks runs for real before the outer program
        #    ever starts. Judge the inner text on its own.
        for m in SUBST.finditer(cmd):
            inner = m.group(1) or m.group(2) or ""
            if not inner.strip():
                continue
            for seg in SPLIT.split(inner):
                if seg.strip():
                    check_segment(seg, cwd)
            if re.search(r"\brm\b", inner):
                deny(
                    "Refusing: this command contains `rm` inside a command "
                    "substitution (backticks or $(...)).\n\n"
                    f"    {m.group(0)[:200]}\n\n"
                    "The shell expands that BEFORE the outer program runs, no "
                    "matter what language the surrounding string is meant to be. "
                    "This is exactly how `rm -rf ~` was executed against a real "
                    "home directory on 2026-08-08. Put the script in a file, or "
                    "use a quoted heredoc:\n\n"
                    "    bun run script.ts\n"
                    "    bun -e \"$(cat <<'EOF'\\n...\\nEOF\\n)\""
                )

        # 2. The ordinary path: each command in the pipeline.
        for seg in SPLIT.split(cmd):
            if seg.strip():
                check_segment(seg, cwd)

    except SystemExit:
        raise
    except Exception as exc:  # fail closed, loudly
        deny(
            "Destructive-path guard failed to parse this command, so it is "
            f"refused rather than allowed ({type(exc).__name__}: {exc}). "
            "Simplify the command or run it yourself."
        )

    allow()


if __name__ == "__main__":
    main()
