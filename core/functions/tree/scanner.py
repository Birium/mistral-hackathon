"""
Filesystem scanner — walks a path and builds a TreeNode tree.

Always scans full depth. Depth limiting is the formatter's job.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from functions.frontmatter.tokens.read import read_tokens

from .models import TreeNode

# ---------------------------------------------------------------------------
# POLICY: file/folder skip rules. Edit these functions to change behavior.
# ---------------------------------------------------------------------------

# POLICY: Binary files are skipped (0 tokens). Modify this set to change.
_BINARY_EXTENSIONS: set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".pdf",
    ".zip", ".tar", ".gz", ".7z", ".rar",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv",
    ".exe", ".dll", ".so", ".dylib",
    ".woff", ".woff2", ".ttf", ".eot",
    ".db", ".sqlite",
}


def _is_hidden(name: str) -> bool:
    # POLICY: Skip files/folders starting with '.'
    return name.startswith(".")


def _is_symlink(path: Path) -> bool:
    # POLICY: Skip symlinks
    return path.is_symlink()


def _is_binary(path: Path) -> bool:
    # POLICY: Skip binary files (counted as 0 tokens)
    return path.suffix.lower() in _BINARY_EXTENSIONS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_mtime(path: Path) -> datetime:
    """Return mtime as timezone-aware UTC datetime."""
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def scan(path: Path) -> TreeNode:
    """Recursively scan *path* and return a complete TreeNode tree.

    Raises FileNotFoundError if path does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if path.is_file():
        return _scan_file(path)

    return _scan_directory(path)


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------


def _scan_file(path: Path) -> TreeNode:
    tokens = 0

    if _is_binary(path):
        # POLICY: Binary files contribute 0 tokens.
        pass
    else:
        tokens = read_tokens(path)

    return TreeNode(
        name=path.name,
        path=str(path),
        is_directory=False,
        tokens=tokens,
        mtime=_get_mtime(path),
    )


def _scan_directory(path: Path) -> TreeNode:
    children: list[TreeNode] = []

    try:
        entries = sorted(
            path.iterdir(),
            key=lambda e: (not e.is_dir(), e.name.lower()),
        )
    except PermissionError:
        entries = []

    for entry in entries:
        # POLICY: skip hidden
        if _is_hidden(entry.name):
            continue

        # POLICY: skip symlinks
        if _is_symlink(entry):
            continue

        if entry.is_dir():
            children.append(_scan_directory(entry))
        elif entry.is_file():
            children.append(_scan_file(entry))

    total_tokens = sum(c.tokens for c in children)

    # Directory mtime = most recent child. None if empty → displays "—".
    latest_mtime: Optional[datetime] = None
    if children:
        child_mtimes = [c.mtime for c in children if c.mtime is not None]
        if child_mtimes:
            latest_mtime = max(child_mtimes)

    return TreeNode(
        name=path.name + "/",
        path=str(path),
        is_directory=True,
        tokens=total_tokens,
        mtime=latest_mtime,
        children=children,
    )
