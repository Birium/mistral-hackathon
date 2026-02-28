from pathlib import Path

from core.functions.utils import _resolve_path
from env import env


def move(from_path: str, to_path: str) -> str:
    vault_root = Path(env.VAULT_PATH).resolve()

    resolved_from = _resolve_path(from_path)
    resolved_to = _resolve_path(to_path)

    # Security: both paths must stay inside vault
    try:
        resolved_from.resolve().relative_to(vault_root)
    except ValueError:
        raise ValueError(f"Source path outside vault: '{from_path}'")

    try:
        resolved_to.resolve().relative_to(vault_root)
    except ValueError:
        raise ValueError(f"Destination path outside vault: '{to_path}'")

    if not resolved_from.exists():
        raise FileNotFoundError(f"Source not found: '{from_path}'")

    from .mover import move as _move

    return _move(resolved_from, resolved_to)
