"""Tree tool — explore vault structure."""

from typing import Optional
from agent.tools.base_tool import BaseTool
from functions.utils import _resolve_path
from functions.tree import get_tree as _tree_impl


def tree(path: str = "", depth: Optional[int] = None) -> str:
    """Explore the structure of the vault with token counts and timestamps.

    Args:
        path: Vault path to scan (e.g. 'vault/', 'vault/projects/startup-x/'). Defaults to the vault root.
        depth: Levels to unfold. None = unlimited, 0 = root only.
    """
    resolved = _resolve_path(path)
    return _tree_impl(path=str(resolved), depth=depth)


TreeTool = BaseTool(tree)


TREE_TOOL_PROMPT = """\
<tree-tool>
Use tree to explore sub-directory contents.

Your initial context includes a `<vault-structure>` block that shows the vault at depth=1.
Folders appear as single entries with a total token count — the individual files inside
are not listed. This means you can see that a bucket folder exists and how heavy it is,
but not what files it contains.

When you need to see the individual files inside a sub-directory — their names, sizes,
timestamps — call tree on that path:
`tree("vault/projects/startup-x/bucket/", depth=1)`

Two things to keep in mind:
First, you rarely need this tool when the question is about a project's core files
(description, state, tasks, changelog). Those are always at the first level and visible
in your vault-structure. Use tree when you need to look inside a bucket or inbox folder
before deciding what to read.
Second, vault-structure is static — it reflects the vault at session start. If the update
agent modifies the vault during a session (not common in search), vault-structure won't
reflect those changes. The tree tool always gives you the live state.
</tree-tool>"""