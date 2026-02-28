# Images

Les images sont des fichiers comme les autres dans le vault.
Elles obéissent aux mêmes règles de stockage et de manipulation —
avec une seule différence fondamentale au moment du `read`.

---

## Stockage

Les images vivent dans les buckets.
Bucket global (`bucket/`) ou bucket d'un projet (`projects/[nom]/bucket/`).
Ce sont les seuls endroits où elles ont du sens dans l'architecture du vault.

Un fichier image dans le vault n'a **pas de frontmatter YAML**.
Contrairement aux fichiers markdown, les images ne portent pas de métadonnées
`created`, `updated`, `tokens`. Le background job les ignore.

---

## Manipulation

Les tools de manipulation du vault fonctionnent sans modification sur les images.

`move(from, to)` — déplacer une image d'un bucket à un autre, ou depuis
le bucket global vers le bucket d'un projet une fois son appartenance clarifiée.

`delete(path)` — supprimer une image devenue obsolète ou dupliquée.

`write`, `edit`, `append` — non pertinents sur une image. L'agent n'écrit pas
de contenu textuel dans un fichier image.

---

## Lecture — le seul comportement distinct

Quand `read(path)` est appelé sur un fichier image, le tool détecte
que c'est une image (par extension : `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`)
et la charge dans le contexte multimodal de la session plutôt que
de retourner du texte numéroté.

L'image est directement disponible pour le raisonnement visuel du modèle.
Pas d'OCR forcé, pas de conversion en description texte.
Le modèle voit l'image comme un outil de vision natif.

L'interface du tool est identique — un seul `read`, pas de `readImage` séparé.

---

## Non-indexation dans QMD

Les images ne sont jamais indexées dans QMD.
Une image n'a pas de contenu textuel à indexer.
Elle n'apparaît donc jamais dans les résultats d'un appel `search()`.

Pour retrouver une image dans le vault, l'agent utilise `tree()`
pour explorer le contenu d'un bucket et identifier
les fichiers par leur nom et leur extension.

---

## Features supplémentaires

**Métadonnées companion** — associer un fichier sidecar `.yaml` à chaque image
(`screenshot-review.yaml` pour `screenshot-review.png`) qui porte
les champs `created`, `updated`, `description`, `topics`.
Ce fichier sidecar serait indexé dans QMD, rendant les images cherchables
via leur description textuelle. Hors scope MVP.

**Tokenisation des images** — les images ont un coût en tokens qui dépend
de leur résolution et de leur format, selon les règles spécifiques des modèles de vision
(découpage en tiles). Le background job pourrait calculer ce coût pour que
le champ `tokens` d'un fichier image reflète son vrai coût en contexte.
Hors scope MVP — ni prioritaire ni bloquant.