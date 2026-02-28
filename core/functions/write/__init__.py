from core.functions.utils import _resolve_path
from env import env
from pathlib import Path
from .writer import write as _write

def write(path: str, content: str) -> str:
    if not content:
        raise ValueError("content must not be empty")

    vault_root = Path(env.VAULT_PATH).resolve()
    resolved = _resolve_path(path)

    # Security: must stay inside vault
    resolved.resolve().relative_to(vault_root)  # raises ValueError if outside

    return _write(resolved, content)