# Interface web

Web app servie par le service local.
Stack : React + shadcn/ui + Tailwind.
Markdown renderer : Streamdown ou Plate.js, read-only pour le MVP.

---

## Philosophie

L'interface est une fenêtre sur le vault, pas un éditeur.
Elle montre ce qui existe, ce qui vient de changer, ce qui attend une réponse.
L'utilisateur ne modifie rien directement depuis l'interface —
il envoie de l'information ou pose des questions via le chat input.
Le vault change, l'interface reflète.

Le chat input est l'unique point d'interaction active.
Tout le reste est de la lecture et de la navigation.

---

## Layout général

Deux colonnes. Sidebar fixe à gauche, zone centrale à droite.
Le chat input flotte au-dessus du contenu, ancré en bas de la zone centrale.

```
┌──────────────┬─────────────────────────────────────────────┐
│              │                                             │
│   Sidebar    │   Zone centrale                             │
│   (fixe)     │   (scrollable)                              │
│              │                                             │
│   File tree  │   Vue fichier / activité / inbox            │
│              │                                             │
│              │                                             │
│              │                                             │
│              │                                             │
│              │                                             │
│              │   ┌───────────────────────────────────────┐ │
│              │   │  ░░░░░░░░░ Chat input ░░░░░░░░░░░░░  │ │
│  ┌────────┐  │   │  ░░░░░░░░░ (floating) ░░░░░░░░░░░░░  │ │
│  │Inbox [2]│  │   └───────────────────────────────────────┘ │
└──┴────────┴──┴─────────────────────────────────────────────┘
```

Le chat input **ne repousse pas** le contenu vers le haut.
Il se superpose. Le contenu de la zone centrale scroll librement
derrière le chat input. Un `padding-bottom` sur la zone scrollable
garantit que le dernier élément n'est jamais masqué.

---

## Le chat input — floating

Le composant central de l'interface. Toujours visible, toujours accessible.

**Position et style :**
- `position: fixed`, ancré en bas de la zone centrale
- Largeur : suit la zone centrale (ne couvre pas la sidebar)
- `backdrop-filter: blur` + fond semi-opaque
- `box-shadow` vers le haut — légère, juste assez pour le détacher du contenu
- Margin bottom par rapport au bord inférieur de la fenêtre
- Coins arrondis

**Composition du chat input :**

```
┌─────────────────────────────────────────────────────────┐
│  [Update ▾]    Votre message...                    📎 ↑ │
└─────────────────────────────────────────────────────────┘
```

De gauche à droite :
- **Toggle de mode** — bouton dropdown qui affiche le mode actif (`Update` ou `Search`)
- **Zone de texte** — auto-resize, une ligne par défaut, grandit avec le contenu
- **Bouton attachment** (📎) — joindre des images
- **Bouton envoyer** (↑) — actif uniquement quand il y a du contenu

**En mode answering** — un bandeau apparaît au-dessus du champ :

```
┌─────────────────────────────────────────────────────────┐
│  ↩ Réponse à : 2025-07-14-vocal-meeting-client       ✕ │
├─────────────────────────────────────────────────────────┤
│  [Update ▾]    Votre réponse...                    📎 ↑ │
└─────────────────────────────────────────────────────────┘
```

Le bandeau rappelle l'item inbox concerné.
Le `✕` annule le mode answering et revient au mode update.
Après envoi, le mode answering se désactive automatiquement.

---

## Les trois modes du chat input

### Mode update (défaut)

L'utilisateur envoie de l'information au système.
Texte libre, images jointes si besoin.
Déclenche l'agent de update via la route `update`.

C'est le mode par défaut. Le toggle affiche `Update`.

### Mode search

L'utilisateur pose une question ou formule une recherche.
Déclenche l'agent de search via la route `search`.

Le switch entre update et search est un **toggle explicite** —
pas de détection automatique d'intention. L'utilisateur clique
sur le dropdown et choisit `Search`. Le toggle affiche `Search`.

### Mode answering

Activé uniquement depuis la vue inbox via le bouton "Répondre".
C'est la seule exception au toggle manuel — le mode se déclenche
automatiquement quand l'utilisateur clique "Répondre" sur un item inbox.

Le bandeau au-dessus du champ identifie l'item inbox concerné.
L'input part vers la route `update` avec la metadata
`inbox_ref: [folder-path]` automatiquement injectée.
L'utilisateur ne voit pas ce mécanisme — il voit juste le bandeau.

Quand la réponse est envoyée, le mode answering se désactive
et le chat input revient au mode update.

---

## Sidebar gauche

Fixe, ne scroll pas indépendamment (sauf si le tree est très long).
Deux zones : le file tree en haut, l'icône inbox en bas.

