# Prebaked cloud-GPU image template.
#
# Goal: the pod does nothing at boot except pull this image, start sshd, and run
# the job. Every install, every download, and every compile happens here, once.
#
# Build and push (from the project root, amd64 even on Apple Silicon):
#   docker buildx build --platform linux/amd64 \
#     -f <path>/Dockerfile -t <registry>/<user>/<project>-runpod:v1 --push .
#
# Validate locally BEFORE pushing; this gate is free, the pod-side one is billed:
#   docker run --platform linux/amd64 --rm <image> <binary> --version
#   docker run --platform linux/amd64 --rm <image> ls /opt/project-env/.venv

# ---------------------------------------------------------------------------
# 1. Prebuilt binaries, copied not compiled.
#
# Pin by digest so the image is reproducible; re-resolve when the upstream tag
# moves:  docker manifest inspect <registry>/<project>:<tag>
#
# Compiling CUDA code under buildx qemu emulation on Apple Silicon is painfully
# slow. Copying a prebuilt artifact is instant.
# ---------------------------------------------------------------------------
ARG PREBUILT_IMAGE=<registry>/<project>@sha256:<digest>
FROM ${PREBUILT_IMAGE} AS prebuilt

# ---------------------------------------------------------------------------
# 2. Base image.
#
# Two constraints:
#   - glibc must match the prebuilt binaries above. Upstream CUDA server images
#     are commonly built on Ubuntu 24.04 (glibc 2.38+, GLIBCXX 3.4.32); copying
#     those onto a 22.04 base (glibc 2.35) fails at runtime with
#     "GLIBC_2.38 not found".
#   - the CUDA minor version must run on every host left by the create call's
#     allowedCudaVersions filter. A 12.6 base covers a 12.6-12.9 filter.
# ---------------------------------------------------------------------------
FROM nvidia/cuda:12.6.3-runtime-ubuntu24.04

# sshd for pod access, rsync for project sync, tmux for detached runs.
# Add any runtime shared libraries the prebuilt binaries need (libgomp1 is a
# common one for CPU-side kernels).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openssh-server rsync curl ca-certificates tmux libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd

COPY --from=prebuilt /app /opt/toolchain
ENV PATH=/opt/toolchain:$PATH \
    LD_LIBRARY_PATH=/opt/toolchain

# ---------------------------------------------------------------------------
# 3. Dependency environment, prebaked from the lockfile.
#
# --no-install-project keeps the project source out of the image (it arrives by
# rsync at run time), so the on-pod `uv sync --frozen --no-dev` after the sync
# is a warm-cache no-op.
#
# Audit anything added here for a transitive deep-learning framework install: a
# tool's own requirements.txt dragging in a second framework copy has filled a
# 60 GB disk before.
# ---------------------------------------------------------------------------
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    UV_LINK_MODE=copy
RUN uv python install 3.12
COPY pyproject.toml uv.lock /opt/project-env/
RUN cd /opt/project-env && uv sync --frozen --no-install-project --no-dev \
    && uv pip install hf_transfer

# Fast weight pulls onto the container volume (~490 MB/s measured; a 17 GB file
# in 34.8 s). HF_HOME must point at the volume, not at a layer.
ENV HF_HUB_ENABLE_HF_TRANSFER=1 \
    HF_HOME=/workspace/hf

# ---------------------------------------------------------------------------
# 4. Publish the environment for ssh, not just for Docker.
#
# sshd spawns clean login environments, so nothing set with ENV above survives
# into an ssh session. ldconfig makes the libraries resolvable process-wide;
# /etc/environment (read by sshd through PAM) carries the variables across.
# ---------------------------------------------------------------------------
RUN echo /opt/toolchain > /etc/ld.so.conf.d/toolchain.conf && ldconfig \
    && printf '%s\n' \
        'PATH=/opt/toolchain:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' \
        'HF_HUB_ENABLE_HF_TRANSFER=1' \
        'HF_HOME=/workspace/hf' \
        >> /etc/environment

COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
