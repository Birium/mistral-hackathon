"""
Glob-based scope filtering.

Patterns follow standard Unix glob (fnmatch):
  "vault/projects/startup-x/*"
  "vault/projects/*/state.md"

Paths coming from QMD are relative to the vault root
after stripping the qmd://vault/ prefix.
We re-add the "vault/" prefix to make glob matching work
against the patterns the agent provides.
"""

import fnmatch


def matches_scopes(path: str, scopes: list[str] | None) -> bool:
    """Return True if *path* matches at least one scope pattern, or if scopes is None."""
    print(f"matching path={path} against scopes={scopes}")
    if scopes is None:
        return True
    # path is e.g. "projects/startup-x/changelog.md"
    # scopes patterns are e.g. "vault/projects/startup-x/*"
    full = "vault/" + path
    return any(fnmatch.fnmatch(full, pattern) for pattern in scopes)
