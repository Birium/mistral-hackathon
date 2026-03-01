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
Read retrieves file contents with line numbers. Your default tool when you know where
information lives — the overview identified the project, the vault-structure confirmed
the file exists, so you read it directly. Do not search first when the destination is
known. Search is for uncertainty; read is for action.

<path-types>
Three types, freely combinable in a single `paths` list:

**Literal path** — one exact file.
`read(["projects/startup-x/state.md"])`

**Directory** — every direct file at that level, non-recursive. Subfolders are not
entered. Use this to load a project's core files in one call, or to see what's inside
a bucket.
`read(["projects/startup-x/"])` → description, state, tasks, changelog (not bucket/).
`read(["projects/startup-x/bucket/"])` → every file in that bucket.

**Glob pattern** — wildcard expansion across the vault. This is the most powerful
capability. One call scans the same file type across every project.

Core glob patterns:
- `projects/*/state.md` — every project's current status snapshot
- `projects/*/description.md` — every project's identity and scope
- `projects/*/changelog.md` — every project's history (combine with `changelog.md` for global)
- `projects/*/tasks.md` — every project's active tasks (combine with `tasks.md` for global)
- `projects/*/bucket/*` — all project bucket files (combine with `bucket/*` for global)
</path-types>

<combined-reads>
Combine paths for multi-source reads in a single call:

Compare two projects:
`read(["projects/startup-x/state.md", "projects/appart-search/state.md"])`

All changelogs everywhere — project-level and global:
`read(["projects/*/changelog.md", "changelog.md"])`

Full project context — core files plus bucket:
`read(["projects/startup-x/", "projects/startup-x/bucket/"])`

Cross-vault status sweep:
`read(["projects/*/state.md", "tasks.md"])`

Load what you need in one call. Multiple paths cost one tool invocation instead of many.
</combined-reads>

<token-guidance>
Load generously. Knowledge tasks benefit from rich context — more information means
better reasoning, not worse. This is the opposite of code generation where precision
degrades with context size.

Under 150k tokens of active context: read without hesitation. A 30k changelog, a 15k
description, five 3k state files in one call — all fine. Do not agonize over whether
a 10k file is "worth" reading. If it might be relevant, read it.

Above 150k tokens: be selective. Target specific files rather than globbing everything.
Use search to locate the exact section you need in very large files, then read only that
file when needed. This threshold is about maintaining response quality, not a hard limit.

Check token counts in your vault-structure before reading large files. A 2k state.md
and a 60k changelog are different decisions — but both are fine to load if you need them,
as long as you stay aware of your cumulative context.
</token-guidance>

<read-vs-search>
**Read when:** the destination is known — you have the project name, the file type, or
a pattern that targets what you need. Read gives you complete content with line numbers,
ready for editing or analysis.

**Search when:** the destination is unknown — you don't know which project holds the
answer, the relevant content could be anywhere, or you need to find a specific passage
buried in a large file without reading the whole thing.

A common effective pattern: search to discover which files are relevant, then read those
files for complete content. Search gives you fragments with scores; read gives you the
full picture.
</read-vs-search>
</read-tool>"""