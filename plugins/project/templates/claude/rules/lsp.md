# Code Intelligence with Language Servers

## When to Use
Use a Language Server Protocol (LSP) server when a task needs symbol-level facts that text search cannot give reliably:
go-to-definition, every reference before a rename or signature change, call hierarchies, inferred types, or diagnostics right after an edit.
For plain lookups, `rg` (or the agent's search tool) plus reading the file is enough;
do not set up a language server for those.

Do not add a third-party code-intelligence Model Context Protocol (MCP) server (such as Serena) as a project dependency.

## Claude Code: Official LSP Plugins
Anthropic publishes one LSP plugin per language in the official `claude-plugins-official` marketplace (`anthropics/claude-plugins-official`).
Each plugin connects a language server to Claude Code's built-in `LSP` tool;
the server binary itself must be on the `PATH` that Claude Code was started with.

| Language | Plugin | Server binary | Install the binary |
|---|---|---|---|
| Python | `pyright-lsp` | `pyright-langserver` | `uv tool install pyright` (the wrapper fetches Node.js on first run if none is installed) |
| TypeScript / JavaScript | `typescript-lsp` | `typescript-language-server` | `bun add -g typescript-language-server typescript` |
| Rust | `rust-analyzer-lsp` | `rust-analyzer` | `rustup component add rust-analyzer` |
| Go | `gopls-lsp` | `gopls` | `go install golang.org/x/tools/gopls@latest` |
| C / C++ | `clangd-lsp` | `clangd` | system package; Homebrew `llvm` is keg-only, so add `$(brew --prefix llvm)/bin` to `PATH` |
| Swift | `swift-lsp` | `sourcekit-lsp` | ships with Xcode or the Swift toolchain |

Other official plugins: `csharp-lsp`, `jdtls-lsp`, `kotlin-lsp`, `lua-lsp`, `php-lsp`, `ruby-lsp`.
For these, read the plugin's README for its server binary and install command;
ask rather than guess.
Install binaries with the project's own tooling (UV for Python tools, Bun for JavaScript tools), never `pip`, `npm`, or conda.
`uv tool install` puts binaries in `~/.local/bin` and `bun add -g` in `~/.bun/bin`;
if `command -v <binary>` fails after an install, that directory is missing from `PATH` (`uv tool update-shell` fixes it for UV).

## Procedure
1. Check whether the `LSP` tool is available in the session (including the deferred-tool list).
   If it is, use it.
   If an LSP call errors or reports no server for the file type, tell the user exactly what failed and go to step 2;
   do not retry silently or fall back unannounced.
2. Check what is missing:
   the plugin (`claude plugin list`; if the `claude-plugins-official` marketplace is absent, it is added with `/plugin marketplace add anthropics/claude-plugins-official`),
   the server binary (`command -v <binary>`),
   or both.
   If neither check can run on this host, treat both as unknown.
3. Never install silently.
   Ask the user, naming the missing pieces, for example:
   "Symbol-level navigation would help here.
   Install `pyright-lsp@claude-plugins-official` (`/plugin install pyright-lsp@claude-plugins-official`) and the server (`uv tool install pyright`)?"
   After an install, run `/reload-plugins` or start a new session before the `LSP` tool appears;
   until then, continue with step 4.
   If you cannot ask (a subagent, a headless `claude -p` run, or another non-interactive worker), do not install;
   use step 4 and report `LSP unavailable: <plugin or binary> missing`.
4. Without a language server, use word-bounded `rg` searches plus the language's own checker
   (`ty` for Python types and `ruff` for lint, `bunx --package typescript tsc --noEmit`, `cargo check`, `go vet`),
   and state that reference results are text-based rather than semantic.

## Empty Results
A language server can return no references while it is still indexing.
Before a rename, signature change, or deletion based on zero or suspiciously few references,
cross-check with a word-bounded `rg` search and report any mismatch.

## Other Agents
Codex, GitHub Copilot CLI, and Cursor: use the host's built-in language-server or IDE code intelligence when it exists;
otherwise follow step 4.
Ask the user before installing any language server.
