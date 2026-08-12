# RunPod Provisioning Pitfall Catalog

Every entry here was hit on a real, billed pod. The point of the prebaked-image workflow is that
none of them get hit twice. Entries are ordered by when they bite: image build first, then pod
creation, then the run itself.

## Image build

### 1. Base-image glibc must match any prebuilt binaries copied in

**Symptom:** the image builds and pushes cleanly, then the binary dies at runtime with
`GLIBC_2.38 not found` or a missing `GLIBCXX_3.4.32`.

**Cause:** official CUDA server images from upstream projects (for example
`ghcr.io/ggml-org/llama.cpp:server-cuda`) are built on Ubuntu 24.04, which ships glibc 2.38 or
newer. Copying those binaries onto an `ubuntu22.04` base (glibc 2.35) produces an image whose
loader cannot satisfy them.

**Fix:** pick the base image release to match the binaries' build environment
(`nvidia/cuda:<ver>-runtime-ubuntu24.04` for a 24.04-built binary), and verify locally before
pushing:

```bash
docker run --platform linux/amd64 --rm "$IMAGE" <the-binary> --version
```

**Cost:** $0 when caught locally. The same catch after a push is a pod create, a pull, an `ssh`,
and a teardown, all billed.

### 2. Never compile, in the image or on the pod

**Symptom:** a build that takes tens of minutes, or a pod that idles while `nvcc` runs.

**Cause:** compiling CUDA code inside `docker buildx` on Apple Silicon runs under qemu emulation,
which is punishingly slow. Compiling on the pod converts build time directly into GPU rental.

**Fix:** `COPY --from` a digest-pinned official prebuilt image. Copying binaries is effectively
instant, and the digest pin makes the image reproducible:

```dockerfile
ARG PREBUILT_IMAGE=<registry>/<project>@sha256:<digest>
FROM ${PREBUILT_IMAGE} AS prebuilt
FROM nvidia/cuda:12.6.3-runtime-ubuntu24.04
COPY --from=prebuilt /app /opt/<tool>
```

Re-resolve the digest when the upstream tag moves:
`docker manifest inspect <registry>/<project>:<tag>`.

### 3. `ssh` sessions do not inherit Docker `ENV`

**Symptom:** the binary runs under `docker run` and under the container's own entrypoint, but over
`ssh` it cannot find its shared libraries, or `PATH` lookups fail.

**Cause:** `sshd` spawns clean login environments. Variables set with Dockerfile `ENV` exist for
the entrypoint process tree and nowhere else.

**Fix:** publish them where a login shell will find them. Register library directories with the
dynamic loader, and write the rest to `/etc/environment`, which `sshd` reads through PAM:

```dockerfile
RUN echo /opt/<tool> > /etc/ld.so.conf.d/<tool>.conf && ldconfig \
    && printf '%s\n' \
        'PATH=/opt/<tool>:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' \
        'HF_HUB_ENABLE_HF_TRANSFER=1' \
        'HF_HOME=/workspace/hf' \
        >> /etc/environment
```

### 4. Prebake the dependency environment, and keep it to exactly one

**Symptom:** the pod spends minutes resolving and downloading dependencies after every code sync,
or the container disk fills unexpectedly.

**Cause:** installing at run time instead of build time. The disk case has a specific culprit: a
tool's bundled `requirements.txt` pulling in a second deep-learning framework install alongside
the one already present. That once filled a 60 GB disk.

**Fix:** build the environment from the lockfile at image-build time, without the project itself,
so the post-sync install on the pod is a warm-cache no-op:

```dockerfile
COPY pyproject.toml uv.lock /opt/<env-dir>/
RUN cd /opt/<env-dir> && uv sync --frozen --no-install-project --no-dev
```

Then audit any tool you add for a transitive framework dependency, and exclude it explicitly.

### 5. Preinstall `hf_transfer` and put `HF_HOME` on the volume

**Symptom:** weight downloads run at a fraction of the available bandwidth, repeated on every pod.

**Fix:** install `hf_transfer` into the image, set `HF_HUB_ENABLE_HF_TRANSFER=1`, and point
`HF_HOME` at the container volume path (`/workspace/hf`) rather than a layer that vanishes.
Measured 2026-08-12: a 17 GB model file in 34.8 s, about 490 MB/s.

