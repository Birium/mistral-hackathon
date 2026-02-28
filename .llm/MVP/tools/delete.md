### `delete(path)`

**Rôle**
Supprime un fichier ou un dossier entier (et tout son contenu récursivement).

**Signature**
```
delete(path: string)
```

**Paramètres**

`path` *(string, obligatoire)*
Chemin du fichier ou dossier à supprimer.
- Fichier : `"vault/inbox/2025-07-14-vocal-meeting/review.md"`
- Dossier : `"vault/inbox/2025-07-14-vocal-meeting/"` (supprime tout le folder)

**Comportement**

Si `path` est un fichier → supprime uniquement ce fichier.
Si `path` est un dossier → supprime récursivement le dossier et tout son contenu.
Après la suppression, le file watcher déclenche :
1. Le background job : mise à jour de `tree.md`, désindexation QMD des fichiers supprimés
2. La mise à jour du badge inbox si un folder inbox a été supprimé :
   le file watcher recompte les folders dans `inbox/` et met à jour le badge

**Suppression d'un folder inbox — flux complet**
C'est le cas d'usage principal de `delete`.
Quand l'utilisateur répond à un item inbox et que l'agent a routé les fichiers,
la séquence est :
1. `move` les fichiers d'input vers leur destination
2. `write` ou `edit` les fichiers du vault concernés par le routing
3. `append` dans `changelog.md` global pour logger l'opération
4. `delete("vault/inbox/[folder-name]/")` — supprime le folder inbox entier
5. Le file watcher décrémente automatiquement le badge inbox

**Ce que `delete` ne fait pas**
Il n'archive pas. Il ne déplace pas vers une corbeille.
La suppression est permanente. L'historique de ce qui s'est passé
est dans le changelog, pas dans des fichiers supprimés.

**Cas d'usage**

- Suppression du folder inbox après résolution :
  `delete("vault/inbox/2025-07-14-vocal-meeting-client/")`

- Suppression d'un item bucket devenu obsolète ou dupliqué

**Edge cases**

- Path inexistant → erreur explicite
- Suppression d'un fichier critique (`overview.md`, `tree.md`, `profile.md`) →
  techniquement possible, mais l'agent ne doit jamais le faire —
  ces fichiers structurels sont recréés à l'initialisation et ne doivent pas être supprimés
- Dossier vide → supprimé sans erreur