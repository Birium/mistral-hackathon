### `read(paths, head, tail)`

**Rôle**
Lit un ou plusieurs fichiers, ou le contenu direct d'un ou plusieurs folders.
Retourne le contenu avec frontmatter, chaque ligne préfixée par son numéro de ligne.

La numérotation des lignes est obligatoire — c'est ce qui permet
à l'agent de référencer des sections précises lors de l'appel à `concat`
ou pour un `edit` chirurgical.

**Signature**
```
read(
  paths: string | string[],
  head: int | null,
  tail: int | null
)
```

**Paramètres**

`paths` *(string ou array de strings, obligatoire)*
Un chemin unique ou une liste de chemins à lire.
Chaque chemin peut pointer vers un fichier ou un folder.

- Fichier unique : `"vault/projects/startup-x/state.md"`
- Folder unique : `"vault/projects/startup-x/"` — lit tous les fichiers directement dans ce folder
- Liste de fichiers : `["vault/projects/startup-x/state.md", "vault/projects/startup-x/tasks.md"]`
- Liste de folders : `["vault/projects/startup-x/", "vault/projects/appart-search/"]`
- Mix : `["vault/projects/startup-x/state.md", "vault/bucket/"]`

**Lecture d'un folder — comportement non-récursif.**
Quand `paths` contient un folder, le tool lit tous les fichiers
directement dans ce folder. Les sous-dossiers sont ignorés.
Pour lire le contenu d'un bucket projet, l'agent passe
`"vault/projects/startup-x/bucket/"` — pas `"vault/projects/startup-x/"`.

`head` *(int | null, optionnel, défaut: null)*
Nombre approximatif de tokens à retourner depuis le début de chaque fichier.
Le calcul utilise l'approximation `text.length / 4`.
Le tool retourne les lignes complètes qui tiennent dans ce budget —
il ne coupe jamais une ligne en milieu.
S'applique individuellement à chaque fichier lu.
`null` = pas de limite.

`tail` *(int | null, optionnel, défaut: null)*
Nombre approximatif de tokens à retourner depuis la fin de chaque fichier.
Même logique que `head`. S'applique individuellement à chaque fichier lu.
`null` = pas de limite.

**Contrainte : `head` et `tail` sont mutuellement exclusifs.**
Passer les deux en même temps → erreur explicite.
Pour un read complet : ne passer ni l'un ni l'autre.

---

**Format de sortie**

