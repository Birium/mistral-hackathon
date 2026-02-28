import os

SEED_FILES = {
    "overview.md": "---\ncreated: now\nupdated: now\ntokens: 0\n---\n\n# Vault Overview\n\nThis vault is empty.",
    "tree.md": "---\ncreated: now\n---\n\n# Tree\n\n(auto-generated)",
    "profile.md": "---\ncreated: now\n---\n\n# Profile\n\nNo profile yet.",
    "tasks.md": "---\ncreated: now\n---\n\n# Tasks\n",
    "changelog.md": "---\ncreated: now\n---\n\n# Changelog\n",
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
