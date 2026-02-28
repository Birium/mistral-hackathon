### `concat(files)`

**Rôle**
Assemble mécaniquement une liste de fichiers (ou ranges de lignes)
en un seul document markdown structuré.
C'est un outil de composition — pas de synthèse, pas de reformulation.
L'agent spécifie ce qu'il veut assembler, le tool le fait sans intelligence.

Exclusif à l'agent de search. Il ne modifie rien dans le vault.

Ce tool est la dernière étape du flux de search :
1. L'agent cherche avec `search()` pour identifier les chunks pertinents
2. L'agent lit certains fichiers avec `read()` pour vérifier leur contenu
3. L'agent appelle `concat()` pour assembler le document de réponse final

**Signature**
```
concat(files: Array<{ path: string, lines: string | null }>)
```

**Paramètres**

`files` *(Array, obligatoire)*
Liste ordonnée de fichiers à assembler.
L'ordre dans la liste est l'ordre d'apparition dans le document de sortie.

Chaque élément de la liste est un objet :
- `path` *(string, obligatoire)* : chemin du fichier dans le vault
- `lines` *(string | null, optionnel)* : range de lignes à extraire
  - `null` : inclure le fichier entier
  - `"1-45"` : inclure les lignes 1 à 45 du fichier
  - `"12-18"` : inclure uniquement les lignes 12 à 18
  - Les numéros de lignes correspondent à la numérotation retournée par `read()`

**Format de sortie**

Le tool retourne un document markdown composé de blocs de code,
un bloc par fichier. Chaque bloc utilise le path du fichier comme annotation
et contient le contenu avec numéros de lignes.

L'utilisation de blocs de code évite toute collision avec les headers markdown
du contenu des fichiers eux-mêmes (ex: si un changelog contient `# 2025-07-14`,
ce header ne pertube pas la structure du document de sortie).

```
```vault/projects/startup-x/state.md
1  | ---
2  | created: 2025-01-10T10:00:00
3  | updated: 2025-07-14T18:30:00
4  | tokens: 380
5  | ---
6  |
7  | ## Statut global
8  | actif
9  |
10 | ## Focus actuel
11 | Intégration du module de paiement
12 |
13 | ## Ce qui bloque
14 | API externe : prestataire indisponible avant juin. Décision d'internaliser.
```

```vault/projects/startup-x/changelog.md (lines 9-14)
9  | ## [décision] Abandon de l'API externe
10 | Le prestataire ne peut pas livrer avant juin. Notre deadline est mars.
11 | Impact : tâches d'intégration supprimées, nouvelles tâches backend créées.
12 |
13 | ## Specs reçues du client v2.1
14 | Changements mineurs sur le module paiement. Pas d'impact planning.
```

```vault/tasks.md
1  | ---
2  | created: 2025-01-10T10:00:00
3  | updated: 2025-07-14T08:00:00
4  | tokens: 290
5  | ---
6  |
7  | # Appeler le comptable pour TVA Q3
8  | status: en-cours | prio: haute | ajoutée: 2025-07-14 | projet: —
9  |
10 | # Valider les maquettes avec Marie
11 | status: à-faire | prio: haute | ajoutée: 2025-07-14 | projet: startup-x
12 | deadline: 2025-07-18
```
```

Quand une range est spécifiée, le header du bloc le mentionne :
`vault/projects/startup-x/changelog.md (lines 9-14)`

Quand le fichier entier est inclus, le header est simplement le path :
`vault/projects/startup-x/state.md`

**Comportement de la numérotation sur les ranges**
Les numéros de lignes dans le contenu sont toujours relatifs au fichier complet.
Une range `"9-14"` affiche les lignes 9, 10, 11, 12, 13, 14
avec leurs numéros originaux — pas renumérotés 1 à 6.
C'est ce qui permet à l'utilisateur de savoir exactement où dans le fichier
se trouve chaque information.

**Rapport avec l'overview de l'agent**
La sortie de `concat` est la deuxième partie de la réponse search.
La première partie est l'overview rédigée par l'agent (quelques lignes
produites par le LLM avant d'appeler `concat`).
Le document final envoyé à l'interface ou au client MCP est :

```
[Overview rédigée par l'agent — 2 à 5 lignes d'orientation]

---

[Sortie du concat tool — fichiers assemblés en blocs de code]
```

**Edge cases**

- `files` vide `[]` → retourne une chaîne vide (pas d'erreur)
- Path inexistant dans la liste → erreur explicite indiquant le path manquant,
  les autres fichiers de la liste sont quand même assemblés (comportement partial)
- Range invalide (`"abc-def"`) → erreur explicite sur le format attendu
- Range out of bounds (`"1-9999"` sur fichier de 100 lignes) → retourne jusqu'à la dernière ligne disponible
- `lines: ""` (chaîne vide) → traité comme `null` (fichier entier)