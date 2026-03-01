"""Concat tool — assemble files for final output."""

from agent.tools.base_tool import BaseTool
from functions.concat import concat as _concat_impl


def concat(files: list[dict]) -> str:
    """Assemble an ordered list of vault files into a single structured markdown document.

    Args:
        files: Ordered list of file objects. Each object must have a 'path' (str) and optional 'lines' (str like 'N-M').
    """
    try:
        return _concat_impl(files=files)
    except Exception as e:
        return f"[CONCAT ERROR] Unexpected error: {e}"


ConcatTool = BaseTool(concat)


CONCAT_TOOL_PROMPT = """\
<concat-tool>
Concat assembles an ordered list of vault files into a single structured markdown
document. Each file becomes a fenced code block prefixed by its path, with line
numbers. It is your finalization tool — call it once, as the very last action.

<how-it-works>
When you call concat, the system captures its result and appends it to your text
overview automatically. The final response the user receives is:

  [your text overview]
  [concat result, appended by the system]

Write your overview as plain text, then call concat. The system handles assembly.
</how-it-works>

<rules>
Call concat once, as your final action. After calling concat, produce your text
overview — no further tool calls. The system appends the concat result to complete
the response.

Only include files you actually retrieved during the session via search or read.
Never pass a path you have not confirmed exists.

If you found no relevant files, do not call concat. Return only your text overview
explaining what you searched and that nothing matched.
</rules>

<ordering>
Order by direct relevance — most relevant first. A state.md that directly answers
the question goes before a changelog that provides supporting history.
</ordering>

<line-ranges>
Each file entry accepts an optional `lines` field (format: `"N-M"`) to extract only
a specific range. Use when a search chunk identified the exact section you need and
the full file would add unnecessary context.
</line-ranges>
</concat-tool>"""