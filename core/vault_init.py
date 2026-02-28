import os

from functions.frontmatter.layout import FM

def _fm(body: str) -> str:
    lines = []
    lines.append("---")
    lines.append(f"{FM.created_key}: 2026-02-28 15:20:07.560840")
    lines.append(f"{FM.updated_key}: 2026-02-28 15:20:07.560840")
    lines.append(f"{FM.tokens_key}: 0")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body

SEED_FILES = {
    "overview.md": _fm("# Vault Overview\n\nThis vault is empty."),
    "tree.md": _fm("# Tree\n\n(auto-generated)"),
    "profile.md": _fm("# Profile\n\nNo profile yet."),
    "tasks.md": _fm("# Tasks\n"),
    "changelog.md": _fm("# Changelog\n"),
}
SEED_DIRS = ["inbox", "bucket", "projects"]

def init_vault():
    vault_path = os.getenv("VAULT_PATH", "")
    if not vault_path:
        raise RuntimeError("VAULT_PATH env var is not set")
    for dir_name in SEED_DIRS:
        os.makedirs(f"{vault_path}/{dir_name}", exist_ok=True)
    for filename, content in SEED_FILES.items():
        path = f"{vault_path}/{filename}"
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(content)
