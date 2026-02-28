from pathlib import Path
from typing import Optional

from core.functions.utils import _resolve_path
from env import env

from .concat import concat as _concat


def concat(files: list[dict]) -> str:
    """
    Assemble an ordered list of vault files into a single markdown document.

    Each item in `files` must have:
      - path  (str)            : vault path
      - lines (str | None)     : line range "N-M", or null for the full file
    """
    if not files:
        return ""

    vault_root = Path(env.VAULT_PATH).resolve()
    blocks: list[str] = []

    for item in files:
        path: str = item.get("path", "")
        lines: Optional[str] = item.get("lines") or None  # "" → None

        resolved = _resolve_path(path)

        # Security: must stay inside vault
        try:
            resolved.resolve().relative_to(vault_root)
        except ValueError:
            blocks.append(f"[CONCAT ERROR] Path escapes vault: '{path}'")
            continue

        block = _concat(path=path, resolved=resolved, lines=lines)
        blocks.append(block)

    return "\n\n".join(blocks)