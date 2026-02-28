### `search(query, mode, scope, date_from, date_to)`

**Rôle**
Cherche dans le vault indexé par QMD.
Retourne des chunks de texte pertinents classés par score de pertinence.
C'est le tool central de navigation sémantique — les deux agents l'utilisent.

**Signature**
```
search(
  query: string,
  mode: "fast" | "deep",
  scope: string | null,
  date_from: string | null,
  date_to: string | null
)
```

**Paramètres**

`query` *(string, obligatoire)*
Le texte de la recherche.
- Termes exacts pour le mode `fast` : `"[décision]"`, `"bloqué"`, `"Marie"`
- Formulation naturelle pour le mode `deep` : `"ce qu'on avait décidé sur l'API de paiement"`
- Wildcard `"*"` pour tout retourner dans un scope/période donné (utile avec date_from/date_to)

`mode` *(string, obligatoire)*
Détermine le pipeline de recherche utilisé.

**`"fast"` — BM25 pur**
Millisecondes. Aucun modèle chargé.
QMD tokenise le corpus, calcule la rareté de chaque terme (IDF),
pondère par la fréquence dans le document (TF), retourne les résultats
classés par score de pertinence TF-IDF standard.
Un terme rare qui apparaît dans 2 chunks sur 200 reçoit un poids énorme.
Un terme omniprésent comme "projet" est quasi ignoré.

À utiliser pour :
- Noms propres et identifiants ("Marie", "startup-x", "TVA Q3")
- Tags exacts ("[décision]", "[blocage]")
- Mots-clés précis avec valeur discriminante ("bloqué", "en-cours", "deadline")
- Dates exactes ("2025-07-14")
- Statuts ("status: bloqué", "status: en-cours")

**`"deep"` — Pipeline complet**
Quelques secondes. Expansion de requête → BM25 → recherche vectorielle →
fusion RRF (Reciprocal Rank Fusion) → re-ranking sémantique.
Trouve des résultats pertinents même sans correspondance exacte de termes.

À utiliser pour :
- Questions sémantiques ("pourquoi a-t-on abandonné l'API externe ?")
- Formulations vagues ("ce truc sur l'architecture de paiement")
- Recherches conceptuelles ("les risk identifiés sur le projet")
- Quand les termes exacts de l'information cherchée ne sont pas connus

`deep` est le choix par défaut quand la précision sémantique compte.
`fast` est le bon choix quand on cherche quelque chose de précis et nommé.

`scope` *(string | null, optionnel, défaut: null)*
Restreint la recherche à une zone du vault.

