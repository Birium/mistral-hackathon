### ✅ **Phase 1 : Refonte du Tool Read et Philosophie de Context Loading**

-   **Refactoring du Tool Read (`core/functions/read/`) :**
    -   **Suppression de la lecture partielle (`head`/`tail`) :** Simplification radicale de `reader.py` et `__init__.py`. Le tool lit désormais systématiquement les fichiers dans leur intégralité. Les paramètres `head` et `tail` ont été retirés de la signature, de la validation et de l'implémentation.
    -   **Support des wildcards (Glob Patterns) :** Ajout de la capacité à résoudre des patterns glob (ex: `projects/*/state.md`) directement dans `read()`. Implémentation des fonctions internes `_has_glob`, `_normalize_pattern`, et `_expand_glob` pour détecter et itérer sur les fichiers correspondants à travers tout le vault.
    -   **Normalisation des chemins :** Ajout de `_display_path` pour garantir que les fichiers lus via l'expansion glob conservent un chemin d'affichage relatif propre (ex: `vault/projects/x/state.md`) dans l'en-tête du bloc markdown retourné.

-   **Mise à jour du Prompt et de la Signature (`core/agent/tools/read_tool.py`) :**
    -   **Nouvelle Signature :** Le tool accepte désormais uniquement une liste de chemins (`paths: list[str]`), documentée pour supporter les chemins exacts, les dossiers (lecture non-récursive des fichiers directs), et les patterns glob.
    -   **Réécriture de `READ_TOOL_PROMPT` (Structure XML) :** Remplacement de l'ancienne prose markdown verbeuse par des balises XML strictes et denses (`<read-tool>`, `<path-types>`, `<combined-reads>`, `<token-guidance>`, `<read-vs-search>`).
    -   **Exemples Concrets de Patterns :** Intégration de cas d'usage combinés directement exploitables par l'agent (ex: `read(["projects/*/changelog.md", "changelog.md"])` pour charger tous les historiques d'un coup, ou la comparaison multi-projets).
    -   **Nouvelle Philosophie Token :** Instruction explicite de charger le contexte généreusement. L'agent est désormais encouragé à lire sans hésiter sous la barre des 150k tokens de contexte actif. Suppression de l'ancienne micro-optimisation par paliers (5k, 20k, 50k) qui limitait la capacité de raisonnement sur les tâches de connaissance.

-   **Ajustements Annexes :**
    -   **`core/agent/agent/context.py` :** Modification de l'appel au tool tree pour la construction du contexte initial (`tree()` au lieu de `tree(depth=1)`), s'alignant sur la nouvelle directive d'exposer la structure complète sans restriction de profondeur.
    -   **`core/sandbox.py` :** Création d'un script de test minimaliste pour valider l'exécution et le rendu de `load_vault_context()`.