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

### `created` field
- `update_created(path) -> datetime` — writes the current datetime to the `created` line. Call once at file creation; never call again.
- `read_created(path) -> datetime | None` — reads the `created` timestamp.

### `updated` field
- `update_updated(path) -> datetime` — writes the current datetime to the `updated` line. Call on every modification.
- `read_updated(path) -> datetime | None` — reads the `updated` timestamp.

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
├── tokens/         — tokens field operations
├── created/        — created field operations
└── updated/        — updated field operations
```

`io/` is the only layer that touches the file directly. Field submodules (`tokens/`, `created/`, `updated/`) build on top of `io/` and `layout.py` — nothing outside this package needs to import from `io/` directly.

## Usage examples

```python
from functions.frontmatter import (
    FM,
    update_created, read_created,
    update_updated, read_updated,
    read_tokens, update_tokens, count_tokens, format_tokens,
)

# On file creation
update_created("vault/notes/foo.md")

# On file modification
update_updated("vault/notes/foo.md")

# Read timestamps
created_at = read_created("vault/notes/foo.md")   # datetime | None
updated_at = read_updated("vault/notes/foo.md")   # datetime | None

# Token counting and display
n = count_tokens(body_text)
update_tokens("vault/notes/foo.md")
print(format_tokens(read_tokens("vault/notes/foo.md")))  # e.g. "9.3k"
```

## Error handling

All read/write functions catch exceptions internally and print a warning prefixed with the function name (e.g. `[read_frontmatter] error ...`). They never raise — callers get `{}`, `None`, or `0` on failure.
