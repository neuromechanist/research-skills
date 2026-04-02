# Serena MCP for Code Intelligence

## When Available
Use Serena MCP tools for efficient code exploration and editing when the MCP server is configured.

## Core Tools

### Exploration (Read-Only)
- `get_symbols_overview` - Get file structure before reading entire files
- `find_symbol` - Search for classes, methods, functions by name
- `find_referencing_symbols` - Find all usages of a symbol
- `search_for_pattern` - Flexible regex search across codebase
- `list_dir` - List directory contents
- `find_file` - Find files by name pattern

### Editing (Symbolic)
- `replace_symbol_body` - Replace entire method/function body
- `insert_after_symbol` - Add code after a symbol
- `insert_before_symbol` - Add code before a symbol
- `rename_symbol` - Rename a symbol across the codebase

## Best Practices

### Prefer Symbolic Tools Over Full File Reads
```
# Good: Get overview first, then read specific symbols
get_symbols_overview(file) -> find_symbol(name, include_body=True)

# Avoid: Reading entire large files when you only need one function
```

### Incremental Exploration
1. Start with `get_symbols_overview` to understand file structure
2. Use `find_symbol` with `depth=1` to see method signatures
3. Only read bodies (`include_body=True`) when needed
4. Use `find_referencing_symbols` to understand usage patterns

### Efficient Editing
- Use `replace_symbol_body` for modifying entire functions
- Use `insert_after_symbol` for adding new methods to a class
- Prefer symbolic editing over line-based edits for complex changes

## Memory Integration
- Use `write_memory` to persist findings across sessions
- Use `read_memory` to recall previous context
- Name memories descriptively for easy retrieval

---
*Token-efficient code exploration and precise symbolic editing.*
