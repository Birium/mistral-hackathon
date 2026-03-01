"""Tree tool — explore vault structure."""

from agent.tools.base_tool import BaseTool
from functions.utils import _resolve_path
from functions.tree import get_tree as _tree_impl


def tree(path: str = "") -> str:
    """Explore the structure of the vault with token counts and timestamps.

    Args:
        path: Vault path to scan (e.g. 'projects/startup-x/'). Defaults to the vault root.
    """
    resolved = _resolve_path(path)
    return _tree_impl(path=str(resolved))


TreeTool = BaseTool(tree)


TREE_TOOL_PROMPT = """\
<tree-tool>
Tree scans a directory and returns its complete structure — every file and folder
with token counts and timestamps. This is your structural reconnaissance tool.

<vault-structure-vs-tree>
Your initial context includes a `<vault-structure>` block — the full vault tree
generated at session start. This is a static snapshot. It does not update if files
are created, moved, or deleted during the session.

Tree gives you the live state. Two scenarios where this matters:

**After vault modifications.** If the update agent wrote, moved, or deleted files
during this session, vault-structure is stale. Tree shows what actually exists now.

**Sub-directory exploration.** When you need to see exactly what's inside a specific
folder before deciding what to read — a bucket with unknown contents, an inbox folder
with multiple items, a project directory you haven't inspected yet.

If vault-structure already answers your question — do not call tree. It adds a tool
call for information you already have.
</vault-structure-vs-tree>

<usage-patterns>
**Scan a specific directory:**
`tree("projects/startup-x/bucket/")` — see every file in a project's bucket
with sizes and dates, before deciding what to read.

`tree("inbox/")` — list all pending inbox folders with their contents.

`tree("projects/startup-x/")` — full project structure including nested folders.

**Scan the entire vault:**
`tree()` — regenerate the complete vault tree. Use after a batch of modifications
to verify the final state, or when vault-structure might be outdated.
</usage-patterns>

<reading-the-output>
Tree output shows token counts and relative timestamps for every entry:

```
projects/startup-x/                [45.2k · 2h ago]
├── bucket/                        [12.1k · 3d ago]
│   ├── email-client-2025-07.md    [4.2k · 3d ago]
│   └── notes-meeting.md           [7.9k · 5d ago]
├── changelog.md                   [28.4k · 2h ago]
├── description.md                 [1.8k · 14d ago]
├── state.md                       [890 · 2h ago]
└── tasks.md                       [2.1k · 6d ago]
```

Token counts are your budget signal — check them before calling read. A 890-token
state.md loads instantly. A 28.4k changelog is fine to read whole under 150k context.
Timestamps tell you what changed recently — useful for prioritizing reads when
investigating recent activity.
</reading-the-output>
</tree-tool>"""