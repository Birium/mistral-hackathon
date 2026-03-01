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

### ✅ **Phase 2 : Rationalisation des Tools et Suppression de Tree**

-   **Gestion du Tool Tree (`core/agent/tools/tree_tool.py`) :**
    -   **Simplification de l'interface :** Retrait du paramètre `depth` dans le wrapper du tool. L'agent n'a plus à gérer la profondeur de scan ; l'outil a été configuré pour renvoyer la structure complète par défaut, simplifiant la prise de décision.
    -   **Refonte du Prompt :** Réécriture complète au format XML strict, définissant clairement les cas d'usage (état "live" après modification vs structure statique initiale).

-   **Désactivation du Tool Tree pour les Agents :**
    -   **Décision d'architecture :** Retrait complet du tool `tree` des agents `SearchAgent` et `UpdateAgent`.
    -   **Justification :** L'injection de la structure complète du vault (`<vault-structure>`) dès le contexte initial rend l'usage d'un tool dédié redondant et coûteux en actions. L'agent possède déjà la carte complète.
    -   **Implémentation :** Suppression des imports `TreeTool` et de leur injection dans les listes `tools=[]` des définitions d'agents. Le fichier `tree_tool.py` reste présent dans la codebase (débranché) pour un usage futur potentiel.

-   **Nettoyage Transversal des Prompts (`core/agent/prompts/`) :**
    -   **Systèmes Prompts :** Retrait de l'injection de `TREE_TOOL_PROMPT` dans `SEARCH_SYSTEM_PROMPT` et `UPDATE_SYSTEM_PROMPT`.
    -   **Context Prompt :** Nettoyage des mentions obsolètes concernant la profondeur limitée (`depth=1`) et les stratégies de lecture partielle (`head`/`tail`) dans la description de `<vault-structure>`.
    -   **Références Indirectes :** Mise à jour des prompts de `concat_tool`, `move_tool` et `env_prompt` pour éliminer les suggestions d'utiliser `tree`. Les agents sont désormais orientés exclusivement vers l'usage de `read` et `search` pour l'exploration.