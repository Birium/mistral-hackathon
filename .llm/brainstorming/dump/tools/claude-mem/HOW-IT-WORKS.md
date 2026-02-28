# `claude-mem` — Documentation Technique Exhaustive
## Compréhension Globale du Système de Mémoire Persistante pour Agents IA

---

## Préambule : La Philosophie du Projet

`claude-mem` résout un problème fondamental des LLMs : **ils oublient tout entre deux sessions**. Chaque fois que vous ouvrez un nouveau chat, l'IA repart de zéro. Elle ne sait pas que vous avez refactorisé l'authentification la semaine dernière, qu'un bug chronique a été corrigé d'une certaine façon, ou que vous avez pris une décision architecturale importante.

La solution naïve serait de coller tout l'historique de chat dans le contexte de l'IA. C'est inutilisable à grande échelle : trop de tokens consommés, trop de bruit, et les LLMs sont mauvais pour extraire l'essentiel d'un long historique brut.

La solution de `claude-mem` est radicalement différente. **Il ne sauvegarde pas la conversation. Il sauvegarde la connaissance extraite de la conversation.** Pour ce faire, pendant que vous interagissez avec votre IA principale, un second agent LLM tourne en arrière-plan, observe ce que fait l'IA principale, et en extrait une mémoire structurée, sémantique, et indexable.

Ce document décrit dans les moindres détails comment ce système fonctionne, depuis la capture d'une action jusqu'à son injection dans un futur contexte.

---

## Partie 1 : L'Architecture Globale

### 1.1 Le Pattern de l'Agent Observateur

L'architecture centrale de `claude-mem` est un **Observer Pattern asynchrone à double agent**. Il faut absolument comprendre cette dualité dès le départ car tout le reste en découle.

- **L'Agent Principal** : C'est l'IA avec laquelle vous travaillez au quotidien (Claude Code, Cursor, etc.). Il répond à vos questions, lit des fichiers, exécute des commandes, écrit du code. Il ne sait pas que `claude-mem` existe. Il travaille normalement.
- **L'Agent Observateur** : C'est un second LLM (Claude, Gemini ou OpenRouter selon la configuration) qui tourne dans un processus Node.js en arrière-plan. Il ne parle jamais à l'utilisateur directement. Son unique rôle est de regarder ce que fait l'Agent Principal et d'en extraire une connaissance structurée.

La communication entre les deux agents n'est pas directe. Elle passe par une infrastructure de capture et de file d'attente qui garantit qu'aucune information n'est perdue, même si le processus crash.

### 1.2 Les Trois Piliers Technologiques

Le système repose sur trois composants technologiques distincts, chacun ayant un rôle précis :

1. **SQLite (via `bun:sqlite`)** : La base de données relationnelle. C'est la source de vérité absolue. Elle stocke toutes les métadonnées, tous les textes, toutes les relations. Elle est configurée en mode WAL (Write-Ahead Logging) pour supporter de fortes concurrences sans bloquer les lectures pendant les écritures.

2. **ChromaDB (via un sous-processus Python `chroma-mcp`)** : La base de données vectorielle. Elle ne stocke pas les données complètes. Elle stocke uniquement des représentations mathématiques (vecteurs) du texte pour permettre la recherche sémantique. Elle est lancée comme un sous-processus `uvx` pour éviter d'alourdir Node.js avec des dépendances de Machine Learning.

3. **Node.js / Bun (le Runtime)** : L'orchestrateur global. Il expose une API HTTP, gère les sessions, héberge l'Agent Observateur, et coordonne les deux bases de données.

### 1.3 Le Flux de Données Global

Pour poser les bases avant d'entrer dans les détails, voici le flux de données de bout en bout :

```
[IDE / CLI]
    │
    │  Action de l'IA principale (ex: lire un fichier)
    ▼
[Hook PostToolUse]
    │
    │  Requête HTTP POST (non-bloquante) vers le Worker
    ▼
[PendingMessageStore - SQLite]  ← Sas de sécurité
    │
    │  Événement Node.js en mémoire (zéro-latence)
    ▼
[SessionQueueProcessor]  ← Générateur asynchrone
    │
    │  Claim du message + transmission à l'Agent
    ▼
[Agent Observateur (Claude/Gemini/OpenRouter)]
    │
    │  Appel API LLM avec prompt de type "observateur XML"
    ▼
[ResponseProcessor + Parser XML]
    │
    │  Transaction atomique SQLite (INSERT + DELETE)
    ▼
[observations / session_summaries - SQLite]  ← Mémoire persistante
    │
    │  Fan-out asynchrone (Fire-and-Forget)
    ├──────────────────────►  [ChromaDB]  ← Indexation vectorielle
    ├──────────────────────►  [CLAUDE.md / .cursor/rules]  ← Injection contexte
    └──────────────────────►  [SSE Broadcaster]  ← Interface web temps réel
```

---

## Partie 2 : Le Modèle de Données

Avant de comprendre comment les données circulent, il faut comprendre ce qu'elles contiennent. `claude-mem` ne stocke pas du texte brut. Il stocke des entités fortement typées.

### 2.1 Les Sessions (`sdk_sessions`)

