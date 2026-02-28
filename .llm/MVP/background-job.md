# Background Job

Le background job est un processus programmatique qui s'exécute après chaque
modification du vault. Ce n'est pas un agent, ce n'est pas un LLM, ce n'est
pas un système de décision. C'est de la plomberie déterministe : même input,
même output, toujours. Il ne lit pas le contenu des fichiers pour en comprendre
le sens, ne prend aucune décision, ne logue rien dans le changelog.

Son rôle est de maintenir trois choses en cohérence après chaque écriture :
le frontmatter des fichiers markdown, le fichier `tree.md`, et l'index QMD.

---

## Déclenchement

Le background job est déclenché par le file watcher — `watchdog`, la lib Python
qui observe le dossier `vault/` en continu. Watchdog émet un event à chaque
changement de fichier : création, modification, suppression, déplacement.

Le background job traite tous ces events de la même façon.
Il n'y a pas de logique différenciée selon le type d'event.
Dès qu'un fichier est touché, le background job s'exécute sur ce fichier.

Le déclenchement est **event-driven, pas périodique**. Il n'y a pas de cron,
pas de scan régulier du vault. Le background job se déclenche immédiatement
après chaque événement filesystem, avec une latence nulle.

---

## Prévention des boucles infinies

Le background job écrit lui-même dans le vault — il met à jour les frontmatters
des fichiers et régénère `tree.md`. Ces écritures déclenchent le file watcher,
qui pourrait re-déclencher le background job indéfiniment.

Pour éviter ça, le système maintient un `Set` de paths en cours d'écriture
par le background job. Avant chaque écriture, le background job ajoute le path
cible à ce `Set`. Le file watcher ignore tous les events dont le path est présent
dans ce `Set`. Après que l'écriture est terminée, le path est retiré du `Set`.

```python
_background_writes: set[str] = set()

def background_write(path: str, content: str):
    _background_writes.add(path)
    try:
        write_file(path, content)
    finally:
        _background_writes.discard(path)

def on_watchdog_event(event):
    if event.src_path in _background_writes:
        return  # ignoré — écriture interne du background job
    trigger_background_job(event.src_path)
```

---

## Fichiers ignorés

Le background job ignore complètement les fichiers image.
Les images sont détectées par leur extension : `.png`, `.jpg`, `.jpeg`,
`.gif`, `.webp`. Quand l'event watchdog concerne un fichier image,
le background job ne fait rien sur ce fichier.

Les images n'ont pas de frontmatter YAML. Le background job n'en crée pas.
Les images ne sont pas indexées dans QMD. Le background job n'y touche pas.

La seule opération qui reste valide quand une image est ajoutée, déplacée,
ou supprimée est la régénération de `tree.md` — puisque le tree reflète
toute l'arborescence du vault, images incluses.
Cette régénération se fait toujours, quel que soit le fichier qui a déclenché
l'event. Elle est décrite en détail dans la section dédiée.

---

## Les quatre opérations, dans l'ordre

Pour chaque fichier markdown concerné par un event, le background job
exécute ces quatre opérations séquentiellement.

### 1. Calcul des tokens

Le nombre de tokens du fichier est estimé avec la formule :

```python
tokens = math.ceil(len(content) / 4)
```

C'est une approximation. Elle est suffisamment précise pour les usages du vault
(affichage dans `tree.md`, budget de contexte pour les agents) sans dépendance
externe ni appel à un tokenizer.

### 2. Mise à jour du frontmatter

Le background job lit le frontmatter YAML existant du fichier.
Il met à jour ou crée les champs suivants :

```yaml
---
created: 2025-07-14T16:42:00   # ne s'écrit qu'une seule fois, à la création
updated: 2025-07-14T18:30:00   # timestamp courant, mis à jour à chaque écriture
tokens: 847                    # valeur calculée à l'étape 1
---
```

Le champ `created` est écrit uniquement si le fichier n'en a pas encore.
Il n'est jamais écrasé. Le champ `updated` est toujours mis à jour avec
le timestamp courant au moment de l'exécution du background job.
Le champ `tokens` est toujours mis à jour avec la valeur fraîchement calculée.

Le background job réécrit le fichier avec le frontmatter mis à jour
et le contenu inchangé. Cette écriture passe par le mécanisme de `Set`
décrit ci-dessus pour ne pas déclencher une nouvelle boucle.

