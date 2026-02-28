# Tools

Les tools sont l'interface entre les agents et le vault.
Chaque tool fait une seule chose. Ce dossier contient un fichier par tool.

---

## Philosophie générale

**Ce que les tools font :**
- Lire des fichiers et explorer la structure du vault
- Écrire, modifier, déplacer, supprimer des fichiers

**Ce que les tools ne font pas :**
- Maintenir `tokens` et `updated` dans le frontmatter → c'est le background job
- Déclencher la ré-indexation QMD → c'est le file watcher
- Prendre des décisions sémantiques → c'est l'agent

À l'entrée des tools, tout est soit du texte, soit une image.
La conversion de formats (PDF, audio, etc.) est faite en amont par le processing pipeline.

---

## Ce qui se passe après chaque écriture

Après chaque tool d'écriture (`write`, `edit`, `append`, `move`, `delete`),
le file watcher déclenche automatiquement le background job.

Le background job — processus programmatique, jamais un LLM — fait dans l'ordre :
1. Calcule les tokens du fichier modifié (`Math.ceil(content.length / 4)`)
2. Met à jour `tokens` et `updated` dans son frontmatter
3. Régénère `tree.md`
4. Ré-indexe le fichier dans QMD (ou le désindexe si `delete`, ou le réindexe au nouvel emplacement si `move`)

**Prévention des boucles infinies :**
Le background job écrit lui-même dans le vault. Pour éviter qu'il se redéclenche,
le système maintient un `Set` des paths en cours d'écriture par le background job —
le file watcher ignore les events sur ces paths.

---

## Disponibilité par agent

| Tool | Agent de update | Agent de search |
|------|:-:|:-:|
| `tree` | ✅ | ✅ |
| `read` | ✅ | ✅ |
| `search` | ✅ | ✅ |
| `concat` | ❌ | ✅ |
| `write` | ✅ | ❌ |
| `edit` | ✅ | ❌ |
| `append` | ✅ | ❌ |
| `move` | ✅ | ❌ |
| `delete` | ✅ | ❌ |

`concat` est exclusif à l'agent de search — c'est lui qui construit
la réponse structurée à retourner à l'utilisateur.

---

## Index

**Lecture et navigation**
- [`tree`](tree.md) — explorer la structure du vault avec tokens et timestamps
- [`read`](read.md) — lire un fichier avec numérotation des lignes
- [`search`](search.md) — chercher dans le vault indexé par QMD
- [`concat`](concat.md) — assembler des fichiers en un document structuré (search uniquement)

**Écriture**
- [`write`](write.md) — créer ou réécrire un fichier entier
- [`edit`](edit.md) — modifier une section précise via search-replace
- [`append`](append.md) — insérer un bloc en début ou fin de fichier sans lecture préalable
- [`move`](move.md) — déplacer un fichier dans le vault
- [`delete`](delete.md) — supprimer un fichier ou un dossier