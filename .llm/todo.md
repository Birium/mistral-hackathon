# Todo

## Search

- [ ] Résoudre le timeout du deep search

  C'est le problème bloquant du projet. Le `search` tool dans `core/agent/tools/tools.py` appelle `asyncio.run(_search_impl(...))`, qui fan-out vers `qmd_client.raw_search()` via `core/functions/search/query.py`. En mode `deep`, les modèles locaux crashent systématiquement — les logs montrent `[qmd] timeout after 30s` sur chaque query, ce qui retourne `merged number = 0` et donc `No results found`. L'agent répond quand même mais sans aucune donnée réelle. À investiguer du côté du client `qmd` et de la configuration des modèles locaux. La fonction `run()` dans `query.py` est l'entrée centrale, et `_search_impl` dans `tools.py` est ce que le LLM appelle via tool call.

- [x] Faire retourner la liste des fichiers concaténés dans la réponse finale de l'agent

  Actuellement, le `SearchAgent` dans `core/agent/agent/search_agent.py` yield tous les events via `base_agent.py`, mais la route `/search` dans `core/api/routes.py` ne collecte que les fragments `answer` pour construire la réponse finale : elle fait `parts.append(event.get("content", ""))` et retourne `{"queries": ..., "answer": answer}`. Le `concat` tool est bien appelé et retourne du contenu (visible dans les logs `[tool←] concat → ...`), mais ce résultat ne remonte jamais dans le JSON de réponse. Il faut collecter les events `tool` de type `end` dont le `name == "concat"` et extraire les paths depuis les arguments, puis les ajouter dans la réponse sous une clé `files` ou similaire. Le schéma de réponse actuel est dans `routes.py`, et `ActivityResult` côté frontend dans `web/src/types.ts` a déjà un champ `touched_files?: string[]` qui attend exactement ça — il suffit de le brancher.

- [x] Nettoyer le formatage du tool concat

  Le format de sortie actuel du tool `concat` n'est pas optimal pour le rendu final. Il génère souvent un bloc global `multi-file-concat` avec des headers internes (H1) pour chaque fichier. Nous voulons une structure beaucoup plus simple et standard : une suite de blocs de code Markdown individuels, où le "langage" du bloc est le chemin du fichier.
  
  Format actuel (à bannir) :
  ```multi-file-concat
  # vault/path/to/file.md
  1 | content...
  ```
  ```

  Format attendu :
  ```vault/path/to/file.md
  1 | content...
  ```
  ```
  Cela nécessite de modifier `core/functions/concat/concat.py` (ou le wrapper qui boucle sur les fichiers) pour supprimer le wrapper global et les headers H1, et retourner simplement les blocs concaténés par des sauts de ligne.

- [ ] Corriger l'erreur de validation Pydantic sur le tool `read`

  L'agent envoie parfois une liste de chaînes (`['path1', 'path2']`) au lieu d'une chaîne unique pour l'argument `paths`, ce qui provoque une erreur de validation Pydantic (`Input should be a valid string`). Il faut mettre à jour la signature de `read` dans `tools.py` pour accepter `Union[str, List[str]]` afin que Pydantic valide correctement l'entrée avant qu'elle n'arrive à la logique du tool.

- [ ] Empêcher le modèle de sortir du contenu brut de fichiers dans sa réponse

  Parfois le modèle paraphrase ou recopie du contenu de fichiers directement dans son texte plutôt que de laisser `concat` s'en charger. C'est un problème de prompt : le `SEARCH_SYSTEM_PROMPT` dans `core/agent/prompts/search_prompt.py` dit bien dans sa section `<rules>` de ne jamais résumer les fichiers à la place de les retourner, mais le modèle ne respecte pas toujours cette consigne. Il faut renforcer cette règle dans le prompt, probablement en ajoutant une contrainte explicite sur le format de la réponse textuelle (overview uniquement, jamais de contenu de fichier inline). Voir aussi `SEARCH_TOOL_PROMPT` et `CONCAT_TOOL_PROMPT` dans `tools_prompt.py` pour ajuster les instructions sur ce que le modèle doit et ne doit pas inclure dans son texte.

## UI

- [ ] Afficher les fichiers concaténés comme éléments cliquables dans la réponse du chat

  Une fois que la liste de fichiers remonte dans la réponse (tâche search ci-dessus), il faut les afficher dans `ActivityView` (`web/src/components/central/ActivityView.tsx`). La structure de base existe déjà : le composant a une section `touched_files` avec des boutons `onClick={() => onSelectFile?.(f)}` — elle est déjà là mais jamais alimentée parce que le backend ne renvoie pas encore les fichiers. Attention : il faut que le contenu Markdown de la réponse (`result.content`) reste bien affiché par `MarkdownRenderer` au-dessus, et que les fichiers apparaissent dessous. Ne pas les fusionner.

