# Architecture — Knower MVP

*Note : La vision produit et les objectifs de démonstration du MVP se trouvent dans `idea.md`. Ce document est la carte technique du système. Il décrit ce qu'on construit et comment les pièces s'articulent entre elles.*

Le détail de chaque domaine vit dans un fichier dédié.

---

## Les composants du système

Le système est un seul service local — pas de cloud, pas de Docker,
pas d'infrastructure complexe. Il tourne directement sur la machine.
Il fait cinq choses : il maintient le vault, il expose un MCP server,
il sert l'interface web, il indexe le vault pour la search,
et il observe les changements de fichiers pour les propager partout.

### Le vault

Un dossier de fichiers markdown sur le filesystem local.
C'est la source de vérité unique du système. Lisible directement
depuis VS Code, un terminal, n'importe quel outil.
Pas de base de données, pas de format propriétaire.

La structure du vault et le détail de chaque fichier → `vault.md`

### Les agents

Deux agents distincts. Un seul modèle — puissant, grand context window.

**L'agent de update** — déclenché quand de l'information arrive.
Il lit le vault, décide du routing, écrit, et logue ses actions.
Contexte mental : *"Où est-ce que je range cette information ?"*

**L'agent de search** — déclenché quand une question est posée.
Il lit le vault, cherche le contexte pertinent, et retourne une réponse structurée.
Read-only. Contexte mental : *"Qu'est-ce que l'utilisateur a besoin de savoir ?"*

Les deux agents, leurs tools, et le system prompt → `agents.md`

### Le MCP server

Expose deux routes : `update` et `search`.
L'interface web et Claude Code sont deux clients de ces mêmes routes.
Ils parlent tous les deux aux mêmes endpoints.
Le vault est la source de vérité — peu importe le client.

Tourne en local uniquement pour le MVP.

Les routes, la queue, le background job, et le processing pipeline → `infrastructure.md`

### Le search engine

QMD indexe les fichiers permanents du vault.
Deux modes : BM25 rapide et pipeline complet avec re-ranking sémantique.
Les résultats sont assemblés par le concat engine avant d'être retournés.

La mécanique de search, QMD, et le concat engine → `search.md`

### Le file watcher

Process qui observe le vault en continu via chokidar.
À chaque changement de fichier — création, modification, suppression, déplacement —
il émet des events vers tous les consumers qui écoutent.

C'est le système nerveux du produit. Sans lui :
- Le file tree de la sidebar ne se met pas à jour
- Les fichiers ouverts dans la zone centrale ne se re-rendent pas
- Le badge inbox ne se rafraîchit pas
- Le background job ne se déclenche pas

Trois consumers principaux :

**Le background job** — sur chaque écriture :
calcule les tokens du fichier, met à jour `tokens` et `updated` dans le frontmatter,
régénère `tree.md`, ré-indexe le fichier dans QMD.

**L'interface web** — sur chaque changement :
re-render du file tree dans la sidebar,
re-render du fichier ouvert dans la zone centrale si c'est le fichier modifié,
mise à jour du badge inbox (compte les folders dans `inbox/`).

**L'agent (indirect)** — les agents ne lisent pas les events directement.
Ils lisent les fichiers au moment de leur exécution.
Mais le background job — déclenché par les events du watcher —
garantit que `tree.md` et les frontmatters sont toujours à jour
quand les agents les lisent.

Le détail du watcher dans le contexte de l'interface → `interface.md`
Le détail du background job → `infrastructure.md`

### L'interface web

Web app servie par le service. React + shadcn/ui + Tailwind.
Sidebar gauche avec file tree + zone centrale avec trois vues + chat input fixe.

Le layout, les vues, et le chat input → `interface.md`

---

## Le flux d'une information qui entre dans le système

1. L'utilisateur envoie du texte ou une image via le chat input en mode update,
   ou via Claude Code qui appelle la route `update` du MCP server.

2. Le processing pipeline transforme les fichiers si nécessaire
   (texte passe tel quel, images passent telles quelles au modèle vision).

3. La route `update` retourne immédiatement un acknowledgment
   et place la requête dans la queue séquentielle.

