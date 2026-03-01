"""Write tool — create or overwrite files."""

from agent.tools.base_tool import BaseTool
from functions.write import write as _write_impl


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


WriteTool = BaseTool(write)


WRITE_TOOL_PROMPT = """\
<write-tool>
Write creates a new file or completely replaces an existing one. The entire content
is yours to define. Parent directories are created automatically if needed.

Do not include frontmatter fields (`created`, `updated`, `tokens`) — the background
job manages those after every write.

<when>
Creating a file that does not exist yet — a new project's description.md, a new
bucket item, an inbox review.md.

Rewriting a file so extensively that surgical editing would be messier than a clean
slate — a full restructuring of state.md, a description.md rebuilt from scratch.
</when>

<not-when>
Adding an entry to a changelog — use append.
Updating a single section of a file — use edit.
Write replaces everything. Be certain that is what you intend.
</not-when>
</write-tool>"""