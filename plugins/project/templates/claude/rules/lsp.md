# Code Intelligence with Language Servers

## When to Use
Use a Language Server Protocol (LSP) server when a task needs symbol-level facts that text search cannot give reliably:
go-to-definition, every reference before a rename or signature change, call hierarchies, inferred types, or diagnostics right after an edit.
For plain lookups, `rg` (or the agent's search tool) plus reading the file is enough;
do not set up a language server for those.

Do not add a third-party code-intelligence Model Context Protocol (MCP) server (such as Serena) as a project dependency.

## Claude Code: Official LSP Plugins
Anthropic publishes one LSP plugin per language in the official `claude-plugins-official` marketplace.
Each plugin connects a language server to Claude Code's built-in `LSP` tool;
the server binary itself must be on `PATH`.

| Language | Plugin | Server binary | Install the binary |
|---|---|---|---|
| Python | `pyright-lsp` | `pyright-langserver` | `uv tool install pyright` |
| TypeScript / JavaScript | `typescript-lsp` | `typescript-language-server` | `bun add -g typescript-language-server typescript` |
| Rust | `rust-analyzer-lsp` | `rust-analyzer` | `rustup component add rust-analyzer` |
| Go | `gopls-lsp` | `gopls` | `go install golang.org/x/tools/gopls@latest` |
| C / C++ | `clangd-lsp` | `clangd` | `brew install llvm` or the system package |
| Swift | `swift-lsp` | `sourcekit-lsp` | ships with Xcode or the Swift toolchain |

Other official plugins: `csharp-lsp`, `jdtls-lsp`, `kotlin-lsp`, `lua-lsp`, `php-lsp`, `ruby-lsp`.
Install binaries with the project's own tooling (UV for Python tools, Bun for JavaScript tools), never `pip`, `npm`, or conda.

## Procedure
1. Check whether the `LSP` tool is available in the session (including the deferred-tool list).
   If it is, use it.
2. If it is not, check whether the plugin is installed (`claude plugin list`) and whether the binary resolves (`command -v <binary>`).
3. Never install silently.
   Ask the user, naming both pieces, for example:
   "Symbol-level navigation would help here.
   Install `pyright-lsp@claude-plugins-official` (`/plugin install pyright-lsp@claude-plugins-official`) and the server (`uv tool install pyright`)?"
   Plugins load at session start, so the `LSP` tool may appear only after a restart.
4. If the user declines, or no plugin covers the language, fall back to word-bounded `rg` searches plus the language's own checker (`ruff` and `ty`, `bunx tsc --noEmit`, `cargo check`, `go vet`),
   and state that reference results are text-based rather than semantic.

## Other Agents
Codex, GitHub Copilot CLI, and Cursor: use the host's built-in language-server or IDE code intelligence when it exists;
otherwise follow step 4.
Ask the user before installing any language server.
