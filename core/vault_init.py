import os

from functions.frontmatter.layout import FM

def _fm(body: str) -> str:
    lines = ["---", ""] * 5
    lines[FM.delimiter_start] = "---"
    lines[FM.created] = f"{FM.created_key}: now"
    lines[FM.updated] = f"{FM.updated_key}: now"
    lines[FM.tokens] = f"{FM.tokens_key}: 0"
    lines[FM.delimiter_end] = "---"
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
    vault_path = os.getenv("VAULT_PATH", "/vault")
    for dir_name in SEED_DIRS:
        os.makedirs(f"{vault_path}/{dir_name}", exist_ok=True)
    for filename, content in SEED_FILES.items():
        path = f"{vault_path}/{filename}"
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(content)
