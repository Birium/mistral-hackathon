"""Read tool — retrieve file content from the vault with line numbers."""

from agent.tools.base_tool import BaseTool
from functions.read import read as _read_impl


def read(paths: list[str]) -> str:
    """Read files from the vault with line numbers. Supports exact paths, directories, and glob patterns.

    Args:
        paths: Vault paths to read. Each entry can be an exact file, a directory (returns all direct files non-recursively), or a glob pattern (e.g. 'projects/*/state.md').
    """
    try:
        return _read_impl(paths=paths)
    except ValueError as e:
        return f"[READ ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[READ ERROR] {e}"


ReadTool = BaseTool(read)


READ_TOOL_PROMPT = """\
<read-tool>
Read is the targeted retrieval tool. It loads file contents with line numbers when you
know where the information lives — the overview identified the project, the vault-structure
confirmed the file exists, or a previous search pointed you there.

<path-types>
Three types, freely combinable in a single `paths` list:

Literal path — one exact file.
`read(["projects/startup-x/state.md"])`

Directory — every direct file at that level, non-recursive. Subfolders are not entered.
`read(["projects/startup-x/"])` → description, state, tasks, changelog (not bucket/).
`read(["projects/startup-x/bucket/"])` → every file in that bucket.

Glob pattern — wildcard expansion across the vault. One call scans the same file type
across every project.

Core patterns:
- `projects/*/state.md` — every project's current status
- `projects/*/description.md` — every project's identity and scope
- `projects/*/changelog.md` — every project's history
- `projects/*/tasks.md` — every project's active tasks
- `projects/*/bucket/*` — all project bucket files
</path-types>

<combined-reads>
Combine paths for multi-source reads in a single call:

Compare two projects:
`read(["projects/startup-x/state.md", "projects/appart-search/state.md"])`

All changelogs everywhere:
`read(["projects/*/changelog.md", "changelog.md"])`

Full project context:
`read(["projects/startup-x/", "projects/startup-x/bucket/"])`

Cross-vault status sweep:
`read(["projects/*/state.md", "tasks.md"])`

Multiple paths cost one tool invocation instead of many.
</combined-reads>

<token-guidance>
Load generously. Knowledge tasks benefit from rich context — more information means
better reasoning, not worse.

Under 150k tokens of active context: read without hesitation. A 30k changelog, a 15k
description, five 3k state files in one call — all fine. Do not agonize over whether
a 10k file is "worth" reading. If it might be relevant, read it.

Above 150k tokens: be selective. Target specific files rather than globbing everything.
Use search to locate the exact section you need in very large files. Check token counts
in your vault-structure before reading large files.
</token-guidance>
</read-tool>"""
