import os
from pathlib import Path
from typing import Optional

from .scanner import scan
from .formatter import format_tree


def get_tree(path: Optional[str] = None, depth: Optional[int] = None) -> str:
    """Scan *path*, render the tree, and write it to tree.md in the vault.

    Parameters
    ----------
    path : str
        Path from vault root.
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
    vault_path = Path(os.getenv("VAULT_PATH", ""))
    tree_file_path = Path(vault_path) if not path else Path(vault_path) / path

    node = scan(tree_file_path)
    return format_tree(node, max_depth=depth)
