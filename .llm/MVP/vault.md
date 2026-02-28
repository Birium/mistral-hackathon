# Vault — Structure et fichiers

Le vault est un dossier de fichiers markdown sur le filesystem local.
C'est la source de vérité unique du système.
Lisible directement depuis VS Code, un terminal, n'importe quel outil.
Pas de base de données, pas de format propriétaire.

---

## Structure

```
vault/
├── overview.md
├── tree.md
├── profile.md
├── tasks.md
├── changelog.md
├── inbox/
│   └── 2025-07-14-vocal-meeting-client/
│       ├── review.md
│       └── transcript-vocal.md
├── bucket/
│   ├── article-ai-memory.md
│   └── screenshot-review.md
└── projects/
    └── startup-x/
        ├── description.md
        ├── state.md
        ├── tasks.md
        ├── changelog.md
        └── bucket/
            ├── vocal-meeting-client.md
            └── email-specs-v2.md
```

---

## Initialisation au premier lancement

Le vault est pré-créé au premier lancement.
L'utilisateur ne démarre pas dans le vide.

Ce qui existe dès le départ :
- Les dossiers vides `inbox/`, `bucket/`, `projects/`
- Les fichiers racine : `overview.md`, `tree.md`, `profile.md`, `tasks.md`, `changelog.md`

Ces fichiers contiennent du contenu commenté qui explique leur rôle.
Par exemple, `profile.md` s'ouvre avec une description de ce qu'il est censé contenir.
Ce n'est pas un wizard d'onboarding — c'est un vault déjà structuré,
avec des fichiers qui savent à quoi ils servent avant même qu'on les remplisse.

---

## Fichiers racine

### `overview.md`

La carte complète de tout ce que contient le vault.
C'est le premier fichier chargé par les deux agents à chaque session —
avant d'ouvrir quoi que ce soit d'autre, ils savent ce qui existe.

L'overview sert deux choses simultanément.
Pour l'agent de search, c'est son point de départ : en lisant l'overview,
il sait dans quels projets chercher, ce que chacun contient,
et où il y a de la pertinence avant de faire le moindre appel outil.
Pour l'agent de update, c'est son état global du système :
il sait ce qui existe avant d'agir.

**Ce qu'elle contient :**

Une section avec la date du jour, mise à jour automatiquement à chaque session.
Utile pour contextualiser les informations récentes et les logs.

Une section de contexte de vie — ce qui est vrai maintenant sur la situation
de l'utilisateur et qui impacte tout : un voyage prévu, une contrainte temporaire,
une période de rush, un changement de situation.
Ces informations n'appartiennent à aucun projet mais elles colorent tout.

Une liste de tous les projets, sans exception, avec pour chacun une description
courte et claire de ce que c'est. Pas juste un nom — une phrase qui dit
ce qu'on construit, pourquoi, et où on en est en quelques mots.
C'est cette description qui rend l'overview utile à la search :
avant d'ouvrir un seul fichier projet, l'agent sait si c'est là qu'il doit chercher.
Le statut (actif / pause / terminé) accompagne chaque projet.

Une section pour les intentions pré-projet — des sujets sur lesquels
l'utilisateur accumule de l'information ou réfléchit, sans avoir encore
créé de projet formellement.

Un count des items en attente dans l'inbox.

**Format et taille :**
L'overview n'a pas de limite de taille. Si elle fait 300 lignes parce qu'il y a
beaucoup de projets avec des descriptions riches, c'est exactement ce qu'elle doit faire.
Sa valeur vient de sa complétude, pas de sa concision.

**Mise à jour :**
Réécrite entièrement (`write`) lors de changements structurels : nouveau projet,
projet archivé, changement de contexte de vie.
Jamais indexée dans QMD — toujours chargée directement en contexte.

---

### `tree.md`

Généré automatiquement par le background job après chaque modification du vault.
Jamais édité manuellement. Jamais indexé dans QMD.
Toujours chargé en contexte par les deux agents, après `overview.md`.

