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

### ✅ **Phase 3 : Refonte des Prompts d'Environnement et de Boucle Agentique**

-   **Restructuration de l'Environnement (`core/agent/prompts/env_prompt.py`) :**
    -   **Arbre ASCII visuel (`<vault-layout>`) :** Remplacement des longues descriptions textuelles par une représentation visuelle canonique de la hiérarchie du vault. Ajout d'annotations inline (`←`) pour une compréhension immédiate du rôle de chaque dossier/fichier. Retrait définitif de `tree.md` de cette structure statique.
    -   **Références denses (`<file-reference>`) :** Compression drastique des descriptions de fichiers (Root, Project, Inbox, Bucket) en 1 à 2 lignes concises, éliminant la prose redondante.
    -   **Spécifications de formats (`<formats>`) :** Intégration d'exemples de code concrets inline pour dicter la structure attendue : Changelogs (H1 pour la date, H2 pour l'entrée, tag `[décision]`), Tasks (métadonnées inline sous le H1), et Frontmatter (avec la consigne stricte de laisser le background job le gérer).
    -   **Indexation de recherche (`<search-index>`) :** Transformation des explications verbeuses en une liste binaire ultra-scannable (✓ Indexé / ✗ Non indexé) justifiant l'usage de `search` vs `read`.
    -   **Fusion du Contexte Initial (`<initial-context>`) :** Migration complète du contenu de l'ancien `context_prompt.py` directement à la fin de l'environnement. Définit clairement les 4 blocs injectés au démarrage (`<date>`, `<overview>`, `<vault-structure>`, `<profile>`).

-   **Philosophie de la Boucle Agentique (`core/agent/prompts/agent_loop_prompt.py`) :**
    -   **Philosophie de chargement généreux (`<context-loading-philosophy>`) :** Introduction d'un changement de paradigme majeur. Le prompt explique désormais explicitement pourquoi les tâches de connaissance (contrairement à la génération de code) bénéficient d'un contexte massif pour améliorer le raisonnement, le routage et la détection de contradictions.
    -   **Seuil opérationnel des 150k tokens :** Instruction donnée à l'agent de charger les fichiers sans aucune hésitation ni micro-optimisation tant que le contexte actif reste sous les 150k tokens. Au-delà, l'agent doit basculer sur une stratégie sélective via `search`.
    -   **Mécanique de boucle (`<loop-mechanics>`) :** Obligation d'analyser la carte initiale (overview/vault-structure) avant le premier appel outil, directive de "batcher" les lectures pour maximiser la vitesse, et nécessité d'itérer avec de nouveaux angles si la première passe échoue.
    -   **Conditions d'arrêt (`<stopping>`) :** Définition stricte de la fin de tâche : l'agent doit s'arrêter dès que sa réponse est ancrée dans les données lues, sans sur-explorer. Autorisation explicite de répondre qu'une information est introuvable si le vault ne la contient pas.

-   **Nettoyage et Architecture des Prompts :**
    -   **Suppression de `core/agent/prompts/context_prompt.py` :** Fichier vidé et retiré de l'architecture suite à la migration de son contenu vers `env_prompt.py`.
    -   **Mise à jour des Agents (`search_agent_prompt.py` & `update_agent_prompt.py`) :** Retrait des imports obsolètes et de l'injection de `INITIAL_CONTEXT_PROMPT`. Les agents héritent désormais de l'intégralité du contexte via le seul import de `ENVIRONMENT_PROMPT`.
  
### ✅ **Phase 4 : Refonte XML Globale et Élévation de la Stratégie de Navigation**

-   **Élévation de la Stratégie de Navigation (Agent Loop) :**
    -   **Centralisation de la dichotomie Search vs Read :** La philosophie expliquant quand chercher (scan) et quand lire (targeted retrieval) a été extraite des prompts individuels des outils pour être placée au cœur de la boucle agentique. Cela évite la duplication et positionne cette logique comme une compétence fondamentale de raisonnement plutôt que comme une simple notice d'utilisation d'outil.
    -   **`core/agent/prompts/agent_loop_prompt.py` :** Ajout d'une section `<navigation>` détaillant le flux naturel (scan d'abord pour s'orienter, read ensuite pour approfondir) et d'une directive `<speed>` imposant à l'agent de privilégier les actions en lots (batch) et les décisions rapides.

-   **Refonte des Prompts Systèmes (Agents) :**
    -   **Transition vers un format XML strict :** Remplacement complet de la prose Markdown verbeuse par des structures XML denses (`<tags>`). Ce format est optimisé pour la compréhension par le LLM, réduisant le bruit tout en conservant 100% des instructions comportementales.
    -   **`core/agent/prompts/search_agent_prompt.py` :** Restructuration de `SEARCH_SYSTEM_PROMPT`. La stratégie a été épurée des redondances avec l'agent loop pour se concentrer sur un mapping direct via `<by-question-type>` (ex: question de statut → `state.md`, historique → changelog). Les règles ont été isolées dans des balises `<rule>` individuelles.
    -   **`core/agent/prompts/update_agent_prompt.py` :** Refonte de `UPDATE_SYSTEM_PROMPT`. La logique complexe a été segmentée en blocs clairs : `<verify-before-writing>`, `<route-by-signal>`, et `<file-routing>`. Réintégration explicite d'une instruction cruciale dans `<inbox-ref-handling>` : l'obligation d'utiliser le `review.md` comme pont entre deux sessions pour ne pas recommencer le raisonnement de zéro.

-   **Refonte des Outils Principaux (Search & Read) :**
    -   **Clarification des rôles et ajout de métriques :** Les outils se définissent désormais uniquement par *comment* les utiliser, la stratégie du *quand* ayant été déléguée à l'agent loop.
    -   **`core/agent/tools/search_tool.py` :** Refonte majeure de `SEARCH_TOOL_PROMPT`. Ajout de timings explicites (`fast` = instantané, `deep` = ~10 secondes) pour guider les choix de vitesse de l'agent. Introduction d'une heuristique simple ("If you can name it, fast. If you can only describe it, deep.") et d'une section `<examples>` fournissant 5 scénarios end-to-end concrets illustrant quand utiliser Search vs Read.
    -   **`core/agent/tools/read_tool.py` :** Nettoyage de `READ_TOOL_PROMPT`. Retrait de la section comparative `read-vs-search` et redéfinition simple de l'outil comme le "targeted retrieval tool".

-   **Compression XML des Outils Secondaires :**
    -   **Standardisation du format :** Application d'une passe rapide de compression sur tous les outils restants pour aligner l'ensemble de la codebase sur le nouveau standard XML, sans altérer la logique sous-jacente.
    -   **`core/agent/tools/append_tool.py` :** Structuration en `<position>`, `<creates-files>`, et `<duplicate-dates>`.
    -   **`core/agent/tools/write_tool.py` :** Simplification via une dichotomie claire `<when>` et `<not-when>`.
    -   **`core/agent/tools/edit_tool.py` :** Isolation des contraintes dans `<precondition>` (obligation de lire avant d'éditer) et `<matching>`.
    -   **`core/agent/tools/move_tool.py` :** Ajout de la balise `<verify>` pour forcer la vérification des chemins sources.
    -   **`core/agent/tools/delete_tool.py` :** Explicitation de la séquence stricte (route → log → delete) dans `<when>` et interdiction du nettoyage spéculatif dans `<never>`.
    -   **`core/agent/tools/concat_tool.py` :** Compression de l'explication du mécanisme système dans `<how-it-works>` et mise en liste des règles d'ordonnancement et de filtrage.