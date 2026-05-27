# Architecture Decision Records

Use this directory for Architecture Decision Records (ADRs): short, dated notes
that explain important project choices and their consequences.

## Naming

Name each record with a numeric prefix and short title:

```text
0001-use-postgres-for-events.md
0002-keep-worker-state-in-redis.md
```

Keep numbers monotonic. Do not renumber existing records after they are merged.

## Workflow

1. Copy `0000-template.md`.
2. Rename it to the next `NNNN-short-title.md`.
3. Fill in Context, Decision, Consequences, Alternatives, and Receipts.
4. Link relevant issues, PRs, docs, or test output under Receipts.

ADRs should be concise enough to read quickly but concrete enough that a future
agent or maintainer can understand why the decision exists.