## Pod creation

### 6. REST-created pods get no auto-injected `ssh` key

**Symptom:** the pod reaches `RUNNING`, `ssh` answers, and every attempt returns
`Permission denied (publickey)`.

**Cause:** RunPod injects account `ssh` keys into pods launched from its own templates. A pod
created through the REST API with a custom image gets nothing.

**Fix:** pass the local public key explicitly in the create call, and have the image's entrypoint
install it:

```jsonc
"env": { "PUBLIC_KEY": "<contents of ~/.ssh/<key>.pub>" }
```

```bash
# in start.sh
mkdir -p /root/.ssh && chmod 700 /root/.ssh
[ -n "${PUBLIC_KEY:-}" ] && echo "$PUBLIC_KEY" >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
/usr/sbin/sshd -p 22 || service ssh start
```

Also expose the port: `"ports": ["22/tcp"]`.

### 7. Pin away from a broken host pool

**Symptom:** the pod is created but the container never starts. Logs show device errors such as
a missing `/dev/dri/cardN`. Retrying lands on another host with the same failure, across more
than one datacenter.

**Cause:** observed July 2026, the CUDA-13 host pool had a fleet-wide container-start bug.

**Fix:** filter the host pool at create time and build the image on a base that runs everywhere in
the filtered set:

```jsonc
"allowedCudaVersions": ["12.6", "12.7", "12.8", "12.9"]
```

A CUDA 12.6 base image runs on every host in that filter. Re-check the filter periodically; it is
a workaround for a provider-side bug, not a permanent rule.

### 8. Availability is per (GPU type, GPU count)

**Symptom:** `There are no instances currently available` on create, for a GPU type the dashboard
lists as available.

**Cause:** stock is tracked per type **and** per requested count. Plenty of 1x availability says
nothing about 2x on one host.

**Fix:** query GraphQL before creating; the REST API has no `gputypes` path.

```graphql
{ gpuTypes { id securePrice lowestPrice(input: {gpuCount: 2, secureCloud: true}) { stockStatus uninterruptablePrice } } }
```

Then pick another type or another count. See [gpu-selection.md](gpu-selection.md).

### 9. Size the container disk for two copies of the model

**Symptom:** the run dies partway through with a full disk, after the weights already downloaded
once.

**Cause:** downloads land in a cache and are then materialized, converted, or re-quantized, so
peak usage is roughly double the final artifact, before logs and intermediate outputs.

**Fix:** `containerDiskInGb` at 2x the model size plus caches and outputs. Disk is far cheaper
than a re-run.

## During the run

### 10. `rsync` into a container fails `chown`

**Symptom:** `rsync` exits with code 23 and a `set -e` launch script stops, even though every file
transferred correctly.

**Cause:** `rsync` tries to preserve ownership, which the container refuses.

**Fix:** `rsync -az --no-owner --no-group ...`. Do not paper over it by dropping `set -e`; the
launch script's failure behavior is what makes marker checks meaningful.

### 11. Marker-check every launch, never fire-and-forget

**Symptom:** the run appears to be going, and 17 minutes of idle billing later nothing has
happened.

**Cause:** the launch silently no-opped. In the real case, a mid-chain rename left the launch
command pointing at a path that no longer existed. A related trap: `scp` keeps the **source**
basename, so a renamed file arrives under its old name and the next step misses it.

**Fix:** echo explicit `STAGE`, `READY`, and `FAILED` markers with timestamps, and verify the
marker before moving on. Confirm the process exists (`tmux has-session`), confirm the log has
grown, and treat a missing marker as a hard failure. Never suppress stderr on an orchestration
path: `2>/dev/null` on a launch `ssh` hid pitfall 17 for half an hour. Capture per-pod logs
instead.

```bash
tmux has-session -t "$SESSION" && echo "=== LAUNCHED ok" || { echo "!!! LAUNCH FAILED"; exit 1; }
```

### 12. Long jobs run detached, with an exit-code marker

**Symptom:** a dropped connection kills a multi-hour run.

**Fix:** run under `tmux` (or `nohup`), tee to a log, and end the command with an explicit
exit-code line so `status` can tell "still running" from "finished" from "crashed":

