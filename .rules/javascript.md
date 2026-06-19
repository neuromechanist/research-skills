# JavaScript And TypeScript

- Use Bun for JavaScript and TypeScript dependency management, scripts, tests,
  and one-off execution.
- Do not introduce `npm`, `pnpm`, or `yarn` workflows unless an upstream tool
  requires them and the reason is documented in the change.
- Prefer:
  - `bun install`
  - `bun add <package>`
  - `bun add -d <package>`
  - `bun test`
  - `bun run <script>`
  - `bunx <tool>` for on-the-fly execution
- Use Biome for formatting and linting when a JS/TS package needs a formatter or
  linter, unless the package already has a different checked-in standard.
- Keep `node_modules/`, build outputs, caches, and generated bundles out of git
  unless the repo explicitly treats them as source artifacts.
