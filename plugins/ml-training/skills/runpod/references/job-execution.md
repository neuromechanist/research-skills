# Running The Job: Sync, Detach, Verify, Fetch, Terminate

The pod is a stateless executor. Code arrives by `rsync`, the job runs detached, results leave by
`scp`, and the pod dies. Nothing of value is ever stored only on the pod.

## Sync the project

```bash
SSH_OPTS="ssh -i $POD_SSH_KEY -o StrictHostKeyChecking=no -p $PORT"
rsync -az --no-owner --no-group --delete -e "$SSH_OPTS" \
    --exclude .git --exclude .venv --exclude results \
    "$LOCAL_ROOT/" "$HOST:$POD_REMOTE_DIR/"
```

`--no-owner --no-group` is mandatory: without it `rsync` tries to `chown` inside the container,
fails with exit code 23, and takes any `set -e` launch script down with it, even though the files
transferred correctly.

Exclude the local virtual environment. The image already carries the dependency environment built
from the lockfile, so the on-pod install step should resolve to a warm-cache no-op:

```bash
uv sync --frozen --no-dev
```

If that step takes more than a few seconds, the image and the lockfile have drifted apart. Rebuild
the image rather than paying the install cost on every pod.

## Launch detached, with markers

Long jobs must survive a dropped connection, and every launch must prove it actually started.

```bash
tmux new-session -d -s "$SESSION" "
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
- **Marked.** The trailing `echo === JOB EXIT $? ===` line is what distinguishes "still running"
  from "finished clean" from "crashed", without guessing from log tails.

### Marker discipline

Never fire-and-forget a launch. A silent no-op looks exactly like a fast start, and the difference
is billed by the minute. One real case cost 17 idle minutes: a mid-chain rename left the launch
command pointing at a path that no longer existed, and nothing checked.

Related trap: `scp` keeps the **source** basename. Renaming a file between steps means it arrives
under the old name and the next step silently misses it. Either pass an explicit destination path
or verify the file exists at the expected path after every copy.

The rule: every stage echoes a timestamped `STAGE` / `READY` / `FAILED` marker, and the calling
script verifies the marker before proceeding. A missing marker is a hard failure, never a warning.

## Poll status

```bash
ssh $SSH_ARGS "$HOST" "cd $POD_REMOTE_DIR && \
    (grep -E 'JOB EXIT|Traceback|Error' run.log | tail -20; echo; tail -2 run.log)"
```

Grep for the exit marker and for error signatures first, then show the tail. A `status` command
that only tails the log will happily report progress on a job that died 40 minutes ago.

## Fetch results before terminating

```bash
scp $SCP_ARGS "$HOST:$POD_REMOTE_DIR/$POD_RESULTS" "$LOCAL_ROOT/$POD_RESULTS"
wc -l "$LOCAL_ROOT/$POD_RESULTS"   # verify locally before the pod goes away
```

Copy results **to the local machine**. Do not stage them through a model hub as the only path off
the pod: free-plan private storage caps have failed uploads mid-chain, and the pod holding the
only copy is usually already scheduled for termination by then.

Verify the retrieved artifact locally (row count, file size, a parse) **before** running
`pod-down.sh`. Verification after termination is not verification.

## Terminate and account

```bash
pod-down.sh                      # reads the id recorded by pod-up.sh
```

Termination is the last step of the job, not a separate cleanup task. Alongside it:

- Give the workload its own budget or time cap flag, so an overrunning run stops itself rather
  than running until someone notices.
- Record the spend where the work is tracked: GPU type, GPU count, hourly rate, wall time, and
  what the run decided. A pod that produced no decision is a finding too.
- Confirm no other pods are running before closing out the session.

## Credentials

Keep the API key out of the shell history and out of the repository. On macOS, read it from the
keychain at use time:

```bash
export RUNPOD_API_KEY="$(security find-generic-password -s <keychain-item> -w)"
```

The `ssh` key used for pods should be a dedicated key pair, not a general-purpose identity, so it
can be rotated independently. Its public half goes into the create call as `PUBLIC_KEY`; the
private half never leaves the local machine.
