"""Edit tool — surgically replace text in a file."""

from agent.tools.tool_base import BaseTool
from functions.edit import edit as _edit_impl


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


EditTool = BaseTool(edit)


EDIT_TOOL_PROMPT = """\
<edit-tool>
Edit modifies a precise section of a file via exact search-and-replace. You provide
the old text and the new text. The tool finds the first occurrence of old_content
and replaces it. Nothing else in the file is touched.

You MUST read the file via `read` before calling edit. Without the exact current
content, you cannot construct a valid old_content. This is a hard precondition —
not a suggestion.

old_content can include line number prefixes from read output (`7  | ## Statut global`).
The tool strips them automatically before matching. This means you can copy directly
from a read result without cleaning it up.

Make old_content unique enough to match exactly one location in the file. If the text
you want to change appears multiple times, include enough surrounding context to
disambiguate. The tool replaces only the first match — if you target the wrong one,
the edit lands in the wrong place.

Use edit for state.md status updates, task metadata changes, overview.md project line
modifications — any case where one section changes and the rest of the file stays identical.
</edit-tool>"""