"""
Formatter — renders a TreeNode tree into an aligned ASCII string.

Depth limiting and summary lines are handled here, not in the scanner.
"""

from typing import Optional


from .models import TreeNode
from .time_format import format_time_ago
from functions.frontmatter.tokens.formatter import format_tokens


def _format_meta(node: TreeNode) -> str:
    """Build the [tokens · time_ago] bracket string."""
    return f"[{format_tokens(node.tokens)} · {format_time_ago(node.mtime)}]"


# ---------------------------------------------------------------------------
# Summary at depth boundary
# ---------------------------------------------------------------------------


def _count_descendants(node: TreeNode) -> tuple[int, int]:
    """Recursively count all file and folder descendants."""
    files = 0
    folders = 0
    for child in node.children:
        if child.is_directory:
            folders += 1
            sub_files, sub_folders = _count_descendants(child)
            files += sub_files
            folders += sub_folders
        else:
            files += 1
    return files, folders


def _summary_text(node: TreeNode) -> str:
    """Generate '... N files, M folders' for a collapsed directory."""
    files, folders = _count_descendants(node)

    parts: list[str] = []
    if files:
        parts.append(f"{files} file{'s' if files != 1 else ''}")
    if folders:
        parts.append(f"{folders} folder{'s' if folders != 1 else ''}")

    return "... " + ", ".join(parts) if parts else "... empty"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def format_tree(root: TreeNode, max_depth: Optional[int]) -> str:
    """Render *root* as an aligned ASCII tree.

    max_depth: levels to unfold from root.
      0    → root line only, no children
      1    → immediate children only
      None → unlimited
    """
    # Collect (left_text, meta_text) pairs, then right-align in one pass.
    lines: list[tuple[str, str]] = []

    # Root line is always shown.
    lines.append((root.name, _format_meta(root)))

    if root.is_directory and (max_depth is None or max_depth > 0):
        _render_children(
            node=root,
            lines=lines,
            prefix="",
            current_depth=1,
            max_depth=max_depth,
        )

    return _align(lines)


# ---------------------------------------------------------------------------
# Recursive renderer
# ---------------------------------------------------------------------------


def _render_children(
    node: TreeNode,
    lines: list[tuple[str, str]],
    prefix: str,
    current_depth: int,
    max_depth: Optional[int],
) -> None:
    children = node.children
    if not children:
        return

    for i, child in enumerate(children):
        is_last = i == len(children) - 1
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "
        child_prefix = prefix + extension

        lines.append((prefix + connector + child.name, _format_meta(child)))

        if child.is_directory:
            at_limit = max_depth is not None and current_depth >= max_depth

            if at_limit:
                # Collapsed: show summary if dir is non-empty
                if child.children:
                    summary = _summary_text(child)
                    lines.append((child_prefix + "└── " + summary, ""))
            else:
                # Expand deeper
                _render_children(
                    child, lines, child_prefix, current_depth + 1, max_depth
                )


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------

_MIN_GAP = 4  # minimum spaces between name and metadata bracket


def _align(lines: list[tuple[str, str]]) -> str:
    """Right-align all metadata brackets to the same column."""
    if not lines:
        return ""

    max_left = max(len(left) for left, _ in lines)

    result: list[str] = []
    for left, meta in lines:
        if meta:
            padding = max_left - len(left) + _MIN_GAP
            result.append(f"{left}{' ' * padding}{meta}")
        else:
            # Summary lines have no metadata
            result.append(left)

    return "\n".join(result)
