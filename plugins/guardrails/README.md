# guardrails

A `PreToolUse` hook that refuses destructive shell commands aimed at paths you
cannot afford to lose. It runs **before** the permission decision, so it holds
under auto-approve and under `--dangerously-skip-permissions`.

## Why this exists

On 2026-08-08 a Claude Code subagent running in auto-approve mode executed
`rm -rf ~` against a real home directory. It ran for the full 2-minute Bash
timeout before SIGTERM stopped it, destroying the user's Desktop, shell
configuration, application state, and every language runtime under `$HOME`.

The agent was fixing a command-injection vulnerability at the time. Its test
payload was written as:

```sh
bun -e "... String.raw`git status && echo ' ; rm -rf ~` ..."
```

Backticks inside a double-quoted shell argument are **command substitution**.
The surrounding JavaScript context is irrelevant — `/bin/sh` expands them
*before* `bun` is ever invoked. The inert-looking test fixture was executed as
a live command.

Approval mode was the only thing standing between that string and the
filesystem, and it was set to auto. This hook is the layer that should have
been there.

## What it refuses

| Category | Examples |
|---|---|
| Destructive verbs | `rm`, `rmdir`, `unlink`, `shred`, `srm`, `trash`, `mv`, `dd`, `truncate`, `mkfs` |
| Recursive permission changes | `chmod -R`, `chown -R` |
| Deletion by traversal | `find … -delete`, `find … -exec rm` |
| Untracked-file wipes | `git clean -xfd` at a protected root |
| **Command substitution** | any `` ` ` `` or `$(…)` region containing `rm` |

Against these targets:

- **Exact directories** — `/`, `$HOME`, `~/Desktop`, `~/Documents`,
  `~/Downloads`, `~/Library`, `~/Documents/git`, `~/.claude`, `~/.config`,
  `~/.local`, `/usr`, `/etc`, `/opt`, `/opt/homebrew`, `/Applications`,
  `/System`, `/Library`, `/Volumes`, `/Users`, and more.
- **Whole subtrees** — `~/.ssh`, `~/.gnupg`, `~/.password-store`, `~/.aws`,
  `~/.kube`, `~/.docker`, `~/.appstoreconnect`, `/System`, `/private/etc`.
  Nothing at or below these may be removed; the blast radius is an account
  compromise, not a rebuild.
- **Any git repository root** — a directory containing `.git`. Deleting a whole
  repo is never routine.
- **A protected working directory** — `rm -rf *` or `rm -rf .` while `cwd` is
  itself protected.

`~` and `$HOME` are expanded before comparison, and a trailing glob is stripped,
so `rm -rf ~`, `rm -rf $HOME`, and `rm -rf ~/*` are all the same target.

## What it deliberately allows

Ordinary work is untouched. Verified non-blocking:

```
rm -rf node_modules              (inside a repo)
rm -rf <repo>/dist
rm -rf /tmp/scratch-xyz
rm -f package-lock.json
find . -name '*.tmp' -delete     (below a repo root)
mv build/a build/b
docker rm -f <container>
echo $(date) ; ls $(pwd)
```

Deleting things *inside* a protected directory is fine — only the directory
itself is defended. `rm -rf ~/Documents/git/foo/node_modules` is normal;
`rm -rf ~/Documents` is not.

## Failure behavior

**Fails closed.** If the guard cannot parse a command, it refuses it rather
than allowing it. A guard that fails open is a guard that lies about protecting
you.

## Install

### As a plugin

```
/plugin marketplace add neuromechanist/research-skills
/plugin install guardrails@research-skills
```

### Standalone (no plugin system)

Copy the script and reference it from `~/.claude/settings.json` so it applies
to every project:

```sh
mkdir -p ~/.claude/hooks
cp hooks/deny-destructive-paths.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/deny-destructive-paths.py
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/usr/bin/python3",
            "args": ["/Users/<you>/.claude/hooks/deny-destructive-paths.py"],
            "timeout": 10,
            "statusMessage": "Checking blast radius"
          }
        ]
      }
    ]
  }
}
```

The `args` form spawns the interpreter directly with no shell, so a path
containing quotes, `$`, or backticks can never reach a shell parser — the same
class of bug this hook defends against.

## Testing

```sh
echo '{"tool_name":"Bash","cwd":"/tmp","tool_input":{"command":"rm -rf ~"}}' \
  | python3 hooks/deny-destructive-paths.py
```

Output is empty for allowed commands, and a `permissionDecision: "deny"` JSON
object for refused ones. Exit status is always 0 — the decision travels in the
body.

## Limits — read these

This hook is a **blast-radius reducer, not a sandbox.** Be honest about what it
does not do:

- It reads the command string. A command that computes its target at runtime
  (`rm -rf "$(cat target.txt)"`) cannot be judged statically — the `$()`
  rule catches the `rm`-bearing cases, but not every indirection.
- It does not cover deletion through a program that is not a known verb: a
  Python or Node script that calls `shutil.rmtree` or `fs.rm` reaches the
  filesystem without passing a destructive verb to the shell.
- It does not protect against a compromised interpreter, or against writes that
  corrupt rather than delete.

Real backups remain the only actual answer. Configure Time Machine.
