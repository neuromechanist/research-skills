# Making CI Faster Without Making It Less Reliable

Use this when CI is slow, a required check takes more than about ten minutes,
or a pipeline is being scaffolded for a suite that will grow.
The order matters: measure first, then fix the longest thing,
then measure again.
Most of the wins below came from one slow job and one stalled install,
not from trimming tests.

## 1. Measure Before Changing Anything

Split every job of the last runs into queueing, setup and running,
and list the jobs by running time.
The critical path is the longest job; speeding up any other job changes nothing.

```bash
# Wall time of recent runs of one workflow
gh run list --workflow test.yml --limit 40 --json databaseId,event,conclusion,createdAt,updatedAt \
  --jq '.[] | "\(.databaseId) \(.event) \(.conclusion) \(((.updatedAt|fromdate)-(.createdAt|fromdate)))s"'

# Per-job and per-step time of one run (skipped jobs have null timestamps)
gh run view <run-id> --json jobs --jq '.jobs[] | select(.startedAt!=null and .completedAt!=null)
  | "\(.name)\t\(((.completedAt|fromdate)-(.startedAt|fromdate)))s"'
gh run view <run-id> --json jobs --jq '.jobs[] | select(.name=="<job>") | .steps[]
  | select(.startedAt!=null and .completedAt!=null)
  | "\(((.completedAt|fromdate)-(.startedAt|fromdate)))s \(.name)"'
```

Per-file test time comes from the job log: `##[group]<file>:` lines carry a timestamp,
and the gap to the next group is that file's time.
Check three places a "slow CI" complaint hides:

- Gates that run after merge (a deploy workflow that re-runs the suite serially).
  The time a person waits is the sum of the PR run, the push run and the deploy gate.
- A single unsharded job next to sharded ones.
- Setup steps (package installs, checkouts) that dwarf the tests of their shard.

## 2. Shard the Longest Job, Balanced by Time

A matrix of shards turns a serial job of N minutes into about N divided by the shard count,
bounded by the longest single file.
Balance by measured per-file time, not by file count:
five files held half the time of a 94-file suite.

Bun has this built in:

```bash
bun test --shard="$i/$N" --timings timings.json --update-timings "${files[@]}"
```

`--timings` balances the shards by recorded milliseconds per file;
`--update-timings` writes this shard's measured durations,
so each shard can upload its file as an artifact and a refresh merges them.
Seed the first file from the log of a green run.
A file missing from the timings still runs, only balanced less well.
For other runners, split with a timings-aware tool (for example `pytest-split`, `jest --shard`).

Keep the gate honest:

- Give the matrix its own name and add a gate job that keeps the old check name,
  so branch protection and anything that reads the job name still work.
  The gate runs with `if: always()` and fails unless the matrix result is `success`;
  a skipped dependency would otherwise read as green.
- Make each shard refuse to pass when it ran nothing.
  `bun test` exits 0 on `Ran 0 tests across 0 files`.
  Read the run's own header and summary, and compare planned against ran.
- Verify that the matrix labels are `1..N` in order, so a slice cannot run twice or never.
- Strip ANSI colors before grepping the runner's output.

More shards are not always better:
each shard repeats checkout, install and tool setup,
and shards that share a backend or a database can interfere.
Concurrent pull-request runs already share staging, so a suite that survives them survives shards;
a suite with exclusive state needs its own database per shard.

## 3. Fix Setup, the Part Nobody Looks At

- **System packages.** A bare `apt-get update && apt-get install` can stall for minutes on a
  slow mirror (one shard lost 9 minutes, another job an hour).
  Cache the `.deb` files with `actions/cache`, install from the cache with `dpkg -i`,
  and on a miss use a short `timeout` per attempt with retries and a long last attempt.
  Put it in one composite action so every job gets the fix.
- **Dependency caches.** A PR cache is readable by its own branch and the refs it was cut from.
  If nothing seeds a cache from the default branch, most PRs start cold and nobody notices.
  Check the cache hit rate across the last 100 runs.
- **Checkout.** Prefer a blobless clone (`filter: blob:none`) over a shallow one when anything
  reads history; a shallow clone breaks those tools.
- **Parallelism versus cores.** Match test concurrency to the runner's cores;
  running 8 tasks on 4 vCPUs was as slow as 4 and flaky.
  Larger runners often beat more shards, because each shard spends most CPU loading modules.

## 4. Run Independent Work in Parallel

Lint, typecheck, build and tests need no order between them.
Run them as separate jobs so the pull request takes as long as the slowest.
Then look at what else the slowest job does (migration checks, other apps' tests)
and move it into its own job.

## 5. Run Only What a Change Touches, and Test the Skip Logic

Path filters or an affected-project graph (Nx, Turborepo, `dorny/paths-filter`)
skip jobs a change cannot affect.
Run the full suite on a schedule and on the default branch.
Test the skip logic itself:
hide a change from the filter on purpose and confirm the run fails,
because a filter that skips everything reports green.
Required checks must still report on every pull request,
so skip inside the job, not at the workflow trigger, when a check is required.

## 6. Make Checks Fast, and Strict, Where the Agent Works

- Rust-based linters and type checkers (Oxlint, Biome, a faster `tsc`) cut minutes to seconds.
  Check the actual lint and typecheck times in the log before switching;
  when they are already under 30 seconds, as with Biome here, there is nothing to win.
- Agents do not tire of strict rules, so enable more of them.
- Run format, lint and typecheck on changed files in a pre-commit or pre-push hook.
  A hook runs every time; a line in `AGENTS.md` is skipped in long sessions.

## 7. Delete Tests Only With Evidence

Audit before cutting: a measured pass over thousands of cases often finds almost nothing
worth deleting, and the time was never in the tests.
Candidates that are safe to cut: duplicated cases, tests of the framework,
tests that assert a mock and nothing else.
Do not delete a test to make a gate faster when sharding would do.

## 8. Cost

More parallelism costs runner minutes, and a team can multiply its CI bill many times over
while saving developers' time.
Estimate runner minutes before and after (the sum of job times, not the wall time),
and note the change in the pull request.
Sharding a serial job barely changes runner minutes, because the work is the same plus setup;
the extra cost is the repeated setup per shard, so keep setup cheap first.

## Checklist

- [ ] Measured the last 20 or more runs per workflow, including post-merge and deploy gates.
- [ ] Identified the critical path job and its largest files or steps.
- [ ] Sharded it with a time-balanced split, with a gate that keeps the old check name.
- [ ] Each shard fails on an empty or short run.
- [ ] Cached or retried the system package install.
- [ ] Independent checks run as separate parallel jobs.
- [ ] Skip logic tested; required checks still report.
- [ ] Re-measured and reported before and after numbers.
