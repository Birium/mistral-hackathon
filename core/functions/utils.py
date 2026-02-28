from pathlib import Path

from env import env


def _resolve_path(path: str) -> Path:
    """Resolve any vault path to an absolute filesystem path.

    Handles all formats the LLM might produce:
      - bare filename:       "overview.md"       -> VAULT_PATH/overview.md
      - vault-prefixed:      "vault/projects/x/" -> VAULT_PATH/projects/x/
      - root aliases:        ".", "./", "vault/"  -> VAULT_PATH/
    """
    vault_root = Path(env.VAULT_PATH).resolve()
    clean = path.strip()

    # Root aliases → return vault root directly
    if clean in (".", "./", "", "vault", "vault/", "vault/."):
        return vault_root

    # Strip leading "vault/" prefix
    if clean.startswith("vault/"):
        clean = clean[len("vault/"):]

    return vault_root / clean.strip("/")