Contient la représentation complète du vault avec pour chaque fichier :
son nom, son nombre de tokens, sa date de dernière modification.
Pour chaque dossier : le total de tokens agrégés de tout son contenu.
Les dossiers projet sont collapsés par défaut — leur structure interne
est connue et répétable, pas besoin de la déplier à chaque fois.

**Format :**

```
vault/                                    [52.4k tokens]
├── overview.md                    340 tk · 2h ago
├── profile.md                     280 tk · 5d ago
├── tasks.md                       520 tk · 1d ago
├── changelog.md                 1,200 tk · 3h ago
├── inbox/                               [890 tokens]
│   └── 2025-07-14-vocal-meeting/   890 tk · 6h ago
├── bucket/                            [8.2k tokens]
│   └── ... 2 files
└── projects/                         [41.3k tokens]
    └── startup-x/                    [18.3k tokens]
        └── ... 5 files, 1 folder
```

**Distinction avec le tool `tree()`** :
`tree.md` est la carte initiale, chargée en contexte au démarrage
de chaque session sans aucun appel outil.
Le tool `tree()` est la loupe dynamique — l'agent l'appelle
pendant son raisonnement pour explorer un dossier spécifique plus en détail.

---

### `profile.md`

Identité durable de l'utilisateur. Ce qui est vrai de façon stable :
préférences de travail, habitudes, contraintes récurrentes,
style de communication, informations d'identité utiles
pour contextualiser les réponses.

Évolue lentement, uniquement via des interactions qui révèlent
quelque chose de nouveau et durable sur l'utilisateur.
Toujours chargé en contexte. Jamais indexé dans QMD.

**Distinction avec `overview.md` :**
`profile.md` capture ce qui EST vrai sur l'utilisateur de façon durable.
`overview.md` capture ce qui SE PASSE maintenant.
"Préfère les réponses directes sans blabla" → `profile.md`.
"Part aux États-Unis pour 2 mois" → `overview.md`.

---

### `tasks.md` (global)

Tâches orphelines — non liées à un projet existant, cross-projet,
ou trop petites pour justifier un projet.

**Vue live uniquement.** Ne contient que les tâches actives.
Quand une tâche est complétée, elle disparaît de `tasks.md`
et devient un événement dans `changelog.md`. Pas d'archivage.

**Format — H1 par tâche :**
Chaque tâche est un H1 autonome avec ses métadonnées dans le corps.
Ce format garantit un chunk QMD propre par tâche.
Searching "status: en-cours" retourne instantanément toutes les tâches actives.

```markdown
# Appeler le comptable pour TVA Q3
status: en-cours | prio: haute | ajoutée: 2025-07-14 | projet: —

Contexte : justificatifs demandés avant fin juillet.

# Valider les maquettes avec Marie
status: à-faire | prio: haute | ajoutée: 2025-07-14 | projet: startup-x
deadline: 2025-07-18
```

Indexé dans QMD.

---

### `changelog.md` (global)

Événements et décisions qui se passent au niveau global —
non rattachés à un projet spécifique.
Pivots de vie, décisions meta, intentions non-projet, changements de situation.
C'est le fil conducteur de ce qui se passe globalement.

Grossit indéfiniment. Jamais archivé. Un log est fait pour grossir.
La search QMD permet de retrouver n'importe quelle entrée
sans lire le fichier entier.

**Format — H1 par jour, H2 par entrée, newest first :**

```markdown
# 2025-07-14

## [décision] Prioriser startup-x pour les 3 prochains mois
Le side-project passe en pause.
Raison : deadline investisseur en octobre.

## Changement de banque pro
Migration vers Qonto initiée.
```

Le H1 de date est le chunk principal dans QMD.
Le H2 par entrée permet à QMD de découper proprement si une journée est dense.
Le tag `[décision]` dans le H2 permet un search BM25 instantané
sur toutes les décisions du vault.

**Mode d'édition :**
`append` avec `position: "top"` pour les nouvelles entrées — jamais une réécriture.
L'agent génère le bloc H1/H2 et l'insère sans charger l'historique.

