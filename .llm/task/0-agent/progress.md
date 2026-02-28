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