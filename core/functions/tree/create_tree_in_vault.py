from pathlib import Path
from typing import Optional

from functions.files import create_file

from .scanner import scan
from .formatter import format_tree


def create_tree_in_vault(path: str, depth: Optional[int]) -> Path:
    """Scan *path*, render the tree, and write it to tree.md in the vault.

    Parameters
    ----------
    path : str
        Starting point. Can be a directory or a single file.
    depth : int | None
        Levels to unfold. ``None`` = unlimited, ``0`` = root line only.

    Returns
    -------
    Path
        The resolved path of the created tree.md file.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    """
    target = Path(path)

    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    node = scan(target)
    content = format_tree(node, max_depth=depth)
    return create_file("tree.md", body=content)
