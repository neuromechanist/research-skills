---
name: runpod
description: "This skill should be used when the user says \"spin up a RunPod pod\", \"rent a GPU\", \"run this on a cloud GPU\", \"RunPod\", \"prebake a GPU image\", \"my pod takes 10 minutes to install\", \"boot-to-ready\", \"which GPU should I rent\", \"2x A100 or 1x H100\", \"is Modal cheaper\", \"multi-GPU pod\", \"pod ssh permission denied\", \"GLIBC not found on my pod\", \"terminate the pod\", \"how much did that pod cost\", or wants to provision, script, debug, or cost-control ephemeral cloud GPU pods for training, benchmarking, or serving."
version: 0.1.0
---

# RunPod Fast Provisioning

Rent a GPU that is ready in seconds, not minutes. The whole method is one rule: everything
installable goes into a prebaked container image, so the pod's only job at boot is to pull that
image, start `sshd`, and run the workload. Pod-side `apt install`, `pip install`, and source
compilation are all billed minutes that buy nothing.

## When to Use

- Work that is impossible or impractically slow on local hardware: needs more VRAM than the
  workstation has, needs CUDA specifically, needs N GPUs on one host.
- Benchmark grids, fine-tuning and distillation runs, short-lived model serving.
- Any repeat rental: the second pod is where a prebaked image pays for itself.

Do not rent for work that fits locally. Write the case for the pod first (what is
locally impossible, what decides when it is done), and give the workload a hard stop before
launching it.

## The core rule: prebake, never install on the pod

| Stage | Prebaked image | Stock image plus pod-side installs |
|---|---|---|
| Boot to verified environment, warm host (image cached) | 16 s | 8-10 min |
| Boot to verified environment, cold host (1.9 GB image pull) | 64 s | 8-10 min |

Measured 2026-08-12 on RunPod secure cloud; "verified" means pod created, `RUNNING`, `ssh`
accepted, and an on-pod check of GPU count, binary version, and the prebaked virtual environment
all passed. Related measurements from the same session:

- A 17 GB model file pulled from HuggingFace on the pod in **34.8 s** (about 490 MB/s) with
  `hf_transfer` preinstalled and enabled. Datacenter network beats any local upload.
- **2x A40 at $0.88/hr total** served a 30B model layer-split across both cards
  (8.2 + 8.6 GiB resident) at **31 tok/s** decode.

Always report the GPU type, GPU count, hourly price, and the date next to any number like these.
Prices and stock move, and a throughput number without its machine spec is not a result.

### Why RunPod over a managed serverless platform

Compared to managed alternatives such as Modal, RunPod runs roughly half the price for the same
card, needs minimal prep work, exposes a usable REST and GraphQL API, and sits on a fast
datacenter network. The trade-off is that the image, the lifecycle, and the cost discipline are
yours to manage, which is exactly what the templates in this skill do.

## Workflow

### Step 1: Pick the GPU and confirm it is in stock

Availability is per (GPU type, GPU count): a type with stock at 1x may have none at 2x. Query
before assuming, because a create call against an unavailable type fails with
"There are no instances currently available".

```bash
curl -s https://api.runpod.io/graphql \
  -H "Authorization: Bearer $RUNPOD_API_KEY" -H 'Content-Type: application/json' \
  -d '{"query":"{ gpuTypes { id securePrice lowestPrice(input:{gpuCount:1, secureCloud:true}) { stockStatus uninterruptablePrice } } }"}'
```

The REST API has no `gputypes` path; stock and pricing come from GraphQL only. For the pricing
ladder, the aggregate-VRAM-per-dollar comparison, and the scale ladder from one card to a
multi-node cluster, see [references/gpu-selection.md](references/gpu-selection.md).

### Step 2: Build the prebaked image

Start from [templates/Dockerfile](templates/Dockerfile). Five rules make it fast and stable:

1. **Match the base image glibc to any prebuilt binaries copied in.** Binaries built on Ubuntu
   24.04 will not run on a 22.04 base.
2. **Never compile, in the image or on the pod.** `COPY --from` a digest-pinned official prebuilt
   image instead. Compiling CUDA code under `buildx` emulation on Apple Silicon is painfully slow;
   copying binaries is instant.
3. **Prebake the dependency environment from the lockfile**
   (`uv sync --frozen --no-install-project --no-dev`), so the post-sync install on the pod is a
   warm-cache no-op. Never let a tool's own `requirements.txt` drag in a second deep-learning
   framework install; that has filled a 60 GB disk before.
4. **Preinstall `hf_transfer`**, set `HF_HUB_ENABLE_HF_TRANSFER=1`, and point `HF_HOME` at the
   container volume so weight pulls run at datacenter speed and survive into the workspace.
5. **Publish environment for `ssh`, not just for Docker.** `sshd` spawns clean login shells that
   do not inherit Dockerfile `ENV`, so register library paths with `ldconfig` and write the
   variables to `/etc/environment`.

Validate locally **before** pushing. This gate costs nothing on a laptop and would otherwise be
paid in billed pod-debugging minutes:

