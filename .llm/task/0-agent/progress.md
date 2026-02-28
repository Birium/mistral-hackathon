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