from pathlib import Path
from env import env
from .deleter import delete as _delete
from core.functions.utils import _resolve_path


def delete(path: str) -> str:
    resolved = _resolve_path(path)

    # Security: must stay inside vault
    resolved.resolve().relative_to(Path(env.VAULT_PATH).resolve())

    if not resolved.exists():
        raise ValueError(f"Path not found: '{path}'")

    return _delete(resolved)