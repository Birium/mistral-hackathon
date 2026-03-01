"""
All vault tools — one file, nine tools.

tree   → real implementation via core/functions/tree
read   → real implementation (filesystem read + line numbering)
search → real implementation via core/functions/search (BM25 + semantic)
write  → real implementation via core/functions/write (update-only)
edit   → dummy
append → real implementation via core/functions/appender (update-only)
move   → real implementation via core/functions/move (update-only)
delete → real implementation via core/functions/delete (update-only)
concat → dummy (search-only)

All path arguments are resolved against VAULT_PATH.

Exported lists:
  UPDATE_TOOLS — all tools except concat
  SEARCH_TOOLS — tree, read, search, concat (read-only)
"""

import asyncio
import logging
from typing import Optional, List

from agent.tools.tool_base import BaseTool
from functions.utils import _resolve_path
from functions.tree import get_tree as _tree_impl
from functions.delete import delete as _delete_impl
from functions.search import search as _search_impl
from functions.write import write as _write_impl
from functions.read import read as _read_impl
from functions.move import move as _move_impl
from functions.appender import append as _append_impl
from functions.concat import concat as _concat_impl
from functions.edit import edit as _edit_impl


# ---------------------------------------------------------------------------
# tree — REAL implementation
# ---------------------------------------------------------------------------


def tree(path: str = "", depth: Optional[int] = None) -> str:
    """Explore the structure of the vault with token counts and timestamps.

    Args:
        path: Vault path to scan (e.g. 'vault/', 'vault/projects/startup-x/').
              Defaults to the vault root.
        depth: Levels to unfold. None = unlimited, 0 = root only.
    """
    resolved = _resolve_path(path)
    return _tree_impl(path=str(resolved), depth=depth)


# ---------------------------------------------------------------------------
# read — REAL implementation
# ---------------------------------------------------------------------------


def read(paths: list[str], head: Optional[int] = None, tail: Optional[int] = None) -> str:
    """Read one or more files or folders from the vault, with line numbers.

    Args:
        paths: List of vault paths. Each path may be a file or a folder
               (folder = all direct files, non-recursive).
        head: Approximate token budget from the start of each file.
        tail: Approximate token budget from the end of each file.
              head and tail are mutually exclusive.
    """
    try:
        return _read_impl(paths=paths, head=head, tail=tail)
    except ValueError as e:
        return f"[READ ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[READ ERROR] {e}"

# ---------------------------------------------------------------------------
# search — real (async bridge)
# ---------------------------------------------------------------------------


def search(
    queries: List[str],
    mode: str = "fast",
    scopes: Optional[List[str]] = None,
) -> str:
    """Search the indexed vault via QMD (BM25 or full semantic pipeline).

    Args:
        queries: One or more search queries to run simultaneously.
        mode: 'fast' for BM25 term matching, 'deep' for full semantic pipeline.
        scopes: Optional list of glob patterns to restrict the search scope.
    """

    try:
        results = asyncio.run(_search_impl(queries=queries, mode=mode, scopes=scopes))
    except Exception as e:
        return f"[SEARCH ERROR] {e}"

    if not results:
        return f"No results found for: {queries}"

    logger = logging.getLogger(__name__)

    logger.info(
        f"[search] returning {len(results)} results for queries={queries} with scopes={scopes}"
    )

    lines = [f"## Search results for `{queries}`\n"]
    for r in results:
        lines.append(f"### {r.path} (score: {r.score}, lines: {r.lines})")
        lines.append(f"```\n{r.chunk_with_context}\n```\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# write — real implementation (update-only)
# ---------------------------------------------------------------------------


def write(path: str, content: str) -> str:
    """Create a new file or fully overwrite an existing file in the vault.

    Args:
        path: Vault path of the file to create or overwrite.
        content: Complete markdown content (frontmatter managed by background job).
    """
    try:
        return _write_impl(path=path, content=content)
    except ValueError as e:
        return f"[WRITE ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[WRITE ERROR] Could not write '{path}': {e}"


# ---------------------------------------------------------------------------
# edit — dummy (update-only)
# ---------------------------------------------------------------------------


def edit(path: str, old_content: str, new_content: str) -> str:
    """Surgically replace a specific section in a file via exact search-replace.

    Args:
        path: Vault path of the file to modify.
        old_content: Exact text to locate (with or without line number prefixes).
        new_content: Replacement text (no line number prefixes).
    """
    try:
        return _edit_impl(path=path, old_content=old_content, new_content=new_content)
    except (ValueError, FileNotFoundError) as e:
        return f"[EDIT ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[EDIT ERROR] Could not edit '{path}': {e}"


# ---------------------------------------------------------------------------
# append — real implementation (update-only)
# ---------------------------------------------------------------------------


def append(path: str, content: str, position: str = "top") -> str:
    """Insert a markdown block at the top or bottom of a file without reading it.

    Args:
        path: Vault path of the target file. Created if it does not exist.
        content: Complete markdown block to insert. Include frontmatter if creating.
        position: 'top' to insert after frontmatter, 'bottom' to append at end.
    """
    try:
        return _append_impl(path=path, content=content, position=position)
    except ValueError as e:
        return f"[APPEND ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[APPEND ERROR] Could not write '{path}': {e}"


# ---------------------------------------------------------------------------
# move — real implementation (update-only)
# ---------------------------------------------------------------------------


def move(from_path: str, to_path: str) -> str:
    """Move a file or folder to a new location within the vault.

    Args:
        from_path: Vault source path of the file or folder to move.
        to_path: Vault destination path. Parent directories created if needed.
    """
    try:
        return _move_impl(from_path=from_path, to_path=to_path)
    except (ValueError, FileNotFoundError) as e:
        return f"[MOVE ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[MOVE ERROR] Could not move '{from_path}': {e}"


# ---------------------------------------------------------------------------
# delete — real implementation (update-only)
# ---------------------------------------------------------------------------


def delete(path: str) -> str:
    """Permanently delete a file or folder (recursive) from the vault.

    Args:
        path: Vault path of the file or folder to delete.
    """
    try:
        return _delete_impl(path=path)
    except ValueError as e:
        return f"[DELETE ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[DELETE ERROR] Could not delete '{path}': {e}"


# ---------------------------------------------------------------------------
# concat — dummy (search-only)
# ---------------------------------------------------------------------------


def concat(files: list[dict]) -> str:
    """Assemble an ordered list of vault files into a single structured markdown document.

    Args:
        files: Ordered list of file objects. Each object has:
               - path  (str)        : vault path of the file
               - lines (str | null) : line range 'N-M' to extract, or null for the full file
    """
    try:
        return _concat_impl(files=files)
    except Exception as e:
        return f"[CONCAT ERROR] Unexpected error: {e}"


# ---------------------------------------------------------------------------
# Tool instances
# ---------------------------------------------------------------------------

TreeTool = BaseTool(tree)
ReadTool = BaseTool(read)
SearchTool = BaseTool(search)
WriteTool = BaseTool(write)
EditTool = BaseTool(edit)
AppendTool = BaseTool(append)
MoveTool = BaseTool(move)
DeleteTool = BaseTool(delete)
ConcatTool = BaseTool(concat)

# Search agent — read-only
SEARCH_TOOLS = [TreeTool, ReadTool, SearchTool, ConcatTool]

# Update agent — full access
UPDATE_TOOLS = [
    TreeTool,
    ReadTool,
    SearchTool,
    WriteTool,
    EditTool,
    AppendTool,
    MoveTool,
    DeleteTool,
]