```
┌──────────────────────┐
│  vault/              │
│  ├── overview.md     │
│  ├── profile.md      │
│  ├── tasks.md        │
│  ├── changelog.md    │
│  ├── inbox/          │
│  │   └── 2025-07-... │
│  ├── bucket/         │
│  │   └── ... 2 files │
│  └── projects/       │
│      ├── startup-x/  │
│      │   └── ...     │
│      └── appart-.../  │
│          └── ...     │
│                      │
│                      │
│ ──────────────────── │
│  📥  Inbox       [2] │
└──────────────────────┘
```

### File tree

Reflète la structure réelle du vault en temps réel.
Mis à jour de façon incrémentale via SSE — pas de rechargement complet.

**Chaque ligne affiche :**
- Icône fichier (📄) ou dossier (📁) — ou chevron pour les dossiers
- Nom du fichier ou dossier
- Tokens — discret, grisé, aligné à droite (ex: `380 tk`)

**Interactions :**
- **Clic sur un fichier** → ouvre la vue fichier dans la zone centrale.
  Le fichier cliqué reçoit un highlighting persistant (fond coloré ou border gauche)
  qui reste actif tant que ce fichier est affiché.
- **Clic sur un dossier** → expand/collapse.
  Chevron rotatif (▸ collapsé, ▾ déplié).
- **Dossiers projet** collapsés par défaut — leur structure interne
  est connue et répétable, pas besoin de la déplier systématiquement.

### Icône inbox

Séparée du file tree par une ligne horizontale.
Position : en bas de la sidebar, toujours visible.

- Affiche un badge numérique quand des folders existent dans `inbox/`
- Le badge est un **tracker programmatique** — le file watcher observe `inbox/`,
  compte les folders, met à jour le badge. Pas l'agent.
- **Clic** → ouvre la vue inbox dans la zone centrale
- Quand l'inbox est vide : pas de badge, icône seule

---

## Zone centrale — trois vues

La zone centrale est scrollable indépendamment.
Son contenu change selon l'interaction : clic sur un fichier,
envoi d'un message, clic sur l'icône inbox.

Le chat input floating se superpose au contenu, toujours visible en bas.

---

### Vue fichier

Déclenchée par un clic sur un fichier dans le file tree.

