#!/usr/bin/env bash
# Sync the project to a pod created by pod-up.sh, run the job detached under
# tmux, poll it, and copy results back. Marker-checked at every stage: a launch
# that silently no-ops looks exactly like a fast start, and costs the same as a
# working one.
#
# Usage:
#   export POD_HOST=root@<ip> POD_PORT=<port>     # printed by pod-up.sh
#   export POD_JOB_CMD='uv run python -m <module> --budget-hours 12 --out <results>'
#   ./pod-run.sh launch
#   ./pod-run.sh status
#   ./pod-run.sh fetch
set -euo pipefail

MODE="${1:?launch|status|fetch}"
HOST="${POD_HOST:?set POD_HOST (root@ip, printed by pod-up.sh)}"
PORT="${POD_PORT:?set POD_PORT (printed by pod-up.sh)}"
SSH_KEY="${POD_SSH_KEY:-$HOME/.ssh/id_runpod}"
REMOTE_DIR="${POD_REMOTE_DIR:-/workspace/project}"
SESSION="${POD_TMUX_SESSION:-job}"
RESULTS="${POD_RESULTS:-results/run.jsonl}"
LOCAL_ROOT="${POD_LOCAL_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"

SSH_OPTS="ssh -i $SSH_KEY -o StrictHostKeyChecking=no -p $PORT"
SSH=(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -p "$PORT" "$HOST")

case "$MODE" in
launch)
    JOB_CMD="${POD_JOB_CMD:?set POD_JOB_CMD to the command to run on the pod}"
    echo "=== rsync project -> $HOST:$REMOTE_DIR"
    # --no-owner --no-group: rsync cannot chown inside the container and exits
    # 23, which takes a `set -e` script down even though the files transferred.
    rsync -az --no-owner --no-group --delete -e "$SSH_OPTS" \
        --exclude .git --exclude .venv --exclude results \
        "$LOCAL_ROOT/" "$HOST:$REMOTE_DIR/"

    echo "=== launch (tmux session: $SESSION)"
    "${SSH[@]}" JOB_CMD="$JOB_CMD" REMOTE_DIR="$REMOTE_DIR" SESSION="$SESSION" 'bash -s' <<'REMOTE'
        set -e
        cd "$REMOTE_DIR"
        # Warm-cache no-op against the environment prebaked in the image. If
        # this is slow, the image and the lockfile have drifted; rebuild.
        uv sync --frozen --no-dev
        mkdir -p results
        tmux new-session -d -s "$SESSION" "PYTHONUNBUFFERED=1 $JOB_CMD 2>&1 | tee run.log; echo === JOB EXIT \$? ==="
        sleep 3
        # Marker check: never fire-and-forget. A no-op launch bills idle time.
        tmux has-session -t "$SESSION" 2>/dev/null && echo "=== LAUNCHED ok" || { echo "!!! LAUNCH FAILED"; exit 1; }
        head -3 run.log 2>/dev/null || true
REMOTE
    ;;
status)
    # Grep the exit marker and error signatures before the tail: a tail-only
    # status happily reports progress on a job that died 40 minutes ago.
    "${SSH[@]}" REMOTE_DIR="$REMOTE_DIR" 'bash -s' <<'REMOTE'
        cd "$REMOTE_DIR"
        grep -E "JOB EXIT|Traceback|Error" run.log | tail -20
        echo
        tail -2 run.log
REMOTE
    ;;
fetch)
    # scp keeps the SOURCE basename: pass an explicit destination path and
    # verify locally BEFORE terminating the pod.
    mkdir -p "$LOCAL_ROOT/$(dirname "$RESULTS")"
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no -P "$PORT" \
        "$HOST:$REMOTE_DIR/$RESULTS" "$LOCAL_ROOT/$RESULTS"
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no -P "$PORT" \
        "$HOST:$REMOTE_DIR/run.log" "$LOCAL_ROOT/$(dirname "$RESULTS")/run.log"
    echo "fetched $RESULTS ($(wc -l < "$LOCAL_ROOT/$RESULTS") lines)"
    echo "verify the results, then terminate: ./pod-down.sh"
    ;;
*)
    echo "unknown mode: $MODE (expected launch|status|fetch)" >&2
    exit 2
    ;;
esac
