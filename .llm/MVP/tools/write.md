### `write(path, content)`

**Rôle**
Crée un nouveau fichier ou réécrit un fichier existant dans sa totalité.
C'est l'outil de réécriture complète — il remplace intégralement le contenu existant.

**Signature**
```
write(path: string, content: string)
```

**Paramètres**

`path` *(string, obligatoire)*
Chemin complet du fichier à créer ou réécrire.
Exemples :
- `"vault/projects/startup-x/description.md"`
- `"vault/bucket/email-specs-juillet.md"`
- `"vault/inbox/2025-07-14-vocal-meeting-client/review.md"`

`content` *(string, obligatoire)*
Contenu markdown complet du fichier, frontmatter NOT inclus.
le background job les gère après l'écriture.

**Comportement**

- Si le fichier n'existe pas → crée le fichier
- Si le fichier existe → écrase complètement son contenu
- Si des dossiers parents n'existent pas dans le path → les crée automatiquement
- Après l'écriture : le file watcher déclenche le background job

**Quand utiliser `write` vs `edit` vs `append`**

`write` quand :
- Le fichier n'existe pas encore (création)
- La réécriture complète est plus cohérente que des éditions chirurgicales
  (ex: `description.md` après un pivot)
- La structure du fichier change significativement
- L'agent génère un nouveau projet entier (description, state, tasks, changelog initiaux)

Ne pas utiliser `write` quand :
- Seule une section précise change → utiliser `edit`
- On ajoute une entrée à un changelog → utiliser `append`

**Cas d'usage**

- Créer un nouvel item dans un bucket (global ou projet)
- Réécrire `description.md` après un pivot de projet
- Réécrire `overview.md` lors de changements structurels (nouveau projet, archive)
- Créer un folder inbox : écrire `review.md` + éventuels fichiers d'input
- Initialiser un nouveau projet : écrire description.md, state.md, tasks.md, changelog.md
- Réécrire `profile.md` lors d'une évolution significative du profil utilisateur

**Edge cases**

- `path` hors du dossier `vault/` → comportement non défini, à éviter
- `content` vide `""` → erreur (un fichier vide sans frontmatter n'est pas valide)