Une Session est l'objet racine. Elle représente une interaction en cours entre l'utilisateur et l'IA principale. Elle est créée au premier message et reste ouverte jusqu'à la fin de la conversation.

La table `sdk_sessions` contient les champs suivants :
- **`id`** : Clé primaire interne.
- **`content_session_id`** : L'ID de la session réelle dans Claude Code ou Cursor. C'est l'identifiant de votre vraie conversation.
- **`memory_session_id`** : L'ID de la session fantôme créée côté API Anthropic pour l'Agent Observateur. C'est un ID séparé pour que les "pensées" de l'Agent Observateur ne contaminent jamais votre historique de conversation. Ce champ est rempli à la première réponse de l'Agent Observateur et sauvegardé pour permettre de reprendre la conversation côté Agent à chaque nouveau message.
- **`project`** : Le chemin du projet (ex: `/home/user/mon-projet`). C'est la clé de partitionnement principale pour toutes les recherches ultérieures.
- **`status`** : L'état de la session (`'active'` ou `'completed'`).
- **`created_at`** et **`updated_at`** : Timestamps ISO.

### 2.2 Les Prompts Utilisateur (`user_prompts`)

Chaque fois que vous tapez une demande à l'IA (ex: "Ajoute un bouton de login"), ce texte est sauvegardé dans la table `user_prompts`. C'est le point d'entrée de toute la chaîne mémorielle. Cette table est essentiellement un log des intentions utilisateur, liées à leur `content_session_id`.

### 2.3 Les Observations (`observations`) — Le Cœur du Système

C'est l'unité atomique de mémoire. Une Observation est générée par l'Agent Observateur à chaque fois qu'il analyse une action de l'IA principale. Elle représente une connaissance extraite d'une action.

La table `observations` contient les champs suivants :

- **`id`** : Clé primaire. Utilisée comme référence dans ChromaDB (les IDs Chroma sont des dérivés de cet ID, ex: `obs_123_narrative`).
- **`session_id`** : Lien vers la session parente.
- **`project`** : Hérité de la session. Utilisé comme filtre principal dans toutes les recherches.
- **`type`** : La catégorie sémantique de l'observation. C'est une valeur parmi : `bugfix`, `feature`, `refactor`, `decision`, `discovery`, `change`. Ce champ est l'un des filtres les plus utilisés dans la recherche SQLite stricte.
- **`title`** : Un titre très court (moins de 10 mots) résumant ce qui s'est passé.
- **`subtitle`** : Un second niveau de résumé, légèrement plus détaillé que le titre.
- **`narrative`** : Le corps principal de l'observation en texte libre. C'est ici que l'Agent Observateur explique en détail : Pourquoi cette action a-t-elle été prise ? Quel problème résout-elle ? Comment ça fonctionne ? Quelles sont les implications ? C'est ce champ qui est découpé et envoyé à ChromaDB pour l'indexation vectorielle.
- **`facts`** : Un tableau JSON de faits concrets, immuables, et vérifiables. Ex: `["La fonction login utilise bcrypt avec salt=12", "Le token JWT expire après 24h"]`. Chaque fait est envoyé individuellement à ChromaDB comme un document séparé pour maximiser la précision de la recherche sémantique.
- **`concepts`** : Un tableau JSON de tags conceptuels qui décrivent la nature de l'observation. Ex: `["how-it-works", "what-changed", "why-decided"]`. Ces tags sont utilisés comme filtres métadonnées dans ChromaDB et comme filtres `json_each` dans SQLite.
- **`files_read`** : Un tableau JSON des chemins de fichiers que l'IA a lus pendant cette action. Indexé pour la recherche par fichier.
- **`files_modified`** : Un tableau JSON des chemins de fichiers que l'IA a modifiés. Indexé pour la recherche par fichier.
- **`discovery_tokens`** : Une métrique de "coût de découverte". Elle représente combien de tokens ont été consommés par l'IA principale pour trouver cette information. Plus ce nombre est élevé, plus l'information est "chère" à redécouvrir et donc plus elle mérite d'être mémorisée.
- **`created_at_epoch`** : Timestamp en millisecondes Unix. Utilisé pour les filtres de plage de dates dans SQLite et pour le filtre de récence (90 jours) dans ChromaDB.

### 2.4 Les Résumés de Session (`session_summaries`)

À la fin d'une session (quand l'IA a fini de répondre), l'Agent Observateur génère un bilan global de tout ce qui s'est passé. Ce n'est pas une Observation supplémentaire mais une synthèse narrative.

La table `session_summaries` contient :
- **`request`** : La paraphrase de ce que l'utilisateur a demandé au début de la session.
- **`investigated`** : Un texte décrivant tout ce que l'IA principale a exploré pour comprendre le problème (fichiers lus, structures analysées, code parcouru).
- **`learned`** : Ce que l'IA a découvert sur le système en cours de route (patterns architecturaux, dépendances inattendues, configurations importantes).
- **`completed`** : Ce qui a été concrètement réalisé (fichiers modifiés, fonctions ajoutées, bugs corrigés).
- **`next_steps`** : Les actions que l'Agent Observateur suggère d'entreprendre lors de la prochaine session pour continuer le travail.