Si la journée en cours existe déjà dans le fichier, l'agent crée quand même
un nouveau bloc H1 avec la même date — deux blocs H1 identiques dans le fichier
sont acceptables et indiquent deux moments de mise à jour distincts.
L'agent ne cherche pas à fusionner avec un H1 existant.
C'est ce qui rend `append` utilisable sans lecture préalable du fichier.

Indexé dans QMD.

---

## `inbox/`

Un folder par item en attente de résolution.
Naming généré par l'agent : `YYYY-MM-DD-description-courte`.

**Contenu d'un folder inbox :**
- Les fichiers d'input originaux tels que reçus (texte, images)
- `review.md` — le raisonnement complet de l'agent

**`review.md` :**
Pas "je ne sais pas où mettre ça."
L'agent expose son travail : ce qu'il a cherché, dans quels projets il est allé,
ce qu'il a trouvé ou pas trouvé, pourquoi le signal était insuffisant,
ce qu'il propose comme routing, et la question précise posée à l'utilisateur.

L'utilisateur lit ça et comprend immédiatement ce que l'agent a essayé.
Il peut corriger une direction, confirmer une hypothèse, ou créer un nouveau projet.
Il ne réexplique pas depuis zéro — il complète un raisonnement exposé.

Exemple :
> "J'ai trouvé mention d'un client dans ce vocal et j'ai cherché dans startup-x,
> mais aucun des clients référencés ne correspond à ce nom. J'ai aussi repéré
> une référence à un appartement rue de Rivoli — j'ai cherché dans tous tes projets
> actifs et il n'y en a aucun lié à une recherche d'appartement.
> Deux pistes : tâche globale + création d'un projet appart-search,
> ou c'est lié à un contexte que je ne connais pas encore."

**Clôture d'un item :**
Quand l'utilisateur répond via le mode answering du chat input,
l'agent exécute le routing, logue dans `changelog.md` global,
supprime le folder inbox entier.

Jamais indexé dans QMD — contenu temporaire.

---

## `bucket/` (global) et `projects/[nom]/bucket/`

Un bucket est un espace de stockage pour tout type de donnée brute :
email, vocal transcrit, article, screenshot, image, note non structurée,
PDF converti, conversation exportée.
Tout ce qui rentre dans le système et qui n'est pas directement
une mise à jour d'un fichier structuré finit dans un bucket.
C'est le matériau brut de la mémoire.

**Deux niveaux de bucket :**

Le **bucket global** (`bucket/` à la racine) contient tout ce qui n'est pas
encore rattaché à un projet, ou ce qui est trop transversal
pour appartenir à un seul projet.
C'est le point d'atterrissage naturel pour les données
dont le routing n'est pas évident.

Les **buckets projet** (`projects/[nom]/bucket/`) contiennent les fichiers
qui appartiennent clairement à un projet spécifique.
Si un fichier concerne deux projets — il est dupliqué dans les deux buckets.
Pas de système de liens croisés. La position dans le file tree EST l'information.

Chaque item dans un bucket est un fichier markdown avec frontmatter YAML.
Tous les buckets sont indexés dans QMD.

---

## Fichiers projet

Chaque projet sous `projects/[nom]/` contient toujours les mêmes fichiers.
La structure est répétable et connue — c'est pourquoi `tree.md`
collapse les dossiers projet par défaut.

### `projects/[nom]/description.md`

Ce qu'est le projet, pourquoi il existe, sa vision, son scope,
ses contraintes, ses décisions structurantes.
Ce qu'on lirait pour comprendre de quoi il s'agit — pas juste le nom.

Ce fichier évolue régulièrement : nouvelle feature ajoutée au scope,
partenaire qui rentre dans la boucle, contrainte technique identifiée,
changement de direction partiel. Il n'est pas réservé aux pivots fondamentaux.
Réécrit entièrement (`write`) quand nécessaire pour garder un document cohérent.

Indexé dans QMD.

---

### `projects/[nom]/state.md`

