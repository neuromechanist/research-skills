#!/usr/bin/env bash
# Create a RunPod secure-cloud pod from a prebaked image and measure
# boot-to-ready. Prints a timestamped marker per stage and exits nonzero on the
# first failure, so a silent no-op can never look like a successful boot.
#
# Usage:
#   export RUNPOD_API_KEY="$(security find-generic-password -s <keychain-item> -w)"
#   export POD_IMAGE=<registry>/<user>/<project>-runpod:v1
#   ./pod-up.sh [--gpus N] [--gpu-type "NVIDIA A40"] [--disk 80]
#
# Reference boot-to-ready with a prebaked image: 16 s on a warm host, 64 s on a
# cold host (1.9 GB pull), against 8-10 min for pod-side installs.
set -euo pipefail

KEY="${RUNPOD_API_KEY:?set RUNPOD_API_KEY}"
IMAGE="${POD_IMAGE:?set POD_IMAGE to the pushed image reference}"
# REST-created pods get NO auto-injected ssh key: RunPod only injects account
# keys into its own templates. Pass the public key explicitly at create time.
SSH_KEY="${POD_SSH_KEY:-$HOME/.ssh/id_runpod}"
PUBKEY="$(cat "$SSH_KEY.pub")"
NAME="${POD_NAME:-gpu-pod}"
API=https://rest.runpod.io/v1

GPUS="${POD_GPUS:-1}"
GPU_TYPE="${POD_GPU_TYPE:-NVIDIA A40}"
# Size for two copies of the model plus caches and outputs.
DISK_GB="${POD_DISK_GB:-80}"
# Pin away from any host pool with a known container-start bug, and keep the
# image's CUDA base inside this range.
CUDA_VERSIONS='["12.6", "12.7", "12.8", "12.9"]'

while [ $# -gt 0 ]; do
    case "$1" in
        --gpus) GPUS="$2"; shift 2 ;;
        --gpu-type) GPU_TYPE="$2"; shift 2 ;;
        --disk) DISK_GB="$2"; shift 2 ;;
        --image) IMAGE="$2"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

say() { echo "=== $(date -u +%FT%TZ) $*"; }
api() { curl -sSf -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' "$@"; }
ssh_pod() { ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=5 -p "$PORT" "root@$IP" "$@"; }

T0=$(date +%s)
say "STAGE: create pod (${GPUS}x ${GPU_TYPE}, ${DISK_GB} GB disk, image ${IMAGE})"
PAYLOAD=$(NAME="$NAME" IMAGE="$IMAGE" GPUS="$GPUS" GPU_TYPE="$GPU_TYPE" \
          DISK_GB="$DISK_GB" CUDA_VERSIONS="$CUDA_VERSIONS" PUBKEY="$PUBKEY" python3 - <<'PY'
import json, os
print(json.dumps({
    "name": os.environ["NAME"],
    "imageName": os.environ["IMAGE"],
    "cloudType": "SECURE",
    "gpuTypeIds": [os.environ["GPU_TYPE"]],
    "gpuCount": int(os.environ["GPUS"]),
    "containerDiskInGb": int(os.environ["DISK_GB"]),
    "ports": ["22/tcp"],
    "allowedCudaVersions": json.loads(os.environ["CUDA_VERSIONS"]),
    "env": {"PUBLIC_KEY": os.environ["PUBKEY"]},
}))
PY
)
# A create failure here is usually "There are no instances currently available",
# which is per (gpu type, gpu count): query GraphQL stock and pick another.
POD=$(api -X POST "$API/pods" -d "$PAYLOAD") \
    || { echo "!!! STAGE FAILED: create (check GraphQL stock for ${GPUS}x ${GPU_TYPE})"; exit 1; }
POD_ID=$(echo "$POD" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])') \
    || { echo "!!! STAGE FAILED: create response had no id field:" >&2; echo "$POD" >&2; exit 1; }
echo "$POD_ID" > "$(dirname "$0")/.last-pod-id"
say "pod id: $POD_ID"

say "STAGE: wait RUNNING"
STATUS=""
for _ in $(seq 1 120); do
    # Guard the poll: one transient API failure must cost one retry, not the
    # whole loop (a bare assignment failing under set -e aborts the script).
    if ! STATUS=$(api "$API/pods/$POD_ID" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("desiredStatus","?"))' 2>/dev/null); then
        sleep 5; continue
    fi
    [ "$STATUS" = "RUNNING" ] && break
    sleep 5
done
[ "$STATUS" = "RUNNING" ] || { echo "!!! STAGE FAILED: not RUNNING after 10m (last status: ${STATUS:-none})"; exit 1; }
T_RUN=$(date +%s); say "RUNNING after $((T_RUN - T0))s"

say "STAGE: wait ssh (public ip + mapped port)"
# Probe stderr goes to a log, not /dev/null: when the final check fails, the
# real ssh error (permission denied vs refused vs timeout) is the diagnosis.
PROBE_LOG="$(dirname "$0")/.ssh-probe.log"
: > "$PROBE_LOG"
IP=""; PORT=""
for _ in $(seq 1 120); do
    read -r IP PORT <<<"$(api "$API/pods/$POD_ID" | python3 -c '
import json, sys
p = json.load(sys.stdin)
print(p.get("publicIp") or "", (p.get("portMappings") or {}).get("22", ""))')"
    [ -n "$IP" ] && [ -n "$PORT" ] && ssh_pod true 2>>"$PROBE_LOG" && break
    sleep 5
done
ssh_pod true 2>>"$PROBE_LOG" || {
    echo "!!! STAGE FAILED: ssh not reachable (is PUBLIC_KEY set in the create call?)"
    echo "    last probe errors:"; tail -3 "$PROBE_LOG"
    exit 1
}
T_SSH=$(date +%s); say "ssh ready after $((T_SSH - T0))s (root@$IP -p $PORT)"

# Verify over ssh, not over docker run: sshd login shells do not inherit the
# image's ENV, so this is the check that catches a missing ldconfig or a
# missing /etc/environment entry.
say "STAGE: verify environment"
ssh_pod '
    set -e
    echo "gpus: $(nvidia-smi -L | wc -l)"; nvidia-smi -L
    uv --version
    ls /opt/project-env/.venv >/dev/null && echo "prebaked venv: ok"
    # <binary> --version 2>&1 | head -1
' || { echo "!!! STAGE FAILED: environment verify"; exit 1; }
T_ENV=$(date +%s)

say "BOOT-TO-READY: create->running $((T_RUN - T0))s, ->ssh $((T_SSH - T0))s, ->verified $((T_ENV - T0))s"
say "COMPLETE (pod $POD_ID is running and billing; ./pod-down.sh to terminate)"
echo
echo "export POD_HOST=root@$IP POD_PORT=$PORT"
