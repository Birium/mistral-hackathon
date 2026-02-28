### `tree(path, depth)`

**Rôle**
Affiche la structure du vault à partir d'un path donné, avec tokens et timestamp.
C'est la loupe dynamique : l'agent l'appelle pendant son raisonnement
pour explorer un sous-dossier spécifique plus en détail.

**Distinction avec `tree.md`**
`tree.md` est un fichier généré automatiquement, chargé dans le contexte initial
des deux agents au démarrage de chaque session. Il est toujours là, sans appel outil.
`tree()` est un tool dynamique, appelé quand l'agent veut zoomer sur une zone précise.
Ils ne sont pas redondants — l'un est la carte générale, l'autre est la loupe.
Les deux utilisent la même logique de génération et le même format de sortie.

**Signature**
```
tree(path: string, depth: int | null)
```

**Paramètres**

`path` *(string, obligatoire)*
Point de départ de l'affichage.
- `"vault/"` — affiche tout depuis la racine
- `"vault/projects/startup-x/"` — affiche un projet spécifique
- `"vault/projects/startup-x/bucket/"` — affiche uniquement le bucket d'un projet
- `"vault/inbox/"` — affiche le contenu de l'inbox

`depth` *(int | null, obligatoire)*
Nombre de niveaux à déplier depuis le path donné.
- `1` — contenu immédiat uniquement (fichiers et dossiers directs, sans déplier)
- `2` — deux niveaux de profondeur
- `null` — déplier tout, sans limite de profondeur

---

**Format de sortie**

Chaque ligne affiche toujours le même format de metadata entre crochets : `[tokens · time_ago]`.
Fichiers et dossiers utilisent la même structure — seule l'échelle des tokens diffère.

```
vault/projects/startup-x/                        [18.3k · 2h ago]
├── description.md                                  [420 · 3d ago]
├── state.md                                        [380 · 2h ago]
├── tasks.md                                        [290 · 1d ago]
├── changelog.md                                   [8.2k · 2h ago]
└── bucket/                                        [9.0k · 5d ago]
    └── ... 3 files
```

**Tokens — format selon l'échelle :**
- En dessous de 1 000 : valeur exacte → `[420 · 3d ago]`
- En milliers : une décimale → `[9k · 3d ago]` ou `[9.3k · 3d ago]`
- En millions : une décimale → `[1.3M · 3d ago]`

Les dossiers affichent le total de tokens agrégés de tout leur contenu.
Le timestamp d'un dossier reflète la dernière modification parmi tous ses fichiers.

**Quand la profondeur maximale est atteinte**, les sous-dossiers non dépliés
affichent un résumé avec leur total de tokens :

```
└── bucket/                                        [9.0k · 5d ago]
    └── ... 3 files
```

```
└── projects/                                     [41.3k · 2h ago]
    ├── startup-x/                                [18.3k · 2h ago]
    │   └── ... 5 files, 1 folder
    └── appart-search/                            [11.2k · 4d ago]
        └── ... 5 files, 1 folder
```

---

**Cas d'usage typiques**

- L'agent voit dans `tree.md` que `startup-x/bucket/` fait 9k tokens.
  Il appelle `tree("vault/projects/startup-x/bucket/", depth=1)`
  pour voir les fichiers individuels et leurs poids avant d'en ouvrir un.

- L'agent reçoit une information liée à un projet.
  Il appelle `tree("vault/projects/", depth=1)` pour voir tous les projets
  et leurs tailles, sans déplier leur contenu.

- L'agent de search veut vérifier le contenu d'un folder inbox.
  Il appelle `tree("vault/inbox/", depth=2)` pour voir les folders
  et les fichiers qu'ils contiennent.

**Edge cases**

- Path inexistant → erreur explicite avec le path fourni
- Dossier vide → affiche `[0 · —]` avec aucun enfant
- `depth=0` → affiche uniquement le dossier racine avec son total, aucun enfant
- Fichier passé en `path` au lieu d'un dossier → retourne la ligne du fichier seul