Pour un fichier unique, le contenu est retourné directement avec numéros de lignes :
````
```vault/projects/startup-x/state.md
1  | ---
2  | created: 2025-07-14T16:42:00
3  | updated: 2025-07-14T18:30:00
4  | tokens: 380
5  | ---
6  |
7  | ## Statut global
8  | actif
9  |
10 | ## Focus actuel
11 | Intégration du module de paiement
```
```

Pour plusieurs fichiers, chaque fichier est précédé d'un header de path.
Les fichiers sont séparés par une ligne vide :
````
```vault/projects/startup-x/state.md
1  | ---
2  | created: 2025-07-14T16:42:00
3  | updated: 2025-07-14T18:30:00
4  | tokens: 380
5  | ---
6  |
7  | ## Statut global
8  | actif
```

```vault/projects/startup-x/tasks.md
1  | ---
2  | created: 2025-07-14T10:00:00
3  | updated: 2025-07-14T18:00:00
4  | tokens: 290
5  | ---
6  |
7  | # Valider les maquettes avec Marie
8  | status: à-faire | prio: haute | ajoutée: 2025-07-14 | projet: startup-x
```
````

Les numéros de lignes représentent toujours la position dans le fichier complet,
même pour un read partiel. Un `read` avec `head=500` qui retourne les lignes 1 à 38
affichera `1  | ` à `38 | ` — jamais recalculé depuis zéro.

---

**Comportement sur les images**

Quand un chemin pointe vers un fichier image (extensions reconnues :
`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`), le tool adopte un comportement distinct.

Au lieu de retourner du texte numéroté, il charge l'image directement
dans le contexte multimodal de la session. Le modèle voit l'image
via ses capacités de vision natives — pas d'OCR, pas de conversion en description texte.

Les paramètres `head` et `tail` sont ignorés pour les fichiers image.

Quand `paths` contient un mix de fichiers texte et d'images, le tool
retourne le texte numéroté pour les fichiers markdown et charge les images
en multimodal — dans le même appel.

Quand `paths` pointe vers un folder contenant des images,
les images du folder sont chargées en multimodal
et les fichiers markdown sont retournés avec numérotation de lignes.

---

**Comportement détaillé pour les reads partiels**

`read("vault/projects/startup-x/changelog.md", head=2000)` :
Retourne les lignes DEPUIS LE DÉBUT du fichier (~2000 tokens).
Dans un changelog newest-first, ce sont les entrées les plus récentes.

`read("vault/projects/startup-x/changelog.md", tail=2000)` :
Retourne les lignes DEPUIS LA FIN du fichier (~2000 tokens).
Dans un changelog, ce sont les entrées les plus anciennes.

Avec plusieurs fichiers, `head` et `tail` s'appliquent à chaque fichier individuellement.
`read(["vault/projects/startup-x/changelog.md", "vault/changelog.md"], head=1000)`
retourne les ~1000 premiers tokens de chacun des deux changelogs.

---

**Cas d'usage typiques**

Agent de update :
- Lire `state.md` avant de le modifier via `edit`
- Lire tous les fichiers d'un projet d'un coup avant de décider quoi mettre à jour :
  `read("vault/projects/startup-x/")` — retourne description, state, tasks, changelog
  (le bucket est un sous-dossier, il n'est pas inclus)
- Lire plusieurs `state.md` pour comparer l'état de plusieurs projets :
  `read(["vault/projects/startup-x/state.md", "vault/projects/appart-search/state.md"])`
- Lire le `review.md` d'un folder inbox avant de router

Agent de search :
- Lire les fichiers identifiés comme pertinents par `search()`
- Lire le contenu complet d'un bucket pour explorer les items disponibles :
  `read("vault/projects/startup-x/bucket/")`
- Lire `head=3000` d'un changelog de 8k tokens pour obtenir les entrées récentes

**Précondition pour `edit`**
L'agent DOIT avoir lu un fichier via `read` avant de pouvoir appeler `edit` dessus.
L'`edit` requiert le texte exact original — sans lecture préalable,
l'agent ne peut pas connaître ce texte exact.

---

**Edge cases**

- Path inexistant → erreur explicite sur le path manquant,
  les autres paths valides de la liste sont quand même traités
- Folder vide → header de path affiché, aucun contenu retourné
- `head=0` ou `tail=0` → erreur (valeur non valide)
- `head` ou `tail` supérieur à la taille d'un fichier → retourne le fichier complet
- Fichier vide (seulement frontmatter) → retourne uniquement le frontmatter
- `head` et `tail` tous deux non-null → erreur explicite
- Fichier image avec `head` ou `tail` → paramètres ignorés silencieusement
- Folder contenant des sous-dossiers → les sous-dossiers sont ignorés,
  seuls les fichiers directs sont lus
- `paths` tableau vide `[]` → erreur explicite


**Features supplémentaires**

**Fold/collapse markdown** — un paramètre `folded: true` qui retournerait
uniquement les headers du fichier (H1, H2) avec `...` pour représenter
le contenu collapsé en dessous. L'agent obtient une vue structurelle
du fichier en quelques lignes, puis fait des reads ciblés sur les sections
qui l'intéressent. Utile sur les gros changelogs ou les fichiers denses
où l'agent veut naviguer avant de lire.
Inspiré du fold de VS Code. Hors scope MVP.