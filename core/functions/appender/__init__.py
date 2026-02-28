from pathlib import Path

from core.functions.utils import _resolve_path
from env import env

VALID_POSITIONS = {"top", "bottom"}


def append(path: str, content: str, position: str = "top") -> str:
    if not content:
        raise ValueError("content must not be empty")
    if position not in VALID_POSITIONS:
        raise ValueError(f"position must be 'top' or 'bottom', got '{position}'")

    vault_root = Path(env.VAULT_PATH).resolve()
    resolved = _resolve_path(path)

    try:
        resolved.resolve().relative_to(vault_root)
    except ValueError:
        raise ValueError(f"Path outside vault: '{path}'")

    from .appender import append as _append

    return _append(resolved, content, position)
