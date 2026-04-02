# Secret Management Guide

## Environment-based Configuration

### Local Development
Use `.env` files (never committed):

```bash
# .env (gitignored)
DATABASE_URL=postgresql://localhost/mydb
API_KEY=dev-key-here
```

Load with:
```python
# Python
from dotenv import load_dotenv
load_dotenv()
```

```typescript
// TypeScript (Bun has built-in .env support)
const apiKey = process.env.API_KEY;
```

### CI/CD (GitHub Actions)
Store in GitHub Settings > Secrets:

```yaml
steps:
  - run: run-tests
    env:
      API_KEY: ${{ secrets.API_KEY }}
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Production
Use platform-specific secret managers:
- **AWS:** Secrets Manager or SSM Parameter Store
- **GCP:** Secret Manager
- **Azure:** Key Vault
- **Docker Swarm:** Docker Secrets
- **Kubernetes:** Kubernetes Secrets (with encryption at rest)

## .gitignore Patterns

Always include these patterns:

```gitignore
# Environment files
.env
.env.*
!.env.example

# Credentials
credentials.json
service-account*.json
*.pem
*.key
*.p12
*.pfx

# IDE secrets
.idea/dataSources.xml

# macOS
.DS_Store
```

## .env.example

Provide a template without real values:

```bash
# .env.example (committed to repo)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
API_KEY=your-api-key-here
SECRET_KEY=generate-with-openssl-rand-hex-32
```

## Rotation

- Rotate secrets on a schedule (90 days recommended)
- Rotate immediately if exposure is suspected
- Use short-lived tokens where possible (OAuth2, JWT with short expiry)
- Never embed long-lived secrets in Docker images or CI artifacts

## Validation

Check for secret exposure:

```bash
# Search for potential secrets in tracked files
git grep -n -i -E '(api_key|apikey|secret|password|token|credential|private_key)\s*[:=]\s*["\x27][^"\x27]{8,}' -- ':!*.md' ':!*.lock' ':!*.example'

# Check git history for leaked secrets
git log --all -p -S 'API_KEY' -- ':!*.md'
```
