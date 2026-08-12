# Fanning Out A Grid Across Pods

An evaluation grid, a benchmark sweep, or a batch of independent cells is embarrassingly parallel: nothing in cell *i* depends on cell *j*. **N** single-GPU pods cost the same total GPU-hours as one pod running the whole grid, and finish in **1/N** of the wall-clock time.

**Do not reach for a multi-node instant cluster for this shape of work.** Clusters are distributed-*training* infrastructure: collective communication, interconnect topology, launcher configuration, and a class of failure modes that independent cells never need. A fleet of independent single-GPU pods is the right instrument. See the scale ladder in [gpu-selection.md](gpu-selection.md) for when a cluster *is* the answer.

## Slice by duration, not by item count

Equal item counts do not mean equal runtime. A long-context bin can take ten times as long as a short one, so slicing "600 items into 6 pods of 100" leaves five pods idle while one finishes.

1. Estimate per-cell duration first, from a smoke run or a previous grid.
2. Sort cells longest-first and pack them into slices of roughly equal **estimated duration** (longest-processing-time-first is enough; this does not need to be optimal, only not naive).
3. Chain several short runs onto one pod inside a single `tmux` session, rather than paying a fresh pod's startup for each:

```bash
POD_JOB_CMD='cmd_a --out results/a.jsonl; cmd_b --out results/b.jsonl; cmd_c --out results/c.jsonl'
```

4. Write **one results file per slice** and merge locally after fetching. Never have two pods append to the same logical output; the merge is a local concatenation and stays trivial as long as each slice owns its file.

## Provision what stock allows, then queue the rest

Availability is per (GPU type, GPU count), so a fleet request is partially fulfilled far more often than it fails outright. Do not block the whole grid waiting for the last pod:

1. Create pods until stock runs out, recording which slices have a home.
2. Queue the unplaced slices onto the pods that *did* provision, round-robin, rebalanced by estimated duration so the queue drains evenly.
3. Re-check stock later only if the remaining queue is long enough to justify another pod.

A grid that runs on 4 pods instead of the 6 requested is a scheduling detail. A grid that waits for 6 is a stalled grid.

## Verify one pod end to end before replicating

Launch **one** pod's slice and confirm all three signals before the launch command is replicated to the rest of the fleet:

- **Session live:** `tmux has-session -t "$SESSION"`.
- **Log advancing:** sample the log line count twice, a few seconds apart, and require growth. A log that exists is not a log that is moving.
- **GPU engaged:** `nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv`. A live session with an idle GPU means the process is stuck before compute, not running.

Replicating an unverified launch multiplies a single mistake by the size of the fleet, and every copy bills while it is wrong.

## Launchers are detached retry loops with a verification connection

A transient network window can fail every pod in one wave. Without retries it looks exactly like a systematic bug, and the natural response (stop, investigate, relaunch by hand) is the expensive one. Every fleet launcher should retry with backoff and verify after each attempt:

```bash
launch_one() {  # $1 = host, $2 = port, $3 = job command
    for attempt in 1 2 3 4 5; do
        # -n is mandatory inside any loop reading stdin; see pitfalls.md #15.
        # stderr is captured, never discarded: it is where the real diagnosis lives.
        ssh -n -o StrictHostKeyChecking=no -p "$2" "$1" \
            "tmux new-session -d -s job \"set -o pipefail; PYTHONUNBUFFERED=1 $3 2>&1 | tee run.log; echo === JOB EXIT \\\$? ===\"" \
            >>"logs/$1.log" 2>&1
        sleep 5
        # Verification connection: a separate probe, not the launch's own exit code.
        if ssh -n -o StrictHostKeyChecking=no -p "$2" "$1" 'tmux has-session -t job' \
             >>"logs/$1.log" 2>&1; then
            echo "=== LAUNCHED ok $1"; return 0
        fi
        echo "=== retry $attempt failed for $1"; sleep $((attempt * 10))
    done
    echo "!!! LAUNCH FAILED $1"; return 1
}
```

Three properties matter here:

- **`ssh -n` everywhere inside a loop.** Without it, `ssh` eats the loop's stdin and only the first iteration runs, while the rest of the fleet boots and bills doing nothing.
- **A verification connection after every attempt.** The launch command's own exit code says the command was accepted, not that the job is running.
- **Per-pod logs, and never `2>/dev/null`.** Suppressing stderr on an orchestration path deletes the only evidence of what actually failed.

Two details in the pane command carry weight: `set -o pipefail` makes the JOB EXIT marker report the job's exit status rather than `tee`'s, and the job command `$3` is interpolated into a nested double-quoted string, so keep job commands free of literal double quotes and unescaped `$`, or build them with `printf %q`.

## Relaunches must be idempotent

