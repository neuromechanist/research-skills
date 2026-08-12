# Running The Job: Sync, Detach, Verify, Fetch, Terminate

The pod is a stateless executor. Code arrives by `rsync`, the job runs detached, results leave by `scp`, and the pod dies. Nothing of value is ever stored only on the pod.

## Sync the project

```bash
SSH_OPTS="ssh -i $POD_SSH_KEY -o StrictHostKeyChecking=no -p $PORT"
rsync -az --no-owner --no-group --delete -e "$SSH_OPTS" \
    --exclude .git --exclude .venv --exclude results \
    "$LOCAL_ROOT/" "$HOST:$POD_REMOTE_DIR/"
```

`--no-owner --no-group` is mandatory: without it `rsync` tries to `chown` inside the container, fails with exit code 23, and takes any `set -e` launch script down with it, even though the files transferred correctly.

Exclude the local virtual environment. The image already carries the dependency environment built from the lockfile, so the on-pod install step should resolve to a warm-cache no-op:

```bash
uv sync --frozen --no-dev
```

If that step takes more than a few seconds, the image and the lockfile have drifted apart. Rebuild the image rather than paying the install cost on every pod.

## Launch detached, with markers

Long jobs must survive a dropped connection, and every launch must prove it actually started.

```bash
tmux new-session -d -s "$SESSION" "
    set -o pipefail
    PYTHONUNBUFFERED=1 $POD_JOB_CMD 2>&1 | tee run.log
    echo === JOB EXIT \$? ===
"
sleep 3
tmux has-session -t "$SESSION" 2>/dev/null && echo "=== LAUNCHED ok" || { echo "!!! LAUNCH FAILED"; exit 1; }
head -3 run.log 2>/dev/null || true
```

Three properties make this safe:

- **Detached.** The local session can disconnect, sleep, or crash without killing the run.
- **Logged.** `tee` gives a file that `status` can poll and that `fetch` can retrieve.
- **Marked.** The trailing `echo === JOB EXIT $? ===` line is what distinguishes "still running" from "finished clean" from "crashed", without guessing from log tails. The `set -o pipefail` is load-bearing: without it, `$?` after `cmd | tee` is `tee`'s exit status, and a crashed job prints `JOB EXIT 0`.

### Marker discipline

Never fire-and-forget a launch. A silent no-op looks exactly like a fast start, and the difference is billed by the minute. One real case cost 17 idle minutes: a mid-chain rename left the launch command pointing at a path that no longer existed, and nothing checked.

Related trap: `scp` keeps the **source** basename. Renaming a file between steps means it arrives under the old name and the next step silently misses it. Either pass an explicit destination path or verify the file exists at the expected path after every copy.

The rule: every stage echoes a timestamped `STAGE` / `READY` / `FAILED` marker, and the calling script verifies the marker before proceeding. A missing marker is a hard failure, never a warning.

**Never suppress stderr on an orchestration path.** A `2>/dev/null` on a launch `ssh` hid a self-killing `pkill -f` for half an hour, where it read as network flakiness ([pitfalls.md](pitfalls.md) #17). Redirect stderr into a per-pod log instead, so every failed step leaves evidence: `ssh ... >>"logs/$HOST.log" 2>&1`.

Scaling this to more than one pod adds its own failure modes (stdin-eating `ssh` in loops, shell word-splitting, partial stock). See [fanout.md](fanout.md).

## Extending a live time cap

`timeout` cannot have its deadline changed after start, but a running job can outlive its cap without a restart when the estimate turns out short. Three steps, in order:

1. **SIGKILL the `timeout` process itself.** SIGKILL cannot be forwarded to the child, so the job survives and is reparented to init. Mind the match: the tmux server and pane shell carry the launch string on their own command lines, so `pgrep -f 'timeou[t] <secs>'` can return all three. In the live incident this section records, killing all three also took the `tee` holding the job's output pipe down with them, which sets up step 3.
2. **Re-arm the cap before anything else.** The cap is the cost discipline; removing it without a replacement trades a clipped run for an unbounded one. `tmux new-session -d -s watchdog 'sleep <secs>; pkill -9 -f <job-patter[n]>'`. The placeholder means: apply the character-class dodge to your own job string, e.g. `evaluat[e]` for a command containing `evaluate`.
3. **Re-attach a reader if `tee` died.** A pipe with no readers returns EPIPE on the next write, which kills a Python job at its next print. Linux can heal it: opening the writer's fd through `/proc` attaches a fresh reader to the same pipe object. `tmux new-session -d -s logger 'cat /proc/<job-pid>/fd/1 >> run.log'`. Then verify end to end by writing a probe line into `/proc/<job-pid>/fd/1` and reading it back from the log.

The exit marker dies with the pane shell, so completion detection for that pod must switch to "job process gone, results present".

## Poll status

```bash
SSH_ARGS="-i $POD_SSH_KEY -o StrictHostKeyChecking=no -p $PORT"
ssh $SSH_ARGS "$HOST" "cd $POD_REMOTE_DIR && \
    (grep -E 'JOB EXIT|Traceback|Error' run.log | tail -20; echo; tail -2 run.log)"
```

Grep for the exit marker and for error signatures first, then show the tail. A `status` command that only tails the log will happily report progress on a job that died 40 minutes ago.

## Fetch results before terminating

```bash
SCP_ARGS="-i $POD_SSH_KEY -o StrictHostKeyChecking=no -P $PORT"
scp $SCP_ARGS "$HOST:$POD_REMOTE_DIR/$POD_RESULTS" "$LOCAL_ROOT/$POD_RESULTS"
wc -l "$LOCAL_ROOT/$POD_RESULTS"   # verify locally before the pod goes away
```

Copy results **to the local machine**. Do not stage them through a model hub as the only path off the pod: free-plan private storage caps have failed uploads mid-chain, and the pod holding the only copy is usually already scheduled for termination by then.

Verify the retrieved artifact locally (row count, file size, a parse) **before** running `pod-down.sh`. Verification after termination is not verification.

## Terminate and account

```bash
pod-down.sh                      # reads the id recorded by pod-up.sh
```

Termination is the last step of the job, not a separate cleanup task. Alongside it:

- Give the workload its own budget or time cap flag, so an overrunning run stops itself rather than running until someone notices.
- Record the spend where the work is tracked: GPU type, GPU count, hourly rate, wall time, and what the run decided. A pod that produced no decision is a finding too.
- Confirm no other pods are running before closing out the session.

## Credentials

Keep the API key out of the shell history and out of the repository. On macOS, read it from the keychain at use time:

```bash
export RUNPOD_API_KEY="$(security find-generic-password -s <keychain-item> -w)"
```

The `ssh` key used for pods should be a dedicated key pair, not a general-purpose identity, so it can be rotated independently. Its public half goes into the create call as `PUBLIC_KEY`; the private half never leaves the local machine.
