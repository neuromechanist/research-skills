---
name: docker-packaging
description: "This skill should be used when the user says \"create Dockerfile\", \"dockerize project\", \"Docker packaging\", \"container setup\", \"multi-stage build\", \"Docker Compose\", \"containerize application\", \"create docker-compose.yml\", \"create .dockerignore\", \"optimize Docker image\", or wants to containerize their project or create Docker configurations."
version: 0.1.0
---

# Docker Packaging

Generate Docker configurations following project conventions. Supports multi-stage builds, uv-based Python images, and health checks.

## When to Use

- Containerizing a new project
- Optimizing existing Docker images
- Setting up Docker Compose for development
- Adding health checks to containers
- Creating production-ready Docker configurations

## Python Project Dockerfile

Multi-stage build with uv for dependency management:

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /app /app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "app"]
```

Key conventions:
- Always multi-stage (build vs runtime)
- Use uv, never pip
- Copy `pyproject.toml` and `uv.lock` first for layer caching
- Slim base images
- Non-root user for production
- Health checks included

## TypeScript/Bun Project Dockerfile

```dockerfile
FROM oven/bun:1 AS builder

WORKDIR /app
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

COPY . .
RUN bun run build

FROM oven/bun:1-slim AS runtime

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["bun", "run", "start"]
```

## Go Project Dockerfile

```dockerfile
FROM golang:1.22-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server ./cmd/server

FROM scratch AS runtime

COPY --from=builder /app/server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

EXPOSE 8080
ENTRYPOINT ["/server"]
```

## Docker Compose (Development)

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=1
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: dev-only
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

## .dockerignore

Always create alongside Dockerfile:

```
.git
.github
.context
.rules
.claude
__pycache__
*.pyc
.venv
node_modules
.env
*.md
!README.md
```

## Workflow

### Step 1: Detect stack and entry point

Identify the application type, main entry point, exposed ports, and any services it depends on.

### Step 2: Generate Dockerfile

Use the appropriate template. Add security hardening for production (non-root user, read-only filesystem).

### Step 3: Generate .dockerignore

Exclude development files, secrets, and unnecessary build context.

### Step 4: Generate docker-compose.yml (if needed)

Add dependent services (databases, caches, message queues) with health checks.

### Step 5: Test

```bash
docker build -t app:test .
docker run --rm app:test
```

## Additional Resources

- Reference: [references/docker-security.md](references/docker-security.md) - Non-root users, secrets management, image scanning
- Reference: [references/docker-optimization.md](references/docker-optimization.md) - Layer caching, image size reduction, BuildKit
