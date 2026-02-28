### ✅ **Phase 1 : Implémentation de l'Architecture Agentique de Base (LLM & CLI)**

-   **Configuration & Environnement :**
    -   **Gestion des dépendances :** Mise à jour de `pyproject.toml` pour inclure `openai` (client compatible OpenRouter) et `pydantic-settings`. Retrait volontaire de `langchain` pour garder une architecture légère et sur-mesure.
    -   **Variables d'environnement :** Création de `core/env.py` utilisant `pydantic-settings` pour typer et valider les variables `OPENROUTER_API_KEY` et `VAULT_PATH`. Ajout d'un `.env.example`.

-   **Schémas de Données (Schemas) :**
    -   **[`schemas/message.py`] :** Définition des classes de messages (`Message`, `SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage`) avec des méthodes `to_dict()` pour sérialiser proprement les échanges vers l'API sans dépendre de LangChain.
    -   **[`schemas/event.py`] :** Création des modèles Pydantic pour le streaming d'événements (`ThinkEvent`, `AnswerEvent`, `ToolEvent`, `UsageEvent`, `ErrorEvent`), permettant au client de réagir dynamiquement à chaque étape de la réflexion du LLM.
    -   **[`schemas/tool.py`] :** Implémentation de la classe `ToolCall` pour représenter et manipuler les appels d'outils demandés par le LLM, incluant le parsing des arguments JSON et le formatage des résultats en `ToolMessage`.

-   **Client LLM (OpenRouter) :**
    -   **[`llm/config.py`] :** Configuration du modèle par défaut (`DEFAULT_MODEL`) pointant vers `google/gemini-2.5-flash` via OpenRouter, avec la logique de calcul des coûts (`CostDetails`) basée sur les tokens en entrée et en sortie.
    -   **[`llm/client.py`] :** Création du `LLMClient` utilisant le SDK `openai`. Implémentation de la méthode `stream()` qui gère la communication avec l'API, parse les chunks en temps réel (texte, réflexion, usage), et exécute les appels d'outils de manière *inline*. Le paramètre `reasoning_effort` a été conservé et intégré aux paramètres de l'API.

-   **Architecture Agentique :**
    -   **[`agent/base_agent.py`] :** Création de la classe `BaseAgent` qui orchestre la boucle de raisonnement. Implémentation d'une boucle à deux passes (`_loop`) : un premier appel LLM, la détection et l'exécution des outils, puis un second appel LLM avec les résultats injectés dans le contexte. Intégration d'une méthode `_display` pour le rendu visuel dans le terminal.
    -   **[`prompts/update_prompt.py` & `prompts/search_prompt.py`] :** Création des instructions système (system prompts) minimalistes (placeholders) définissant les rôles respectifs des agents de mise à jour (écriture/routing) et de recherche (lecture seule).
    -   **[`agent/update_agent.py`] :** Implémentation de l'`UpdateAgent`. Surcharge de la méthode `process()` pour charger automatiquement le contexte initial du vault (`overview.md`, `tree.md`, `profile.md`) avant d'y concaténer l'input utilisateur et l'éventuelle référence d'inbox (`inbox_ref`).
    -   **[`agent/search_agent.py`] :** Implémentation du `SearchAgent` sur le même modèle que l'UpdateAgent, mais dédié aux requêtes en lecture seule.

-   **Interface Utilisateur (CLI) :**
    -   **[`terminal.py`] :** Création du point d'entrée interactif en ligne de commande. Mise en place d'une boucle permettant à l'utilisateur de choisir le mode (`update` ou `search`), d'instancier l'agent correspondant, et d'envoyer des requêtes en continu avec un affichage formaté des réponses et des actions d'outils.

### ✅ **Phase 2 : Réintroduction de LangChain, Système d'Outils et Boucle Agentique Dynamique**