---

## Partie 3 : Le Pipeline de Maintien de la Mémoire

### 3.1 Étape 1 — La Capture (Les Hooks)

Tout commence par des "Hooks" qui s'intègrent dans l'IDE ou le CLI. Ces hooks sont des callbacks déclarés dans la configuration de l'outil (ex: `.claude/hooks.json` pour Claude Code, ou dans les paramètres de Cursor).

Il existe trois hooks principaux, chacun correspondant à un moment précis du cycle de vie d'une interaction :

**Hook `session-init` (Début de session) :**
Il se déclenche quand l'utilisateur envoie son premier message. Le hook capture le texte brut du prompt utilisateur. Avant de l'envoyer, il applique un pré-traitement : il supprime les blocs `<private>...</private>` que l'utilisateur aurait pu inclure pour cacher des informations sensibles (mots de passe, clés API). Il envoie ensuite le texte nettoyé via une requête HTTP `POST /api/sessions/init` au Worker en arrière-plan.

**Hook `PostToolUse` (Pendant le travail) :**
C'est le hook le plus fréquent. Il se déclenche après chaque utilisation d'outil par l'IA principale. Un "outil" désigne : lire un fichier (`Read`), écrire du code (`Edit`), exécuter une commande bash (`Bash`), faire une recherche (`Grep`), etc. Le hook capture trois informations :
- Le nom de l'outil utilisé (ex: `"Bash"`).
- Les paramètres d'entrée (ex: `{"command": "cat package.json"}`).
- Le résultat de sortie (ex: `{"output": "{\"name\": \"mon-projet\", ...}"}`).

Ces trois données sont packagées et envoyées via `POST /api/sessions/observations`.

**Hook `Stop` (Fin de session) :**
Il se déclenche quand l'IA principale a terminé de répondre et que la conversation est en attente de votre prochaine question. C'est le signal pour l'Agent Observateur de générer le résumé de session global (`session_summary`). Il envoie un signal via `POST /api/sessions/summarize`.

**L'impératif de la non-blocage :**
Toutes ces requêtes HTTP sont envoyées avec un timeout très court (quelques centaines de millisecondes) et les erreurs sont silencieusement ignorées (bloc `catch` sans `throw`). Si le Worker est arrêté ou en surcharge, votre IDE continue de fonctionner normalement. La mémoire de cette action sera simplement perdue, ce qui est un compromis acceptable face à la dégradation de l'expérience utilisateur.

### 3.2 Étape 2 — Le Sas de Sécurité (PendingMessageStore)

Quand le Worker reçoit une requête HTTP, il ne traite pas immédiatement le message. Il l'enregistre d'abord dans une table SQLite dédiée : `pending_messages`. C'est **le composant le plus critique pour la fiabilité du système**.

**Pourquoi ne pas traiter directement le message ?**
Si le Worker traitait le message directement (appel LLM synchrone), un crash pendant l'appel API ferait perdre l'information pour toujours. En le stockant d'abord dans SQLite, le message survit à n'importe quel crash.

**La structure d'un message en queue :**
Chaque message dans `pending_messages` contient :
- **`id`** : Clé primaire.
- **`session_id`** : Lien vers la session parente.
- **`payload`** : Le JSON brut contenant (nom de l'outil, inputs, outputs).
- **`status`** : L'état actuel du traitement. Peut être `'pending'` (en attente), `'processing'` (en cours de traitement par l'Agent).
- **`created_at`** : Timestamp de création.
- **`claimed_at`** : Timestamp du moment où l'Agent a commencé à traiter ce message.

**Le Pattern "Claim-Confirm" (Réserver et Confirmer) :**
C'est le cœur de la robustesse du système. Ce pattern garantit qu'un message est traité exactement une fois.
1. **Enqueue** : Le message est inséré avec le statut `'pending'`.
2. **Claim** : Quand l'Agent Observateur est libre, il exécute un `UPDATE pending_messages SET status='processing', claimed_at=NOW() WHERE id=? AND status='pending'`. La condition `AND status='pending'` garantit qu'un seul processus peut "prendre" le message même en cas de concurrence.
3. **Confirm** : Une fois que l'Agent a terminé son analyse et que la mémoire est sauvegardée (voir Étape 5, la Transaction Atomique), le message est définitivement supprimé de `pending_messages` avec un `DELETE`.

**Le mécanisme d'Auto-guérison (Self-Healing) :**
Au démarrage du Worker et périodiquement pendant son fonctionnement, le `PendingMessageStore` exécute une requête de "reset" : `UPDATE pending_messages SET status='pending', claimed_at=NULL WHERE status='processing' AND claimed_at < (NOW() - 60 seconds)`. Si un message est resté bloqué en `'processing'` depuis plus de 60 secondes, c'est qu'un crash s'est produit pendant son traitement. Le système le remet en `'pending'` pour qu'il soit retraité au prochain cycle.

### 3.3 Étape 3 — Le Réveil de l'Agent (Zéro-Latence)

Une fois le message dans `pending_messages`, comment l'Agent Observateur sait-il qu'il doit se réveiller ? Il ne fait pas de "polling" (vérifier la base de données toutes les X secondes), car ce serait coûteux en CPU et introduirait une latence inutile.

