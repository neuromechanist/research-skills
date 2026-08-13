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

# This is the one script whose whole job is stopping the meter: a silent
# failure here (stale id, rotated key, network blip) costs money by the hour,
# so the failure branch is explicit and loud.
if curl -sSf -X DELETE -H "Authorization: Bearer $KEY" \
    "https://rest.runpod.io/v1/pods/$POD_ID"; then
    echo "terminated $POD_ID"
else
    echo "!!! TERMINATE FAILED for $POD_ID -- the pod may still be billing." >&2
    echo "    Check manually: curl -sS -H 'Authorization: Bearer \$RUNPOD_API_KEY' https://rest.runpod.io/v1/pods" >&2
    exit 1
fi

# Confirm nothing else is left billing before closing out the session.
LEFT=$(curl -sS -H "Authorization: Bearer $KEY" https://rest.runpod.io/v1/pods \
    | python3 -c 'import json,sys; pods=json.load(sys.stdin); print(len(pods))' 2>/dev/null) \
    || { echo "could not list remaining pods; check the dashboard" >&2; exit 0; }
echo "pods still running on the account: $LEFT"
