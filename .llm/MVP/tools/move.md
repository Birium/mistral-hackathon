### `move(from, to)`

**Rôle**
Déplace un fichier d'un emplacement à un autre dans le vault.
C'est une opération filesystem pure — le contenu du fichier n'est pas lu
ni réécrit. Seule la position dans l'arborescence change.

**Signature**
```
move(from: string, to: string)
```

**Paramètres**

`from` *(string, obligatoire)*
Chemin source complet du fichier à déplacer.
Exemple : `"vault/bucket/email-specs.md"`

`to` *(string, obligatoire)*
Chemin destination complet.
Exemple : `"vault/projects/startup-x/bucket/email-specs.md"`
Si des dossiers parents n'existent pas dans `to` → les crée automatiquement.

**Comportement**

Le fichier est déplacé sans modification de son contenu.
Après le déplacement, le background job se déclenche et :
1. Met à jour le champ `updated` dans le frontmatter du fichier
2. Régénère `tree.md`
3. Désindexe le fichier de son ancien emplacement dans QMD
4. Ré-indexe le fichier à son nouvel emplacement dans QMD

Ce qui change dans le vault : uniquement la position du fichier dans l'arborescence.
Ce qui ne change pas : le contenu du fichier (frontmatter inclus, sauf `updated`).

**Move de dossier**
`move` fonctionne également sur les dossiers entiers.
Tout le contenu du dossier est déplacé récursivement.
Le background job traite chaque fichier individuellement pour la ré-indexation.

**Cas d'usage**

- Déplacer un fichier du bucket global vers le bucket d'un projet
  une fois son appartenance clarifiée :
  `move("vault/bucket/email-specs.md", "vault/projects/startup-x/bucket/email-specs.md")`

- Corriger un routing initial incorrect où un fichier a été mis dans le mauvais projet

- Déplacer les fichiers d'input d'un folder inbox vers leur destination finale
  après confirmation de l'utilisateur (avant de supprimer le folder inbox)

**Edge cases**

- `from` inexistant → erreur explicite
- `to` existe déjà → écrase le fichier existant à la destination
- `from` et `to` identiques → no-op, pas d'erreur
- Move vers hors du vault → error (le path doit rester sous `vault/`)