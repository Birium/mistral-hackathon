"""Move tool — relocate files or folders."""

from agent.tools.base_tool import BaseTool
from functions.move import move as _move_impl


def move(from_path: str, to_path: str) -> str:
    """Move a file or folder to a new location within the vault.

    Args:
        from_path: Vault source path of the file or folder to move.
        to_path: Vault destination path. Parent directories created if needed.
    """
    try:
        return _move_impl(from_path=from_path, to_path=to_path)
    except (ValueError, FileNotFoundError) as e:
        return f"[MOVE ERROR] {e}"
    except (OSError, PermissionError) as e:
        return f"[MOVE ERROR] Could not move '{from_path}': {e}"


MoveTool = BaseTool(move)


MOVE_TOOL_PROMPT = """\
<move-tool>
Move relocates a file or directory from one path to another. Content is untouched —
only the vault position changes. Parent directories at the destination are created
automatically.

<when>
Routing files from an inbox folder to their final destination after user confirmation.
Correcting an initial routing mistake. Relocating inbox folders wholesale when the
entire contents move together.
</when>

<verify>
Confirm the source path exists before calling move — use vault-structure or a prior
read result. A move to a wrong destination is harder to fix than a failed read.
</verify>
</move-tool>"""