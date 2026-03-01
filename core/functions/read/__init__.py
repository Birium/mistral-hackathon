from pathlib import Path

from functions.utils import _resolve_path
from env import env

from .reader import read_file, format_pairs
from .folder import expand_folder
from .images import is_image, load_image


GLOB_CHARS = {"*", "?", "["}


def _has_glob(path: str) -> bool:
    return any(c in path for c in GLOB_CHARS)


def _normalize_pattern(raw: str) -> str:
    """Strip 'vault/' prefix and leading/trailing slashes for glob resolution."""
    clean = raw.strip()
    if clean.startswith("vault/"):
        clean = clean[len("vault/"):]
    return clean.strip("/")


def _expand_glob(pattern: str, vault_root: Path) -> list[Path]:
    """Expand a glob pattern relative to the vault root, returning only files."""
    normalized = _normalize_pattern(pattern)
    matches = sorted(vault_root.glob(normalized))
    return [m for m in matches if m.is_file()]


def _display_path(file_path: Path, vault_root: Path) -> str:
    """Build a vault-relative display path like 'vault/projects/x/state.md'."""
    rel = file_path.relative_to(vault_root)
    return f"vault/{rel}"


def read(paths: list[str]) -> str:
    """Read files from the vault. Supports literal paths, directories, and glob patterns."""
    if not paths:
        raise ValueError("paths must not be empty")

    vault_root = Path(env.VAULT_PATH).resolve()
    blocks: list[str] = []

    for raw_path in paths:
        if _has_glob(raw_path):
            files = _expand_glob(raw_path, vault_root)
            if not files:
                blocks.append(f"[READ] No files matched pattern: '{raw_path}'")
                continue
            for file_path in files:
                display = _display_path(file_path, vault_root)
                blocks.append(_read_one(file_path, display))
        else:
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
                    display = _display_path(file_path, vault_root)
                    blocks.append(_read_one(file_path, display))
            else:
                blocks.append(_read_one(resolved, raw_path))

    return "\n\n".join(blocks)


def _read_one(resolved: Path, display_path: str) -> str:
    """Read a single file and return a fenced block string."""
    if is_image(resolved):
        return load_image(resolved)

    try:
        pairs = read_file(resolved)
    except (OSError, PermissionError) as e:
        return f"[READ ERROR] Could not read '{display_path}': {e}"

    body = format_pairs(pairs)
    return f"```{display_path}\n{body}\n```"