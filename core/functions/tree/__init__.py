"""
tree(path, depth) — dynamic vault structure viewer.

Usage:
    from tools.tree import tree

    print(tree("vault/projects/startup-x/", depth=2))
    print(tree("vault/inbox/", depth=None))
"""

from pathlib import Path
from typing import Optional

from .scanner import scan
from .formatter import format_tree
from .toon_formatter import format_tree_toon


def tree(path: str, depth: Optional[int]) -> str:
    """Display vault structure from *path* with token counts and timestamps.

    Parameters
    ----------
    path : str
        Starting point. Can be a directory or a single file.
    depth : int | None
        Levels to unfold. ``None`` = unlimited, ``0`` = root line only.

    Returns
    -------
    str
        Formatted ASCII tree.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    """
    target = Path(path)

    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    node = scan(target)
    return format_tree(node, max_depth=depth)


def tree_toon(path: str, depth: Optional[int]) -> str:
    """LLM-optimised vault structure using toon encoding.

    Same parameters as tree(). Returns a toon-format string.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    """
    target = Path(path)

    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    node = scan(target)
    return format_tree_toon(node, max_depth=depth)