`null` — couvre tout le vault indexé (tous les fichiers listés dans la table d'indexation QMD)

`"project:[nom]"` — un projet spécifique uniquement.
Cherche dans : `projects/[nom]/description.md`, `state.md`, `tasks.md`,
`changelog.md`, et `bucket/*`.
Exemple : `"project:startup-x"`

`"all-states"` — tous les `projects/*/state.md` sans exception.
Cas d'usage : "Quels projets sont bloqués ?" → search `"bloqué"` sur `all-states`.

`"all-changelogs"` — tous les `projects/*/changelog.md` + le `changelog.md` global.
Cas d'usage : "Toutes les décisions prises sur l'architecture" → search `"[décision] architecture"` sur `all-changelogs`.

`"all-tasks"` — tous les `projects/*/tasks.md` + le `tasks.md` global.
Cas d'usage : "Toutes les tâches en cours avec haute priorité" → search `"prio: haute"` sur `all-tasks`.

`"all-buckets"` — tous les `projects/*/bucket/*` + le `bucket/` global.
Cas d'usage : "Trouver tous les vocaux qui mentionnent le client Dupont" → search `"Dupont"` sur `all-buckets`.

`"all-descriptions"` — tous les `projects/*/description.md`.
Cas d'usage : "Trouver un projet existant lié à la comptabilité" → search sémantique sur `all-descriptions`.

`date_from` *(string | null, optionnel, défaut: null)*
Filtre les résultats : retourne uniquement les chunks dont la date est >= date_from.

Formats acceptés :
- `"2025-07-14"` — date ISO
- `"2025-06-01"` — début de mois
- `"7 days ago"` — expression relative
- `"30 days ago"`, `"3 months ago"` — expressions relatives acceptées

Comportement selon le type de fichier :
- **Sur les changelogs** : filtre sur le H1 de date (`# 2025-07-14`).
  Un chunk appartenant à un H1 daté avant `date_from` est exclu.
- **Sur tous les autres fichiers indexés** : filtre sur le champ `updated` du frontmatter.
  Si `updated` est antérieur à `date_from`, le fichier entier est exclu de la recherche.

`date_to` *(string | null, optionnel, défaut: null)*
Filtre les résultats : retourne uniquement les chunks dont la date est <= date_to.
Mêmes formats et même comportement que `date_from`, mais dans l'autre sens.

`date_from` et `date_to` sont indépendants et peuvent être utilisés ensemble
pour définir une plage temporelle.

**Format de sortie**

Array de chunks classés par score décroissant :
```
[
  {
    "path": "projects/startup-x/changelog.md",
    "chunk": "## [décision] Abandon de l'API externe\nLe prestataire ne peut pas livrer avant juin...",
    "score": 0.89,
    "lines": "9-14"
  },
  {
    "path": "projects/startup-x/state.md",
    "chunk": "## Ce qui bloque\nAPI externe : prestataire indisponible avant juin.",
    "score": 0.71,
    "lines": "22-24"
  },
  {
    "path": "vault/changelog.md",
    "chunk": "## Décision de pivot technique sur startup-x\nAbandon de l'approche API externe...",
    "score": 0.58,
    "lines": "45-51"
  }
]
```

Chaque résultat contient :
- `path` : chemin du fichier source
- `chunk` : contenu textuel du chunk retourné par QMD
- `score` : score de pertinence (0.0 à 1.0)
- `lines` : range de lignes dans le fichier original

**Ce qui est indexé dans QMD (et donc cherchable)**
Les fichiers non-indexés (overview.md, tree.md, profile.md, inbox/*) ne sont
jamais retournés par `search`. Les chercher n'aurait aucun sens — ils sont
déjà en contexte direct ou sont temporaires.

| Fichier | Indexé |
|---|:-:|
| `overview.md` | ❌ |
| `tree.md` | ❌ |
| `profile.md` | ❌ |
| `inbox/*` | ❌ |
| `changelog.md` (global) | ✅ |
| `tasks.md` (global) | ✅ |
| `projects/*/description.md` | ✅ |
| `projects/*/state.md` | ✅ |
| `projects/*/tasks.md` | ✅ |
| `projects/*/changelog.md` | ✅ |
| `bucket/*` (global) | ✅ |
| `projects/*/bucket/*` | ✅ |

**Exemples d'appels**

```
// Toutes les décisions du vault
search("[décision]", mode: "fast", scope: null, date_from: null, date_to: null)

// Projets bloqués
search("bloqué", mode: "fast", scope: "all-states", date_from: null, date_to: null)

// Décisions de startup-x en juin 2025
search("[décision]", mode: "fast", scope: "project:startup-x",
  date_from: "2025-06-01", date_to: "2025-06-30")

// Tout ce qui s'est passé cette semaine
search("*", mode: "fast", scope: null, date_from: "7 days ago", date_to: null)

// Question sémantique sur l'architecture de paiement
search("décision architecture paiement", mode: "deep", scope: "all-changelogs",
  date_from: null, date_to: null)

// Trouver un projet existant avant de router une nouvelle info
search("comptabilité fiscalité", mode: "deep", scope: "all-descriptions",
  date_from: null, date_to: null)
```

**Edge cases**

- Aucun résultat : retourne un array vide `[]`
- Query vide `""` → erreur explicite
- Scope invalide (non reconnu dans la liste) → erreur explicite avec la liste des scopes valides
- `date_from` > `date_to` → erreur explicite
- Format de date non reconnu → erreur explicite
- Search sur un vault vide (rien d'indexé) → retourne `[]`