-   **Gestion des Dépendances & Environnement :**
    -   **Réintroduction stratégique de LangChain :** Abandon de l'approche d'introspection customisée pour la génération des schémas d'outils. Réintégration de `langchain-core` (et dépendances associées) pour exploiter le décorateur `@tool`, garantissant une génération de JSON schemas robuste et standardisée pour OpenRouter/OpenAI.
    -   **[`pyproject.toml`] :** Ajout des dépendances `langchain>=0.3.26,<1.0.0`, `langchain-community==0.3.27`, `langchain-core==0.3.81` et `langchain-openai==0.3.8`. Abaissement de la contrainte Python de `>=3.12` à `>=3.10` pour assurer la compatibilité avec les environnements locaux (`pyenv`) sans casser le conteneur Docker.
    -   **[`knower`] (CLI Bash) :** Ajout de la commande `shell` (`docker compose exec -it core bash`) pour faciliter le workflow de développement interactif directement à l'intérieur du conteneur en tâche de fond.

-   **Système d'Outils (Tool Wrapper) :**
    -   **[`tools/tool_base.py`] :** Création de la classe `BaseTool` qui agit comme un pont entre le client LLM et LangChain. Utilisation du décorateur `@tool` pour encapsuler les fonctions Python. Implémentation de la méthode `to_schema()` pour extraire le `model_json_schema()` et de la méthode `invoke()`. Ajout d'une propriété `@property def name` pour permettre au `LLMClient` de résoudre l'outil par son nom lors du parsing du stream.
    -   **[`tools/dummy_tools.py`] :** Création d'outils factices (`tree` et `read`) retournant des chaînes de caractères mockées. Ces outils permettent de valider la mécanique complète de la boucle agentique (LLM -> Tool -> LLM) avant de brancher les véritables interactions avec le système de fichiers.
    -   **[`agent/vault_tools.py`] :** Suppression du fichier devenu obsolète suite à la création du package `tools/`.

