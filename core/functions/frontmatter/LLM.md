# y-knot core toolkit — LLM reference

Two packages for managing a Markdown vault: `frontmatter` tracks token counts in a fixed YAML header, `tree` scans and renders the vault structure with that metadata. Timestamps are read from OS filesystem metadata, not stored in frontmatter.

---

## Vault file format

Every vault file begins with a fixed 3-line frontmatter block:

```
---            # line 0  FM.delimiter_start
tokens: 1500   # line 1  FM.tokens       / FM.tokens_key
---            # line 2  FM.delimiter_end
```

- Layout is fixed; order must not change.
- Always use `FM.*` constants to reference line positions and key names — never hardcode integers or strings.

---

## `frontmatter` API

```python
from functions.frontmatter import (
    FM,
    read_tokens, update_tokens, count_tokens, format_tokens,
)
```

### FM — layout singleton

| Attribute | Value | Type |
|-----------|-------|------|
| `FM.tokens` | 1 | int (line index) |
| `FM.tokens_key` | `"tokens"` | str |

### tokens field

| Function | Signature | Returns | Notes |
|----------|-----------|---------|-------|
| `count_tokens` | `(content: str) -> int` | int | Approximation: `len(content) // 4`, min 1 for non-empty |
| `update_tokens` | `(path: str\|Path) -> int` | new token count | Reads full file, counts, writes to FM.tokens line |
| `read_tokens` | `(path: str\|Path) -> int` | int (0 if missing) | Reads FM.tokens line |
| `format_tokens` | `(n: int) -> str` | formatted string | `420` → `"420"`, `9300` → `"9.3k"`, `1_300_000` → `"1.3M"` |

### Low-level I/O (rarely needed directly)

| Function | Signature | Notes |
|----------|-----------|-------|
| `read_frontmatter` | `(path, line=None) -> dict` | Full frontmatter or single-line dict |
| `write_frontmatter` | `(path, data, body="") -> None` | Overwrites entire file |
| `update_frontmatter` | `(path, updates, line=None) -> None` | Merges updates; preserves body |

Import from `functions.frontmatter.io` if needed — the `tokens/` submodule uses these internally.

---

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

Read tokens and OS timestamps for display.

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

---

## `tree` API

```python
from functions.tree import tree
```

### `tree(path, depth) -> str`

| Parameter | Type | Notes |
|-----------|------|-------|
| `path` | `str` | Starting directory or file |
| `depth` | `int\|None` | `None` = unlimited; `0` = root line only; `1` = immediate children |

Returns: formatted ASCII tree string. Raises `FileNotFoundError` if path does not exist.

**Output format** (each line):

```
name/                   [tokens · time_ago]
├── child.md            [420 · 3d ago]
└── subdir/             [9.3k · 1h ago]
    └── note.md         [9.3k · 1h ago]
```

At depth boundary, collapsed directories show: `... N files, M folders`

**`format_tokens` examples:**

| Input | Output |
|-------|--------|
| 420 | `"420"` |
| 9300 | `"9.3k"` |
| 9000 | `"9k"` |
| 1_300_000 | `"1.3M"` |

---

## Invariants and constraints

- **`FM` is the single source of truth** for line positions. Do not hardcode line numbers.
- **`count_tokens` is a placeholder** (~4 chars/token). Replace with a real tokenizer (e.g. `tiktoken`) by implementing the same `(str) -> int` signature in `tokens/count.py`.
- **Functions never raise.** On error they print a warning prefixed with the function name and return a safe default: `{}` (read_frontmatter), `0` (read_tokens). Callers do not need try/except.
- **Hidden files, symlinks, and binary files** are skipped by the tree scanner. Binary files contribute 0 tokens.
- **Body content is always preserved** by `update_frontmatter` and `update_tokens`.
