#!/usr/bin/env bash
# Terminate a pod (default: the one recorded by pod-up.sh).
#
# Termination is the last step of the job, not a separate cleanup task. Run it
# in the same breath as `pod-run.sh fetch`, once the results are verified
# locally.
#
# Usage:
#   ./pod-down.sh [pod-id]
set -euo pipefail

KEY="${RUNPOD_API_KEY:?set RUNPOD_API_KEY}"
POD_ID="${1:-$(cat "$(dirname "$0")/.last-pod-id" 2>/dev/null || true)}"
[ -n "$POD_ID" ] || { echo "usage: pod-down.sh <pod-id>" >&2; exit 2; }

curl -sf -X DELETE -H "Authorization: Bearer $KEY" \
    "https://rest.runpod.io/v1/pods/$POD_ID" \
    && echo "terminated $POD_ID"

# Confirm nothing else is left billing before closing out the session:
#   curl -sf -H "Authorization: Bearer $RUNPOD_API_KEY" https://rest.runpod.io/v1/pods
