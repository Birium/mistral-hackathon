### `append(path, content, position)`

**Rôle**
Insère un bloc markdown complet au début ou à la fin d'un fichier,
**sans lire le fichier préalablement**.
C'est l'outil d'insertion nulle-lecture — son avantage principal est économique :
sur un changelog de 300 jours (potentiellement 50k tokens), l'agent peut
ajouter une entrée sans charger l'historique existant en contexte.

**Signature**
```
append(path: string, content: string, position: "top" | "bottom")
```

**Paramètres**

`path` *(string, obligatoire)*
Chemin du fichier cible.
Si le fichier n'existe pas, il est créé avec `content` comme seul contenu.
(Ne pas oublier d'inclure le frontmatter dans ce cas.)

`content` *(string, obligatoire)*
Bloc markdown complet à insérer.
Pour un changelog : un bloc H1 avec ses H2 et leur contenu.
Pour un tasks.md : un bloc H1 de tâche avec ses métadonnées.

`position` *("top" | "bottom", obligatoire)*
- `"top"` : insère le contenu AVANT le contenu existant du fichier (prepend)
- `"bottom"` : insère le contenu APRÈS le contenu existant (append classique)

**Comportement**

- Le tool n'ouvre pas le fichier pour lire son contenu existant
- Il insère le contenu à la position spécifiée directement
- Si `position: "top"`, le contenu est placé en début de fichier,
  après le frontmatter YAML (le frontmatter reste en tête, le nouveau contenu
  vient juste après la fermeture `---` du frontmatter)
- Le background job se déclenche après l'opération

**Comportement spécial : deux H1 de même date dans un changelog**

Sur un changelog avec `position: "top"`, si la journée du jour existe déjà
(il y a déjà un `# 2025-07-14` dans le fichier), l'agent peut créer
un nouveau bloc `# 2025-07-14` — le fichier contiendra alors deux H1 identiques.

C'est un comportement explicitement accepté. Deux H1 identiques signifient
deux moments de mise à jour distincts pour la même journée.
QMD gère ce cas correctement — il chunke chaque bloc H1 séparément.
L'agent ne cherche pas à fusionner avec un H1 existant :
ça nécessiterait de lire le fichier, ce qui détruit l'avantage d'`append`.

**Cas d'usage**

Ajout d'une entrée dans un changelog projet (`position: "top"`) :
```markdown
# 2025-07-14

## [décision] Abandon de l'API externe
Le prestataire ne peut pas livrer avant juin. Notre deadline est mars.
Impact : tâches d'intégration supprimées, nouvelles tâches backend créées.

## Specs reçues du client v2.1
Changements mineurs sur le module paiement. Pas d'impact planning.
```

Ajout d'une tâche dans `tasks.md` (`position: "bottom"`) :
```markdown
# Appeler le comptable pour TVA Q3
status: à-faire | prio: haute | ajoutée: 2025-07-14 | projet: —

Contexte : justificatifs demandés avant fin juillet.
```

**Edge cases**

- Fichier inexistant → crée le fichier avec `content` comme contenu initial
- `content` vide `""` → erreur
- `position` invalide (autre que "top" ou "bottom") → erreur
- Fichier existant sans frontmatter → comportement non défini (tous les fichiers doivent avoir frontmatter)