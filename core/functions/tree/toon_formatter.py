"""
toon_formatter — renders a TreeNode tree as a toon-encoded flat list.

LLM-optimised: uniform tabular array, one row per node.
Hierarchy is encoded in the path column (directories have trailing /).
"""

from typing import Optional

from toon_format import encode

from .models import TreeNode
from .time_format import format_time_ago
from functions.frontmatter.tokens.formatter import format_tokens


def _collect_nodes(root: TreeNode, max_depth: Optional[int]) -> list[dict]:
    """Walk the tree and flatten it into a list of row dicts."""
    rows: list[dict] = []

    def walk(node: TreeNode, rel_path: str, depth: int) -> None:
        rows.append({
            "path": rel_path,
            "tokens": format_tokens(node.tokens),
            "mtime": format_time_ago(node.mtime),
        })
        if node.is_directory and (max_depth is None or depth < max_depth):
            for child in node.children:
                suffix = "/" if child.is_directory else ""
                walk(child, rel_path + child.name + suffix, depth + 1)

    root_suffix = "/" if root.is_directory else ""
    walk(root, root.name + root_suffix, 0)
    return rows


def format_tree_toon(root: TreeNode, max_depth: Optional[int]) -> str:
    """Return the tree encoded as a toon string."""
    rows = _collect_nodes(root, max_depth)
    return encode(rows)