```
┌─────────────────────────────────────────────────────────┐
│  projects/startup-x/state.md                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ## Statut global                                       │
│  actif                                                  │
│                                                         │
│  ## Focus actuel                                        │
│  Intégration du module de paiement                      │
│                                                         │
│  ## Ce qui bloque                                       │
│  API externe : prestataire indisponible avant juin.     │
│  Décision d'internaliser.                               │
│                                                         │
│                                                         │
│                                         (scrollable)    │
│                                                         │
│   ┌───────────────────────────────────────────────────┐ │
│   │  [Update ▾]    Votre message...              📎 ↑ │ │
│   └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Header** — le path complet du fichier, affiché comme breadcrumb simple.
`projects / startup-x / state.md` — chaque segment cliquable
pour naviguer dans le file tree.

**Contenu** — rendu markdown, read-only.
Pas d'édition pour le MVP.
Le frontmatter YAML n'est pas affiché — ce sont des métadonnées système,
pas du contenu utile pour l'utilisateur.

**Mise à jour en temps réel** — si le fichier affiché est modifié
(par l'agent, par le background job), le contenu se re-render automatiquement
via SSE. Le scroll position est préservé — le re-render ne ramène pas
l'utilisateur en haut de page.

**Temps de chargement** — négligeable. Les fichiers sont locaux,
la lecture est quasi-instantanée. Pas d'état de loading visible.

---

### Vue activité

Déclenchée par l'envoi d'un message via le chat input.
C'est la vue qui montre ce que le système fait ou a trouvé.

**Pour le MVP : pas de streaming.**
Le frontend envoie la requête, affiche un état de chargement,
et attend la réponse complète du backend.
Pas de WebSocket, pas d'étapes en temps réel.

#### Après un update

L'agent a routé l'information, écrit les fichiers, loggé dans le changelog.
La vue affiche une confirmation sobre.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ✓  Mémoire mise à jour                                │
│                                                         │
│  state.md mis à jour — statut passé à bloqué            │
│  1 tâche ajoutée dans tasks.md                          │
│  Entrée ajoutée dans changelog.md                       │
│                                                         │
│  Fichiers touchés :                                     │
│   → projects/startup-x/state.md                        │
│   → projects/startup-x/tasks.md                        │
│   → projects/startup-x/changelog.md                    │
│                                                         │
│                                                         │
│   ┌───────────────────────────────────────────────────┐ │
│   │  [Update ▾]    Votre message...              📎 ↑ │ │
│   └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

- **Micro-résumé** — quelques lignes qui disent ce que l'agent a fait.
  Pas un paragraphe. Des phrases courtes, factuelles.
- **Fichiers touchés** — liste de paths, chacun cliquable.
  Clic → ouvre le fichier dans la vue fichier.
  L'utilisateur peut vérifier ce que l'agent a écrit.

#### Après un search

L'agent a trouvé du contexte pertinent. La vue affiche
l'overview de l'agent suivie des fichiers concaténés par le concat engine.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  J'ai trouvé 3 références à la décision sur l'API      │
│  dans startup-x. La décision a été prise le 14 juillet  │
│  suite à l'indisponibilité du prestataire.              │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  projects/startup-x/state.md                            │
│  ┌─────────────────────────────────────────────────┐    │
│  │ ## Statut global                                │    │
│  │ bloqué                                          │    │
│  │                                                 │    │
│  │ ## Ce qui bloque                                │    │
│  │ API externe : prestataire indisponible...       │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  projects/startup-x/changelog.md (lines 9-14)          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ ## [décision] Abandon de l'API externe          │    │
│  │ Le prestataire ne peut pas livrer avant juin.   │    │
│  │ Notre deadline est mars. Impact : tâches        │    │
│  │ d'intégration supprimées.                       │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│   ┌───────────────────────────────────────────────────┐ │
│   │  [Search ▾]    Votre question...             📎 ↑ │ │
│   └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

- **Overview de l'agent** — 2 à 5 lignes d'orientation.
  Rendu markdown normal. C'est du texte rédigé par le LLM.
- **Séparateur** — ligne horizontale entre l'overview et les fichiers.
- **Fichiers concaténés** — chaque bloc a un header avec le path du fichier
  (et la range de lignes si applicable). Le contenu est rendu en markdown
  dans un bloc visuellement distinct (fond légèrement différent, bordure).
  Les headers de path sont cliquables → ouvrent le fichier complet
  dans la vue fichier.

#### Après un answering

L'agent a intégré la réponse, routé les fichiers, supprimé le folder inbox.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ✓  Item inbox fermé                                    │
│                                                         │
│  2025-07-14-vocal-meeting-client résolu.                │
│  Nouveau projet créé : appart-search                    │
│  Vocal routé vers projects/appart-search/bucket/        │
│  Tâche ajoutée dans tasks.md global                     │
│                                                         │
│  Fichiers touchés :                                     │
│   → projects/appart-search/description.md              │
│   → projects/appart-search/bucket/vocal-meeting.md     │
│   → tasks.md                                           │
│   → changelog.md                                       │
│                                                         │
│   ┌───────────────────────────────────────────────────┐ │
│   │  [Update ▾]    Votre message...              📎 ↑ │ │
│   └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

Même format que la confirmation update :
micro-résumé + fichiers touchés cliquables.

---

### Vue inbox

Déclenchée par un clic sur l'icône inbox de la sidebar.
Deux niveaux : la liste des items, et le détail d'un item.

#### Liste des items inbox

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Inbox (2)                                              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  📩  2025-07-14-vocal-meeting-client             │    │
│  │      il y a 6 heures                            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  📩  2025-07-13-email-comptable                  │    │
│  │      il y a 1 jour                              │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│                                                         │
│   ┌───────────────────────────────────────────────────┐ │
│   │  [Update ▾]    Votre message...              📎 ↑ │ │
│   └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

Chaque item affiche :
- Nom du folder inbox (ex: `2025-07-14-vocal-meeting-client`)
- Temps relatif depuis la création (`il y a 6 heures`)
- Clic → ouvre le détail de l'item

**Inbox vide :**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Inbox                                                  │
│                                                         │
│  Aucun item en attente.                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Détail d'un item inbox

```
┌─────────────────────────────────────────────────────────┐
│  ← Inbox                                                │
│  2025-07-14-vocal-meeting-client                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  J'ai trouvé mention d'un client dans ce vocal et j'ai │
│  cherché dans startup-x, mais aucun des clients         │
│  référencés ne correspond à ce nom.                     │
│                                                         │
│  J'ai aussi repéré une référence à un appartement rue   │
│  de Rivoli — j'ai cherché dans tous tes projets actifs  │
│  et il n'y en a aucun lié à une recherche d'appart.     │
│                                                         │
│  Deux pistes :                                          │
│  - Tâche globale + création d'un projet appart-search   │
│  - Ou c'est lié à un contexte que je ne connais pas     │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  Fichiers d'input :                                     │
│   → transcript-vocal.md                                │
│                                                         │
│                               [ Répondre ]              │
│                                                         │
│   ┌───────────────────────────────────────────────────┐ │
│   │  [Update ▾]    Votre message...              📎 ↑ │ │
│   └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

