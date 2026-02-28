# frontmatter

Reads, writes, and updates the YAML frontmatter block at the top of Markdown vault files.

## Frontmatter format

Every vault file starts with a fixed-layout frontmatter block:

```
---
tokens: 1500
---

Body content starts here.
```

The layout is fixed: `tokens` is always line 1. This is defined in `layout.py`.

Timestamps (created/modified) are read from OS filesystem metadata, not stored in frontmatter.

## Public API

Imported from `functions.frontmatter`:

### `FM` — the layout constant
An instance of `FrontMatterLayout` (from `layout.py`) that holds the line position and YAML key name:

```python
FM.tokens         # 1  (line index)
FM.tokens_key     # "tokens"
```

Always use `FM` to reference positions and key names — never hardcode integers or strings.

### `tokens` field
- `read_tokens(path) -> int` — reads the token count from frontmatter.
- `update_tokens(path) -> int` — writes a new token count; returns the new value.
- `count_tokens(content) -> int` — approximates token count from a string (~4 chars/token). Drop-in replacement point for a real tokenizer.
- `format_tokens(n) -> str` — formats a count for display: `420`, `9.3k`, `1.2M`.

## Package structure

```
frontmatter/
├── layout.py       — FM singleton (shared by all submodules)
├── io/             — raw file I/O layer
│   ├── reader.py   — read_frontmatter
│   ├── writer.py   — write_frontmatter
│   ├── updater.py  — update_frontmatter
│   └── utils.py    — iter_frontmatter_lines (internal generator)
└── tokens/         — tokens field operations
```

`io/` is the only layer that touches the file directly. The `tokens/` submodule builds on top of `io/` and `layout.py` — nothing outside this package needs to import from `io/` directly.

## Usage examples

```python
from functions.frontmatter import (
    FM,
    read_tokens, update_tokens, count_tokens, format_tokens,
)

# Token counting and display
n = count_tokens(body_text)
update_tokens("vault/notes/foo.md")
print(format_tokens(read_tokens("vault/notes/foo.md")))  # e.g. "9.3k"
```

## Workflows

### New file

Write the frontmatter with `tokens: 0`, then update tokens after writing the body.

```python
from pathlib import Path
from functions.frontmatter import update_tokens
from functions.frontmatter.io import write_frontmatter

path = Path("vault/notes/foo.md")

# Write initial frontmatter + body
write_frontmatter(path, data={}, body="# My Note\n\nContent here.")

# Compute and store token count
update_tokens(path)
```

### File modification

Call `update_tokens` whenever the file body changes.

```python
from functions.frontmatter import update_tokens

path = "vault/notes/foo.md"

# ... write new body content to the file ...

update_tokens(path)    # recount tokens from full file
```

### Display metadata

Read tokens and OS timestamps for display (this is what `dev.py frontmatter` does).

```python
from datetime import datetime, timezone
from pathlib import Path
from functions.frontmatter import read_tokens, format_tokens

path = Path("vault/notes/foo.md")
stat = path.stat()

created = datetime.fromtimestamp(getattr(stat, "st_birthtime", stat.st_mtime), tz=timezone.utc)
updated = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
print(f"created:  {created}")
print(f"updated:  {updated}")

tokens = read_tokens(path)
print(f"tokens:   {tokens} ({format_tokens(tokens)})")
# tokens:   9300 (9.3k)
```

## Constraints

- **`count_tokens` is approximate** (~4 chars/token). To use a real tokenizer, replace the implementation in `tokens/count.py` — the signature `(str) -> int` must stay the same.

## Error handling

All read/write functions catch exceptions internally and print a warning prefixed with the function name (e.g. `[read_frontmatter] error ...`). They never raise — callers get `{}`, `None`, or `0` on failure.
