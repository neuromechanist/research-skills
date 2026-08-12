# ML Training

The `ml-training` plugin covers machine-learning work that has to leave the local machine: renting cloud GPUs for training, distillation, benchmark grids, and short-lived model serving. Its first skill, `runpod`, captures a battle-tested provisioning workflow whose whole premise is that a pod should be ready in seconds rather than minutes.

## Prebake the image, do nothing on the pod

Stock GPU images arrive empty, so the usual pattern spends 8 to 10 billed minutes on `apt`, `pip`, and sometimes compilation before any real work starts, once per pod. The `runpod` skill moves all of that into a container image built once on a laptop, so the pod's only boot-time job is to pull the image, start `sshd`, and run the workload.

Measured 2026-08-12 on RunPod secure cloud, where "ready" means created, `RUNNING`, `ssh` accepted, and an on-pod check of GPU count, binary version, and prebaked environment all passed:

| Boot to verified environment | Prebaked image | Stock image plus pod-side installs |
|---|---|---|
| Warm host (image cached) | 16 s | 8-10 min |
| Cold host (1.9 GB image pull) | 64 s | 8-10 min |

Weights are pulled on the pod rather than uploaded: a 17 GB model file arrived in 34.8 s (about 490 MB/s) with `hf_transfer` preinstalled and enabled.

## Buy the constraint, not the flagship

Most evaluation work is bound by aggregate VRAM rather than tensor throughput, and the price ladder is not monotonic in VRAM. In the prices observed on 2026-08-12, 2x A100-SXM ($3.18/hr, 160 GB aggregate) undercut a single H100 ($3.29/hr, 80 GB) on both price and memory, while an A40 at $0.44/hr per 48 GB was the cheapest way to buy VRAM for accuracy-only grids. A 2x A40 pod at $0.88/hr served a 30B model layer-split across both cards at 31 tok/s decode.

Availability is per (GPU type, GPU count), so a type with 1x stock may have no 2x capacity at all; the skill queries GraphQL for stock before planning a run around a card, because the REST API exposes no equivalent path.

Shape matters as much as size. An evaluation grid is embarrassingly parallel, so N independent single-GPU pods burn the same GPU-hours as one pod and finish in 1/N of the wall-clock time; a multi-node instant cluster is distributed-training infrastructure and the wrong instrument for independent cells. The fan-out reference covers slicing by estimated duration rather than item count (a long-context bin can run 10x a short one), queueing leftover slices onto whichever pods stock allowed, verifying one pod end to end before replicating the launch, and shrinking the roughly 4-minute per-pod startup to about 90 seconds by baking the evaluation datasets and every dependency group into the image.

## Never hit the same pitfall twice

The skill ships a pitfall catalog where every entry was hit on a real, billed pod: a base image whose glibc did not match the prebuilt binaries copied into it, `ssh` sessions that do not inherit Docker `ENV`, REST-created pods that get no injected `ssh` key, `rsync` failing `chown` inside a container and killing a `set -e` launch script, a host pool with a fleet-wide container-start bug, and a fire-and-forget launch that silently no-opped and billed 17 idle minutes. Fleet work adds three more, each of which impersonates a different bug: `ssh` inside a loop eats the loop's stdin so only the first pod launches while the rest boot and bill, zsh does not word-split an unquoted variable the way bash does so a generated command chain collapses into one malformed command, and `pkill -f` matches full command lines including the `ssh` session running it, killing that session mid-command and reading as network flakiness. Each entry pairs the symptom with the fix, and the templates have the fixes already applied.

## Skills

- **runpod**: fast, cost-controlled cloud GPU provisioning: prebaked images that boot in seconds, pod lifecycle scripts (`pod-up`, `pod-run`, `pod-down`), GPU selection and pricing ladders, detached job execution with marker checks, fanning a grid out across a fleet of independent pods, and the full provisioning pitfall catalog

## Try it

```
"Spin up a RunPod pod with 2 GPUs and run this benchmark grid on it"
"My pod spends 10 minutes installing before every run, fix that"
"Which GPU should I rent for a 30B model, 2x A100 or 1x H100?"
"Fan this benchmark grid out across 6 pods and merge the results"
"The pod boots but ssh says permission denied"
"Fetch the results and terminate the pod"
```

## Learn more

There is no dedicated course week for `ml-training` yet. The [Agentic Research Course](https://courses.osc.earth/agentic-research/) week 3, "Project Management with AI," covers the surrounding workflow discipline (branches, issues, and tracked spend) that the cost-control parts of this plugin assume.