- [ ] Supprimer les tokens affichés dans la sidebar des nœuds fichiers

  Dans `FileTreeNode` (`web/src/components/sidebar/FileTreeNode.tsx`), les fichiers et dossiers affichent `{node.tokens > 0 && <span ...>{node.tokens}</span>}`. Ces tokens viennent de `TreeNode.tokens` dans `types.ts`, lui-même rempli par `_node_to_dict()` dans `routes.py` qui lit `node.tokens` depuis le scanner. Ce n'est pas l'info à mettre dans la sidebar. À supprimer ou remplacer par quelque chose d'utile (date, rien du tout).

- [x] Implémenter un loading state avec événements streamés depuis l'API

  Actuellement `/search` et `/update` dans `routes.py` sont des endpoints REST synchrones — ils attendent la fin de l'agent avant de répondre. Pour avoir du feedback en temps réel, il faudrait les convertir en SSE ou utiliser le canal SSE existant (`/sse` via `watcher.py`). Le frontend a déjà `useSSE` dans `web/src/hooks/useSSE.ts` et `EventSourceResponse` est déjà importé dans `routes.py`. L'agent émet des events typés (`think`, `tool`, `answer`, `usage`) via `BaseAgent._loop()` dans `base_agent.py` — ces events pourraient être relayés vers le frontend directement. En fallback acceptable : un loading state simple avec le message `pendingMessage` existant dans `App.tsx`, qui est déjà passé à `ActivityView` mais seulement affiché avec un spinner générique.

- [ ] Refaire la chat input avec les composants Vercel

  `ChatInput` dans `web/src/components/chat/ChatInput.tsx` est positionnée en `fixed` avec `bottom-6` et un calcul de left manuel (`calc(18rem + 2rem)`), ce qui est fragile. Elle doit être plus large, centrée, et construite avec les composants Vercel AI qu'on avait référencés. Le textarea existe (`textareaRef`) et l'auto-resize fonctionne, mais toute la structure visuelle est à revoir. Garder la logique (mode toggle, recording, send) mais refaire le shell.

- [ ] Brancher correctement le contexte inbox dans le chat

  Quand l'utilisateur clique "Reply" sur un inbox item, `onReply(name)` dans `InboxDetailView` appelle `onReply` dans `App.tsx` qui passe `chatMode` en `'answering'` et met `answeringRef` au nom de l'inbox. La `ChatInput` affiche le `AnsweringBanner` et envoie `sendUpdate(query, ref)` avec le `inbox_ref`. Côté backend dans `routes.py`, `inbox_ref` est bien passé à `agent.process(payload.user_query, inbox_ref=payload.inbox_ref)` dans `UpdateAgent`. Ce qui manque : s'assurer que le contenu de l'inbox (le `review.md` et les fichiers sources) est effectivement chargé et injecté dans le contexte de l'agent quand `inbox_ref` est présent. Voir `UpdateAgent.process()` dans `update_agent.py` — actuellement `inbox_ref` est juste appendé en texte brut (`payload += f"\n\ninbox_ref: {inbox_ref}"`), ce qui ne garantit pas que le modèle lira le contenu de l'inbox.

## Agent

- [x] Injecter la date du jour avant chaque appel search ou update agent

  Ni `SearchAgent.process()` ni `UpdateAgent.process()` dans leurs fichiers respectifs n'injectent la date courante dans le payload. Ils construisent `payload = f"{vault_context}\n\n---\n\n{content}"` sans timestamp. La date est critique pour les changelogs (l'`UpdateAgent` doit écrire des entrées `# YYYY-MM-DD` correctes) et pour contextualiser les recherches temporelles. À ajouter dans `_load_vault_context()` de chaque agent ou directement en tête de payload, en `datetime.now().strftime(...)`.

- [ ] Supprimer complètement `tree.md` de partout

  Deux endroits à nettoyer. Dans `SearchAgent._load_vault_context()` et `UpdateAgent._load_vault_context()` (`search_agent.py` et `update_agent.py`), les deux agents font `vault_tree = f"``` tree.md\n{tree(depth=1)}\n```"` et injectent ça dans le prompt avec le label `tree.md`. Le fichier `tree.md` est aussi référencé dans `ENVIRONMENT_PROMPT` (`env_prompt.py`) : `**tree.md** — The complete file structure...` et dans `INITIAL_CONTEXT_PROMPT` : `tree.md — the structure. Use it to assess file sizes...`. Dans `exclusions.py` (`core/functions/search/exclusions.py`), `"tree.md"` est dans `EXCLUDED_EXACT` — cette ligne reste, mais les labels et références au fichier dans les prompts et les agents doivent être remplacés par un label neutre comme "vault structure" ou "trie structure". Le contenu injecté (`tree(depth=1)`) reste utile, seul le nom disparaît.

