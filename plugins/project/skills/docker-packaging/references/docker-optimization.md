# Docker Image Optimization

## Layer Caching

Order Dockerfile instructions from least to most frequently changing:

```dockerfile
# 1. Base image (rarely changes)
FROM python:3.12-slim

# 2. System dependencies (changes occasionally)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev && rm -rf /var/lib/apt/lists/*

# 3. Application dependencies (changes with lockfile updates)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 4. Application code (changes frequently)
COPY . .
RUN uv sync --frozen --no-dev
```

## Image Size Reduction

### Use slim/alpine base images
- `python:3.12-slim` (~50MB) vs `python:3.12` (~350MB)
- `node:22-alpine` (~50MB) vs `node:22` (~350MB)

### Multi-stage builds
Keep build tools out of the runtime image:
```dockerfile
FROM python:3.12-slim AS builder
# Install build dependencies, compile, etc.

FROM python:3.12-slim AS runtime
# Only copy the built artifacts
COPY --from=builder /app/.venv /app/.venv
```

### Clean up in the same layer
```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    make build && \
    apt-get purge -y build-essential && \
    rm -rf /var/lib/apt/lists/*
```

## BuildKit Features

Enable BuildKit for faster builds:
```bash
DOCKER_BUILDKIT=1 docker build .
```

### Parallel stages
BuildKit builds independent stages in parallel automatically.

### Cache mounts
```dockerfile
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
```

## Health Checks

Always include health checks:

```dockerfile
# HTTP endpoint check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# TCP port check (if no HTTP endpoint)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD nc -z localhost 8000 || exit 1

# Process check (minimal)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD pgrep -x python || exit 1
```
