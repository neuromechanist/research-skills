# Docker Security Best Practices

## Non-root User

Always run containers as a non-root user in production:

```dockerfile
# Create user in build stage
RUN addgroup --system app && adduser --system --ingroup app app

# Switch to non-root user
USER app
```

## Secrets Management

Never pass secrets through:
- `ARG` instructions (visible in image history)
- `ENV` instructions (persisted in image layers)
- `COPY` of .env files

Instead:
- Use Docker secrets (Swarm/Compose)
- Use environment variables at runtime (`docker run -e`)
- Use secret mount in BuildKit:
```dockerfile
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    some-command --key "$API_KEY"
```

## Image Scanning

Scan images for vulnerabilities before deployment:

```bash
# Using Docker Scout
docker scout cves myimage:latest

# Using Trivy
trivy image myimage:latest

# Using Grype
grype myimage:latest
```

## Read-only Filesystem

For production, use read-only root filesystem where possible:

```yaml
# docker-compose.yml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /app/cache
```

## Network Security

- Don't expose unnecessary ports
- Use internal networks for service-to-service communication
- Never use `--network host` in production

```yaml
services:
  app:
    networks:
      - frontend
  db:
    networks:
      - backend  # Not accessible from frontend
```

## Base Image Pinning

Pin to specific digests for reproducibility:

```dockerfile
# Pin to specific version, not 'latest'
FROM python:3.12.3-slim@sha256:abc123...

# Or at minimum, pin to minor version
FROM python:3.12-slim
```