- [ ] Corriger le bug de dates incorrectes dans le changelog

  Quand l'`UpdateAgent` ajoute une entrée dans un changelog, les dates générées sont mauvaises. Probablement lié à l'absence d'injection de date (tâche ci-dessus) combinée au fait que `update_updated()` dans `core/functions/frontmatter/updated/update.py` écrit `datetime.now()` sans timezone, tandis que `update_created()` dans `core/functions/frontmatter/created/update.py` lit `os.stat(path).st_birthtime` qui est OS-dépendant. L'`APPEND_TOOL_PROMPT` dans `tools_prompt.py` précise bien le format `# 2025-07-14` et que deux H1 identiques sont acceptables — mais si le modèle n'a pas la date, il invente. Combiner l'injection de date avec une vérification que le format attendu est explicite dans le prompt.

- [ ] Corriger le déclenchement intempestif de concat sur un simple tree

  L'agent en Y (probablement le `SearchAgent`) appelle parfois `concat` alors que la requête ne le justifie pas — par exemple pour une simple question de structure. Le `CONCAT_TOOL_PROMPT` dans `tools_prompt.py` dit "Always the last tool you call in a session" et que c'est pour assembler les fichiers pertinents — mais le modèle peut interpréter ça trop largement. À investiguer dans les prompts : soit renforcer la condition d'usage de `concat` dans `CONCAT_TOOL_PROMPT`, soit ajouter une règle dans `<search-strategy>` de `search_prompt.py` qui précise quand `concat` ne doit pas être appelé.

## Prompts

- [ ] Mettre à jour tous les prompts des tools

  Les prompts dans `core/agent/prompts/tools_prompt.py` n'ont pas été mis à jour depuis les dernières évolutions de l'architecture. Chaque tool a son bloc : `SEARCH_TOOL_PROMPT`, `READ_TOOL_PROMPT`, `TREE_TOOL_PROMPT`, `CONCAT_TOOL_PROMPT`, `WRITE_TOOL_PROMPT`, `EDIT_TOOL_PROMPT`, `APPEND_TOOL_PROMPT`, `MOVE_TOOL_PROMPT`, `DELETE_TOOL_PROMPT`. À passer en revue un par un et aligner sur l'état actuel du code, notamment en tenant compte de la suppression de `tree.md` et des changements de comportement attendus des agents.

## Init Agent (Scan Agent)

- [ ] Implémenter le Scan Agent

  Troisième agent à créer, qui n'existe pas encore. Le pattern à suivre est celui de `SearchAgent` et `UpdateAgent` dans `core/agent/agent/` : hériter de `BaseAgent`, définir un `process()` avec injection de contexte, et choisir un subset de tools. Ce Scan Agent reçoit un chemin sur le filesystem local (pas dans le vault) et une description de ce que ça représente. Il explore la structure par lui-même avec `tree` et `read`, identifie les fichiers pertinents, et envoie leur contenu à l'`UpdateAgent` pour ingestion dans le vault. Pas d'embedding, pas de `search` — exploration pure. Il faudra probablement une route dédiée dans `routes.py` et un tool MCP correspondant dans `mcp_server/tools.py` (à côté de `update` et `search` existants).

## Mock Data

- [ ] Affiner les mock data pour la démo

  Des mock data existent déjà dans le vault de test. Il faut construire un scénario narratif cohérent — plusieurs projets, plusieurs clients, des états variés (actif, bloqué, terminé), des changelogs avec des décisions tagguées `[décision]`, des inbox items en attente. Le scénario doit montrer les deux agents sous leur meilleur jour : une recherche complexe cross-projet qui démontre la pertinence du search, et un update qui route intelligemment vers plusieurs fichiers. Le format attendu est documenté dans `ENVIRONMENT_PROMPT` (`env_prompt.py`) — `overview.md`, `projects/[name]/state.md`, `projects/[name]/changelog.md`, etc. Brainstormer un persona utilisateur spécifique (freelance dev, consultant, etc.) avec des projets qui ont une vraie tension narrative pour la démo MCP avec différents clients.

## Logging

- [x] Restreindre les logs au mode dev uniquement

  `object_logger` dans `core/agent/utils/raw_logger.py` sauvegarde tous les appels LLM bruts dans `./logs/raw_requests/` et imprime `[DEBUG] Raw stream logs saved to ...` — ça arrive en prod. `log_agent_event()` dans `core/agent/utils/logger.py` écrit dans stdout via `logger.info/debug` et dans un fichier NDJSON `logs/agent_events_*.jsonl`. Conditionner tout ça à une variable d'environnement (`DEV=true` ou `LOG_LEVEL`), probablement dans `env.py`. Les routes `/search` et `/update` dans `routes.py` appellent `log_agent_event(event)` dans leur boucle — ce sont les points d'entrée à conditionner.