# Security Audit Procedure

The reviewer's contract on every host: the bundled `security-audit` agent, a configured Codex or Copilot agent, or the session itself when no agent is available.

## Scope and independence

Audit the repository or the paths the caller names, from a fresh context.
Judge only what is in the tree, its git history, and its configuration; do not accept the author's account of why a pattern is safe.
A finding needs a file and line (or a config key), the evidence, and a concrete fix.
Never print a secret value in the report: give the file, line, and secret type, and mask everything after the first four characters.

This audit is read-only. Do not rotate credentials, edit files, or run fixes; report them.

## Audit checklist

### 1. Credential and Secret Scanning

Check for exposed secrets in the codebase:

```bash
# Check for common secret patterns in tracked files
git grep -n -i -E '(api_key|apikey|secret|password|token|credential|private_key)\s*[:=]' -- ':!*.md' ':!*.lock'

# Check for .env files tracked in git
git ls-files | grep -i '\.env'

# Check .gitignore covers sensitive files
for f in .env .env.local credentials.json secrets.yaml; do
  git check-ignore "$f" 2>/dev/null || echo "WARNING: $f not in .gitignore"
done
```

Files that must never be committed:
- `.env`, `.env.*` (environment variables)
- `credentials.json`, `service-account.json` (cloud credentials)
- `*.pem`, `*.key` (private keys)
- `*.p12`, `*.pfx` (certificates with private keys)

### 2. Dependency Vulnerability Scan

**Python:**
```bash
uv run pip-audit
```

**JavaScript/TypeScript:**
```bash
bun pm audit
# or check with npm for broader database
npm audit --omit=dev
```

**Go:**
```bash
govulncheck ./...
```

When the dispatcher runs the `dependency-auditor` agent alongside this audit, skip the package scans below and cite its report instead; run them here only when no dependency report exists.

Review results against the severity rubric (shared with the
dependency-auditor agent):

- Critical: exploitable now or actively exploited (leaked live credential,
  known-exploited CVE in a reachable path). Must fix before release; blocks
  release-prep.
- High: known vulnerability with a plausible attack path. Fix before the next
  release.
- Medium: vulnerability with mitigating factors, or a major-version lag on a
  security-relevant package. Fix within the sprint.
- Low: outdated without known vulnerabilities; license concerns to review.
  Track in backlog.

### 3. Code Vulnerability Patterns

Scan for common vulnerability patterns:

**SQL Injection:**
```bash
# Look for string interpolation in SQL
grep -rn 'f".*SELECT\|f".*INSERT\|f".*UPDATE\|f".*DELETE' --include='*.py'
grep -rn "format.*SELECT\|format.*INSERT" --include='*.py'
```

**Command Injection:**
```bash
# Look for shell=True or unsanitized subprocess calls
grep -rn 'shell=True\|os\.system\|subprocess\.call.*shell' --include='*.py'
grep -rn 'exec(\|eval(' --include='*.py' --include='*.js' --include='*.ts'
```

**XSS (Cross-Site Scripting):**
```bash
# Look for dangerouslySetInnerHTML or unescaped output
grep -rn 'dangerouslySetInnerHTML\|innerHTML\s*=' --include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.js'
```

**Path Traversal:**
```bash
grep -rn 'open(.*\+\|os\.path\.join.*input\|req\.\(params\|query\|body\)' --include='*.py' --include='*.js'
```

### 4. Authentication and Authorization

Review:
- [ ] Authentication endpoints use constant-time comparison for secrets
- [ ] Session tokens have appropriate expiration
- [ ] Cross-Origin Resource Sharing (CORS) configuration is restrictive (not `*` in production)
- [ ] Rate limiting on auth endpoints
- [ ] Password hashing uses bcrypt/argon2 (not MD5/SHA1)

### 5. Configuration Hardening

- [ ] Debug mode disabled in production configs
- [ ] HTTPS enforced (HTTP Strict Transport Security (HSTS) headers)
- [ ] Security headers present (Content Security Policy (CSP), X-Frame-Options, X-Content-Type-Options)
- [ ] Error messages do not leak stack traces in production
- [ ] Logging does not include sensitive data (passwords, tokens)

### 6. Docker Security (if applicable)

- [ ] Non-root user in Dockerfile
- [ ] Base image is pinned to specific version (not `latest`)
- [ ] No secrets in Docker build args or layers
- [ ] Health checks configured
- [ ] Read-only filesystem where possible

### 7. Continuous Integration and Delivery (CI/CD) Security

- [ ] Secrets stored in GitHub Secrets (not in workflow files)
- [ ] Third-party actions pinned to SHA (not tags)
- [ ] Minimal permissions in workflow `permissions:` block
- [ ] No `pull_request_target` with `actions/checkout` of PR head

## Output Format

Present findings as a prioritized list:

```
## Security Audit Results

### Critical (must fix)
1. [CRED] API key found in src/config.py:42 - move to environment variable
2. [DEP] lodash 4.17.20 has prototype pollution (CVE-2021-23337)

### High (fix before release)
3. [CODE] SQL injection risk in src/db.py:88 - use parameterized queries

### Medium (fix within sprint)
4. [CONFIG] CORS allows * origin in production config

### Low (backlog)
5. [STYLE] Error responses include stack traces in non-debug mode

### Passed
- [x] No .env files in git
- [x] Docker runs as non-root
- [x] Dependencies up to date
```

## Security references

- [owasp-top-10.md](owasp-top-10.md): Open Worldwide Application Security Project (OWASP) Top 10 checklist with project-specific examples; apply the categories that match the project type.
- [secret-management.md](secret-management.md): how secrets should be stored and rotated; use it to write the fix for each credential finding.