4. L'agent de update est déclenché depuis la queue.
   Il charge `overview.md`, `tree.md`, `profile.md` en contexte.
   Il navigue le vault avec ses tools, décide du routing, écrit.
   Il logue ses actions dans `changelog.md`.

5. Chaque écriture déclenche le file watcher.
   Le background job met à jour les frontmatters et régénère `tree.md`.
   L'interface re-render le file tree et le fichier ouvert si concerné.

6. Si le signal est insuffisant pour router avec confiance,
   l'agent crée un folder dans `inbox/` avec un `review.md`
   qui expose son raisonnement et pose une question précise.
   Le badge inbox s'incrémente automatiquement.

---

## Le flux d'une question posée au système

1. L'utilisateur pose une question via le chat input en mode search,
   ou via Claude Code qui appelle la route `search` du MCP server.

2. L'agent de search est déclenché immédiatement — la search est read-only,
   elle ne passe pas par la queue.

3. L'agent charge `overview.md`, `tree.md`, `profile.md` en contexte.
   Il utilise le search tool pour identifier les chunks pertinents.
   Il lit les fichiers nécessaires pour construire du contexte complet.

4. L'agent produit une overview de 2 à 5 lignes sur ce qu'il a trouvé.
   Il spécifie les fichiers et sections pertinents.
   Le concat engine assemble le tout en un document markdown structuré.

5. La réponse est retournée — dans l'interface ou au client MCP.

---

## Le flux d'une réponse à un item inbox

1. L'utilisateur voit le badge inbox dans la sidebar.
   Il ouvre la vue inbox, lit le `review.md` de l'item en attente.

2. Il clique "Répondre" — le chat input passe en mode answering.
   Un bandeau rappelle à quel item la réponse est liée.

3. Il envoie sa réponse. Elle part vers la route `update` avec
   la metadata `inbox_ref: [folder-path]` qui identifie l'item inbox concerné.

4. L'agent de update voit l'`inbox_ref` dans la requête.
   Il lit le folder inbox correspondant en premier, intègre la réponse,
   route les fichiers vers leur destination, supprime le folder,
   logue dans `changelog.md` global.

5. Le file watcher détecte la suppression du folder inbox.
   Le badge inbox se décrémente automatiquement.

---

## Invariants du système

Ces principes ne changent pas, quelle que soit la feature ou la décision d'implémentation.

**Le vault est la source de vérité.**
Deux clients, un vault. L'interface et Claude Code lisent et écrivent au même endroit.

**À l'entrée des agents, tout est soit du texte, soit une image.**
Le processing pipeline garantit cet invariant quelle que soit la source.

**Un agent ne maintient jamais ses propres métadonnées de fichier.**
Les champs `tokens` et `updated` dans le frontmatter sont gérés
exclusivement par le background job — jamais par un LLM.

**Les updates sont séquentielles, les searches sont parallèles.**
La queue garantit qu'un seul agent de update écrit dans le vault à la fois.
Les searches sont read-only et peuvent tourner sans restriction en parallèle.

**L'inbox est le seul point de friction volontaire.**
Pour tout le reste, l'agent agit et l'utilisateur voit dans le changelog.
La friction n'existe que quand l'ambiguïté est réelle.

**Pas d'archivage.**
`tasks.md` est une vue live — les tâches complétées disparaissent
et deviennent des événements dans le changelog.
Les changelogs grandissent indéfiniment — c'est prévu, c'est voulu.

---

## Hors scope MVP

- Notifications externes (Discord, Telegram) et inbox reply depuis canal externe
- Streaming WebSocket en temps réel des actions de l'agent
- Séparation orchestrateur / worker (deux tiers de modèles)
- Paramètres `head` et `tail` sur le tool `read`
- Scopes cross-cutting (`all-states`, `all-changelogs`, etc.)
- Filtrage par date sur le search tool
- Code execution tool
- MCP en cloud et authentification
- Sync git ou rsync du vault
- Édition des fichiers depuis l'interface
- Support Windows et cross-platform
- Streaming WebSocket en temps réel des actions de l'agent
- Différenciation de la sortie search entre MCP et interface
  (le format overview + fichiers concaténés est identique dans les deux contextes pour le MVP)
- Archivage de quelque nature que ce soit — `tasks.md` est une vue live,
  les changelogs grossissent indéfiniment, rien n'est jamais archivé