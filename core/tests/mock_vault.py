"""
Creates a realistic mock vault under a temp directory for testing.

Usage:
    python tests/mock_vault.py        # prints vault path
    python tests/mock_vault.py --keep # keeps the dir, prints path
"""

import sys
import tempfile
from pathlib import Path

VAULT_FILES = {
    "overview.md": "---\ntokens: 0\n---\n\n# Vault Overview\n",
    "tree.md": "---\ntokens: 0\n---\n\n# Tree\n",
    "profile.md": "---\ntokens: 0\n---\n\n# Profile\n\nUser: Alice\n",
    "changelog.md": "---\ntokens: 0\n---\n\n# Changelog\n\n## [décision] Architecture\nWe chose FastAPI over Django.\n",
    "tasks.md": "---\ntokens: 0\n---\n\n# Tasks\n\n- [ ] prio: haute — fix auth bug\n- [x] prio: basse — update readme\n",
    "inbox/pending.md": "---\ntokens: 0\n---\n\n# Pending item\n\nAwaiting user input.\n",
    "bucket/note-001.md": "---\ntokens: 0\n---\n\n# Note\n\nRue de Rivoli, appartement T3, 1200€/mois.\n",
    "projects/startup-x/description.md": "---\ntokens: 0\n---\n\n# Startup X\n\nB2B SaaS for invoice management.\n",
    "projects/startup-x/state.md": (
        "---\ntokens: 0\n---\n\n# State\n\n## Focus actuel\n"
        "Intégration du module de paiement.\n\n## Ce qui bloque\n"
        "API externe : prestataire indisponible avant juin.\n"
    ),
    "projects/startup-x/tasks.md": "---\ntokens: 0\n---\n\n# Tasks\n\n- [ ] prio: haute — intégration paiement\n",
    "projects/startup-x/changelog.md": (
        "---\ntokens: 0\n---\n\n# Changelog\n\n"
        "## [décision] Abandon de l'API externe\n"
        "Le prestataire ne peut pas livrer avant juin.\n"
        "Impact : internalisation du module paiement.\n"
    ),
    "projects/appart-search/description.md": "---\ntokens: 0\n---\n\n# Appart Search\n\nFinding a flat in Paris.\n",
    "projects/appart-search/state.md": "---\ntokens: 0\n---\n\n# State\n\nEn avance sur planning.\n",
}


def create_mock_vault(base: Path) -> Path:
    vault = base / "vault"
    for rel_path, content in VAULT_FILES.items():
        target = vault / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return vault


if __name__ == "__main__":
    keep = "--keep" in sys.argv
    if keep:
        tmp = Path(tempfile.mkdtemp())
    else:
        tmp = Path(tempfile.mkdtemp())

    vault = create_mock_vault(tmp)
    print(vault)
