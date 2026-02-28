"""
Policy: which vault paths are never returned by search.
Edit EXCLUDED_EXACT and EXCLUDED_PREFIXES to change behaviour.
"""

EXCLUDED_EXACT: frozenset[str] = frozenset(
    {
        "overview.md",
        "tree.md",
        "profile.md",
    }
)

EXCLUDED_PREFIXES: tuple[str, ...] = ("inbox/",)


def is_excluded(path: str) -> bool:
    """Return True if *path* (relative to vault root) should never appear in results."""
    if path in EXCLUDED_EXACT:
        return True
    return any(path.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
