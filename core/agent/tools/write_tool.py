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
is yours to define. Parent directories are created automatically — any path you
provide will work, even if none of the intermediate folders exist yet.

Do not include frontmatter fields (`created`, `updated`, `tokens`) — the background
job manages those after every write.

<creating-structures>
Write is your tool for creating complete file structures in a single sequence of
calls. Every call creates its parent directories, so you can build an entire project
or inbox item from scratch by writing its files one after another.

New project — call write once per file:
  `write("projects/new-project/description.md", ...)`
  `write("projects/new-project/state.md", ...)`
  `write("projects/new-project/tasks.md", ...)`
  `write("projects/new-project/changelog.md", ...)`
The `projects/new-project/` folder and any parents are created on the first call.
The `bucket/` subfolder is created whenever a bucket file is first written.

New inbox item — same principle:
  `write("inbox/2025-07-14-description-courte/review.md", ...)`
  `write("inbox/2025-07-14-description-courte/original-content.md", ...)`
The `inbox/2025-07-14-description-courte/` folder is created automatically.

New bucket file at any level:
  `write("bucket/email-client-2025-07.md", ...)`
  `write("projects/startup-x/bucket/meeting-notes-july.md", ...)`

Never hesitate to create the full structure in one pass. Multiple sequential writes
is the intended pattern for new projects and inbox items.
</creating-structures>

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
