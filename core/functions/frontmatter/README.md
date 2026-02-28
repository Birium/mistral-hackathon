# ADR: Frontmatter Parsing — Library & Architecture Decisions

**Status:** Accepted
**Date:** 2026-02-28

---

## Context

We need to parse, write, and update YAML frontmatter from Markdown files. Two decisions had to be made: which library to use, and how to structure the code.

---

## Decision 1 — PyYAML with CLoader over `python-frontmatter`

### What we chose

Raw PyYAML with the C loader (`yaml.CLoader`), paired with a lazy line-by-line reader, instead of the `python-frontmatter` package.

### Why not `python-frontmatter`

`python-frontmatter` is a well-maintained convenience wrapper, but convenience has a cost:

- It uses PyYAML under the hood anyway, so there is no parsing advantage.
- On top of PyYAML it adds regex-based delimiter detection, a handler resolution system (YAML / TOML / JSON), and its own `Post` object wrapping. All of that runs on every parse call.
- The abstraction is optimized for ergonomics, not throughput.

In a project where speed is a key constraint, paying for abstraction we do not need is not acceptable.

### Why PyYAML + CLoader

PyYAML ships with two loader backends:

| Loader       | Implementation         | Relative speed |
| ------------ | ---------------------- | -------------- |
| `FullLoader` | Pure Python            | Baseline       |
| `CLoader`    | C bindings via libyaml | ~10× faster    |

`CLoader` is the fastest YAML parser available in the Python ecosystem for our use case. The reader opens the file lazily via `iter_frontmatter_lines` (see `utils.py`): it reads line-by-line and stops as soon as the closing `---` delimiter is found (200-line hard cap). Only the frontmatter block is ever loaded into memory — the rest of the file, however large, is never touched. Any IO or parse failure is caught and returns an empty dict with a contextual error message rather than propagating an exception.

### Trade-offs accepted

- We must ensure `libyaml` is installed in our Docker images (`apt-get install -y libyaml-dev`). This is a one-line change and a fully controlled environment.
- We lose automatic support for TOML/JSON frontmatter. This is intentional — we standardize on YAML only.
- We write slightly more code than `frontmatter.load(path)`. The implementation is still under 25 lines and has no hidden complexity.

---

## Decision 2 — Module of plain functions over a single class

### What we chose

A small `frontmatter/` package exposing plain functions (`read_frontmatter`, `write_frontmatter`, `update_frontmatter`) rather than a class with methods.

```
frontmatter/
├── __init__.py     # public re-exports
├── reader.py
├── writer.py
├── updater.py
└── utils.py        # shared internal helpers (iter_frontmatter_lines)
```

`utils.py` is internal — it is not re-exported from `__init__.py`. It contains `iter_frontmatter_lines`, a generator used by both `reader.py` and `updater.py` to yield frontmatter lines from an open file handle (after the opening `---`). It raises `EOFError` on premature EOF and `ValueError` if the 200-line cap is exceeded, letting each caller decide how to surface the error.

### Why not a class

A class is the right tool when you need to hold state across calls or manage shared dependencies (a database connection, an auth token, a file system abstraction). Frontmatter parsing has none of that:

- Every operation is self-contained: input in, output out.
- There is no shared state between a read and a write.
- There is no lifecycle to manage.

Wrapping stateless operations in a class adds `__init__`, `self` plumbing, and instantiation overhead for zero architectural benefit. It also makes the code harder to tree-shake, import selectively, and test in isolation.

### Why plain functions in a module

- **No unnecessary instantiation.** Functions are called directly; no object allocation per usage.
- **Explicit imports.** Callers import exactly what they need: `from frontmatter import read_frontmatter`.
- **Easier to test.** Each function is a pure unit. No setup, no teardown, no mocking of `self`.
- **Idiomatic Python.** The standard library, `pathlib`, `json`, and `os` all follow this pattern for stateless utilities.
- **Composable.** Functions can be passed as arguments, mapped over lists, and wrapped with `functools` without any class ceremony.

### When we would revisit this

If a future requirement introduces a dependency that needs injection (e.g. a remote file system, a cache layer, or a configurable YAML schema), wrapping the functions in a class that holds those dependencies would be appropriate. The current flat structure makes that refactor straightforward since the function signatures would not change.

---

## Summary

| Question  | Decision         | Primary reason                                        |
| --------- | ---------------- | ----------------------------------------------------- |
| Library   | PyYAML + CLoader | ~10× faster than pure Python; no abstraction overhead |
| Structure | Plain functions  | Stateless operations do not benefit from a class      |
