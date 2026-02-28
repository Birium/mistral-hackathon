# Todo

Ce fichier est la source de vérité de tout ce qui reste à faire, à clarifier, et à documenter dans le projet. Il capture sans exception tout le contexte des sessions de brainstorming, de l'analyse critique des specs tools, et des feedbacks de révision. Rien ne doit être perdu ici.

---

## Contexte général — décisions structurantes à garder en tête

Avant toute chose, plusieurs décisions ont été prises lors de la dernière session de révision qui impactent de nombreux fichiers en même temps. Elles sont listées ici pour qu'elles ne soient jamais perdues de vue pendant les réécriture.

**Read + Edit avec lignes — décision finale.** Les deux tools utilisent les numéros de lignes. Le `read` retourne toujours le contenu avec les lignes numérotées. Le `edit` travaille également avec les lignes — il y aura une abstraction interne qui ajoute les numéros pour localiser la section à éditer, puis les retire pour appliquer le remplacement dans le fichier réel. Cela rend l'agent plus structuré et plus précis dans ses opérations d'édition.

**Scopes du search tool — simplification radicale.** Les scopes prédéfinis comme `"project:[nom]"` ou `"all-states"` dégagent complètement. Le format naturel est un path avec wildcard : `projects/startup-x/` pour un projet précis, `projects/*/state.md` pour tous les states. L'agent connaît parfaitement cette notation et n'a pas besoin d'abstractions supplémentaires. Les scopes cross-cutting de type `all-*` ne sont pas non plus des features supplémentaires à documenter — c'est juste une façon de formuler un path wildcard que l'agent sait déjà faire.

**Dates dans le search — feature supplémentaire, pas dans le tool de l'agent.** Les paramètres `date_from` et `date_to` sont documentés uniquement dans le gros fichier `search.md` (le fichier de compréhension du composant), pas dans le fichier tool `tools/search.md` qui décrit comment l'agent utilise le tool. Les dates restent une amélioration future, pas un paramètre exposé à l'agent dans le MVP.

**Features hors scope — section dans chaque fichier tool.** Tout ce qui est intéressant mais pas MVP ne disparaît pas. Chaque fichier tool aura une section dédiée en bas "Features supplémentaires" qui liste les améliorations identifiées. Comme ça, le potentiel d'évolution de chaque tool est toujours visible dans sa doc.

**Pas de fichier QMD séparé.** Tout ce qui concerne QMD vit dans un seul `search.md` (le fichier de compréhension, pas l'outil). Ce fichier explique tout : comment QMD fonctionne, la stratégie de chunking, les modes BM25 et pipeline complet, l'indexation incrémentale, ce qui est indexé ou non. Le tool `tools/search.md` reste léger — il dit juste comment l'agent utilise le search, pas comment QMD fonctionne en dessous.

**Images — comportement simple.** Les images vont dans le bucket comme n'importe quel fichier. Quand un agent fait un `read` sur une image, le tool la charge dans la conversation (contexte multimodal) — même fonction `read`, le tool détecte que c'est une image et la traite en conséquence. Pas d'OCR forcé, pas de conversion en texte. Le tokeniser d'images (calculer combien de tokens coûte une image selon son format/résolution) est une feature supplémentaire documentée dans le fichier du background job.

**Tree — aligné, pas de changement majeur.** Le paramètre `metadata` du tool `tree` disparaît. La sortie affiche toujours et uniquement : nom du fichier, tokens, date de dernière modification. `tree.md` (le fichier auto-généré) utilise la même fonction que le tool `tree()` — ce sont deux faces de la même logique, pas deux implémentations séparées.

---

## Fichier à créer — `search.md` (version complète)

Ce fichier remplace et étend largement le `search.md` actuel du dossier MVP. C'est le fichier de compréhension complète du composant search — il couvre tout ce qui se passe sous le capot, de QMD jusqu'au concat engine.

Ce que le fichier devra couvrir :

**QMD — la couche d'indexation.** Ce qu'est QMD, comment il s'installe et se configure, les trois modes natifs (`search`, `vsearch`, `query`) et lesquels on expose dans le tool (fast = `search`, deep = `query`). La stratégie de chunking : QMD chunke aux breakpoints de score élevé dans la structure markdown. H1 = score 100, H2 = score 90. Ce sont les points de découpe naturels. Comment ça s'applique aux différents types de fichiers du vault : changelogs (H1 par jour reste cohérent, découpe au H2 si une journée est très dense), tasks (H1 par tâche = un chunk par tâche), fichiers courts comme `state.md` et `description.md` (généralement un seul chunk par fichier), items bucket (un ou plusieurs chunks selon la taille mit frontmatter inclus). L'indexation incrémentale : le background job ré-indexe uniquement le fichier modifié après chaque écriture, pas un full re-scan. La table de ce qui est indexé et ce qui ne l'est pas (inchangée par rapport à `vault.md`).

**La mécanique de retour des chunks.** C'est un point à clarifier à l'écriture. Quelques questions à trancher dans le fichier : est-ce que le retour est toujours un chunk ou parfois un fichier entier ? Comment on détermine si un chunk représente le fichier entier ou seulement une partie ? La décision en cours d'écriture devra répondre à ça. Ce qui est acté : pour chaque chunk retourné, le tool inclut N lignes de contexte au-dessus et N lignes en-dessous dans le fichier source. Cette fenêtre de contexte donne à l'agent une vue suffisante pour raisonner sans avoir à faire un `read` du fichier.

**Le concat engine.** Composant mécanique (pas un LLM) qui assemble les fichiers identifiés par l'agent de search en un document structuré. L'agent lui fournit une liste de fichiers avec pour chacun soit le fichier entier soit une range de lignes. L'engine préfixe chaque bloc par le path du fichier.

**Le format de sortie.** Deux parties dans l'ordre : l'overview de l'agent (2-5 lignes rédigées par le LLM qui oriente l'utilisateur sur ce qui a été trouvé et pourquoi c'est pertinent) suivie du document concaténé produit par l'engine (contenu brut des fichiers avec leurs paths comme headers). Format identique pour le MCP et l'interface web dans le MVP.

**Section features supplémentaires à inclure dans ce fichier :**
- Filtrage par date (`date_from`, `date_to`) : explication complète du comportement sur changelogs vs autres fichiers, formats acceptés, cas d'usage.
- Différenciation de la sortie entre MCP et interface web : le MVP retourne le même format partout, mais à terme l'interface pourrait avoir un rendu plus riche (fichiers cliquables, collapsibles) et l'API MCP un format plus programmatique.