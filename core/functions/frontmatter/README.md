# frontmatter

Reads, writes, and updates the YAML frontmatter block at the top of Markdown vault files.

## Frontmatter format

Every vault file starts with a fixed-layout frontmatter block:

```
---
created: 2025-02-28T10:00:00
updated: 2025-02-28T10:00:00
tokens: 1500
---

Body content starts here.
```

The layout is fixed: `created` is always line 1, `updated` line 2, `tokens` line 3. This is defined in `layout.py`.

## Public API

Imported from `functions.frontmatter`:

### `read_frontmatter(path, line=None) -> dict`
Reads frontmatter from a Markdown file.
- Without `line`: parses and returns the full frontmatter as a dict.
- With `line` (int, zero-indexed): reads only that single line and returns a one-key dict. Faster — skips full YAML parsing.
- Returns `{}` on missing frontmatter, parse errors, or missing line.

### `write_frontmatter(path, data, body="") -> None`
Overwrites the file entirely with new frontmatter + optional body.
Use this when creating a new file or replacing all frontmatter at once.

### `update_frontmatter(path, updates, line=None) -> None`
Merges updates into existing frontmatter without touching the body.
- Without `line`: parses the full block, merges the updates dict in, rewrites.
- With `line` (int, zero-indexed): replaces only that line in-place. No YAML parsing of the rest — used for hot-path updates like token counts.

### `FM` — the layout constant
An instance of `FrontMatterLayout` (from `layout.py`) that holds the line positions and YAML key names:

```python
FM.created        # 1  (line index)
FM.updated        # 2
FM.tokens         # 3
FM.created_key    # "created"
FM.updated_key    # "updated"
FM.tokens_key     # "tokens"
```

Always use `FM` to reference positions and key names — never hardcode integers or strings.

## Internal files

| File | Role |
|---|---|
| `layout.py` | Defines `FrontMatterLayout` dataclass and the `FM` singleton constant |
| `reader.py` | Implements `read_frontmatter` |
| `writer.py` | Implements `write_frontmatter` |
| `updater.py` | Implements `update_frontmatter` |
| `utils.py` | `iter_frontmatter_lines()` — internal generator that streams raw lines between the `---` delimiters |

## Usage examples

```python
from functions.frontmatter import read_frontmatter, write_frontmatter, update_frontmatter, FM

# Read full frontmatter
data = read_frontmatter("vault/notes/foo.md")
# {'created': '2025-02-28', 'updated': '2025-02-28', 'tokens': 1500}

# Read only the tokens line (fast path)
data = read_frontmatter("vault/notes/foo.md", line=FM.tokens)
# {'tokens': 1500}

# Update only the tokens line in-place (fast path)
update_frontmatter("vault/notes/foo.md", {FM.tokens_key: 2000}, line=FM.tokens)

# Merge multiple fields into the full block
update_frontmatter("vault/notes/foo.md", {"updated": "2025-03-01", "tokens": 2000})

# Create or overwrite a file
write_frontmatter("vault/notes/new.md", {"created": "2025-03-01", "updated": "2025-03-01", "tokens": 0}, body="# Title\n")
```

## Error handling

All three public functions catch exceptions internally and print a warning prefixed with the function name (e.g. `[read_frontmatter] error ...`). They never raise — callers get `{}` or `None` on failure.
