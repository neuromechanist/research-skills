# Testing

- Test real behavior. Do not add mocks, stub services, or fake datasets unless
  the user explicitly approves that tradeoff for a specific case.
- Prefer focused integration tests, filesystem-backed checks, manifest
  validation, and real parser/format validation over assumption-heavy unit tests.
- If real verification is not possible, state what is missing and do not create a
  false-confidence test.
- For Python, run tests through `uv run`.
- For JavaScript and TypeScript, run tests through `bun test` or the package's
  existing Bun script.
- For marketplace or manifest changes, validate JSON/TOML structure and run the
  marketplace integrity tests.
- Report tests that were not run and why.
