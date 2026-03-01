### ✅ **Phase 1 : Refactoring du Contexte Vault et Injection de la Date**

-   **Centralisation et Formatage du Contexte :**
    -   **Mutualisation de la logique :** Création d'un nouveau module dédié pour gérer le contexte du vault partagé entre les différents agents, éliminant ainsi la duplication de code existante.
    -   **Injection de la date du jour :** Ajout systématique de la date actuelle au format `YYYY-MM-DD` via `datetime.now()`. Cela permet aux agents (notamment l'`UpdateAgent`) d'avoir un repère temporel fiable pour la rédaction des changelogs, corrigeant le bug des dates inventées ou incorrectes.
    -   **Suppression de la référence `tree.md` :** Retrait du bloc markdown factice ````tree.md` qui enveloppait l'arborescence. L'output de `tree(depth=1)` est désormais injecté directement, évitant la confusion du modèle avec un fichier physique inexistant.
    -   **Structuration en XML :** Refonte du format de sortie du contexte en utilisant des balises XML explicites (`<date>`, `<overview>`, `<vault-structure>`, `<profile>`). Cette approche améliore grandement la capacité du LLM à parser et isoler les différentes sections du contexte.
    -   **[`core/agent/agent/context.py`] :** Implémentation de la fonction `load_vault_context()`. Utilisation de constantes de templates (`VAULT_CONTEXT_TEMPLATE` et `VAULT_CONTEXT_ERROR_TEMPLATE`) formatées via `.format()` avec des arguments nommés (kwargs), remplaçant les f-strings concaténées pour un code beaucoup plus propre et lisible. Gestion des erreurs conservée avec un template XML de fallback (`<vault-context-error>`).

-   **Mise à jour des Agents :**
    -   **Nettoyage et intégration :** Les agents de recherche et de mise à jour ont été allégés de leur logique de chargement de contexte interne.
    -   **[`core/agent/agent/search_agent.py`] & [`core/agent/agent/update_agent.py`] :** Suppression de la méthode `_load_vault_context()` dans les deux classes. Remplacement des imports directs des outils `read` et `tree` par l'import de la nouvelle fonction `load_vault_context`. Le payload principal reste inchangé dans sa structure globale (`vault_context\n\n---\n\nquery`), mais bénéficie désormais du nouveau formatage XML et de la date.

### ✅ **Phase 2 : Intégration du Contenu Fichier dans la Réponse SearchAgent**

-   **Logique d'Accumulation et de Buffering :**
    -   **Modification du flux de réponse :** Le `SearchAgent` a été refactorisé pour ne plus émettre les chunks `answer` textuels (l'overview) en temps réel. Ces fragments sont désormais interceptés et accumulés dans une liste interne (`answer_parts`) tout au long de l'exécution.
    -   **Préservation du Streaming Technique :** Les événements de type `think`, `tool` (start/end/error), `usage` et `error` continuent d'être streamés normalement pour assurer le feedback visuel et le logging en temps réel.

-   **Gestion du Tool `concat` :**
    -   **Interception du Résultat :** Mise en place d'une écoute spécifique sur les événements `tool` dans la boucle d'exécution. Lorsqu'un événement `concat` avec le statut `end` est détecté, son résultat (qui contient déjà les fichiers formatés en blocs markdown) est capturé et stocké (`concat_result`).
    -   **Assemblage Final :** À la fin du processus, l'agent construit une réponse unique en concaténant l'overview accumulé et le contenu des fichiers capturé.

-   **Émission de la Réponse Unique :**
    -   **Event Final Unifié :** L'agent émet un seul et unique événement `answer` (`id="final"`) contenant la totalité de la réponse (Texte explicatif + Contenu brut des fichiers).
    -   **[`core/agent/agent/search_agent.py`] :** Implémentation de la logique de filtrage, d'accumulation et d'assemblage dans la méthode `process`. Cela garantit que l'API et le frontend reçoivent un payload markdown complet et cohérent, simplifiant grandement le traitement côté client.

### ✅ **Phase 3 : Nettoyage et Standardisation du Format de Sortie `concat`**

-   **Raffinement de l'Affichage des Tools :**
    -   **Simplification des En-têtes de Blocs :** Modification de la logique de génération des code fences dans le tool `concat`. Suppression de l'annotation dynamique `(lines N-M)` dans le header du bloc markdown. Désormais, seul le chemin du fichier est utilisé comme identifiant de langage, ce qui garantit une compatibilité maximale avec les parseurs markdown et évite la redondance d'information (les numéros de ligne étant déjà explicites dans le contenu).
    -   **Harmonisation Visuelle :** Ajustement du formatage des numéros de ligne dans `_format_lines`. Passage de 1 à 2 espaces avant le séparateur vertical (`|`), alignant ainsi strictement le style visuel de `concat` sur celui du tool `read`. Cela assure une cohérence parfaite de la présentation des fichiers, quelle que soit la méthode d'accès utilisée par l'agent.
    -   **[`core/functions/concat/concat.py`] :** Mise à jour des fonctions `_format_lines` et `concat` pour implémenter ces changements de formatage.

### ✅ **Phase 4 : Refonte et Unification du Système de Logs par Requête**

-   **Architecture du Logging :**
    -   **Log par requête (Per-Request Logging) :** Abandon de l'approche hybride (un log global pour le serveur + un log par appel LLM) au profit d'un système unifié où chaque requête API (ex: `/search` ou `/update`) génère un et un seul fichier de log. Ce fichier regroupe chronologiquement tous les événements streamés par l'agent (`think`, `tool`, `answer`, `usage`, `error`).
    -   **Isolation des contextes :** En passant d'une fonction globale à une classe instanciée localement, on garantit que les requêtes concurrentes sur le serveur FastAPI ne mélangent plus leurs événements dans le même fichier.
    -   **Gate de Développement (`DEV`) :** L'écriture des fichiers JSONL sur le disque est désormais strictement conditionnée à l'activation du mode développement. L'affichage humain dans le terminal (stdout) reste quant à lui toujours actif pour le monitoring en production.

-   **Implémentation du RequestLogger :**
    -   **[`core/agent/utils/logger.py`] :** Réécriture complète du module. Création de la classe `RequestLogger` qui gère un buffer en mémoire (`self.events`). La méthode `log()` affiche dans le terminal et ajoute l'événement au buffer. La méthode `save()` écrit le buffer dans `logs/requests/{name}_{timestamp}.jsonl` uniquement si `env.DEV` est vrai. Le chemin du dossier de logs a été hardcodé pour simplifier le code et retirer la dépendance à `os.getenv`.
    -   **[`core/agent/utils/raw_logger.py`] :** Fichier supprimé. La journalisation des chunks bruts de l'API LLM (qui générait un dossier par appel LLM et spammait le disque) a été retirée, les événements structurés de l'agent étant amplement suffisants pour le débogage.

-   **Nettoyage et Intégration aux Points d'Entrée :**
    -   **[`core/agent/llm/client.py`] :** Purge de toutes les références à `object_logger`. Le client LLM retrouve un rôle pur : il génère et `yield` des événements structurés sans aucune responsabilité d'écriture sur le disque.
    -   **[`core/api/routes.py`] & [`core/mcp_server/tools.py`] :** Intégration du nouveau logger dans les routes `/search`, `/update` et les outils MCP. Mise en place d'un pattern robuste : instanciation de `log = RequestLogger("nom")` au début de la fonction `_run()`, appel de `log.log(event)` dans la boucle de l'agent, et garantie de l'écriture via un bloc `finally: log.save()`. Nettoyage d'un import `uuid` mort dans les tools MCP.
    -   **[`core/env.py`] & [`.env.example`] :** Ajout de la variable `DEV: bool = False` dans le schéma Pydantic `EnvVariables` pour centraliser la configuration, avec mise à jour du fichier d'exemple.

### ✅ **Phase 5 : Streaming Temps Réel des Events Agent vers le Frontend**

-   **Contexte et Objectif :**
    -   **Problème initial :** Les endpoints `/search` et `/update` étaient des routes REST synchrones — ils attendaient la fin complète de l'exécution de l'agent avant de retourner une réponse JSON. L'utilisateur voyait uniquement un spinner pendant toute la durée du traitement (parfois 15-30 secondes), sans aucun feedback sur ce que l'agent faisait.
    -   **Objectif :** Streamer chaque event de l'agent (`think`, `tool`, `answer`, `usage`, `error`) en temps réel vers le frontend pour afficher la progression, et conserver ces events visibles au-dessus du résultat final une fois le traitement terminé.

-   **Architecture du Streaming — Backend :**
    -   **Choix technique — NDJSON via `StreamingResponse` :** La première implémentation utilisait `EventSourceResponse` de `sse-starlette` avec un parsing SSE manuel côté client. Cette approche s'est révélée défaillante en pratique : le proxy Vite + `fetch` POST ne streamait pas la réponse correctement, résultant en une livraison groupée en fin de connexion et des events jamais parsés côté frontend. La solution finale remplace entièrement cette approche par `StreamingResponse` (built-in Starlette) au format NDJSON — chaque event est un `json.dumps(event) + "\n"`. Ce format est trivial à parser, robuste au buffering, et compatible sans configuration spéciale avec tous les proxies.
    -   **Bridge Sync → Async — `_stream_agent` :** Les agents (`SearchAgent`, `UpdateAgent`) sont des générateurs synchrones Python. Pour les connsommer dans un contexte async FastAPI sans bloquer l'event loop, on utilise `threading.Thread(target=_worker, daemon=True)` — un thread dédié (non issu du pool d'exécuteurs) qui itère le générateur et place chaque event dans un `stdlib_queue.Queue`. L'async generator consomme cette queue via `await asyncio.to_thread(q.get)`, transformant chaque `q.get()` bloquant en coroutine awaitable. Un sentinel `None` en fin de thread signal la terminaison naturelle du stream. Ce choix de `threading.Thread` explicite plutôt que `loop.run_in_executor` élimine toute ambiguïté sur la gestion du pool de threads et le cycle de vie des tâches.
    -   **Headers anti-buffering :** La `StreamingResponse` est construite avec `Cache-Control: no-cache`, `Connection: keep-alive`, et `X-Accel-Buffering: no` pour désactiver le buffering de tout proxy intermédiaire (nginx, Vite proxy). Le `media_type="text/event-stream"` signale aux proxies de traiter ce flux comme un stream continu.
    -   **Event sentinelle `done` :** Un event final `{"type": "done"}` est émis après l'épuisement du générateur agent. Cela permet au frontend de détecter explicitement la fin du stream indépendamment de la fermeture de la connexion TCP.
    -   **Logging préservé :** Le `RequestLogger` reste dans le worker thread (`_worker`). Chaque event est loggé via `log.log(event)` avant d'être mis dans la queue, et `log.save()` est appelé dans le bloc `finally` pour garantir l'écriture JSONL même en cas d'exception.
    -   **[`core/api/routes.py`] :** Refactoring complet des routes `/update` et `/search`. Ajout de `_stream_agent` (async generator, bridge sync/async via queue) et `_streaming_response` (factory function qui crée la `StreamingResponse` avec les bons headers). Chaque route instancie l'agent, appelle `agent.process(...)` pour obtenir le générateur, et le passe à `_streaming_response`. Import de `threading` et `starlette.responses.StreamingResponse` ; suppression de la dépendance à `asyncio.to_thread` pour la gestion principale.

-   **Architecture du Streaming — Frontend :**
    -   **Parser NDJSON — `consumeStream` :** Fonction centrale dans `api.ts` qui consomme un `ReadableStream` (via `response.body.getReader()`). La logique maintient un buffer string, décode chaque chunk via `TextDecoder({ stream: true })`, et split sur `"\n"`. Le dernier fragment potentiellement incomplet est remis dans le buffer (`lines.pop()`). Chaque ligne complète et non-vide est parsée via `JSON.parse` et transmise au callback `onEvent`. Le buffer résiduel après fermeture du stream est traité séparément pour ne pas perdre le dernier event.
    -   **`streamSearch` et `streamUpdate` :** Deux fonctions async exportées qui font le `fetch` POST vers `/search` et `/update`, passent la réponse à `consumeStream`, et acceptent un callback `onEvent: (event: AgentEvent) => void`. Elles retournent `Promise<void>` et résolvent quand le stream est épuisé. Les anciennes fonctions `sendSearch` et `sendUpdate` (REST synchrones) sont conservées pour compatibilité future.
    -   **[`web/src/api.ts`] :** Ajout de `consumeStream` (parsing NDJSON), `streamSearch`, `streamUpdate`. Ajout d'un `console.warn` défensif sur les lignes non-parsables pour faciliter le debug.

-   **Typage des Events Agent :**
    -   **[`web/src/types.ts`] :** Ajout d'interfaces TypeScript discriminées pour chaque type d'event émis par le backend : `AgentThinkEvent`, `AgentAnswerEvent` (avec champ optionnel `tool_calls`), `AgentToolEvent` (avec `status: 'start' | 'end' | 'error'`), `AgentUsageEvent`, `AgentErrorEvent`, `AgentDoneEvent`. L'union discriminée `AgentEvent` regroupe tous ces types. Ce typage strict permet des narrowing TypeScript précis dans `EventStream.tsx` et `App.tsx` pour filtrer les events par type et par propriétés.

-   **Composant `EventStream` — Affichage Temps Réel :**
    -   **Design général :** Nouveau composant `EventStream` prenant `events: AgentEvent[]` en prop. Chaque render appelle `processEvents(events)` (fonction pure, sans state) qui transforme le tableau plat en `DisplayItem[]` — une représentation visuelle groupée.
    -   **Fusion des events `think` :** Les events `think` arrivent en dizaines de petits chunks (les reasoning tokens du modèle). `processEvents` les fusionne en un seul `ThinkItem` en concaténant le contenu tant que les events consécutifs sont de type `think`. Les balises `<think>` et `</think>` émises par le client LLM sont nettoyées via `stripThinkTags` (regex). L'affichage ne montre que les 4 dernières lignes non-vides tronquées à 220 caractères — suffisant pour voir l'avancement sans flood visuel.
    -   **Gestion des paires `tool start/end` :** Un event `tool` avec `status: 'start'` crée un `ToolItem` avec `status: 'running'`. L'event correspondant `end` ou `error` est matché par recherche inverse (`[...items].reverse().find(...)`) sur le nom et le status `running`, puis met à jour l'objet en place avec le résultat. Cela produit une liste sans doublons où chaque tool call est un bloc unique qui évolue d'état.
    -   **Formatage des arguments :** `formatArgs` parse le JSON des arguments et formate en `key="value"` tronqués à 50 chars chacun pour une lecture rapide.
    -   **Visuel :** Bordure gauche `border-l-2` comme fil directeur. `think` en italique gris muted avec `✦`. Tool `running` avec `→`, `done` avec `✓` (vert implicite via `text-foreground`), `error` avec `✗` en `text-destructive`. Résultat des tools en bloc `bg-muted/40` avec troncature à 240 chars. Usage en ligne discrète `text-muted-foreground/50` (50% opacity).
    -   **[`web/src/components/central/EventStream.tsx`] :** Création ex nihilo du composant.

-   **Intégration dans `ActivityView` :**
    -   **Nouvelle prop `streamEvents: AgentEvent[]` :** `ActivityView` reçoit le tableau des events accumulés depuis `App`.
    -   **Loading en deux phases :** Avant le premier event : spinner centré classique (`Loader2` 6×6). Dès le premier event : `<EventStream events={streamEvents} />` s'affiche avec un petit spinner inline (`Loader2` 3×3) + label en bas. Transition naturelle sans saut visuel.
    -   **Persistance des events :** Une fois `isLoading` passé à `false`, les events restent visibles au-dessus du résultat final dans les deux cas (search et update). Le résultat est rendu par `MarkdownRenderer` en dessous, séparé par un `space-y-6`.
    -   **[`web/src/components/central/ActivityView.tsx`] :** Ajout de la prop, restructuration du bloc `isLoading` en deux cas conditionnels, ajout du rendu `EventStream` persistant dans les deux blocs de résultat.

-   **Propagation du State dans `CentralZone` et `App` :**
    -   **[`web/src/components/central/CentralZone.tsx`] :** Ajout de `streamEvents: AgentEvent[]` dans l'interface `CentralZoneProps` et pass-through vers `ActivityView`. Import du type `AgentEvent`.
    -   **[`web/src/App.tsx`] :** Ajout du state `const [streamEvents, setStreamEvents] = useState<AgentEvent[]>([])`. Reset à `[]` en début de chaque nouvelle requête. Remplacement de `sendSearch`/`sendUpdate` par `streamSearch`/`streamUpdate` avec le callback `onEvent`. Utilisation d'un tableau local `collected: AgentEvent[]` synchrone pour accumuler les events — cette approche contourne le problème d'asynchronicité du state React (qui n'est pas lisible immédiatement via `streamEvents` après `setStreamEvents`). Le callback `onEvent` pousse dans `collected` (sync) ET appelle `setStreamEvents(prev => [...prev, event])` (async, pour les re-renders progressifs). Après résolution du stream, le résultat final est extrait depuis `collected` : pour search, le dernier event `answer` avec `id === 'final'`; pour update, concaténation de tous les events `answer` sans `tool_calls` non-vides. L'event `done` est filtré (ignoré) dans `onEvent` avant accumulation.

### ✅ **Phase 6 : Nettoyage et Optimisation de l'Infrastructure de Streaming**

-   **Nettoyage du Code Mort Frontend :**
    -   **Suppression des appels REST obsolètes :** Suite à la transition vers le streaming NDJSON, les anciennes fonctions d'appel synchrones étaient non seulement inutilisées mais structurellement cassées (l'appel à `res.json()` déclenchant une erreur de syntaxe face à un flux NDJSON). Dans une optique "less is more", ces fonctions ont été purgées pour garantir une base de code propre et sans ambiguïté.
    -   **[`web/src/api.ts`] :** Retrait définitif des fonctions `sendUpdate` et `sendSearch`. Le fichier est désormais strictement concentré sur le parser NDJSON (`consumeStream`), les appels de streaming (`streamSearch`, `streamUpdate`) et les requêtes REST classiques toujours valides (`fetchTree`, `fetchFile`, `fetchInboxDetail`).

-   **Correction Sémantique du Backend :**
    -   **Ajustement du MIME Type :** Le format de réponse streamé par l'API est du NDJSON (Newline Delimited JSON), mais l'en-tête déclarait historiquement un format SSE. Bien que fonctionnel côté code, cela pouvait causer des erreurs silencieuses dans les DevTools du navigateur qui tentaient de parser le flux avec les règles du Server-Sent Events.
    -   **[`core/api/routes.py`] :** Modification du paramètre `media_type` dans la factory `_streaming_response`, passant de `"text/event-stream"` à `"application/x-ndjson"`. Le flux continu et la désactivation du buffering par les proxys (Vite, Nginx) restent garantis par les headers explicites (`Connection: keep-alive`, `Cache-Control: no-cache`, `X-Accel-Buffering: no`).

-   **Validation de l'Architecture et Diagnostic :**
    -   **Audit de la plomberie :** Validation de la robustesse du pattern de bridge sync/async (via `threading.Thread` et `stdlib_queue.Queue`) côté backend, et de l'orchestration locale du state React (pattern `collected[]` pour contourner l'asynchronicité du state) côté frontend. L'architecture a été jugée saine, minimale et pérenne.
    -   **Analyse des fuites de Tool Calls :** Diagnostic d'un comportement inattendu où un bloc JSON (pattern ReAct avec `action` et `action_input` pour l'outil `concat`) apparaissait parfois à la fin de la réponse du `SearchAgent`. Il a été confirmé qu'il s'agit d'une "hallucination" de formatage du modèle LLM (qui écrit son intention d'appel d'outil dans le texte au lieu d'utiliser le mécanisme natif `tool_calls`), validant de fait que l'infrastructure de streaming et d'accumulation des événements fonctionne parfaitement et retranscrit fidèlement l'output du modèle.

### ✅ **Phase 7 : Typage Strict et Correction de la Validation de l'Outil `read`**

-   **Refonte de la Signature et Validation du Tool :**
    -   **Correction du crash Pydantic :** Résolution de l'erreur de validation (Input should be a valid string) qui survenait lorsque le LLM passait un tableau de chemins à l'outil `read`. La signature de la fonction exposée au modèle a été modifiée de `paths: str` à `paths: list[str]`. Cela permet à LangChain de générer un schéma JSON correct (attendant un array) et à Pydantic de valider l'entrée nativement.
    -   **Nettoyage du code mort :** Suppression du bloc de fallback (qui tentait de faire un `json.loads` si la chaîne commençait par `[`) devenu obsolète, car la validation stricte intervient en amont. Mise à jour de la docstring pour refléter ce changement de contrat.
    -   **[`core/agent/tools/tools.py`] :** Modification de la signature de `read` et nettoyage de la logique interne.

-   **Alignement de l'Implémentation Source et des Appels Internes :**
    -   **Simplification de la fonction source :** Pour garantir une source de vérité unique et un typage strict de bout en bout, la fonction sous-jacente a été modifiée pour n'accepter exclusivement qu'une `list[str]`. L'union type `str | list[str]` et la logique de conversion conditionnelle (`isinstance(paths, str)`) ont été retirées.
    -   **[`core/functions/read/__init__.py`] :** Mise à jour de la signature de `read` et suppression de la normalisation des chemins. Ajout d'une validation `if not paths:` pour rejeter les listes vides.
    -   **Correction des appels directs :** Les appels internes à la fonction `read` (qui contournent le LLM) ont été mis à jour pour respecter le nouveau contrat strict. Les chemins simples passés en arguments ont été encapsulés dans des listes (ex: `read(["overview.md"])`).
    -   **[`core/agent/agent/context.py`] :** Modification de `load_vault_context` pour passer des listes lors de la lecture de `overview.md` et `profile.md`.