import os
from pathlib import Path
from typing import Union

from functions.frontmatter import update_tokens
from functions.frontmatter.io import write_frontmatter

_VAULT = os.getenv("VAULT_PATH", "")


def create_file(path: Union[str, Path], body: str = "") -> Path:
    """Create a new Markdown file with valid frontmatter inside the vault.

    `path` is resolved relative to VAULT_PATH if not absolute.
    Raises RuntimeError if VAULT_PATH is not set.
    Raises ValueError if the resolved path escapes the vault.
    Creates parent directories if needed, writes frontmatter, computes token count.
    Returns the resolved Path.
    """
    if not _VAULT:
        raise RuntimeError("VAULT_PATH env var is not set")

    vault = Path(os.path.normpath(_VAULT))
    p = Path(os.path.normpath(vault / path))

    if not str(p).startswith(str(vault)):
        raise ValueError(f"Path must be within vault: {p}")

    p.parent.mkdir(parents=True, exist_ok=True)
    write_frontmatter(p, data={}, body=body)
    update_tokens(p)
    return p
