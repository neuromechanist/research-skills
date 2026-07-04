# Long-Running Jobs: Benchmarks, Training, Batch Work

Born from a real incident: a session's context compaction reaped its tracked
background shells and silently killed a half-finished benchmark campaign.

## [CRITICAL] Detach long jobs from the agent session

Session-tracked background shells die when the agent session compacts,
restarts, or disconnects. Any job longer than ~10 minutes (benchmarks, model
downloads, training, batch processing) MUST be launched detached:

```bash
nohup ./job.sh > /tmp/job.log 2>&1 & disown
```

Then watch the log, never the shell:

```bash
tail -f /tmp/job.log   # or the agent's log-monitoring tool on the log file
```

The watcher is expendable; the job is not. If the watcher dies, re-attach to
the log; the job keeps running.

## Job script requirements

- Stage markers: echo a recognizable line per stage (`=== STAGE: ... ===`)
  and a terminal marker (`=== COMPLETE ===`); failures print loudly
  (`!!! STAGE FAILED`), never exit silently mid-pipeline.
- Resumable: completed work is recorded (results files, checkpoints) and
  skipped on relaunch; a killed job costs minutes, not the whole run.
- Serial measurement: never run two measurement jobs concurrently on one
  machine; they contend for memory/compute and corrupt each other's numbers.
- Logs to stable paths: /tmp or a project log dir, not the agent harness's
  task output files (those vanish with the session).

## Completion detection

Poll the process, never guess a sleep duration:

```bash
while pgrep -f <job-name> > /dev/null; do sleep 20; done
grep -E "COMPLETE|FAILED" /tmp/job.log | tail -4
```

Run the poll loop itself in the background. A fixed timeout may wrap the loop
as an outer safety net; it must never be the primary signal (jobs regularly
outlive any guessed duration).

## Verification

`pgrep -fl <job>` right after launch; check the log's mtime when in doubt. A
quiet log with a live process is normal. A stale mtime with no process means
the job died: relaunch from its resume point.

## Campaign bookkeeping

- An unattended multi-stage campaign is complete when every flagged or
  disputed cell has a named resolution, not when the process exits 0. Keep a
  "disputed cells" list (anything near a threshold, at low sample count, or
  anomalous) as the sweep runs; resolve it explicitly afterward.
- If a cell fails in a way that the next stage would repeat (an out-of-memory
  at a given size), stop the dependent stages immediately and diagnose before
  burning more compute.
- Capture evidence out of temp dirs into committed artifacts before it is
  garbage-collected.
- Under broad "run overnight, merge when done" authorization, state up front,
  once, the evidence threshold that would make you stop and flag instead of
  proceeding; "merge when done" always means "when the stated gate is met".