```bash
tmux new-session -d -s "$SESSION" "$JOB_CMD 2>&1 | tee run.log; echo === JOB EXIT \$? ==="
```

### 13. Copy results back; do not stage them through a model hub

**Symptom:** results uploaded to a hub fail mid-chain, and the pod holding the only copy is
already terminated.

**Cause:** free-plan private storage caps.

**Fix:** `scp` or `rsync` results to the local machine as an explicit `fetch` step, verify the row
or file count locally, and only then terminate.

### 14. Terminating is part of the job

**Symptom:** a pod discovered still running hours after its results were fetched.

**Fix:** make `fetch` and `pod-down.sh` one motion. Give the workload its own budget or time cap
flag as the hard stop, so an overrunning job stops itself. Record the spend, with GPU type,
count, hourly rate, and wall time, wherever the work is tracked.

## Fleet orchestration

These three only appear once more than one pod is in play, and all three look like something else
when they hit. See [fanout.md](fanout.md) for the surrounding fan-out method.

### 15. `ssh` inside a `while read` loop eats the loop's stdin

**Symptom:** a fleet launcher reports `1/N launched`. The other N-1 pods are up, idle, and
billing. The loop looks correct on inspection, and running its body by hand works every time.

**Cause:** `ssh` reads stdin by default. Inside a `while read ... done < list.txt` loop, the first
`ssh` consumes the **rest of the loop's input**, so the loop body executes exactly once and the
loop then exits normally, with no error anywhere.

**Fix:** `ssh -n` in every loop, without exception. `-n` redirects stdin from `/dev/null` and costs
nothing when it is not needed.

```bash
while read -r host port; do
    ssh -n -p "$port" "$host" "$CMD"   # -n: do not touch the loop's stdin
done < fleet.txt
```

The same applies to any stdin-reading command in a loop body. Note that a deliberate heredoc
(`ssh host 'bash -s' <<'EOF'`) is the opposite case: it *needs* stdin, so keep it out of loops that
read from stdin, or feed the loop from a file descriptor other than 0.

**Cost when hit:** 3 pods idle for about 8 minutes.

### 16. zsh does not word-split unquoted variables

**Symptom:** every pod in the fleet fails instantly with an argparse error, all with the same
malformed argument such as `--tasks a b c` where three separate invocations were intended.

**Cause:** shells disagree about unquoted variable expansion. bash splits on `IFS`; zsh does not.
A command chain built in an interactive zsh with `for F in $FILTERS` iterates **once**, with the
whole string as a single word, collapsing an intended chain of commands into one malformed
command. The orchestration script is usually written and tested in bash, then pasted into an
interactive zsh session, which is where the behavior changes.

**Fix:** never rely on shell word-splitting in orchestration. Generate command chains in Python
(or another real language) and pass each as a single quoted argument; or run orchestration under
`bash` explicitly rather than in whatever interactive shell happens to be open.

```python
chain = "; ".join(f"uv run python -m <module> --task {t} --out results/{t}.jsonl" for t in tasks)
```

**Cost when hit:** a full relaunch wave, plus the pods' idle time while the error is diagnosed.

### 17. `pkill -f <name>` matches, and kills, its own `ssh` session

**Symptom:** the launch `ssh` exits 255 with **zero output**, every time, while a plain probe
connection to the same pod succeeds every time. It looks exactly like network flakiness, and
retrying produces the identical result.

**Cause:** `pkill -f` matches against **full command lines**, and the remote command line executed
by `ssh` contains the pattern as a literal. The remote shell therefore matches its own pattern and
kills itself mid-command, so the connection dies before any output is flushed.

**Fix:** make the pattern unable to match its own literal, with the character-class dodge, or match
an exact process name instead:

```bash
# 'serve[r]' matches the process "server" but never its own literal on the command line
ssh -n -p "$PORT" "$HOST" "pkill -f 'serve[r]' || true"
ssh -n -p "$PORT" "$HOST" "pkill -x exact-process-name || true"
```

And keep stderr: this one hid behind a `2>/dev/null` on the launch `ssh` for half an hour. Never
suppress stderr on an orchestration path; capture per-pod logs instead.

**Cost when hit:** about 30 minutes of misdiagnosis plus repeated relaunch waves.
