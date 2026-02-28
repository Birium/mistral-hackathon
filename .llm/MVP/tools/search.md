### `search(queries, mode, scopes)`

**Rôle**
Cherche du contenu dans le vault indexé par QMD.
Retourne les chunks les plus pertinents avec leur contexte immédiat,
classés par score de pertinence.

C'est l'outil de navigation sémantique principal des deux agents.
Il permet de trouver de l'information précise sans ouvrir les fichiers un par un —
et souvent sans avoir besoin d'un `read` supplémentaire,
grâce aux lignes de contexte incluses dans chaque résultat.

La mécanique interne de QMD, la stratégie de chunking, les modes fast et deep,
et le détail de ce qui est indexé → `search.md`

**Signature**
```
search(
  queries: string[],
  mode: "fast" | "deep",
  scopes: string[] | null
)
```

**Paramètres**

`queries` *(array de strings, obligatoire)*
Une ou plusieurs requêtes de recherche.
Passer plusieurs queries dans un seul appel permet de chercher plusieurs concepts
ou mots-clés simultanément. Les résultats sont fusionnés, dédupliqués
(un même chunk ne ressort jamais deux fois même s'il matche plusieurs queries),
et triés par score de pertinence global.

Formats selon le mode :
- Mode `fast` : termes exacts, identifiants, tags, statuts
- Mode `deep` : formulations naturelles, questions, concepts

Exemples :
```
// Un seul terme précis
queries: ["[décision]"]

// Plusieurs mots-clés à chercher en parallèle
queries: ["comptabilité", "TVA", "bilan"]

// Mix de termes avec valeur discriminante
queries: ["bloqué", "en attente prestataire"]

// Formulation naturelle pour le mode deep
queries: ["décision architecture de paiement", "abandon API externe"]
```

`mode` *(string, obligatoire)*
Détermine le moteur de recherche utilisé pour toutes les queries de l'appel.

**`"fast"` — BM25**
Millisecondes. Aucun modèle chargé. Recherche par correspondance de termes.
QMD tokenise, pondère les termes par rareté (IDF) et fréquence locale (TF),
retourne les résultats classés par score BM25.
Un terme rare présent dans 2 chunks sur 200 reçoit un poids énorme.
Un terme omniprésent comme "projet" est quasi ignoré.

À utiliser pour :
- Noms propres : `"Marie"`, `"startup-x"`, `"Dupont"`
- Tags : `"[décision]"`, `"[blocage]"`
- Statuts : `"status: bloqué"`, `"status: en-cours"`, `"prio: haute"`
- Dates exactes : `"2025-07-14"`
- Identifiants : `"API Stripe"`, `"TVA Q3"`

**`"deep"` — Pipeline complet**
Quelques secondes. Expansion de requête → BM25 → recherche vectorielle →
fusion RRF (Reciprocal Rank Fusion) → re-ranking sémantique.
Trouve des résultats pertinents même sans correspondance exacte de termes.

À utiliser pour :
- Questions sémantiques : `"pourquoi a-t-on abandonné l'API externe ?"`
- Formulations vagues : `"ce truc sur l'architecture de paiement"`
- Recherches conceptuelles : `"decision sur le stack technique"`
- Cross-projet : `"relation avec le client stratégique"`
- Tout cas où les termes exacts dans les fichiers sont inconnus

`deep` est souvent le choix par défaut quand la précision sémantique compte.
`fast` est le choix quand on cherche quelque chose de précis et nommé.

`scopes` *(array de strings | null, optionnel, défaut: null)*
Restreint la recherche à des fichiers ou dossiers spécifiques.
Si `null`, la recherche couvre tout le vault indexé.

L'agent utilise des patterns glob standards avec `*` comme wildcard.
Plusieurs scopes dans un même appel permettent de cibler des zones disjointes
sans faire appel à deux `search` séparés.

Patterns typiques :
```
// Un projet spécifique — tous ses fichiers indexés
scopes: ["vault/projects/startup-x/*"]

// Un type de fichier à travers tous les projets
scopes: ["vault/projects/*/state.md"]

// Tous les changelogs — projets + global
scopes: ["vault/projects/*/changelog.md", "vault/changelog.md"]

// Toutes les tasks — projets + global
scopes: ["vault/projects/*/tasks.md", "vault/tasks.md"]

// Tous les buckets — projets + global
scopes: ["vault/projects/*/bucket/*", "vault/bucket/*"]

// Croisement précis — le bucket et le changelog d'un projet donné
scopes: ["vault/projects/startup-x/bucket/*", "vault/projects/startup-x/changelog.md"]

// Deux projets sans élargir au reste du vault
scopes: ["vault/projects/startup-x/*", "vault/projects/appart-search/*"]

// Tous les fichiers description pour trouver un projet existant
scopes: ["vault/projects/*/description.md"]
```

Un path dans `scopes` qui ne correspond à aucun fichier indexé est ignoré silencieusement —
la recherche s'effectue sur les scopes valides restants.

---

**Format de sortie**

Array d'objets triés par score décroissant.
Chaque objet représente un chunk de contenu distinct.
Les résultats issus de plusieurs queries sont fusionnés et dédupliqués —
un chunk ne ressort jamais deux fois même s'il matche plusieurs queries.

Pour chaque chunk, le système inclut automatiquement les lignes de contexte
immédiat (quelques lignes au-dessus et en-dessous du match) pour permettre
à l'agent de raisonner sur l'information sans avoir à appeler `read` sur le fichier.

```
[
  {
    "path": "vault/projects/startup-x/changelog.md",
    "score": 0.89,
    "lines": "9-14",
    "chunk_with_context": "7  | \n8  | ## [décision] Abandon de l'API externe\n9  | Le prestataire ne peut pas livrer avant juin. Notre deadline est mars.\n10 | Impact : tâches d'intégration supprimées, nouvelles tâches backend créées.\n11 | \n12 | ## Specs reçues du client v2.1\n13 | Changements mineurs sur le module paiement. Pas d'impact planning."
  },
  {
    "path": "vault/projects/startup-x/state.md",
    "score": 0.71,
    "lines": "20-24",
    "chunk_with_context": "18 | \n19 | ## Focus actuel\n20 | Intégration du module de paiement.\n21 | \n22 | ## Ce qui bloque\n23 | API externe : prestataire indisponible avant juin. Décision d'internaliser.\n24 | \n25 | ## Deadlines en cours"
  },
  {
    "path": "vault/changelog.md",
    "score": 0.58,
    "lines": "45-51",
    "chunk_with_context": "43 | \n44 | ## Décision de pivot technique sur startup-x\n45 | Abandon de l'approche API externe pour le module paiement.\n46 | L'équipe va builder in-house sur les 6 prochaines semaines.\n47 | \n48 | ## Point hebdo — projets actifs\n49 | Startup-x bloqué sur API. Appart-search en avance sur planning."
  }
]
```

Champs de chaque objet :
- `path` : chemin complet du fichier source dans le vault
- `score` : score de pertinence entre 0.0 et 1.0
- `lines` : range de lignes du chunk dans le fichier original (numérotation absolue)
- `chunk_with_context` : contenu du chunk avec les lignes de contexte.
  La numérotation des lignes (`N  | `) est celle du fichier complet —
  les numéros permettent à l'agent de passer des ranges précises au `concat` tool
  ou d'identifier exactement quelle section cibler pour un `edit`.

---

**Exemples d'appels complets**

```
// Toutes les décisions dans tout le vault
search(
  queries: ["[décision]"],
  mode: "fast",
  scopes: null
)

// Projets bloqués, partout
search(
  queries: ["bloqué", "en attente"],
  mode: "fast",
  scopes: ["vault/projects/*/state.md"]
)

// Vérifier si une information sur la comptabilité existe déjà avant d'écrire
search(
  queries: ["comptable", "TVA", "bilan"],
  mode: "fast",
  scopes: null
)

// Trouver un projet existant sur un sujet avant d'en créer un
search(
  queries: ["recherche appartement", "immobilier"],
  mode: "deep",
  scopes: ["vault/projects/*/description.md"]
)

// Reconstituer tout le contexte autour d'une décision passée
search(
  queries: ["abandon API externe", "prestataire paiement"],
  mode: "deep",
  scopes: ["vault/projects/startup-x/*"]
)

// Toutes les tâches haute priorité dans tout le système
search(
  queries: ["prio: haute"],
  mode: "fast",
  scopes: ["vault/projects/*/tasks.md", "vault/tasks.md"]
)

// Ce qui s'est passé récemment dans deux projets actifs
search(
  queries: ["meeting", "client", "décision"],
  mode: "deep",
  scopes: [
    "vault/projects/startup-x/changelog.md",
    "vault/projects/appart-search/changelog.md"
  ]
)

// Retrouver un fichier bucket par son contenu
search(
  queries: ["rue de Rivoli", "appartement T3"],
  mode: "deep",
  scopes: ["vault/projects/*/bucket/*", "vault/bucket/*"]
)
```

---

**Ce qui est indexé dans QMD — et donc cherchable**

Les fichiers non-indexés ne sont jamais retournés par `search`.
Chercher dans `overview.md`, `tree.md`, ou `profile.md` ne retournera rien —
ces fichiers sont toujours en contexte direct, les indexer serait redondant.

| Fichier | Cherchable |
|---|:-:|
| `vault/overview.md` | ❌ |
| `vault/tree.md` | ❌ |
| `vault/profile.md` | ❌ |
| `vault/inbox/*` | ❌ |
| `vault/changelog.md` (global) | ✅ |
| `vault/tasks.md` (global) | ✅ |
| `vault/projects/*/description.md` | ✅ |
| `vault/projects/*/state.md` | ✅ |
| `vault/projects/*/tasks.md` | ✅ |
| `vault/projects/*/changelog.md` | ✅ |
| `vault/bucket/*` (global) | ✅ |
| `vault/projects/*/bucket/*` | ✅ |

---

**Edge cases**

- `queries` vide `[]` → erreur explicite
- Aucun résultat → retourne un array vide `[]`
- Scope qui ne correspond à aucun fichier indexé → ignoré silencieusement.
  Les autres scopes valides de l'appel sont traités normalement.
  Si tous les scopes sont invalides → retourne `[]`
- Pattern glob mal formé dans `scopes` → erreur explicite sur le pattern concerné
- Mêmes chunks matchés par plusieurs queries → dédupliqués, un seul objet retourné,
  avec le score le plus élevé parmi toutes les queries qui l'ont matché
- Vault vide ou aucun fichier indexé → retourne `[]`

---

## Features supplémentaires (Hors scope MVP)

**Filtrage temporel (`date_from`, `date_to`)**

Deux paramètres optionnels qui restreignent les résultats à une fenêtre de temps,
appliqués comme pré-filtre avant la recherche textuelle.

Signature étendue :
```
search(
  queries: string[],
  mode: "fast" | "deep",
  scopes: string[] | null,
  date_from: string | null,
  date_to: string | null
)
```

Formats acceptés pour `date_from` et `date_to` :
- Date ISO : `"2025-07-14"`, `"2025-06-01"`
- Expression relative : `"7 days ago"`, `"30 days ago"`, `"3 months ago"`

Comportement selon le type de fichier :

Sur les **changelogs** (qui utilisent des headers H1 de date) :
QMD filtre sur le header `# YYYY-MM-DD` associé au chunk.
Un chunk appartenant à un jour hors de la fenêtre est exclu — même si
le reste du contenu du fichier est dans la fenêtre.
Exemple : `search(["[décision]"], mode: "fast", date_from: "2025-06-01", date_to: "2025-06-30")`
ne retourne que les décisions dont le H1 parent est entre le 1er et le 30 juin.

Sur les **autres fichiers indexés** (tasks, state, description, bucket items) :
QMD filtre sur le champ `updated` du frontmatter YAML.
Si `updated` est hors de la fenêtre, le fichier entier est exclu.

Les deux paramètres sont indépendants et peuvent être utilisés séparément ou ensemble.

Exemples d'appels avec dates :
```
// Décisions startup-x pendant le Q2 2025
search(
  queries: ["[décision]"],
  mode: "fast",
  scopes: ["vault/projects/startup-x/changelog.md"],
  date_from: "2025-04-01",
  date_to: "2025-06-30"
)

// Tout ce qui s'est passé cette semaine dans le vault
search(
  queries: ["*"],
  mode: "fast",
  scopes: null,
  date_from: "7 days ago",
  date_to: null
)

// Fichiers bucket ajoutés récemment et non encore routés
search(
  queries: ["type: vocal", "type: email"],
  mode: "fast",
  scopes: ["vault/bucket/*"],
  date_from: "30 days ago",
  date_to: null
)
```

Edge cases spécifiques aux dates :
- `date_from` > `date_to` → erreur explicite
- Format non reconnu → erreur explicite
- Fichier sans frontmatter ou sans champ `updated` → traité comme non daté,
  exclu quand un filtre de date est actif

---

**Adressage par header markdown dans le scope**

En complément des wildcards de fichiers, permettre de cibler un header
spécifique à l'intérieur d'un fichier dans le scope.

Exemple de syntaxe envisagée :
```
scopes: ["vault/projects/startup-x/changelog.md#2025-07"]
```
Ce scope ne retournerait que les chunks appartenant aux headers de juillet 2025
dans ce changelog.

Particulièrement utile sur les gros changelogs pour éviter de recevoir
des chunks de tout l'historique quand on cherche quelque chose de récent.
Plus précis que `date_from`/`date_to` pour les cas où on connaît
la période exacte. À concevoir conjointement avec la stratégie de chunking
de QMD qui associe chaque chunk à son header parent.

---

**Mode `explain` sur les résultats**

Un paramètre optionnel `explain: true` qui enrichit chaque objet retourné
avec un champ `relevance_reason` — une courte phrase générée par le modèle
qui explique en quoi ce chunk répond à la query.

```
{
  "path": "vault/projects/startup-x/state.md",
  "score": 0.71,
  "lines": "22-24",
  "chunk_with_context": "...",
  "relevance_reason": "Mentionne directement le blocage sur l'API externe,
    la raison principale de la query."
}
```

Utile pour l'agent de search quand il doit construire une overview de qualité
sur une question complexe avec beaucoup de résultats: plutôt que de relire
chaque chunk pour comprendre pourquoi il a été retourné, il a déjà
le raisonnement de pertinence.

---

**Score minimum (`min_score`)**

Un paramètre optionnel `min_score: float` qui filtre les résultats
inférieurs à ce seuil.

```
search(
  queries: ["décision architecture"],
  mode: "deep",
  scopes: null,
  min_score: 0.4
)
```

Utile pour les recherches `deep` sur des sujets vastes qui peuvent retourner
des dizaines de chunks avec des scores très faibles et peu utiles.
L'agent peut calibrer ce seuil selon la précision attendue.
Sans ce paramètre, tous les résultats sont retournés quel que soit leur score.