"""Read tool — retrieve file content from the vault with line numbers."""

from typing import Optional
from agent.tools.base_tool import BaseTool
from functions.read import read as _read_impl


def read(paths: list[str], head: Optional[int] = None, tail: Optional[int] = None) -> str:
    """Read one or more files or folders from the vault, with line numbers.

    Args:
        paths: List of vault paths. Each path may be a file or a folder (folder = all direct files, non-recursive).
        head: Approximate token budget from the start of each file.
        tail: Approximate token budget from the end of each file. head and tail are mutually exclusive.
    """
    try:
        return _read_impl(paths=paths, head=head, tail=tail)
    except ValueError as e:
        return f"[READ ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[READ ERROR] {e}"


ReadTool = BaseTool(read)


READ_TOOL_PROMPT = """\
<read-tool>
Read is your default tool for retrieving file content. When you know where the
information lives — because the overview identified the project, or the vault-structure
showed the file — read it directly. Do not search first. Read is always the simpler
and more reliable path when the destination is known.

**Token budget — always check before reading.**
Your vault-structure and tree tool shows token counts for every file. Consult them before calling read.
A rough guide:
- Under 5k tokens: read whole, no concern.
- 5k–20k tokens: read whole if directly relevant, use head/tail if you only need
  a specific section (recent entries, current status).
- 20k–50k tokens: use head or tail. Read whole only if you have strong reason to believe
  the entire file is needed.
- Above 50k tokens: never read whole. Use head for newest-first files (changelogs),
  tail for bottom-appended files (tasks), or rely on search chunks to locate the
  relevant section first.

Never load more than roughly 50k tokens of content across a single read call
without a deliberate reason. If you need multiple large files, split into separate
read calls across loop iterations so you can evaluate each result before proceeding.

**head and tail parameters.**
`head=N` returns approximately N tokens from the start of the file.
`tail=N` returns approximately N tokens from the end.
They are mutually exclusive. Use head on changelogs (newest-first, recent entries at top).
Use tail on files where new content is appended at the bottom.

**Reading directories.**
Pass a directory path to get all direct files at that level, non-recursively:
`read(["vault/projects/startup-x/"])` returns description, state, tasks, changelog —
but not the bucket sub-directory. To read bucket contents:
`read(["vault/projects/startup-x/bucket/"])`.

**Batching multiple files.**
Read multiple files in a single call when they are all needed and their combined
token count stays within budget:
`read(["vault/projects/startup-x/state.md", "vault/projects/appart-search/state.md"])`.
Batching is efficient but respect the total — check each file's token count in
vault-structure before combining them.
</read-tool>"""