Le système utilise une combinaison d'un `EventEmitter` Node.js et d'un générateur asynchrone.

**Le `SessionManager` (L'émetteur d'événements) :**
Le `SessionManager` est le composant qui reçoit les requêtes HTTP. Dès qu'il a écrit un message dans `pending_messages` (Étape 2), il émet immédiatement un événement Node.js en mémoire : `emitter.emit('message', sessionId)`. Cet événement en mémoire est instantané et sans coût.

**Le `SessionQueueProcessor` (Le générateur asynchrone `async*`) :**
Le `SessionQueueProcessor` est un générateur asynchrone (un `AsyncIterableIterator`). Il est attaché à un `EventEmitter` et se comporte comme suit :
- Dans son état normal, il est suspendu (`await new Promise(resolve => emitter.once('message', resolve))`).
- Quand il reçoit l'événement `'message'`, il se réveille, fait un `claimNextMessage()` dans SQLite, et `yield` (donne) le message à l'Agent Observateur.
- Il se rendort immédiatement après, prêt pour le prochain événement.

Ce design garantit que l'Agent Observateur reçoit un nouveau message à traiter dans les millisecondes qui suivent son insertion en base, sans jamais consommer de CPU en attente.

### 3.4 Étape 4 — L'Agent Observateur (La Transformation Intelligente)

C'est ici que la donnée brute (nom d'outil, input, output) est transformée en connaissance structurée. Cela se passe dans `SDKAgent.ts`, `GeminiAgent.ts` ou `OpenRouterAgent.ts` selon la configuration.

**L'Historique de Conversation de l'Agent :**
L'Agent Observateur maintient son propre historique de conversation (`conversationHistory`), distinct de votre historique de conversation avec l'IA principale. Cet historique lui permet de comprendre le contexte de chaque action. Par exemple, si l'IA principale lit d'abord un fichier, puis en modifie un autre, l'Agent Observateur peut voir la séquence complète et comprendre le lien entre les deux actions.

**L'Isolation via le `memory_session_id` :**
Pour que les messages de l'Agent Observateur n'apparaissent pas dans votre interface Claude Code, le système utilise un second ID de session auprès de l'API Anthropic (le `memory_session_id`). À la première réponse de l'Agent, le SDK Anthropic génère un `session_id` pour cette conversation. `claude-mem` capture cet ID et le sauvegarde dans `sdk_sessions.memory_session_id`. Lors du prochain message dans la même session utilisateur, `claude-mem` utilise ce `memory_session_id` pour continuer la conversation côté Agent Observateur, en préservant son fil de pensée.

**La Construction du Prompt d'Initialisation (`buildInitPrompt`) :**
La toute première fois que l'Agent Observateur reçoit un message dans une nouvelle session, un System Prompt massif est construit. Ce prompt contient :
- La définition du rôle de l'Agent : "Tu es un Agent Observateur. Tu ne parles pas à l'utilisateur. Tu analyses les actions d'un autre agent IA."
- Les instructions de format de sortie : "Tu dois répondre UNIQUEMENT en XML. Tes balises sont `<observation>`, `<type>`, `<title>`, `<subtitle>`, `<narrative>`, `<facts>`, `<concepts>`, `<files_read>`, `<files_modified>`."
- Les définitions de chaque type d'observation (quand utiliser `bugfix` vs `decision` vs `discovery`).
- Des exemples de bonne et mauvaise observation pour guider le LLM (few-shot prompting).
- Le contexte du projet (nom, chemin, technologies utilisées si elles sont disponibles).

**La Construction du Prompt d'Observation (`buildObservationPrompt`) :**
Pour chaque outil utilisé par l'IA principale, un prompt spécifique est construit et ajouté à `conversationHistory` :
```xml
<observed_from_primary_session>
  <what_happened>Bash</what_happened>
  <parameters>{"command": "grep -r 'useAuth' src/ --include='*.ts'"}</parameters>
  <outcome>{"output": "src/components/Header.tsx:8: const { user } = useAuth();\nsrc/pages/Profile.tsx:12: const auth = useAuth();"}</outcome>
</observed_from_primary_session>
```
L'Agent Observateur reçoit ce prompt et doit répondre avec sa balise `<observation>` correspondante.

**La Construction du Prompt de Résumé (`buildSummaryPrompt`) :**
Quand le hook `Stop` se déclenche, un prompt différent est construit. Il dit à l'Agent Observateur : "La session est terminée. En te basant sur toutes les observations que tu as générées jusqu'ici, génère maintenant un résumé global au format XML avec les balises `<request>`, `<investigated>`, `<learned>`, `<completed>`, `<next_steps>`."

### 3.5 Étape 5 — La Transaction Atomique (Le Verrouillage de la Mémoire)

L'Agent Observateur a généré sa réponse XML. Il faut maintenant la parser et la sauvegarder. C'est le rôle du `ResponseProcessor.ts` et de `parser.ts`.

