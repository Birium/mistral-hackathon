"""Delete tool — permanently remove files or folders."""

from agent.tools.base_tool import BaseTool
from functions.delete import delete as _delete_impl


def delete(path: str) -> str:
    """Permanently delete a file or folder (recursive) from the vault.

    Args:
        path: Vault path of the file or folder to delete.
    """
    try:
        return _delete_impl(path=path)
    except ValueError as e:
        return f"[DELETE ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[DELETE ERROR] Could not delete '{path}': {e}"


DeleteTool = BaseTool(delete)


DELETE_TOOL_PROMPT = """\
<delete-tool>
Delete permanently removes a file or an entire directory recursively. There is no
trash, no archive, no recovery. Be certain before calling this tool.

<when>
Removing an inbox folder after resolution. The sequence is always: route the files
to their destination, log the operation in global changelog, then delete the inbox
folder. Never delete before routing and logging.
</when>

<never>
Do not delete files to "clean up" content that might still be useful. If uncertain,
leave the file in place and flag it in your changelog entry. Deletion is irreversible
— history lives in the changelog, not in deleted files.
</never>
</delete-tool>"""