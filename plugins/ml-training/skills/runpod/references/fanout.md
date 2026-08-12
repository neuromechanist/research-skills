# Fanning Out A Grid Across Pods

An evaluation grid, a benchmark sweep, or a batch of independent cells is embarrassingly
parallel: nothing in cell *i* depends on cell *j*. **N** single-GPU pods cost the same total
GPU-hours as one pod running the whole grid, and finish in **1/N** of the wall-clock time.

**Do not reach for a multi-node instant cluster for this shape of work.** Clusters are
distributed-*training* infrastructure: collective communication, interconnect topology, launcher
configuration, and a class of failure modes that independent cells never need. A fleet of
independent single-GPU pods is the right instrument. See the scale ladder in
[gpu-selection.md](gpu-selection.md) for when a cluster *is* the answer.

## Slice by duration, not by item count

Equal item counts do not mean equal runtime. A long-context bin can take ten times as long as a
short one, so slicing "600 items into 6 pods of 100" leaves five pods idle while one finishes.

1. Estimate per-cell duration first, from a smoke run or a previous grid.
2. Sort cells longest-first and pack them into slices of roughly equal **estimated duration**
   (longest-processing-time-first is enough; this does not need to be optimal, only not naive).
3. Chain several short runs onto one pod inside a single `tmux` session, rather than paying a
   fresh pod's startup for each:

```bash
POD_JOB_CMD='cmd_a --out results/a.jsonl; cmd_b --out results/b.jsonl; cmd_c --out results/c.jsonl'
```

4. Write **one results file per slice** and merge locally after fetching. Never have two pods
   append to the same logical output; the merge is a local concatenation and stays trivial as long
   as each slice owns its file.

## Provision what stock allows, then queue the rest

Availability is per (GPU type, GPU count), so a fleet request is partially fulfilled far more often
than it fails outright. Do not block the whole grid waiting for the last pod:

1. Create pods until stock runs out, recording which slices have a home.
2. Queue the unplaced slices onto the pods that *did* provision, round-robin, rebalanced by
   estimated duration so the queue drains evenly.
3. Re-check stock later only if the remaining queue is long enough to justify another pod.

A grid that runs on 4 pods instead of the 6 requested is a scheduling detail. A grid that waits
for 6 is a stalled grid.

## Verify one pod end to end before replicating

Launch **one** pod's slice and confirm all three signals before the launch command is replicated to
the rest of the fleet:

- **Session live:** `tmux has-session -t "$SESSION"`.
- **Log advancing:** sample the log line count twice, a few seconds apart, and require growth. A
  log that exists is not a log that is moving.
- **GPU engaged:** `nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv`. A live
  session with an idle GPU means the process is stuck before compute, not running.

Replicating an unverified launch multiplies a single mistake by the size of the fleet, and every
copy bills while it is wrong.

## Launchers are detached retry loops with a verification connection

A transient network window can fail every pod in one wave. Without retries it looks exactly like a
systematic bug, and the natural response (stop, investigate, relaunch by hand) is the expensive
one. Every fleet launcher should retry with backoff and verify after each attempt:

```bash
launch_one() {  # $1 = host, $2 = port, $3 = job command
    for attempt in 1 2 3 4 5; do
        # -n is mandatory inside any loop reading stdin; see pitfalls.md #15.
        # stderr is captured, never discarded: it is where the real diagnosis lives.
        ssh -n -o StrictHostKeyChecking=no -p "$2" "$1" \
            "tmux new-session -d -s job \"$3 2>&1 | tee run.log; echo === JOB EXIT \\\$? ===\"" \
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

- **`ssh -n` everywhere inside a loop.** Without it, `ssh` eats the loop's stdin and only the first
  iteration runs, while the rest of the fleet boots and bills doing nothing.
- **A verification connection after every attempt.** The launch command's own exit code says the
  command was accepted, not that the job is running.
- **Per-pod logs, and never `2>/dev/null`.** Suppressing stderr on an orchestration path deletes
  the only evidence of what actually failed.

## Generate command chains in Python, not in the shell

Build the per-pod command chain with a real programming language and pass it as a single quoted
argument. Shell word-splitting differs between shells (zsh does not split unquoted variables the
way bash does), so a chain assembled from a variable in an interactive shell can silently collapse
into one malformed command. See [pitfalls.md](pitfalls.md) #16.

```python
chain = "; ".join(
    f"uv run python -m <module> --task {t} --out results/{t}.jsonl" for t in tasks
)
```

## Startup anatomy, and how to shrink it

Per-pod startup, measured on a partially prebaked image, runs about **4 minutes** across four
stages: dependency sync, model weight pull, evaluation-dataset pulls, and server or harness load.
Multiplied across a fleet, that is real money for zero output.

| Stage | Partially prebaked | Fully prebaked |
|---|---|---|
| Dependency sync | Installs the missing groups | Warm-cache no-op |
| Model weight pull | Full download | Full download (keep; weights are large and change per run) |
| Evaluation dataset pulls | Per-pod download | Already in the image |
| Server or harness load | Unchanged | Unchanged |
| **Total** | **~4 min** | **~90 s** |

Two changes buy that: bake the evaluation datasets into the image, and bake **all** dependency
groups, not just the default one. A per-pod `uv sync` that installs an extra group is startup cost
paid N times for a build step that could have been paid once.
