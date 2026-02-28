from pathlib import Path

from functions.utils import _resolve_path
from env import env

from .reader import read_file, format_pairs
from .folder import expand_folder
from .images import is_image, load_image


def read(
    paths: str | list[str],
    head: int | None = None,
    tail: int | None = None,
) -> str:
    # --- Validate ---
    if isinstance(paths, list) and len(paths) == 0:
        raise ValueError("paths must not be empty")
    if head is not None and tail is not None:
        raise ValueError("head and tail are mutually exclusive")
    if head is not None and head == 0:
        raise ValueError("head must be > 0")
    if tail is not None and tail == 0:
        raise ValueError("tail must be > 0")

    vault_root = Path(env.VAULT_PATH).resolve()
    path_list: list[str] = [paths] if isinstance(paths, str) else paths

    blocks: list[str] = []

    for raw_path in path_list:
        resolved = _resolve_path(raw_path)

        # Security: must stay inside vault
        try:
            resolved.resolve().relative_to(vault_root)
        except ValueError:
            blocks.append(f"[READ ERROR] Path outside vault: '{raw_path}'")
            continue

        if not resolved.exists():
            blocks.append(f"[READ ERROR] Path not found: '{raw_path}'")
            continue

        if resolved.is_dir():
            files = expand_folder(resolved)
            if not files:
                blocks.append(f"```{raw_path}\n(empty folder)\n```")
            for file_path in files:
                blocks.append(_read_one(file_path, str(file_path), head, tail))
        else:
            blocks.append(_read_one(resolved, raw_path, head, tail))

    return "\n\n".join(blocks)


def _read_one(
    resolved: Path, display_path: str, head: int | None, tail: int | None
) -> str:
    """Read a single file and return a fenced block string."""
    if is_image(resolved):
        return load_image(resolved)

    try:
        pairs = read_file(resolved, head, tail)
    except (OSError, PermissionError) as e:
        return f"[READ ERROR] Could not read '{display_path}': {e}"

    body = format_pairs(pairs)
    return f"```{display_path}\n{body}\n```"
