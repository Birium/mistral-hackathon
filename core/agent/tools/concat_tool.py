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
Concat is your finalization tool. It assembles an ordered list of vault files into
a single structured markdown document where each file becomes a fenced code block
prefixed by its path, with line numbers.

**How the system uses concat output:**
When you call concat, the system automatically captures its result and appends it
to your text response to form the final answer. You do not need to format or include
the file contents yourself. The final answer the user receives is:

  [your text overview]
  [concat result, appended automatically by the system]

This means your job is simple: write your overview as plain text, then call concat
once with the files that answer the question. The system handles the rest.

**Rules:**
Call concat once, as the very last action of your session. After calling concat, you will produce your overview without any tool calls. 
The system will append the concat result to your overview to create the final answer.

Only concat files you actually retrieved during the session via search, read, or tree.
Never pass a path you haven't confirmed exists.

If you found no relevant files — your search returned nothing, your reads yielded no
matching content — do not call concat. Return only your text overview explaining what
you searched, where you looked, and that no matching information was found.

**Ordering:**
Order files by direct relevance to the question — most relevant first.
A state.md that directly answers "where does this project stand?" goes before a changelog
that provides supporting history.

**Line ranges:**
Each file entry can include an optional `lines` field (format: "N-M") to extract only
a specific range instead of the full file. Use this when you identified the relevant
section via search chunks and don't need the entire file.
</concat-tool>"""