```bash
docker buildx build --platform linux/amd64 -f Dockerfile -t "$IMAGE" --push .
docker run --platform linux/amd64 --rm "$IMAGE" <the-binary> --version   # runtime linkage check
docker run --platform linux/amd64 --rm "$IMAGE" ls /opt/<env-dir>/.venv  # prebaked env present
```

### Step 3: Create the pod

[templates/pod-up.sh](templates/pod-up.sh) creates the pod and prints a timestamped marker for
every stage, exiting nonzero on the first failure. Four fields in the create call matter:

- `env: {"PUBLIC_KEY": "<contents of the local .pub key>"}`. Pods created through the REST API get
  **no** auto-injected `ssh` key; RunPod only injects account keys into its own templates.
- `allowedCudaVersions: ["12.6","12.7","12.8","12.9"]`, pinning away from a host pool with a
  known container-start bug (see the pitfall catalog).
- `containerDiskInGb` sized for **two copies of the model plus caches**.
- `gpuCount: N` for a single-host multi-GPU pod. Same call, same pod, N cards.

### Step 4: Sync the project and launch the job detached

[templates/pod-run.sh](templates/pod-run.sh) has three modes: `launch`, `status`, `fetch`. Long
jobs run detached under `tmux` with an explicit exit-code marker line, so the local session can
disconnect without killing the run.

Two non-obvious flags carry real scar tissue: `rsync` into a container fails `chown` (exit code
23) and kills a `set -e` script even though every file transferred, so always pass
`--no-owner --no-group`. And every launch must be **marker-checked**, never fire-and-forget: echo
an explicit `STAGE` / `READY` / `FAILED` marker and verify it. A launch that silently no-opped on a
renamed path once burned 17 idle billed minutes.

### Step 5: Fetch results, then terminate immediately

Copy results **back to the local machine** with `scp` or `rsync`. Do not stage them through a
model hub; free-plan private storage caps have failed uploads mid-chain. Then
[templates/pod-down.sh](templates/pod-down.sh), which reads the pod id recorded by `pod-up.sh`.

Terminating is part of finishing the job, not a separate cleanup task. Full detached-run,
marker, and cost protocol: [references/job-execution.md](references/job-execution.md).

## Templates

| File | Purpose |
|---|---|
| [templates/Dockerfile](templates/Dockerfile) | Prebaked CUDA image: matched glibc base, copied prebuilt binaries, locked dependency environment, `ssh`-visible environment |
| [templates/start.sh](templates/start.sh) | Entrypoint: inject `PUBLIC_KEY`, start `sshd`, print the ready marker, idle |
| [templates/pod-up.sh](templates/pod-up.sh) | Create the pod, wait for `RUNNING` and `ssh`, verify the environment, print boot-to-ready timings |
| [templates/pod-run.sh](templates/pod-run.sh) | `launch` / `status` / `fetch`: rsync the project, run detached under `tmux`, copy results back |
| [templates/pod-down.sh](templates/pod-down.sh) | Terminate the pod recorded by `pod-up.sh` |

Every template is parameterized through environment variables (`RUNPOD_API_KEY`, `POD_IMAGE`,
`POD_SSH_KEY`, `POD_NAME`, `POD_REMOTE_DIR`, `POD_JOB_CMD`, `POD_RESULTS`). Copy them into the
project, fill in the job command, and commit them next to the code they run.

## Pitfalls, in short

Each of these was hit for real. The full catalog, with symptoms and fixes, is
[references/pitfalls.md](references/pitfalls.md).

| Symptom | Cause | Fix |
|---|---|---|
| `GLIBC_2.38 not found` at runtime | Base image older than the prebuilt binaries copied in | Match the base image release to the binaries' build image; verify with `docker run` locally |
| Binary works in `docker run`, not over `ssh` | `sshd` login shells do not inherit Docker `ENV` | `ldconfig` for libraries plus `/etc/environment` for variables |
| `Permission denied (publickey)` on a fresh pod | REST-created pods get no injected key | Pass the public key as the `PUBLIC_KEY` env var at create time |
| Launch script dies at exit code 23 after a successful transfer | `rsync` cannot `chown` inside the container | `rsync --no-owner --no-group` |
| Container never starts, device errors in the log | Host pool with a container-start bug | Pin `allowedCudaVersions` away from it and build on a matching base |
| `There are no instances currently available` | Availability is per (type, count) | Query GraphQL stock, then pick another type or count |
| Disk full mid-run | A second framework install, or one model copy of headroom | One environment only; size disk for 2x model plus caches |

## Cost discipline

- Write the case for the pod before creating it: what is locally impossible, and what decides
  that the run is done.
- Give the workload itself a budget or time cap flag as the hard stop, so an overrun ends the
  work rather than the billing.
- `pod-down.sh` runs immediately after `fetch`, in the same breath.
- Record the spend where the work is tracked, with GPU type, count, hourly rate, and wall time.

## Additional Resources

- Reference: [references/pitfalls.md](references/pitfalls.md) - the full provisioning pitfall catalog with symptoms, causes, fixes, and what each one cost
- Reference: [references/gpu-selection.md](references/gpu-selection.md) - stock queries, the pricing ladder, VRAM per dollar, and the single-card to multi-node scale ladder
- Reference: [references/job-execution.md](references/job-execution.md) - detached `tmux` runs, marker discipline, result retrieval, and cost accounting
