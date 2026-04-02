# OWASP Top 10 Checklist

Practical checklist for each OWASP Top 10 category, tailored to common project patterns.

## A01: Broken Access Control

- [ ] Every API endpoint checks authorization (not just authentication)
- [ ] Server-side enforcement, not client-side only
- [ ] Deny by default; explicit allow-list for permissions
- [ ] No direct object references without ownership check
- [ ] Rate limiting on sensitive endpoints
- [ ] CORS restricted to known origins

## A02: Cryptographic Failures

- [ ] Passwords hashed with bcrypt or argon2 (not MD5/SHA1/SHA256)
- [ ] Sensitive data encrypted at rest (database, file storage)
- [ ] TLS 1.2+ for all network communication
- [ ] No hardcoded encryption keys or salts
- [ ] Secrets not logged or included in error messages

## A03: Injection

- [ ] SQL: parameterized queries or ORM (no string concatenation)
- [ ] OS commands: no `shell=True`, no `os.system()` with user input
- [ ] LDAP/NoSQL/XPath: input validation on all query parameters
- [ ] Template: no raw user input in template rendering

## A04: Insecure Design

- [ ] Threat modeling done for new features
- [ ] Business logic limits enforced server-side
- [ ] Fail-safe defaults (deny on error, not allow)
- [ ] Segregation of duties where applicable

## A05: Security Misconfiguration

- [ ] Debug mode disabled in production
- [ ] Default credentials changed
- [ ] Unnecessary features/ports/services disabled
- [ ] Error messages don't expose stack traces
- [ ] Security headers set (CSP, HSTS, X-Frame-Options)
- [ ] Directory listing disabled

## A06: Vulnerable and Outdated Components

- [ ] Dependencies audited regularly (`pip-audit`, `npm audit`)
- [ ] No components with known vulnerabilities
- [ ] Components from official sources only
- [ ] Unused dependencies removed

## A07: Identification and Authentication Failures

- [ ] Multi-factor authentication available for sensitive operations
- [ ] Session tokens regenerated after login
- [ ] Session timeout configured
- [ ] Account lockout after failed attempts
- [ ] Password complexity requirements enforced

## A08: Software and Data Integrity Failures

- [ ] CI/CD pipeline secured (no untrusted code execution)
- [ ] Dependencies verified (lockfiles committed)
- [ ] Third-party GitHub Actions pinned to SHA
- [ ] Serialization input validated

## A09: Security Logging and Monitoring Failures

- [ ] Authentication events logged (success and failure)
- [ ] Access control failures logged
- [ ] Input validation failures logged
- [ ] Logs don't contain sensitive data
- [ ] Log tampering prevented

## A10: Server-Side Request Forgery (SSRF)

- [ ] URL validation on server-side requests
- [ ] Allow-list for external service destinations
- [ ] No raw URL forwarding from user input
- [ ] Internal network access restricted from user-facing services