-   **Boucle Agentique Dynamique (N-itérations) :**
    -   **[`agent/base_agent.py`] :** Refonte majeure de la méthode `_loop`. Remplacement de la logique statique à deux passes par une boucle `while` dynamique. L'agent peut désormais enchaîner un nombre indéfini d'actions (réflexion, appel d'outil, analyse du résultat, nouvel appel) jusqu'à ce qu'il décide de formuler sa réponse finale (absence de `tool_calls`). Ajout d'un garde-fou `max_iterations = 15` pour prévenir les boucles infinies.
    -   **[`agent/update_agent.py` & `agent/search_agent.py`] :** Injection des instances `TreeTool` et `ReadTool` dans l'initialisation des agents. Correction de la méthode `_load_vault_context` pour utiliser la fonction `read` factice au lieu d'une dépendance `mcp_server` non encore implémentée, évitant ainsi les crashs au démarrage.

-   **Fixes, Débogage & Ajustements d'Exécution :**
    -   **Affichage des tokens de réflexion (Thinking) :** Résolution d'un bug où l'agent semblait "silencieux" malgré la consommation de tokens. Mise à jour de la méthode `_display` dans `base_agent.py` pour intercepter les événements de type `think` (générés par le paramètre `reasoning_effort`) et les afficher en gris (`\033[90m`). Cela rend le processus de raisonnement du modèle visible et facilite grandement le débogage.
    -   **[`terminal.py`] :** Résolution de l'erreur `ModuleNotFoundError: No module named 'env'` lors de l'exécution directe du script dans le conteneur. Ajout d'une manipulation du `sys.path` (`sys.path.append(...)`) en tête de fichier pour forcer la résolution des imports absolus depuis la racine du dossier `core/`.
    -   **[`llm/config.py`] :** Changement du modèle par défaut de `google/gemini-2.5-flash` vers `google/gemini-3-flash-preview`. Le modèle 2.5 présentait des difficultés à formater correctement les appels d'outils (JSON) après avoir généré un bloc de réflexion textuelle (`<think>`) via OpenRouter, tandis que la version 3 gère parfaitement la transition vers le *tool calling*.

### ✅ **Phase 3 : Refonte du Logging Terminal — Séparation Display/Agent et Formatage Propre**

-   **Problème initial et objectif :**
    -   **Constat :** Le terminal affichait un logging dégueulasse — les tool calls sur une ligne compressée avec résultat tronqué à 80 caractères, des emojis partout, et le `BaseAgent` était responsable de tout l'affichage via une méthode `_display()` interne. L'agent et la présentation étaient couplés.
    -   **Objectif :** Extraire toute la logique d'affichage hors de l'agent, obtenir un format de log lisible orienté debug (`ToolCall ->`, `ToolResult:`, `Tokens:`), et implémenter une séparation stricte des responsabilités.

-   **Refonte architecturale — Agent → Generator :**
    -   **[`agent/base_agent.py`] :** Transformation de `run()` et `_loop()` de méthodes retournant une `str` en generators (`Generator[dict, None, None]`). La méthode `_stream_and_collect()` a été supprimée — le streaming se fait désormais directement dans `_loop()` via `yield from self.llm.stream(messages)`. La méthode `_display()` et ses helpers ont été entièrement retirés. L'agent ne printe plus rien. En cas d'atteinte du `max_iterations`, un event `{"type": "error", "id": "max_iter", ...}` est yielded plutôt qu'un print direct. Ajout d'une unique docstring de classe exhaustive remplaçant tous les commentaires inline.
    -   **[`agent/search_agent.py`] et [`agent/update_agent.py`] :** `process()` converti en generator avec `yield from self.run(payload)`. Les type hints de retour ont été retirés (implicitement generator).

-   **Fix source — Ordre des events `usage` :**
    -   **Problème :** L'event `usage` était yielded par `client.py` au moment où il arrivait dans le stream LLM, soit *avant* les events `tool`. Il apparaissait donc dans le terminal entre le message utilisateur et le premier `ToolCall`, ce qui n'avait aucun sens sémantique.
    -   **[`llm/client.py`] :** Introduction d'une variable locale `usage_event = None` dans `stream()`. Lors du processing des chunks, si un `UsageEvent` est détecté via `isinstance(event, UsageEvent)`, il est stocké au lieu d'être yielded immédiatement. Il est yielded en dernier, après tous les tool events, garantissant que `Tokens:` apparaît toujours à la fin du bloc correspondant. Cette décision de fixer le problème à la source (dans le client) plutôt que dans le display a été explicitement choisie pour éviter tout buffering artificiel côté affichage.

-   **Création de `Display` — Logique d'affichage isolée :**
    -   **[`agent/display.py`] (nouveau fichier) :** Classe `Display` avec une unique instance variable `agent_started: bool` remplaçant l'ancienne variable globale. Le flag est nécessaire pour le streaming : les events `answer` arrivent en dizaines de chunks (un par token), et `Agent:` ne doit être printé qu'une seule fois avant le premier chunk. Chaque requête instancie un nouveau `Display()`, ce qui reset le flag naturellement sans état global.
    -   **Helpers privés :** `_format_tool_args(args_str)` parse le JSON des arguments et les formate en `key="value"` lisibles. `_indent_result(result)` indente chaque ligne du résultat avec 3 espaces pour l'affichage dans le code fence.
    -   **Format final validé :**
        ```
        ToolCall -> tree(path=".")
        ToolResult:
        ```
           [contenu indenté]
        ```
        Tokens: [313 in / 7 out | $0.00018]
        ```

-   **[`terminal.py`] — Épuration complète :**
    -   Toute logique d'affichage retirée. Le fichier se réduit à 40 lignes : instanciation de l'agent choisi, boucle `input()` avec `User:` comme prompt (servant simultanément de label et de prompt de saisie, évitant tout doublon d'affichage), instanciation d'un `Display()` frais par requête, itération sur `agent.process(user_input)` et dispatch de chaque event à `display.event(event)`.
    -   Suppression de tous les emojis (`🧠`, `✓`, `🔧`, `✗`, `❌`, `→`), du commentaire `sys.path`, et du print redondant du message utilisateur.

-   **Nettoyage transversal :**
    -   **[`llm/client.py`] :** Suppression de l'attribut `last_event_type` jamais utilisé fonctionnellement. Suppression du commentaire `lazy import to avoid circular`. Retrait de tous les commentaires inline dans `stream()`, `_process_chunk()`, et `_execute_tool()`.
    -   **[`agent/base_agent.py`] :** `from typing import List` étendu à `List, Generator`. Suppression de `_stream_and_collect` comme couche intermédiaire devenue inutile.

### ✅ **Phase 4 : Sécurisation de la Boucle Agentique et Graceful Degradation**

-   **Architecture & Mécanique de la Boucle Agentique :**
    -   **Clarification du mécanisme de sortie naturel :** Validation du fait que l'agent n'a pas besoin d'un outil explicite (type `finish()`) pour terminer sa tâche. La boucle s'arrête organiquement lorsque le LLM décide de générer du texte final (`content`) sans inclure de `tool_calls`.
    -   **Séparation Planification / Action :** Confirmation que la planification interne du modèle (via les tokens de `reasoning` ou de manière latente pour les modèles standards) ne déclenche pas de sortie prématurée. Le modèle peut "penser" puis agir dans la même itération sans briser la boucle.

-   **Implémentation du Filet de Sécurité (Graceful Degradation) :**
    -   **[`agent/base_agent.py`] :** Refonte de la gestion de la limite d'itérations pour éviter une coupure brutale (crash) et la perte du contexte de travail de l'agent.
    -   **Extraction des constantes :** Ajout de `MAX_ITERATIONS = 25` (limite élargie pour des tâches complexes de mémoire) et de `FORCE_FINISH_MESSAGE` (directive stricte ordonnant au modèle de résumer son travail et de s'arrêter) au niveau du module.
    -   **Conservation de l'état :** Modification de `__init__` pour stocker `self.model`, `self.system_prompt` et `self.tools` directement sur l'instance de l'agent. Ces références sont nécessaires pour reconstruire un client LLM de secours.
    -   **Création de la méthode `_force_finish` :** Implémentation d'un chemin d'exécution distinct appelé à la fin du `while` si la limite est atteinte.
    -   **Garantie structurelle de sortie :** Dans `_force_finish`, instanciation d'un nouveau `LLMClient` (`final_llm`) en lui passant explicitement `tools=[]`. Cette absence d'outils garantit mécaniquement (au niveau de l'API) que le modèle ne pourra pas tenter de nouveaux appels et sera forcé de produire une réponse textuelle de clôture.
    -   **Traçabilité et Debugging :** Ajout d'un événement `yield {"type": "error", "id": "max_iterations", ...}` au déclenchement du `_force_finish`. Bien que l'arrêt soit géré proprement, l'utilisation du type `error` (défini dans `schemas/event.py`) permet au système d'affichage (`display.py`) de signaler visuellement l'anomalie, atteindre 25 itérations n'étant pas un comportement nominal pour l'agent.

### ✅ **Phase 5 : Correction du Reasoning OpenRouter et Fix du Streaming de Transition**

-   **Configuration du Reasoning (OpenRouter API) :**
    -   **Alignement avec le schéma OpenRouter :** Le modèle s'arrêtait après avoir "pensé" sans exécuter d'actions car le paramètre `reasoning_effort` était envoyé en top-level (format natif OpenAI) au lieu d'être encapsulé dans `extra_body`, ce qui entraînait son ignorance par OpenRouter. De plus, la valeur `"low"` bridait la capacité du modèle à planifier des appels d'outils.
    -   **[`llm/client.py`] :** Simplification de l'initialisation du `LLMClient` pour accepter une simple string `reasoning` (`"low"`, `"medium"`, `"high"`, ou `None`). Modification de la méthode `stream()` pour construire et injecter dynamiquement le dictionnaire `stream_params["extra_body"] = {"reasoning": {"effort": self.reasoning}}` uniquement si le paramètre est défini.
    -   **[`agent/base_agent.py`] :** Mise à jour de l'instanciation du `LLMClient` (dans `__init__` et dans le fallback `_force_finish`) pour passer explicitement `reasoning="high"`. Cela garantit que l'agent dispose du budget de tokens nécessaire pour analyser le contexte et orchestrer ses actions.

-   **Résolution du Bug de Transition (Streaming) :**
    -   **Prévention de la perte de données (Data Loss) :** Identification et correction d'un bug latent critique dans le traitement des chunks de streaming. Lors de la transition exacte entre la fin de la réflexion et le début d'un appel d'outil, le code retournait immédiatement la balise `</think>`, ignorant le reste du chunk. Cela entraînait la perte du premier fragment de l'appel d'outil (souvent le nom de la fonction), causant des erreurs silencieuses ou des échecs de type `Tool '' not found`.
    -   **[`llm/client.py`] :** Refonte de la logique dans `_process_chunk()`. Au lieu d'un `return` anticipé lors de la détection de la fin du thinking (`is_thinking_started = False`), l'événement est désormais stocké dans une variable locale (`end_think_event`). Le code utilise ensuite un *fall-through* pour descendre dans les blocs d'évaluation `content` et `tool_calls`. Les fragments d'outils du chunk de transition sont ainsi accumulés par effet de bord dans `self.tool_calls`, et l'événement `</think>` est retourné proprement à la fin de la fonction.

-   **Validation de la Boucle Agentique :**
    -   **Exécution N-itérations fonctionnelle :** Test et validation d'une boucle agentique complète. Le modèle est désormais capable d'enchaîner de multiples itérations (ex: 4 passes) de manière autonome : il génère des blocs de réflexion (`<think>`), déclenche un ou plusieurs outils simultanément (ex: `tree` puis de multiples `read`), analyse les retours factices, et décide naturellement de sortir de la boucle pour formuler sa réponse textuelle finale.

### ✅ **Phase 6 : Implémentation du Système d'Outils (Tools) et Résolution des Chemins du Vault**

-   **Centralisation et Définition du Registre d'Outils :**
    -   **Création du module unifié :** Remplacement de l'ancien système temporaire par un registre complet implémentant les 9 outils définis dans la spécification du MVP (`tree`, `read`, `search`, `write`, `edit`, `append`, `move`, `delete`, `concat`).
    -   **[`tools/tools.py`] :** Création du fichier central. Les outils d'écriture, de recherche sémantique et de manipulation de fichiers (`write`, `edit`, `append`, `move`, `delete`, `search`, `concat`) ont été initialisés sous forme de *dummy functions* retournant des chaînes formatées. Cela permet de valider la logique de *tool calling* du LLM avant de brancher les véritables actions système.
    -   **Ségrégation des accès (RBAC) :** Définition de deux listes exportées distinctes : `SEARCH_TOOLS` (lecture seule : `tree`, `read`, `search`, `concat`) et `UPDATE_TOOLS` (accès complet, sans `concat`).
    -   **Nettoyage :** Suppression définitive de l'ancien fichier `tools/dummy_tools.py`.

-   **Implémentation Réelle des Outils de Lecture et Navigation :**
    -   **[`tools/tools.py` - `read`] :** Transformation du *dummy* en véritable implémentation lisant le système de fichiers. Ajout de la logique de budget de tokens via les paramètres `head` et `tail` (approximation à 4 caractères par token) pour tronquer intelligemment les longs fichiers. Implémentation du formatage automatique des retours : chaque ligne est préfixée par son numéro absolu (`N  | content`), et le tout est encapsulé dans un bloc de code Markdown avec le chemin du fichier en en-tête.
    -   **[`tools/tools.py` - `tree`] :** Câblage de l'outil sur l'implémentation réelle existante (`core/functions/tree`), permettant à l'agent de scanner dynamiquement l'arborescence du vault avec le décompte des tokens et les timestamps.

-   **Résolution Robuste des Chemins (Path Resolution) :**
    -   **[`tools/tools.py` - `_resolve_path`] :** Création d'un helper critique pour normaliser les chemins générés par le LLM. Il gère les noms de fichiers simples (`overview.md`), les chemins préfixés (`vault/projects/...`), et les alias de racine (`.`, `./`, `vault/`).
    -   **Support des environnements locaux :** Ajout de `.resolve()` sur `Path(env.VAULT_PATH)` pour convertir dynamiquement les chemins relatifs du `.env` (ex: `../vault`) en chemins absolus basés sur le contexte d'exécution (`cwd`). Cela corrige l'erreur `Path does not exist: /vault` rencontrée en local.
    -   **Fix du scope de `tree` :** Application de `_resolve_path` à l'outil `tree`. Cela corrige un bug majeur où l'appel `tree(".")` scannait le répertoire du code source Python au lieu du vault, ce qui entraînait des crashs de décodage UTF-8 en tentant de lire les métadonnées de fichiers binaires compilés (`.pyc`).

-   **Mise à jour et Simplification des Agents :**
    -   **[`agent/search_agent.py` & `agent/update_agent.py`] :** Injection des nouvelles listes `SEARCH_TOOLS` et `UPDATE_TOOLS` dans l'initialisation des agents respectifs, garantissant que l'agent de recherche ne peut physiquement pas altérer le vault.
    -   **Refactoring de `_load_vault_context` :** Simplification drastique de la méthode. Puisque le nouvel outil `read` retourne désormais le contenu pré-formaté avec des blocs Markdown et le nom du fichier, les ajouts manuels d'en-têtes (`## overview.md\n`) ont été retirés. Les appels aux fichiers de contexte (`overview.md`, `tree.md`, `profile.md`) sont maintenant de simples concaténations directes. Le *lazy import* de la fonction `read` a également été remonté au niveau du module.

### ✅ **Phase 7 : Modularisation des Prompts Système & Finalisation du Search Agent**

-   **Architecture des Prompts (DRY & Modularité) :**
    -   **Stratégie de factorisation :** Adoption d'une approche modulaire pour la gestion des *system prompts*. Au lieu de dupliquer les descriptions de l'environnement et des outils dans chaque agent, ces blocs textuels sont extraits dans des fichiers de constantes partagées. Cela garantit une cohérence absolue entre l'`UpdateAgent` et le `SearchAgent` et facilite la maintenance future.
    -   **[`prompts/env_prompt.py`] :** Création de ce module pour stocker les constantes contextuelles communes :
        -   `ENVIRONMENT_PROMPT` : Description exhaustive de l'architecture du vault (rôle de chaque fichier, indexation QMD vs lecture directe).
        -   `AGENTIC_MODEL_PROMPT` : Définition de la boucle autonome (raisonnement, appels d'outils, condition d'arrêt).
        -   `INITIAL_CONTEXT_PROMPT` : Explication des trois fichiers chargés au démarrage (`overview`, `tree`, `profile`) et comment s'en servir pour s'orienter sans coût.
    -   **[`prompts/tools_prompt.py`] :** Centralisation des descriptions stratégiques des outils (le *quand* et le *comment*, pas la signature technique). Implémentation des constantes pour les outils de lecture et navigation :
        -   `SEARCH_TOOL_PROMPT` : Stratégies `fast` (BM25) vs `deep` (sémantique), usage des scopes.
        -   `READ_TOOL_PROMPT` : Gestion des gros fichiers (`head`/`tail`) et lecture de dossiers.
        -   `TREE_TOOL_PROMPT` : Usage pour l'exploration structurelle fine.
        -   `CONCAT_TOOL_PROMPT` : Instructions pour l'assemblage final de la réponse (spécifique au Search, mais stocké ici pour cohérence).

-   **Finalisation du Prompt Search Agent :**
    -   **[`prompts/search_prompt.py`] :** Réécriture complète du fichier pour assembler dynamiquement le prompt final via des f-strings.
    -   **Structure composite :** Le prompt combine désormais les constantes importées (`env_prompt`, `tools_prompt`) avec les sections spécifiques à l'agent de recherche :
        -   `<identity>` : Définition stricte du rôle *read-only* et de l'objectif "What does the user need to know?".
        -   `<search-strategy>` : Documentation des patterns de recherche multi-pass adaptés au type de question (temporelle, statut, historique, cross-projet, vague).
        -   `<rules>` : Invariants absolus (jamais écrire, jamais inventer, jamais halluciner des paths).
        -   `<output>` : Format de sortie strict en deux parties (Overview rédigée + Fichiers concaténés).

### ✅ **Phase 8 : Standardisation des Prompts Système & Implémentation de l'Update Agent**

-   **Refonte Qualitative du Search Prompt :**
-   **Alignement sur les standards de qualité :** Réécriture complète de `search_prompt.py` pour abandonner le format "manuel procédural" (listes à puces, sous-catégories rigides) au profit d'une prose fluide et directive. Adoption du pattern "Bold Lead-in + Paragraphe" pour transmettre le *mindset* de l'agent plutôt qu'une simple suite d'instructions.
-   **[`prompts/search_prompt.py`] :**
    -   **`<identity>` :** Resserrée à l'essentiel (3 lignes), suppression des justifications défensives ("this is not a limitation").
    -   **`<search-strategy>` :** Transformation radicale. Les 5 catégories de questions (temporelle, statut, etc.) sont tissées organiquement dans le texte. L'accent est mis sur le raisonnement initial (utiliser `overview` et `tree` avant tout outil) et l'itération (ne pas s'arrêter à une recherche infructueuse).
    -   **`<rules>` :** Condensation des règles absolues. Suppression des explications évidentes pour un LLM ("Even if you think a file has a typo...").

-   **Extension du Système de Prompts (Outils d'Écriture) :**
-   **[`prompts/tools_prompt.py`] :** Ajout des 5 constantes manquantes pour les outils de modification, suivant le même standard de qualité (instructions stratégiques sur le *quand* et le *comment*, pas de détails techniques).
    -   `WRITE_TOOL_PROMPT` : Distinction claire entre création/réécriture complète et modification partielle.
    -   `EDIT_TOOL_PROMPT` : Insistance sur la précondition de lecture (`read` obligatoire avant `edit`) et l'unicité du contexte de remplacement.
    -   `APPEND_TOOL_PROMPT` : Explication du workflow "zero-read" pour les changelogs et tasks (insertion aveugle en haut ou en bas).
    -   `MOVE_TOOL_PROMPT` : Cas d'usage pour le routing et la correction d'erreurs.
    -   `DELETE_TOOL_PROMPT` : Usage principal pour le nettoyage de l'inbox après résolution.

-   **Implémentation du Prompt Update Agent :**
-   **[`prompts/update_prompt.py`] :** Création du prompt système complet pour l'agent d'écriture, remplaçant le placeholder existant.
    -   **Architecture Modulaire :** Assemblage dynamique via f-strings incluant `env_prompt`, `agentic_model`, `initial_context` et les 8 outils (lecture + écriture).
    -   **`<identity>` :** Définition du rôle de "sole writer" et de la question directrice "Where does this information belong?".
    -   **`<update-strategy>` :** Directives de haut niveau sur le routing (signal fort vs ambiguïté), la gestion de l'`inbox_ref` (priorité absolue), et la création de dossiers inbox avec `review.md` en cas de doute.
    -   **`<rules>` :** Interdictions strictes : ne jamais toucher au frontmatter (géré par le background job), ne jamais régénérer `tree.md`, et ne jamais terminer sans logger dans `changelog.md`.