Photo instantanée du projet à cet instant. Volatile — mis à jour très fréquemment.

Contient : statut global (actif / pause / bloqué / terminé), focus actuel,
ce qui est validé, ce qui bloque, deadlines en cours, date de dernière mise à jour.

**Format à sections nommées avec ancres claires pour édition chirurgicale.**
L'agent met à jour uniquement la section concernée (`edit`), pas le fichier entier.

Indexé dans QMD.
Avec 30+ projets, "quels projets sont bloqués ?" se résout via un search BM25
sur "bloqué" dans les `state.md` — sans ouvrir chaque projet manuellement.

---

### `projects/[nom]/tasks.md`

Identique à `tasks.md` global — vue live uniquement.
Même format H1 par tâche. Tâches complétées → événement dans `changelog.md` du projet.
Indexé dans QMD.

---

### `projects/[nom]/changelog.md`

Historique et décisions du projet, unifiés en un seul fichier.
Même format que `changelog.md` global — H1 par jour, H2 par entrée, newest first.
Tag `[décision]` pour les décisions avec leur raisonnement.
Grossit indéfiniment. Jamais archivé. Indexé dans QMD.

```markdown
# 2025-07-14

## [décision] Abandon de l'API externe — build in-house
Le prestataire ne peut pas livrer avant juin. Notre deadline est mars.
Impact : tâches d'intégration supprimées, nouvelles tâches backend créées.

## Specs reçues du client v2.1
Changements mineurs sur le module paiement. Pas d'impact planning.

## Réunion avec Marie — maquettes validées sans modification
Prêtes pour l'intégration.
```

**Question ouverte — relation avec le changelog global :**
Quand l'agent de update touche un changelog projet, doit-il générer
automatiquement une entrée correspondante dans le `changelog.md` global ?
Deux approches possibles :
le global ne capture que ce qui lui est explicitement adressé (événements cross-projet,
décisions meta, pivots de vie) — les mises à jour projet restent dans leur changelog local.
Ou le global reçoit automatiquement un résumé de chaque opération de update
quelle que soit son origine.
À trancher lors de l'implémentation.

---

## YAML frontmatter

Tous les fichiers du vault ont du frontmatter YAML.
Minimum : `created`, `updated`, `tokens`.

```yaml
---
created: 2025-07-14T16:42:00
updated: 2025-07-14T18:30:00
tokens: 847
---
```

Les champs `updated` et `tokens` sont gérés exclusivement par le background job —
un processus programmatique, pas un LLM. Il se déclenche après chaque écriture,
calcule les tokens du fichier, et met à jour les deux champs.
L'agent ne pense jamais à maintenir ces métadonnées.

Le frontmatter rend le vault programmable : filtrer par date, trier par ancienneté,
trouver les fichiers les plus lourds, chercher par statut.
C'est un investissement de fondation — chaque fichier qui arrive dans le vault
est immédiatement équipé de ces métadonnées.

---

## Ce qui est indexé dans QMD

| Fichier | Indexé | Raison |
|---|---|---|
| `overview.md` | ❌ | Toujours en contexte direct, redondant de l'indexer |
| `tree.md` | ❌ | Auto-généré, toujours en contexte direct |
| `profile.md` | ❌ | Toujours en contexte direct |
| `inbox/*` | ❌ | Contenu temporaire — disparaît après résolution |
| `changelog.md` (global) | ✅ | Décisions et événements cherchables |
| `tasks.md` (global) | ✅ | Tâches cherchables par statut, sujet |
| `projects/*/description.md` | ✅ | Chercher un projet par ce qu'il fait |
| `projects/*/state.md` | ✅ | Chercher les projets par statut ou focus |
| `projects/*/tasks.md` | ✅ | Chercher une tâche dans tous les projets |
| `projects/*/changelog.md` | ✅ | Décisions et historique cherchables |
| `bucket/*` (global) | ✅ | Découverte de contenu non encore rattaché |
| `projects/*/bucket/*` | ✅ | Contenu projet cherchable |