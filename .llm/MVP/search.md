# Search

La search repose sur deux composants distincts qui travaillent en séquence :
QMD indexe le vault et retourne des chunks pertinents,
le concat engine assemble ces chunks en un document structuré.
L'agent de search orchestre les deux.

---

## QMD — l'engine d'indexation

QMD indexe les fichiers markdown du vault et expose des modes de recherche
avec classement par pertinence. C'est la couche qui permet de trouver
du contexte précis dans un vault qui peut atteindre des centaines de milliers de tokens
sans charger l'intégralité des fichiers en contexte.

Seuls les fichiers permanents et structurés du vault sont indexés.
Les fichiers toujours déjà en contexte direct (`overview.md`, `tree.md`, `profile.md`)
et le contenu temporaire (`inbox/`) ne sont jamais indexés.
La table complète de ce qui est indexé → `vault.md`.

### Stratégie de chunking

QMD chunke aux breakpoints de score élevé dans la structure markdown.
H1 = score 100, H2 = score 90. Ce sont les points de découpe naturels.

Cette stratégie est alignée avec le format des fichiers du vault :

**Changelogs** (H1 par jour, H2 par entrée) :
Le H1 de date est le chunk principal — une journée entière reste cohérente.
La séquence des événements d'une journée conserve son contexte narratif.
Si une journée est très dense, QMD découpe au H2 entre deux entrées —
jamais au milieu d'une entrée. Le contenu d'une entrée reste intact.

**Tasks** (H1 par tâche) :
Chaque tâche est un chunk QMD séparé.
Un search BM25 sur "status: en-cours" retourne toutes les tâches actives
de tous les fichiers tasks indexés — sans ouvrir chaque fichier manuellement.

**Fichiers courts** (`description.md`, `state.md`) :
Généralement un seul chunk par fichier.
Ces fichiers sont conçus pour être lus en entier quand ils sont pertinents.

**Bucket items** :
Chaque fichier bucket est un chunk ou plusieurs selon sa taille.
Le frontmatter YAML est inclus dans le chunk — il porte les métadonnées
qui enrichissent les résultats de search.

---

## Les deux modes du search tool

### `mode: "fast"` — BM25

BM25 pur. Millisecondes, aucun modèle chargé.

BM25 tokenise le corpus, calcule la rareté de chaque terme (IDF),
pondère par la fréquence dans le document (TF), et retourne des résultats
classés par score de pertinence. Un terme rare qui apparaît dans 2 chunks
sur 200 reçoit un poids énorme. Un terme omniprésent comme "projet" est quasi ignoré.

**Quand l'utiliser :**
- Noms propres, dates, identifiants
- Tags exacts : `[décision]`, `status: bloqué`, `status: en-cours`
- Recherches de termes précis : "Marie", "API externe", "TVA Q3"
- Requêtes structurées sur les métadonnées frontmatter

**Exemples :**
```
search("[décision]", mode: "fast")
→ toutes les décisions du vault, classées par pertinence BM25

search("bloqué", mode: "fast", scope: "project:startup-x")
→ tous les chunks de startup-x contenant "bloqué"
```

### `mode: "deep"` — pipeline complet

Pipeline complet : expansion de requête, BM25, recherche vectorielle,
fusion RRF (Reciprocal Rank Fusion), re-ranking sémantique.
Quelques secondes.

**Quand l'utiliser :**
- Questions sémantiques et formulations vagues
- Recherches conceptuelles sans termes exacts connus
- "Ce truc qu'on avait décidé sur l'architecture de paiement"
- "Tout ce qui concerne la relation avec le client principal"
- Recherches cross-projet où la pertinence est sémantique

**Exemples :**
```
search("décision sur l'architecture de paiement", mode: "deep")
→ chunks sémantiquement liés, même sans correspondance exacte de termes

search("relation client", mode: "deep", scope: "project:startup-x")
→ tout le contexte lié au client dans startup-x, par similarité sémantique
```

L'agent choisit le mode selon la nature de la requête.
`deep` est souvent le choix par défaut quand la précision compte.
`fast` est le bon choix quand on cherche quelque chose de précis et nommé.

### Le paramètre `scope`

Optionnel. Sans scope, la search couvre tout le vault indexé.

`scope: "project:[nom]"` — restreint la search aux fichiers d'un projet spécifique :
`description.md`, `state.md`, `tasks.md`, `changelog.md`, `bucket/*`.

```
search("deadline", mode: "fast", scope: "project:startup-x")
→ uniquement dans les fichiers de startup-x
```

---

## Le concat engine

Le concat engine est un composant mécanique — pas un LLM, pas un agent.
Son rôle : assembler les fichiers identifiés par l'agent de search
en un seul document markdown structuré, prêt à être retourné.

L'agent de search lui fournit une liste de fichiers,
avec pour chacun soit un adressage par fichier complet,
soit un adressage par range de lignes (`lines 1-45`).
L'engine assemble le tout en préfixant chaque bloc par le path du fichier concerné.

**L'adressage par range de lignes** est utile sur les longs changelogs :
l'agent identifie via `search()` que les lignes 1-45 d'un changelog
contiennent les entrées pertinentes, sans avoir besoin de charger
le fichier entier (potentiellement 50k tokens) pour construire sa réponse.

---

## Format de sortie

La sortie du search est composée de deux parties dans l'ordre suivant.

**Partie 1 — L'overview de l'agent.**
Rédigée par l'agent de search au terme de son exploration.
Il résume ce qu'il a trouvé, dans quels fichiers, et en quoi
c'est pertinent par rapport à la question posée.
Ce n'est pas une synthèse profonde — c'est une orientation.
Deux à cinq lignes. Produite par le LLM.

**Partie 2 — Les fichiers concaténés.**
Produite mécaniquement par le concat engine.
Pas de résumé, pas de reformulation. Le contenu brut des fichiers,
avec leur path comme header pour savoir d'où vient chaque bloc.

```
[overview rédigée par l'agent — 2 à 5 lignes d'orientation]

---

## projects/startup-x/state.md

[contenu complet du fichier]

## projects/startup-x/changelog.md (lines 1-45)

[contenu des lignes 1 à 45]

## vault/tasks.md

[contenu complet du fichier]
```

Ce format est identique pour le MCP et pour l'interface web.
L'interface rend la partie 1 comme du markdown normal,
et la partie 2 comme des blocs de fichiers avec leur header de path.

---

## Flux complet d'une recherche

1. L'agent de search reçoit la question.
   Il charge `overview.md`, `tree.md`, `profile.md` en contexte.

2. Il lit l'overview pour identifier les projets potentiellement pertinents
   avant tout appel outil.

3. Il appelle `search()` avec le mode et le scope appropriés.
   Il reçoit des chunks classés par pertinence.

4. En fonction des chunks reçus, il décide quels fichiers lire en entier
   via `read()` pour construire un contexte complet.
   Il peut appeler `tree()` pour explorer la structure d'un projet
   si des fichiers supplémentaires semblent pertinents.

5. Il rédige son overview — 2 à 5 lignes sur ce qu'il a trouvé
   et en quoi c'est pertinent par rapport à la question.

6. Il spécifie au concat engine la liste des fichiers et ranges à assembler.

7. Le concat engine produit le document structuré.

8. La réponse complète (overview + fichiers concaténés) est retournée
   à l'interface ou au client MCP.