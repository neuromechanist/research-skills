#!/usr/bin/env bash
# Container entrypoint for a prebaked cloud-GPU image.
#
# Installs the public key passed in the pod create call (REST-created pods get
# no auto-injected ssh key), starts sshd, prints a ready marker, and idles so
# the pod stays alive for interactive and detached work.
set -u

mkdir -p /root/.ssh && chmod 700 /root/.ssh
if [ -n "${PUBLIC_KEY:-}" ]; then
    echo "$PUBLIC_KEY" >> /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
else
    echo "!!! WARNING: PUBLIC_KEY not set; ssh will refuse every key" >&2
fi

/usr/sbin/sshd -p 22 || service ssh start

# Ready marker: the launcher greps for this rather than assuming a boot worked.
# Verify sshd is actually listening first; a pod that prints READY with no sshd
# wastes the launcher's whole ssh-wait window before anyone reads this log.
if pgrep -x sshd >/dev/null; then
    echo "=== POD READY $(date -u +%FT%TZ) ==="
else
    echo "!!! SSHD FAILED TO START $(date -u +%FT%TZ) -- pod is unreachable" >&2
fi
nvidia-smi -L 2>/dev/null || echo "nvidia-smi unavailable"
# Print the version of whatever binary the workload depends on, so a linkage
# failure surfaces here rather than at the start of a billed run:
#   <binary> --version 2>&1 | head -1

sleep infinity
