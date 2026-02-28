# Infrastructure

Le système est un seul service local.
Pas de Docker, pas de cloud, pas d'infrastructure complexe.
Il tourne directement sur la machine avec Node.js ou Bun.

---

## Le service

Le service fait cinq choses :
- Il maintient le vault (via les agents et le background job)
- Il expose un MCP server (deux routes : `update` et `search`)
- Il sert l'interface web (React app statique)
- Il observe les changements de fichiers (chokidar → SSE vers le frontend)
- Il indexe le vault pour la search (QMD)

Tout tourne dans le même process.
L'interface et Claude Code sont deux clients des mêmes routes MCP.
Ils parlent au même service, ils lisent et écrivent dans le même vault.

---

## Le MCP server

Expose deux routes. Tourne en local uniquement pour le MVP.

### Route `update`

Reçoit de l'information : texte, images, fichiers convertis.

Retourne immédiatement un acknowledgment sans attendre le processing :
```json
{ "status": "accepted", "id": "update-xyz" }
```

Le processing se fait en background via la queue séquentielle.
L'appelant ne bloque pas — il continue son travail.

**Payload entrant :**
- Contenu texte ou images
- Optionnel : `inbox_ref: [folder-path]` si c'est une réponse à un item inbox

Quand `inbox_ref` est présent, l'agent de update sait qu'il s'agit
d'une réponse à un item inbox en attente.
Il lit le folder inbox concerné en premier, intègre la réponse,
route les fichiers, supprime le folder, logue dans `changelog.md` global.

### Route `search`

Reçoit une query textuelle.

Traitement immédiat — la search ne passe pas par la queue.
Read-only, pas de risque de conflit d'écriture sur le vault.
Peut tourner en parallèle des updates en cours de processing.

Retourne du markdown structuré :
une overview rédigée par l'agent suivie des fichiers pertinents
assemblés par le concat engine.

Le format de sortie exact → `search.md`.

---

## Le processing pipeline

Avant que quoi que ce soit n'arrive à la queue et aux agents,
les données entrantes passent par un pipeline de transformation
qui vit dans le backend, en amont de la queue.

**Ce qui passe directement, sans transformation :**
- Le texte brut, sous n'importe quelle forme (messages, notes, contenus copiés-collés)
- Les images — passées directement au modèle vision, jamais converties en descriptions texte

**Ce qui est transformé avant d'arriver :**
- Les PDFs → convertis en markdown par une lib de conversion
  *(les PDFs sont le premier fast-follow post-MVP — pas dans le scope initial)*

**L'invariant du système :**
à l'entrée des agents, tout est soit du texte, soit une image.
Ce principe reste vrai quelle que soit la source ou le format d'origine.

Au lancement du MVP : texte et images uniquement.

---

## La queue des updates

In-memory, séquentielle.
Une update ne commence pas son processing tant que la précédente
n'est pas terminée.

**Pourquoi séquentielle :**
Deux agents de update en parallèle qui écrivent dans les mêmes fichiers
créeraient des conflits d'écriture impossibles à résoudre proprement.
La queue séquentielle évite ça de façon triviale.

**Pourquoi in-memory :**
Usage personnel, quelques updates par heure au maximum.
Pas de Redis, pas d'infrastructure de queue distribuée.
Le truc le plus simple qui marche.
La complexité peut grandir si le besoin se fait sentir concrètement, pas avant.

**Flux d'une update dans la queue :**

1. La route `update` reçoit la requête
2. Elle retourne immédiatement l'acknowledgment au client
3. Elle place la requête en fin de queue
4. Quand c'est son tour, le processing pipeline transforme les fichiers si nécessaire
5. L'agent de update est déclenché avec le contenu transformé
6. L'agent navigue le vault, décide du routing, écrit les fichiers
7. Chaque écriture déclenche le file watcher → background job + SSE vers le frontend

---

## Le background job

Process programmatique — pas un agent, pas un LLM.
Déclenché par le file watcher après chaque écriture, suppression,
ou déplacement de fichier dans le vault.
Event-driven, pas périodique. Immédiat, sans overhead.

**À chaque déclenchement :**

1. **Calcule les tokens du fichier modifié**
   Formule : `Math.ceil(text.length / 4)` — approximation suffisante,
   rapide, sans dépendance externe.

2. **Met à jour le frontmatter du fichier**
   Écrit les champs `tokens` (valeur calculée) et `updated` (timestamp courant).
   L'agent ne pense jamais à maintenir ces métadonnées — c'est de la plomberie,
   pas du raisonnement.

3. **Régénère `tree.md`**
   Recalcule le tree complet du vault avec les nouvelles valeurs de tokens
   et timestamps. Le format exact → `vault.md`.

4. **Ré-indexe le fichier modifié dans QMD**
   Uniquement le fichier qui vient d'être modifié — pas un full re-scan.
   Économie massive d'I/O sur un vault qui peut contenir des centaines de fichiers.

**Prévention de la boucle infinie :**
Le background job écrit dans le vault (frontmatter des fichiers, `tree.md`).
Ces écritures déclenchent le file watcher, qui pourrait re-déclencher
le background job indéfiniment.

Pour éviter ça : le background job marque ses propres écritures
avec un flag interne avant de les effectuer.
Le file watcher ignore les events qui portent ce flag.
Concrètement — chokidar expose une option `awaitWriteFinish` et le service
maintient un `Set` de paths en cours d'écriture par le background job.
Quand un event arrive sur un path présent dans ce `Set`, il est ignoré.

**Ce que le background job ne fait pas :**
Il ne lit pas le contenu des fichiers pour en comprendre le sens.
Il ne prend pas de décisions. Il ne logue pas dans le changelog.
Il est entièrement déterministe — même input, même output, toujours.

---

## Connexions entre composants

```
                        ┌─────────────────┐
                        │   MCP Server    │
                        │  /update        │
                        │  /search        │
                        └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
             route /update             route /search
                    │                         │
         ┌──────────▼──────────┐    ┌─────────▼─────────┐
         │  Processing pipeline │    │  Agent de search   │
         │  (texte / images)    │    │  (read-only)       │
         └──────────┬──────────┘    └─────────┬──────────┘
                    │                         │
         ┌──────────▼──────────┐              │
         │  Queue séquentielle  │         concat engine
         └──────────┬──────────┘              │
                    │                         │
         ┌──────────▼──────────┐    ┌─────────▼──────────┐
         │  Agent de update     │    │  Réponse formatée  │
         │  (lecture + écriture)│    │  overview + fichiers│
         └──────────┬──────────┘    └────────────────────┘
                    │
              écriture dans le vault
                    │
         ┌──────────▼──────────┐
         │   File watcher       │◄──────────── chokidar
         │   (chokidar)         │
         └──────┬───────────────┘
                │
      ┌─────────┴──────────┐
      │                    │
┌─────▼──────┐    ┌────────▼──────┐
│ Background │    │  SSE stream   │
│    job     │    │  → frontend   │
│            │    │               │
│ - tokens   │    │ - file tree   │
│ - updated  │    │ - open file   │
│ - tree.md  │    │ - inbox badge │
│ - QMD idx  │    └───────────────┘
└────────────┘
```

---

## Ce qui est hors scope MVP côté infrastructure

- MCP en cloud et authentification
- Sync git ou rsync du vault
- Notifications externes (Discord, Telegram) et inbox reply depuis canal externe
- Séparation orchestrateur / worker (deux tiers de modèles)
- Support Windows et cross-platform (macOS uniquement pour le MVP)