- **Bouton retour** (`← Inbox`) — revient à la liste des items
- **Titre** — nom du folder inbox
- **Contenu de `review.md`** — rendu markdown. C'est le raisonnement complet
  de l'agent : ce qu'il a cherché, ce qu'il a trouvé, ce qu'il propose.
- **Fichiers d'input** — listés sous un séparateur. Chaque fichier cliquable
  → ouvre le fichier dans la vue fichier.
- **Bouton "Répondre"** — clic déclenche le mode answering du chat input.
  Le bandeau `↩ Réponse à : 2025-07-14-vocal-meeting-client` apparaît
  au-dessus du champ de saisie. La metadata `inbox_ref` est injectée
  automatiquement.

---

## File watcher & SSE

Le file watcher observe le vault en continu via chokidar.
C'est le composant qui rend l'interface vivante.

À chaque changement de fichier dans le vault
(création, modification, suppression, déplacement),
chokidar émet un event côté serveur.
Le serveur pousse cet event vers le frontend via Server-Sent Events (SSE).

Le frontend écoute ce stream SSE en permanence et réagit à chaque event.

### Trois effets côté interface

**Re-render du file tree** —
À chaque changement, le file tree de la sidebar se met à jour.
Le re-render est **incrémental** — seuls les éléments modifiés changent,
pas un rechargement complet du tree.
L'utilisateur voit les fichiers apparaître, changer, disparaître en temps réel.
C'est le moment visible qui prouve que le système travaille.

**Re-render du fichier ouvert** —
Si le fichier actuellement affiché dans la vue fichier vient d'être modifié,
il se re-render automatiquement. Le **scroll position est préservé** —
le re-render ne ramène pas l'utilisateur en haut de page.

**Mise à jour du badge inbox** —
Le file watcher observe spécifiquement `inbox/`.
À chaque création ou suppression d'un folder dans `inbox/`,
il recompte les folders présents et met à jour le badge numérique.
C'est un tracker programmatique — pas l'agent qui maintient ce compteur.

### Pourquoi SSE plutôt que WebSocket

Les events du file watcher sont unidirectionnels : serveur → client.
SSE est la solution native pour ce cas d'usage —
plus simple à implémenter qu'un WebSocket bidirectionnel,
pas de reconnexion à gérer manuellement, support natif dans les navigateurs.

---

## États de l'interface

### Loading

Après envoi d'un message, la zone centrale affiche un état de chargement
pendant que le backend traite la requête.

**Update en cours :**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ⟳  Mise à jour en cours...                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Search en cours :**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ⟳  Recherche en cours...                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

Le chat input reste visible et accessible pendant le loading,
mais le bouton d'envoi est désactivé tant que la requête précédente
n'est pas terminée.

Pendant un update en cours, le file tree continue de se mettre à jour
via SSE — l'utilisateur voit les fichiers changer dans la sidebar
pendant que la confirmation n'est pas encore arrivée.
C'est le premier signal que le système travaille.

### Résultat vide (search)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Aucun résultat trouvé pour "architecture de paiement"  │
│                                                         │
│  Suggestions :                                          │
│  - Reformulez avec des termes différents                │
│  - Essayez le mode Search deep pour une recherche       │
│    sémantique                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Erreur

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ✕  Erreur                                              │
│                                                         │
│  Le service ne répond pas. Vérifiez que le service      │
│  local est bien lancé.                                  │
│                                                         │
│                               [ Réessayer ]             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Inbox vide

Quand l'utilisateur clique sur l'icône inbox et qu'il n'y a rien :
message sobre, pas de contenu fantôme. Documenté dans la section vue inbox.

### État initial

Au premier lancement, avant toute interaction, la zone centrale
affiche un état d'accueil simple — le contenu de `overview.md` rendu
en markdown. C'est la carte du vault, c'est ce que l'utilisateur voit
en ouvrant l'interface. Ça lui donne immédiatement du contexte
sur ce que contient sa mémoire.

---

## Hors scope MVP

- Streaming WebSocket en temps réel des actions de l'agent
- Édition des fichiers depuis la zone centrale
- Support mobile optimisé
- Notifications push externes (Discord, Telegram)
- Différenciation du format de sortie search entre MCP et interface
  (même format overview + fichiers concaténés dans les deux contextes)
- Toggle pour afficher/masquer le frontmatter YAML dans la vue fichier
- Drag & drop de fichiers sur le chat input
- Historique des messages dans le chat input (flèche haut pour rappeler)
- Raccourcis clavier (Cmd+K pour search, etc.)
- Thème sombre / clair (un seul thème pour le MVP)