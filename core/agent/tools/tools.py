"""
All vault tools — one file, nine tools.

tree   → real implementation via core/functions/tree
read   → real implementation (filesystem read + line numbering)
search → dummy
write  → dummy
edit   → dummy
append → dummy
move   → dummy
delete → dummy
concat → dummy (search-only)

All path arguments are resolved against VAULT_PATH.

Exported lists:
  UPDATE_TOOLS — all tools except concat
  SEARCH_TOOLS — tree, read, search, concat (read-only)
"""

from pathlib import Path
from typing import Optional, List

from tools.tool_base import BaseTool
from functions.tree import tree as _tree_impl
from env import env


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


def _resolve_path(path: str) -> Path:
    """Resolve any vault path to an absolute filesystem path.

    Handles all formats the LLM might produce:
      - bare filename:       "overview.md"       -> VAULT_PATH/overview.md
      - vault-prefixed:      "vault/projects/x/" -> VAULT_PATH/projects/x/
      - root aliases:        ".", "./", "vault/"  -> VAULT_PATH/
    """
    vault_root = Path(env.VAULT_PATH).resolve()
    clean = path.strip()

    # Root aliases → return vault root directly
    if clean in (".", "./", "", "vault", "vault/", "vault/."):
        return vault_root

    # Strip leading "vault/" prefix
    if clean.startswith("vault/"):
        clean = clean[len("vault/"):]

    return vault_root / clean.strip("/")


# ---------------------------------------------------------------------------
# tree — REAL implementation
# ---------------------------------------------------------------------------


def tree(path: str = "vault/", depth: Optional[int] = None) -> str:
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


def read(paths: str, head: Optional[int] = None, tail: Optional[int] = None) -> str:
    """Read a file from the vault and return its content with line numbers.

    Args:
        paths: Path relative to vault root (e.g. 'overview.md' or
               'vault/projects/startup-x/state.md').
        head: Approximate token budget from the start of the file.
        tail: Approximate token budget from the end of the file.
    """
    target = _resolve_path(paths)

    if not target.exists():
        return f"[READ ERROR] Path not found: '{paths}'"

    try:
        content = target.read_text(encoding="utf-8")
    except (OSError, PermissionError) as e:
        return f"[READ ERROR] Could not read '{paths}': {e}"

    lines = content.splitlines()

    # Apply head / tail budget (approx 4 chars per token)
    if head is not None:
        budget = head * 4
        selected, total = [], 0
        for line in lines:
            total += len(line) + 1
            if total > budget:
                break
            selected.append(line)
        lines = selected
    elif tail is not None:
        budget = tail * 4
        selected, total = [], 0
        for line in reversed(lines):
            total += len(line) + 1
            if total > budget:
                break
            selected.insert(0, line)
        lines = selected

    width = len(str(max(len(lines), 1)))
    formatted = "\n".join(f"{i + 1:<{width}}  | {line}" for i, line in enumerate(lines))

    return f"```{paths}\n{formatted}\n```"


# ---------------------------------------------------------------------------
# search — dummy
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
    scope_info = f", scopes={scopes}" if scopes else ""
    return (
        f"[DUMMY SEARCH] Queries: {queries}, mode={mode}{scope_info}\n"
        f"Results:\n"
        f"  - vault/projects/startup-x/state.md (score: 0.89)\n"
        f"    Line 22: 'API externe : prestataire indisponible avant juin.'\n"
        f"  - vault/projects/startup-x/changelog.md (score: 0.71)\n"
        f"    Line 9: '[décision] Abandon de l API externe'\n"
        f"  - vault/changelog.md (score: 0.58)\n"
        f"    Line 45: 'Décision de pivot technique sur startup-x'\n"
    )


# ---------------------------------------------------------------------------
# write — dummy (update-only)
# ---------------------------------------------------------------------------


def write(path: str, content: str) -> str:
    """Create a new file or fully overwrite an existing file in the vault.

    Args:
        path: Vault path of the file to create or overwrite.
        content: Complete markdown content (frontmatter managed by background job).
    """
    preview = content[:80].replace("\n", "\\n") + ("..." if len(content) > 80 else "")
    return f"[DUMMY WRITE] Written to '{path}': \"{preview}\""


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
    old_preview = old_content[:60].replace("\n", "\\n") + ("..." if len(old_content) > 60 else "")
    return f"[DUMMY EDIT] Replaced in '{path}': \"{old_preview}\""


# ---------------------------------------------------------------------------
# append — dummy (update-only)
# ---------------------------------------------------------------------------


def append(path: str, content: str, position: str = "top") -> str:
    """Insert a markdown block at the top or bottom of a file without reading it.

    Args:
        path: Vault path of the target file.
        content: Complete markdown block to insert.
        position: 'top' to prepend (after frontmatter), 'bottom' to append.
    """
    preview = content[:60].replace("\n", "\\n") + ("..." if len(content) > 60 else "")
    return f"[DUMMY APPEND] Inserted at {position} of '{path}': \"{preview}\""


# ---------------------------------------------------------------------------
# move — dummy (update-only)
# ---------------------------------------------------------------------------


def move(from_path: str, to_path: str) -> str:
    """Move a file or folder to a new location within the vault.

    Args:
        from_path: Vault source path of the file or folder to move.
        to_path: Vault destination path. Parent directories created if needed.
    """
    return f"[DUMMY MOVE] Moved '{from_path}' → '{to_path}'"


# ---------------------------------------------------------------------------
# delete — dummy (update-only)
# ---------------------------------------------------------------------------


def delete(path: str) -> str:
    """Permanently delete a file or folder (recursive) from the vault.

    Args:
        path: Vault path of the file or folder to delete.
    """
    return f"[DUMMY DELETE] Deleted '{path}'"


# ---------------------------------------------------------------------------
# concat — dummy (search-only)
# ---------------------------------------------------------------------------


def concat(files: List[str]) -> str:
    """Assemble a list of files into a single structured markdown document.

    Args:
        files: Ordered list of vault file paths to assemble.
    """
    blocks = [
        f"```{f}\n1  | [DUMMY CONCAT] Mock content for '{f}'\n```"
        for f in files
    ]
    return "\n\n".join(blocks) if blocks else ""


# ---------------------------------------------------------------------------
# Tool instances
# ---------------------------------------------------------------------------

TreeTool   = BaseTool(tree)
ReadTool   = BaseTool(read)
SearchTool = BaseTool(search)
WriteTool  = BaseTool(write)
EditTool   = BaseTool(edit)
AppendTool = BaseTool(append)
MoveTool   = BaseTool(move)
DeleteTool = BaseTool(delete)
ConcatTool = BaseTool(concat)


# ---------------------------------------------------------------------------
# Tool sets per agent
# ---------------------------------------------------------------------------

# Search agent — read-only: tree, read, search, concat
SEARCH_TOOLS = [TreeTool, ReadTool, SearchTool, ConcatTool]

# Update agent — full access: everything except concat
UPDATE_TOOLS = [TreeTool, ReadTool, SearchTool, WriteTool, EditTool, AppendTool, MoveTool, DeleteTool]