A retry loop that can fire twice must be safe to fire twice. Begin every launch attempt by killing the previous session and any orphaned worker process, using the character-class dodge so the kill cannot match its own command line ([pitfalls.md](pitfalls.md) #17):

```bash
ssh -n -p "$PORT" "$HOST" \
    "tmux kill-session -t job 2>/dev/null; pkill -9 -f 'serve[r]' 2>/dev/null; true"
```

Skipping this stacks a second server onto the same GPU after a half-failed attempt: the port or the memory is already taken, and the new run fails for a reason that did not exist a minute earlier. The orphan also poisons verification. A worker left over from a failed wave holds the GPU at high utilization, so "GPU engaged" reads as proof the *new* launch worked when nothing is running. That is why the verify step requires the log to advance, not just the GPU to be busy.

## Generate command chains in Python, not in the shell

Build the per-pod command chain with a real programming language and pass it as a single quoted argument. Shell word-splitting differs between shells (zsh does not split unquoted variables the way bash does), so a chain assembled from a variable in an interactive shell can silently collapse into one malformed command. See [pitfalls.md](pitfalls.md) #16.

```python
chain = "; ".join(
    f"uv run python -m <module> --task {t} --out results/{t}.jsonl" for t in tasks
)
```

## Monitor the fleet from one detached loop

Run one detached monitor on the local machine that polls every pod on a fixed interval (about ten minutes) and prints only signal lines per pod: a count of progress signatures, any error signatures, and the exit marker.

```bash
ssh -n -p "$PORT" "$HOST" \
    "grep -cE 'acc=' run.log; grep -E 'Traceback|JOB EXIT' run.log | tail -3; exit 0"
```

Two rules keep a monitor honest:

- **End remote content pipelines with `; exit 0`.** `grep` exits 1 on zero matches, `ssh` forwards the remote exit code, and a monitor that treats nonzero as "unreachable" reports a healthy pod that simply has no results yet as down ([pitfalls.md](pitfalls.md) #19). An unreachable verdict must be earned by a failed dedicated probe (`ssh -n ... true`), never inferred from a content pipeline.
- **Force unbuffered output on everything the monitor reads.** Python block-buffers stdout when it is piped, so a healthy run under `tmux ... | tee` can show an empty log for minutes ([pitfalls.md](pitfalls.md) #18). `PYTHONUNBUFFERED=1` on every remote run.

### Calibrate an ETA from measured throughput, not from silence

Know the job's result granularity before trusting the absence of results. If a progress line only prints when a whole cell completes, the first half hour of a healthy run is indistinguishable from a stalled one by result count alone. Pull a finer signal from the worker's own log in the first minutes (a serving log's tokens-per-second, a step counter) and turn it into arithmetic: seconds per sample from prefill and decode rates, minutes per cell from the sample count.

From the grid this document came from: prefill at about 1,350 tok/s on an A40 put an 8K-token sample near 12 s including decode, a 30-sample cell near 6 minutes, and a 32K cell near half an hour. With that math in hand, "zero cells complete after 20 minutes" was on schedule rather than a stall, and the fleet's health check became "log advancing at the predicted rate" instead of "any results yet?".

## Reap on completion: fetch, verify, terminate, automatically

A finished pod bills at the full hourly rate until something terminates it, and a monitor that only *reports* progress does not stop the meter. Completion must trigger an action, not an observation. The first pod of a real grid sat idle for 15 minutes because a human had to notice the finished chain; a reaper loop caps that tail at its poll interval.

Run one detached local loop over the fleet that, per cycle:

1. **Probes reachability first.** An unreachable pod is never terminated; transient network reads as "finished" otherwise.
2. **Detects completion as chain-process-gone**, not as a log marker: `pgrep -cf '<job-patter[n]>' == 0` (the character-class dodge applied to your own job string, e.g. `evaluat[e]` for a chain running `evaluate`). The chain shell's own command line contains the job pattern, so the count stays nonzero in the gap between chained invocations, and this detection also survives the exit marker being lost (a killed pane shell takes the marker's `echo` with it).
3. **Fetches results and the log, then verifies.** `scp` the per-slice results and the run log to the local machine and check them there.
4. **Terminates only after a verified fetch.** If the fetch fails while the pod still holds slice files, leave the pod running and alert; a dropped `scp` must never race the delete. If the pod holds no results at all (a crash before output), fetch the log as evidence and terminate anyway.

Ordering is the whole design: probe, detect, fetch, verify, and only then delete. The tempting alternative, pod-side self-termination after the job's last command, is worse on both axes that matter: it needs the account API key on rented hardware, and it puts the delete before any off-pod copy of the results has been verified.

## Startup anatomy, and how to shrink it

Per-pod startup, measured on a partially prebaked image, runs about **4 minutes** across four stages: dependency sync, model weight pull, evaluation-dataset pulls, and server or harness load. Multiplied across a fleet, that is real money for zero output.

| Stage | Partially prebaked | Fully prebaked |
|---|---|---|
| Dependency sync | Installs the missing groups | Warm-cache no-op |
| Model weight pull | Full download | Full download (keep; weights are large and change per run) |
| Evaluation dataset pulls | Per-pod download | Already in the image |
| Server or harness load | Unchanged | Unchanged |
| **Total** | **~4 min** | **~90 s** |

Two changes buy that: bake the evaluation datasets into the image, and bake **all** dependency groups, not just the default one. A per-pod `uv sync` that installs an extra group is startup cost paid N times for a build step that could have been paid once.
