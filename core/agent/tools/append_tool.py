"""Append tool — insert content at the top or bottom of a file."""

from agent.tools.base_tool import BaseTool
from functions.appender import append as _append_impl


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


AppendTool = BaseTool(append)


APPEND_TOOL_PROMPT = """\
<append-tool>
Append inserts a markdown block into a file without reading it first. This is the
zero-read insertion tool — its value is that it never loads existing content into
context.

<position>
`top` — inserts after the closing `---` of frontmatter. Use for changelogs: they are
newest-first, so new entries go at the top. A changelog with 300 days of history at
60k tokens gets a new entry without loading a single token of past content.

`bottom` — appends at the end. Use for tasks.md, where new tasks are added last.
</position>

<creates-files>
If the file does not exist, append creates it. Include full content in that case —
but omit frontmatter fields (`created`, `updated`, `tokens`), those are managed by
the background job.
</creates-files>

<duplicate-dates>
Two identical H1 dates in a changelog are explicitly acceptable. If you append a
`# 2025-07-14` block and one already exists, the file will have two — marking two
distinct update moments for the same day. Do not try to merge with an existing H1
date. That would require reading the file, which defeats the purpose of append.
</duplicate-dates>
</append-tool>"""