**Le Parsing XML (`parser.ts`) :**
Le système utilise des expressions régulières pour extraire les balises XML de la réponse du LLM. Ce choix (Regex plutôt qu'un vrai parser XML) est délibéré : les LLMs produisent parfois du XML légèrement malformé (balises oublié, espaces parasites). Les Regex sont plus tolérantes que les parsers XML stricts.

Pour chaque balise extraite, le système valide le contenu :
- Le `type` doit être l'une des valeurs autorisées. Si ce n'est pas le cas, il est mis à `'discovery'` par défaut.
- Les tableaux JSON (`facts`, `concepts`, `files_modified`, `files_read`) sont parsés avec un `JSON.parse()` encapsulé dans un `try-catch`. Si le JSON est invalide, le champ est mis à `[]` (tableau vide) sans faire crasher le système.
- Si le LLM hallucine un résultat et ne produit pas de `<observation>` du tout (ce qui arrive rarement), le message est marqué comme "failed" dans `pending_messages` mais la session continue.

**La Transaction Atomique (`transactions.ts`) :**
C'est le moment le plus important pour la cohérence des données. Le système utilise la capacité de SQLite à exécuter des transactions (blocs `db.transaction(() => { ... })`). Le principe est le suivant : toutes ces opérations s'exécutent, ou aucune ne s'exécute.

La transaction contient :
1. `INSERT INTO observations (session_id, project, type, title, ...) VALUES (?, ?, ?, ?, ...)`
2. Si c'est un résumé : `INSERT INTO session_summaries (...) VALUES (...)`
3. `DELETE FROM pending_messages WHERE id = ?`

Si une de ces opérations échoue (ex: disque plein, contrainte de clé étrangère), SQLite fait un Rollback complet. L'observation n'est pas sauvegardée, et le message reste dans `pending_messages` avec son statut `'processing'`. Le mécanisme d'Auto-guérison de l'Étape 2 le reprendra au prochain cycle et tentera de le retraiter.

Cette transaction atomique garantit deux propriétés fondamentales :
- **Pas de mémoire fantôme** : Il est impossible d'avoir une observation sauvegardée sans que le pending message correspondant soit supprimé.
- **Pas de perte de données** : Il est impossible de supprimer un pending message sans que la mémoire correspondante soit définitivement sauvegardée.

### 3.6 Étape 6 — Le Fan-Out Asynchrone (La Distribution de la Connaissance)

Une fois la donnée en sécurité dans SQLite, le `ResponseProcessor` déclenche plusieurs actions de distribution en parallèle, toutes en mode "Fire-and-Forget". Si l'une de ces actions échoue, SQLite reste la source de vérité et les données ne sont pas perdues.

**A. La Synchronisation ChromaDB (`ChromaSync.ts`) :**
C'est ici que le contenu textuel de l'observation est transformé en vecteurs pour permettre la recherche sémantique.

La granularité du découpage est cruciale : une seule observation n'est pas envoyée comme un seul document. Elle est découpée en plusieurs micro-documents :
- Le `narrative` complet devient un document avec l'ID `obs_{id}_narrative`.
- Chaque `fact` individuel du tableau JSON devient son propre document avec l'ID `obs_{id}_fact_{index}`.

Ce découpage est intentionnel. Un vecteur représentant un court fait précis ("La fonction login utilise bcrypt avec salt=12") est beaucoup plus précis et utile pour la recherche que le vecteur d'un long paragraphe qui mélange plusieurs sujets.

Chaque document envoyé à ChromaDB est accompagné de métadonnées :
```json
{
  "doc_type": "observation_narrative",
  "observation_id": 123,
  "project": "/home/user/mon-projet",
  "type": "bugfix",
  "created_at_epoch": 1734567890000
}
```
Ces métadonnées sont utilisées pour le pré-filtrage dans ChromaDB avant le calcul vectoriel (voir Partie 4).

**B. La Mise à Jour des Fichiers Contextuels (`claude-md-utils.ts`) :**
`claude-mem` maintient des fichiers Markdown dans le projet pour injecter du contexte directement dans l'IDE.

Si l'observation mentionne des fichiers dans `src/components/`, le système cherche (ou crée) un fichier `src/components/CLAUDE.md`. Il y injecte un bloc Markdown résumant les observations récentes concernant ce dossier. La prochaine fois que l'IA principale navigue dans ce dossier et lit ce fichier, elle a accès au contexte mémoriel sans même avoir besoin de faire une recherche explicite.

**C. La Mise à Jour des Règles Cursor (`CursorHooksInstaller.ts`) :**
Si l'utilisateur utilise Cursor, le système met à jour le fichier `.cursor/rules/claude-mem-context.mdc`. Ce fichier est automatiquement injecté dans chaque nouveau contexte de chat Cursor par les règles de l'IDE. Il contient la Timeline récente générée par le `TimelineBuilder`.

**D. La Mise à Jour de `CLAUDE.md` (Pour Claude Code) :**
Le fichier `CLAUDE.md` à la racine du projet est le mécanisme d'injection de contexte pour Claude Code. `claude-mem` y maintient une section dédiée avec la Timeline récente. Claude Code injecte automatiquement le contenu de `CLAUDE.md` dans le contexte de chaque nouvelle conversation.

**E. Le Broadcast SSE (`SSEBroadcaster.ts`) :**
Un événement Server-Sent Events est émis vers l'interface web locale (`http://localhost:37777`). Cet événement contient la nouvelle observation sérialisée en JSON. L'interface web reçoit cet événement sans avoir besoin de recharger la page et affiche la nouvelle mémoire en temps réel, avec une animation de "clignotement".

---

## Partie 4 : Le Système de Recherche

### 4.1 L'Orchestrateur de Recherche (`SearchOrchestrator`)

Le `SearchOrchestrator` est le point d'entrée unique pour toute recherche. Il prend en paramètre un objet `SearchQuery` qui peut contenir :
- `query` : Un texte de recherche en langage naturel (optionnel).
- `project` : Le projet dans lequel chercher (obligatoire).
- `type` : Un filtre sur le type d'observation (optionnel).
- `concepts` : Un filtre sur les tags conceptuels (optionnel).
- `files` : Un filtre sur les fichiers touchés (optionnel).
- `dateFrom` / `dateTo` : Une plage de dates (optionnel).
- `limit` : Le nombre maximum de résultats souhaités.

L'Orchestrateur analyse ces paramètres et applique l'arbre de décision suivant :

**Nœud 1 :** Y a-t-il un texte de recherche (`query`) ?
- **NON** → Routage vers la **Recherche SQLite Stricte** (les filtres structurés suffisent).
- **OUI** → Vérification si ChromaDB est disponible.

**Nœud 2 (si `query` présent) :** ChromaDB est-il disponible et opérationnel ?
- **NON** → Fallback vers la **Recherche SQLite Stricte** avec le `query` utilisé comme filtre `LIKE` sur le `narrative`.
- **OUI** → Vérification de la complexité des filtres.

**Nœud 3 (si ChromaDB disponible) :** Y a-t-il des filtres structurés en plus du texte (`type`, `concepts`, `files`, dates) ?
- **NON** → Routage vers la **Recherche Sémantique Pure** (Chroma seul).
- **OUI** → Routage vers la **Recherche Hybride** (Chroma + SQLite en intersection).

### 4.2 Moteur 1 — La Recherche SQLite Stricte (`SQLiteSearchStrategy`)

Ce moteur est utilisé quand on veut une précision de 100% sur des critères objectifs. Il construit une requête SQL dynamiquement selon les paramètres fournis.

**La construction de la requête :**

La requête de base est toujours :
```sql
SELECT * FROM observations WHERE project = ?
```

Des clauses `WHERE` supplémentaires sont ajoutées dynamiquement :

**Filtre de type :**
```sql
AND type = 'bugfix'
```
Simple comparaison d'égalité. Très rapide car le champ `type` est indexé.

**Filtre de date :**
```sql
AND created_at_epoch >= 1734480000000
AND created_at_epoch <= 1734566400000
```
Comparaison numérique sur les timestamps Unix en millisecondes. Extrêmement rapide sur un champ indexé.

**Filtre de concepts (Tags JSON) :**
SQLite propose la fonction `json_each()` qui "déplie" un tableau JSON en lignes. Le filtre sur les concepts utilise une sous-requête avec `EXISTS` pour maximiser les performances :
```sql
AND EXISTS (
  SELECT 1
  FROM json_each(concepts)
  WHERE value = 'what-changed'
)
```
Si la colonne `concepts` contient `["how-it-works", "what-changed"]`, cette requête trouvera bien l'observation.

**Filtre de fichiers :**
Même principe avec `json_each()` mais on utilise un `LIKE` avec un wildcard pour permettre les chemins partiels (ex: chercher "auth" trouvera `src/auth.ts` et `src/lib/auth/utils.ts`) :
```sql
AND EXISTS (
  SELECT 1
  FROM json_each(files_modified)
  WHERE value LIKE '%auth%'
)
```

**Filtre de texte (fallback sans ChromaDB) :**
Si ChromaDB n'est pas disponible mais qu'un `query` textuel est fourni, un `LIKE` est appliqué sur le `narrative` et le `title` :
```sql
AND (narrative LIKE '%authentification%' OR title LIKE '%authentification%')
```
Ce filtre est moins précis (il ne comprend pas la sémantique) mais garantit un résultat même sans le sous-processus Python.

**Le tri final :**
Les résultats sont toujours triés par `created_at_epoch DESC` (les plus récents d'abord) puis `LIMIT ?` est appliqué.

### 4.3 Moteur 2 — La Recherche Sémantique Pure (`ChromaSearchStrategy`)

Ce moteur est utilisé quand on veut trouver des observations liées à un concept ou une question posée en langage naturel.

**Étape 1 — Le Pré-filtrage par Métadonnées :**
Avant tout calcul vectoriel, ChromaDB reçoit une clause `where` basée sur les métadonnées :
```json
{
  "project": "/home/user/mon-projet",
  "doc_type": {"$in": ["observation_narrative", "observation_fact"]}
}
```
Ce pré-filtrage élimine immédiatement tous les documents qui n'appartiennent pas au projet actuel. C'est critique : sans ce filtre, un projet très actif polluerait les résultats d'un autre projet avec des observations sémantiquement similaires mais contextuellement hors-sujet.

**Étape 2 — Le Calcul Vectoriel :**
ChromaDB transforme le `query` textuel (ex: "Comment est gérée l'authentification ?") en un vecteur de nombres flottants via un modèle d'embedding (ex: `all-MiniLM-L6-v2` par défaut dans Chroma). Il calcule ensuite la "distance cosinus" entre ce vecteur et tous les vecteurs des documents pré-filtrés. La distance cosinus mesure l'angle entre deux vecteurs : plus l'angle est petit (plus ils pointent dans la même direction sémantique), plus les documents sont pertinents.

ChromaDB renvoie les 100 meilleurs résultats (paramètre `n_results=100`) avec pour chacun :
- Son ID (ex: `obs_123_fact_0`).
- Sa distance cosinus (ex: `0.1823`).
- Ses métadonnées (ex: `{observation_id: 123, project: "...", type: "decision"}`).

**Étape 3 — Dédoublonnage et Extraction des IDs SQLite :**
Comme une observation peut avoir plusieurs fragments dans ChromaDB (narrative + plusieurs facts), la même observation peut apparaître plusieurs fois dans les 100 résultats. Le système fait deux choses :
- Il utilise une Regex pour extraire l'ID SQLite de l'ID Chroma : `/obs_(\d+)_(narrative|fact_\d+)/`.
- Pour chaque `observation_id` SQLite, il ne conserve que le fragment avec le **meilleur score** (la distance cosinus la plus faible).

Cette déduplication garantit qu'on obtient une liste d'IDs SQLite uniques, classés par pertinence sémantique.

**Étape 4 — Le Filtre de Récence :**
Un filtre supplémentaire est appliqué en mémoire après la réponse de ChromaDB : toute observation dont le `created_at_epoch` est plus vieux que `Date.now() - (90 * 24 * 60 * 60 * 1000)` est éliminée. L'argument est que le code évolue trop vite pour que des souvenirs de plus de 90 jours soient encore pertinents. Ce filtre est configurable.

**Étape 5 — L'Hydratation depuis SQLite :**
ChromaDB ne renvoie jamais les données textuelles complètes. Il renvoie uniquement des IDs. Le système prend la liste finale d'IDs SQLite uniques et fait :
```sql
SELECT * FROM observations WHERE id IN (123, 456, 789)
```
Il reconstitue ensuite les résultats complets en respectant l'ordre de classement dicté par les scores de ChromaDB (le SQL `IN` ne garantit pas l'ordre, donc un tri manuel est appliqué après).

### 4.4 Moteur 3 — La Recherche Hybride (`HybridSearchStrategy`)

C'est le moteur le plus puissant. Il combine la précision absolue de SQLite avec la pertinence sémantique de ChromaDB.

**L'Algorithme d'Intersection avec Maintien du Rang (`intersectWithRanking`) :**

**Phase 1 — Le Tamis SQLite :**
Le système lance en premier la recherche SQLite stricte avec tous les filtres structurés disponibles (`type`, `concepts`, `files`, `dates`). Il récupère une liste d'IDs d'observations strictement conformes aux filtres. Disons qu'il récupère `[10, 15, 42, 89, 105, 223]`.

Cette liste représente "la vérité absolue" : ce sont les seules observations éligibles selon les critères objectifs.

**Phase 2 — Le Classement Chroma :**
En parallèle (ou séquentiellement), le système lance la recherche sémantique dans ChromaDB avec le texte du `query`. Chroma renvoie une liste d'IDs classés par pertinence : disons `[89, 2, 42, 99, 10, 501, 15, 223]`.

Cette liste représente "l'opinion" de l'IA vectorielle sur ce qui est pertinent, mais sans tenir compte des contraintes structurelles.

**Phase 3 — L'Intersection :**
La fonction `intersectWithRanking` parcourt la liste de Chroma (qui a le bon ordre) et ne conserve que les éléments qui sont aussi présents dans la liste SQLite (qui a la vérité stricte) :
- `89` : présent dans SQLite ✅ → Résultat 1
- `2` : absent de SQLite ❌ → Éliminé
- `42` : présent dans SQLite ✅ → Résultat 2
- `99` : absent de SQLite ❌ → Éliminé
- `10` : présent dans SQLite ✅ → Résultat 3
- `501` : absent de SQLite ❌ → Éliminé
- `15` : présent dans SQLite ✅ → Résultat 4
- `223` : présent dans SQLite ✅ → Résultat 5

**Résultat final** : `[89, 42, 10, 15, 223]`. Ces éléments sont à la fois strictement conformes aux filtres (SQLite) ET classés par pertinence sémantique (Chroma).

**Phase 4 — Complétion si insuffisant :**
Si après l'intersection il y a moins de résultats que le `limit` demandé (ex: il ne reste que 2 résultats sur 10 demandés), le système peut opter à compléter avec les observations SQLite restantes (celles qui étaient dans la liste SQLite mais pas dans la liste Chroma), triées par date. Cela garantit un nombre de résultats suffisant même dans des cas rares.

---

## Partie 5 : Le Rendu et l'Injection de Contexte

### 5.1 Le `ContextBuilder` et le `TimelineBuilder`

Avoir une base de mémoire est inutile si l'IA ne peut pas y accéder facilement. Le `ContextBuilder` et le `TimelineBuilder` sont responsables de transformer les résultats de recherche bruts en un format consommable par un LLM de manière efficiente (peu de tokens).

**Le Groupement par Date :**
Les observations récupérées sont d'abord groupées par jour avec la fonction `groupByDate`. Chaque groupe est affiché sous un en-tête de date formaté : `### Dec 14, 2025`.

**Le Groupement par Fichier :**
À l'intérieur de chaque groupe de date, les observations sont re-groupées par fichier touché (via `files_modified`). Cela crée une structure hiérarchique :
```
### Dec 14, 2025
  **src/auth.ts**
    - [bugfix] Fix JWT expiration logic
  **src/components/Login.tsx**
    - [feature] Add remember-me checkbox
```

**La Génération du Tableau Markdown Optimisé :**
Le tableau final est généré en Markdown ultra-dense pour minimiser les tokens consommés. Chaque ligne ressemble à :
```
| #123 | 14:30 | 🐛 | Fix: JWT expiration logic | ~45 tokens |
```
Les champs sont :
- L'ID de l'observation (pour permettre un appel de recherche précis).
- L'heure (et non la date complète, pour éviter la répétition dans le groupe).
- Un emoji représentant le type (`🐛` = bugfix, `✨` = feature, `🔄` = refactor, `🏛️` = decision, `🔍` = discovery, `📝` = change).
- Le titre de l'observation.
- Une estimation du coût en tokens pour aller lire le détail complet.

**L'Estimation de Tokens (`estimateTokens`) :**
Pour chaque observation, le système estime le nombre de tokens que consommerait la lecture de son `narrative` et de ses `facts` complets. Cette estimation permet à l'IA de prendre une décision économique : "Cette observation coûterait 200 tokens à lire. Est-ce que ça vaut le coup pour ma question actuelle ?" L'estimation est basée sur une heuristique simple : `Math.ceil(texte.length / 4)` (approximation de la tokenisation GPT/Claude).

### 5.2 L'Injection Physique dans l'IDE

Le tableau Markdown généré par le `TimelineBuilder` est injecté dans le contexte de l'IA principale de deux façons :

**Pour Claude Code :**
Le tableau est écrit dans la section `## Recent Memory` du fichier `CLAUDE.md` à la racine du projet. Claude Code lit ce fichier automatiquement au début de chaque session. L'IA principale peut voir la timeline et utiliser les IDs pour appeler l'outil `get_observations(ids=[123])` via MCP pour aller lire les détails complets.

**Pour Cursor :**
Le tableau est écrit dans `.cursor/rules/claude-mem-context.mdc`. Les règles Cursor sont injectées automatiquement dans chaque contexte de chat. L'IA Cursor peut lire la timeline et demander des détails via l'outil MCP correspondant.

### 5.3 L'Exposition via MCP (Model Context Protocol)

Le MCP est le protocole qui permet à l'IA principale de communiquer avec des outils externes de manière structurée. `claude-mem` expose plusieurs outils via MCP :

- **`search_memory(query, project, type, concepts, files, ...)`** : Lance le SearchOrchestrator avec les paramètres fournis et renvoie la liste d'observations formatées.
- **`get_observations(ids[])`** : Récupère les données complètes (narrative, facts, tous les champs) pour une liste d'IDs précis. C'est le moyen pour l'IA d'aller "lire le détail" d'une ligne de la timeline.
- **`get_session_summary(session_id)`** : Récupère le résumé d'une session passée.
- **`get_project_context(project)`** : Renvoie un résumé global du projet en agrégeant les observations récentes les plus importantes.

---

## Conclusion : La Boucle Complète

Pour récapituler et visualiser comment tout s'imbrique dans une interaction réelle :

1. **Vous posez une question** à l'IA principale. Le hook `session-init` capture votre prompt et l'envoie au Worker.
2. **L'IA principale commence à travailler**. Elle lit des fichiers, exécute des commandes. Chaque action déclenche le hook `PostToolUse`, qui enqueue le message dans `pending_messages`.
3. **En parallèle et de manière invisible**, l'Agent Observateur se réveille à chaque nouveau message, l'analyse, et génère une observation XML qu'il sauvegarde dans SQLite via une transaction atomique.
4. **ChromaDB est mis à jour** avec les fragments vectoriels de la nouvelle observation. `CLAUDE.md` est mis à jour avec la nouvelle timeline.
5. **L'IA principale finit de répondre**. Le hook `Stop` déclenche la génération du résumé de session.
6. **La session est terminée**. La mémoire est prête pour la prochaine session.
7. **Au début de votre prochaine question**, l'IA principale lit `CLAUDE.md` et voit la timeline. Elle peut utiliser les IDs pour appeler `get_observations()` via MCP et récupérer les détails de n'importe quel souvenir pertinent pour votre question.

Le résultat : une IA qui sait ce qu'elle a fait la semaine dernière, pourquoi elle a pris certaines décisions, quels bugs elle a corrigés et comment, et qui peut reprendre n'importe quel travail en cours sans que vous ayez à tout réexpliquer.