Si le fichier n'existe plus au moment du traitement (cas d'une suppression),
cette étape est ignorée.

### 3. Régénération de `tree.md`

Après chaque modification de tout fichier dans le vault — markdown ou image —
le background job régénère `tree.md` en intégralité.

Le background job parcourt récursivement l'arborescence du vault.
Pour chaque fichier markdown, il lit le frontmatter pour récupérer la valeur
`tokens` et le champ `updated`. Pour les dossiers, il calcule le total de tokens
agrégés de tout le contenu qu'ils contiennent. Le format exact de la sortie
est défini dans `vault.md` et `tools/tree.md`.

`tree.md` n'est jamais indexé dans QMD. Il est toujours chargé directement
en contexte initial par les deux agents. Le background job écrit `tree.md`
via le mécanisme de `Set` pour qu'il ne se redéclenche pas lui-même.

### 4. Ré-indexation dans QMD

Le fichier modifié est ré-indexé dans QMD. Il n'y a pas d'indexation incrémentale,
pas d'optimisation : le fichier entier est re-chunké et re-indexé à chaque fois.

Avant d'indexer la nouvelle version, l'ancienne version du fichier est supprimée
de l'index QMD. Cette désindexation + ré-indexation garantit que l'index
reste cohérent même quand le contenu d'un fichier change radicalement.

Si le fichier a été supprimé (event de suppression), seule la désindexation
est effectuée — il n'y a rien à indexer.

Si le fichier a été déplacé, l'ancien path est désindexé et le nouveau path
est indexé avec le contenu du fichier à sa nouvelle position.

---

## Quels fichiers sont indexés dans QMD

Le background job n'indexe pas tous les fichiers du vault. La table suivante
définit ce qui est indexé et ce qui ne l'est pas.

Les fichiers non-indexés n'ont pas d'entrée dans QMD, quelle que soit
leur fréquence de modification.

```
Indexé dans QMD :
  vault/changelog.md
  vault/tasks.md
  vault/bucket/*.md
  vault/projects/[nom]/description.md
  vault/projects/[nom]/state.md
  vault/projects/[nom]/tasks.md
  vault/projects/[nom]/changelog.md
  vault/projects/[nom]/bucket/*.md

Non-indexé dans QMD :
  vault/overview.md       → toujours chargé directement en contexte
  vault/tree.md           → toujours chargé directement en contexte
  vault/profile.md        → toujours chargé directement en contexte
  vault/inbox/**          → contenu temporaire, supprimé après résolution
  *.png, *.jpg, *.jpeg,
  *.gif, *.webp           → les images ne sont jamais indexées
```

Le background job applique ces règles avant chaque opération d'indexation.
Si le path du fichier ne correspond pas à la liste des chemins indexables,
l'étape 4 est ignorée.

---

## Ce que le background job ne fait pas

Il ne lit pas le contenu des fichiers pour en comprendre le sens ou en extraire
des informations structurées. Il compte des caractères et lit des frontmatters.

Il ne prend pas de décisions de routing. Il ne sait pas si une information
appartient à un projet plutôt qu'un autre.

Il ne logue rien dans le changelog. Les opérations de maintenance
du vault sont loguées par l'agent de update, pas par la plomberie.

Il ne modifie jamais le contenu markdown des fichiers — uniquement
le frontmatter YAML. Le body du fichier est toujours préservé tel quel.

Il ne gère pas `overview.md`, `tree.md`, ou `profile.md` différemment
des autres fichiers sur le plan du frontmatter. Ces trois fichiers ont leur
frontmatter mis à jour exactement comme les autres fichiers markdown.
Ce qui les distingue, c'est uniquement l'absence d'indexation dans QMD.

---

## Features supplémentaires

**Tokenisation des images.** Les images ont un coût en tokens qui dépend
de leur résolution, de leur format, et des règles spécifiques des modèles
de vision (découpage en tiles). La formule `text.length / 4` ne s'applique
pas aux fichiers binaires. À terme, le background job pourrait implémenter
un tokeniser d'images qui calcule le coût réel de charger une image en contexte
multimodal, et stocker cette valeur dans un fichier sidecar YAML associé
à chaque image (ex: `screenshot.png.meta.yaml` avec les champs `created`,
`updated`, `tokens`). Cela permettrait à `tree.md` d'afficher un count token
réel pour les images, et aux agents de planifier leur budget de contexte
en incluant les images dans leurs calculs. Hors scope MVP.