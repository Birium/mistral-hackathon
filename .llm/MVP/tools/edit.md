### `edit(path, old_content, new_content)`

**Rôle**
Modifie une section précise d'un fichier via un pattern search-replace exact.
C'est l'outil d'édition chirurgicale — il ne touche qu'à exactement
ce qui doit changer.

Le mécanisme search-replace est connu. L'implémentation de référence
est dans `example/editor/` (`editor.py` + `prompt_editor.py`) —
le tool Knower suit le même pattern.

**Signature**
```
edit(path: string, old_content: string, new_content: string)
```

**Paramètres**

`path` *(string, obligatoire)*
Chemin du fichier à modifier.

`old_content` *(string, obligatoire)*
Texte exact à localiser dans le fichier.

L'agent peut passer `old_content` de deux façons :

**Avec numéros de lignes** — en collant directement le contenu tel que retourné par `read()`,
numérotation incluse. Le tool détecte et strip les préfixes `N  | ` avant d'effectuer
la recherche dans le fichier réel.

```
old_content: "7  | ## Statut global\n8  | actif"
```

**Sans numéros de lignes** — texte brut. Correspondance exacte requise :
même indentation, même ponctuation, même sauts de ligne.

```
old_content: "## Statut global\nactif"
```

Les deux formats produisent le même résultat. L'agent utilise le format
avec numéros de lignes quand il copie directement depuis une sortie `read()` —
pas besoin de nettoyer manuellement avant de passer à `edit`.

`new_content` *(string, obligatoire)*
Texte de remplacement. Toujours sans numéros de lignes.
Peut être plus court, plus long, ou de même longueur que `old_content`.

**Comportement**

1. Le tool strip les préfixes `N  | ` de `old_content` si présents
2. Il localise la **première occurrence** du texte résultant dans le fichier
3. Il remplace cette occurrence par `new_content`
4. Il écrit le fichier modifié

**Pourquoi la première occurrence seulement**
Traiter toutes les occurrences serait dangereux — une section répétée
ne signifie pas que toutes les répétitions doivent changer.
L'agent formule un `old_content` suffisamment unique pour cibler
exactement ce qu'il veut modifier.
Si plusieurs occurrences existent et que l'agent doit modifier la deuxième,
il inclut plus de contexte dans `old_content` pour le rendre unique.

**Précondition obligatoire**
L'agent DOIT avoir lu le fichier via `read()` avant d'appeler `edit()`.
Sans lecture préalable, il ne peut pas connaître le texte exact à remplacer.

**Cas d'usage**

Mise à jour du statut dans `state.md` (avec numéros de lignes depuis `read`) :
```
old_content: "7  | ## Statut global\n8  | actif"
new_content: "## Statut global\nbloqué"
```

Déplacement d'une tâche de "à-faire" à "en-cours" dans `tasks.md` :
```
old_content: "7  | # Valider les maquettes avec Marie\n8  | status: à-faire | prio: haute"
new_content: "# Valider les maquettes avec Marie\nstatus: en-cours | prio: haute"
```

Mise à jour du statut d'un projet dans `overview.md` :
```
old_content: "- startup-x · actif"
new_content: "- startup-x · bloqué"
```

**Edge cases**

- `old_content` introuvable dans le fichier → erreur explicite
  (l'agent doit vérifier qu'il a bien lu le fichier et que le texte est exact)
- `old_content` avec numéros de lignes malformés → erreur explicite sur le format détecté
- `old_content` et `new_content` identiques → pas d'erreur, opération no-op
- `old_content` vide `""` → erreur
- `new_content` vide `""` → valide (supprime la section, comportement légal)
- Fichier inexistant → erreur explicite