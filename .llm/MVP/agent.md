# Agents

Deux agents distincts opèrent sur le vault.
Un seul modèle pour les deux — puissant, grand context window.
Pas de séparation orchestrateur/worker pour le MVP.

L'architecture du vault → `vault.md`
L'infrastructure, la queue, le background job → `infra.md`
Le détail de chaque tool → `tools/`
La mécanique interne du search engine → `search.md`

---

## La context window — philosophie fondamentale

C'est le point de départ de tout le design des agents. Il faut comprendre
pourquoi Knower peut se permettre d'être généreux sur les tokens —
et pourquoi ce n'est pas le cas pour d'autres types de systèmes.

### Pourquoi les tâches de mémoire sont fondamentalement différentes

Dans les systèmes de génération de code, chaque token compte.
Le modèle doit produire une syntaxe exacte, respecter des conventions précises,
ne pas inventer une API qui n'existe pas, ne pas halluciner une fonction.
La moindre erreur dans 10 000 lignes de code peut tout casser.
C'est pourquoi les benchmarks de coding montrent une dégradation notable
des performances au-delà de 128k à 200k tokens en contexte —
la précision syntaxique et la cohérence du code généré commencent à souffrir.

Les tâches de Knower sont d'une nature radicalement différente.
L'agent ne génère pas de code. Il lit du markdown structuré,
comprend de l'information, prend des décisions de routing,
écrit des entrées de changelog, met à jour des sections de fichiers.
Ces tâches sont beaucoup plus tolérantes à la quantité de contexte.

Voilà pourquoi : si on charge 700k ou 900k tokens d'un vault entier
dans le contexte d'un agent, il comprendra la structure globale,
les projets, les décisions, les états. S'il doit ensuite écrire
une entrée de changelog sur une décision de 3 lignes,
il le fera avec une précision quasi parfaite — parce que le contexte
énorme lui donne exactement la compréhension qu'il faut.
L'hallucination sur ce type de tâche, à ces volumes de contexte,
est marginale comparée à une tâche de génération de code.

C'est la thèse centrale du design : **charger plus de contexte rend
les agents meilleurs sur les tâches de mémoire, pas pires.**
Ce n'est pas le cas pour le code. C'est le cas pour la connaissance.

### Le budget réel — 200-300k tokens par session

L'objectif opérationnel est de rester sous 200-300k tokens par session.
300k est le maximum qu'on vise. Ce n'est pas une contrainte technique
insurmontable — c'est un budget de travail confortable qui permet
de gérer des vaults denses avec des dizaines de projets actifs.

À 200-300k tokens en contexte, les modèles récents opèrent encore
avec une très haute fiabilité sur des tâches de compréhension et de routing.
La zone de dégradation identifiée dans la littérature pour les tâches
de traitement de l'information est nettement plus haute que pour le code.
On exploite cette marge.

Une session typique, sans aucune optimisation, reste très en dessous du seuil :
`overview.md` (300-400 tokens) + `tree.md` (1-2k tokens selon la taille du vault) +
`profile.md` (200-300 tokens) + quelques fichiers projet lus intégralement (10-30k tokens)
+ des chunks de search (2-5k tokens) = 15-40k tokens de contexte.
Sur 200k disponibles, la marge est énorme.

### Les outils d'optimisation — pourquoi ils changent tout

Le système dispose de tools spécifiquement conçus pour économiser des tokens.
Ce n'est pas de l'optimisation prématurée — c'est de l'architecture.

**`append` sans lecture préalable** — sur un changelog de 300 jours d'historique
qui fait 60k tokens, l'agent veut ajouter une entrée pour aujourd'hui.
Sans l'outil `append`, il devrait lire les 60k tokens, les charger en contexte,
puis réécrire le fichier entier. Avec `append`, il génère le nouveau bloc
et l'insère en haut du fichier sans jamais ouvrir le contenu existant.
60k tokens économisés sur une seule opération.

**`read` avec `head` et `tail`** — sur un changelog de 60k tokens,
l'agent n'a souvent besoin que des entrées récentes pour calibrer
ce qu'il va écrire. `read(path, head=2000)` retourne les 2000 premiers tokens
du fichier — les entrées les plus récentes puisque le changelog est newest-first.
58k tokens économisés, contexte récent préservé.

**`search` pour des chunks ciblés** — au lieu de lire 5 fichiers en entier
pour trouver une décision passée, l'agent fait un `search` et reçoit
les 3-4 chunks pertinents avec leurs scores. Il charge 2k tokens
au lieu de 30k. Si un chunk confirme qu'il a besoin du fichier complet,
il fait un `read` ciblé ensuite.

**`tree` pour décider avant de lire** — avant d'ouvrir le bucket d'un projet,
l'agent appelle `tree` sur ce dossier et voit que le bucket fait 45k tokens
répartis sur 12 fichiers. Il peut décider quels fichiers ouvrir
en fonction de leur taille et de leur date de modification,
sans charger un seul token de contenu.

Avec ces outils combinés, un agent peut gérer des vaults de plusieurs centaines
de milliers de tokens en restant systématiquement sous 200-300k tokens
de contexte actif par session. Des tâches qui sembleraient impossibles
sans optimisation deviennent triviales — parce que l'agent ne charge jamais
plus que ce dont il a besoin pour prendre la prochaine décision.

C'est ça la puissance réelle du système : pas la taille brute du context window,
mais la combinaison d'un context window généreux et d'outils d'accès ciblé.
Même sans aucun outil d'optimisation, un agent pourrait résoudre des tâches
correctement en chargeant tout ce dont il a besoin. Avec les outils,
il peut résoudre des tâches d'une complexité sans commune mesure
en restant dans un budget confortable.

**Les agents ne micro-optimisent pas.** Ils chargent ce qu'il faut pour bien
raisonner. L'objectif est la qualité du raisonnement, pas l'économie de tokens
pour l'économie. Les outils existent pour rendre possibles les tâches complexes —
pas pour rendre les agents paranoïaques sur chaque lecture de fichier.

---

## Le modèle agentique — une boucle, pas une conversation

Les agents de Knower ne sont pas dans un chat avec l'utilisateur.
Il n'y a pas d'échange, pas de clarification, pas de
"est-ce que tu voulais dire X ?" pendant l'exécution.
L'utilisateur envoie une tâche — du texte, des images, une question —
et l'agent la traite intégralement sans jamais attendre de réponse humaine.

Concrètement, un agent est un LLM qui s'appelle en boucle.
Il reçoit son contexte initial, raisonne, appelle un tool,
reçoit le résultat du tool, raisonne à nouveau, appelle un autre tool,
et ainsi de suite jusqu'à ce qu'il décide qu'il a terminé.
À ce moment-là seulement, il retourne son résultat final.

Ce modèle a des conséquences directes sur le design :

**L'agent doit être autonome dès le départ.**
Il n'a pas la possibilité de poser des questions à l'utilisateur en cours de route.
Tout ce dont il a besoin pour prendre ses décisions doit être disponible
dans son contexte initial ou accessible via ses tools.
C'est pourquoi le contexte initial est riche — overview, tree, profile —
et pourquoi le system prompt est exhaustif sur les conventions et l'architecture.

**L'agent décide quand il a fini.**
Il n'y a pas de nombre fixe d'itérations, pas de limite de tools appelés.
L'agent tourne aussi longtemps qu'il estime ne pas avoir terminé sa tâche.
Un update simple — une note rapide à ajouter dans le bucket — peut se résoudre
en 2-3 appels tools. Un update complexe — une information qui touche
plusieurs projets, contredit une décision existante, et nécessite
une réorganisation — peut demander 10-15 appels tools avec du raisonnement
entre chaque étape. L'agent est le seul juge.

**Il n'y a pas de flowchart prescrit.**
Les sessions de brainstorming ont délibérément tranché cette question :
on ne trace pas un arbre de décision pas-à-pas pour l'agent.
Le vault est une structure suffisamment répétable et connue pour qu'un agent
intelligent — équipé du bon system prompt et du bon contexte — navigue,
décide, et agisse sans qu'on lui dicte chaque étape.
Le system prompt lui donne la compréhension de l'environnement.
Les tools lui donnent les capacités d'action.
Le reste, c'est du raisonnement — et c'est exactement ce pourquoi
on utilise un modèle puissant.

**L'output est atomique.**
Du point de vue de l'utilisateur, il envoie quelque chose
et il reçoit un résultat. Ce qui se passe entre les deux est invisible
pour le MVP — le streaming des actions est une amélioration post-MVP.
L'utilisateur ne voit pas les 8 appels tools intermédiaires.
Il voit le résultat final : une confirmation de mise à jour
ou un document de réponse assemblé.

---

## Contexte initial — ce avec quoi les agents démarrent

À chaque session, les deux agents chargent systématiquement en contexte
trois fichiers avant de faire quoi que ce soit d'autre :

1. **`overview.md`** — la carte de tout ce qui existe dans le vault.
   Projets, contexte de vie, intentions pré-projet, count inbox.
   C'est le point d'entrée pour savoir où chercher.

2. **`tree.md`** — la structure complète des fichiers avec tokens et timestamps.
   L'agent sait immédiatement combien pèse chaque dossier,
   quand chaque fichier a été modifié pour la dernière fois,
   et combien de fichiers contient chaque bucket.

3. **`profile.md`** — l'identité durable de l'utilisateur.
   Préférences, contraintes récurrentes, style de communication.

Ces trois fichiers sont le socle. Ils donnent à l'agent une représentation
complète du vault avant le premier appel outil. L'agent n'a pas à construire
cette représentation depuis zéro — elle est là, en contexte, prête.

L'overview lui dit ce qui existe et dans quel état c'est.
Le tree lui dit combien ça pèse et où c'est.
Le profile lui dit à qui il a affaire.

À partir de ce contexte, l'agent peut déjà prendre 80% de ses décisions
de navigation. Il sait si un projet existe, combien de tokens fait
son changelog, quand sa dernière mise à jour a eu lieu.
Les tools servent à aller chercher le détail — pas à découvrir la structure.

Ces trois fichiers représentent en général 2-5k tokens au total.
C'est le coût d'entrée de chaque session — négligeable sur un budget de 200-300k.

---

## Le system prompt — le contrat avec l'agent

Le system prompt n'est pas de la configuration technique.
C'est un composant produit à part entière — c'est le contrat entre
le développeur et l'agent. C'est ce qui rend l'agent autonome.

Chaque agent a son propre system prompt. Ce prompt contient tout ce dont
l'agent a besoin pour comprendre son environnement et prendre ses décisions
sans guidance externe pendant l'exécution.

**La compréhension complète de l'architecture du vault.**
L'agent sait ce que représente chaque type de fichier, pourquoi il existe,
ce qu'on y trouve et ce qu'on n'y trouve pas.
Il sait qu'un `state.md` est une photo instantanée volatile,
qu'un `description.md` est l'identité stable d'un projet,
qu'un changelog est un log structuré H1/jour H2/entrée qui grossit indéfiniment,
qu'un `tasks.md` est une vue live où les tâches complétées disparaissent.
Un agent qui connaît cette architecture sait où chercher
et où écrire avant de faire le moindre appel outil.

**Le rôle et le contexte mental de l'agent.**
L'agent de update se demande en permanence
*"Où est-ce que je range cette information ?"*
L'agent de search se demande *"Qu'est-ce que l'utilisateur a besoin de savoir ?"*
Cette intention guide chaque décision de la boucle agentique.
Ce n'est pas un slogan — c'est le filtre à travers lequel l'agent
évalue chaque résultat de tool et décide de la prochaine action.

**Les conventions d'écriture dans chaque type de fichier.**
Le format des changelogs — H1 par jour, H2 par entrée, newest first.
La structure des tasks — H1 par tâche avec métadonnées inline.
Ce qu'on met dans un bucket vs dans un changelog.
Comment on nomme les folders inbox — `YYYY-MM-DD-description-courte`.
Quand on utilise `write` vs `edit` vs `append`.
L'agent ne découvre pas ces conventions en cours de route — il les connaît
dès le début de sa boucle agentique.

**Les tools disponibles et leur usage.**
Pas juste une liste de signatures. Une compréhension de quand utiliser
`append` plutôt qu'`edit` — parce que lire un changelog de 50k tokens
pour ajouter une entrée en top est du gaspillage quand `append` le fait
sans lecture. Quand faire un `search` avant d'écrire — parce qu'une information
peut déjà exister ou contredire quelque chose dans le vault.
Quand créer un folder inbox plutôt que de tenter un routing incertain.

C'est ce system prompt qui permet au modèle agentique de fonctionner.
Sans lui, l'agent tourne en boucle sans direction.
Avec lui, l'agent sait où il est, ce qu'il peut faire, et comment le faire —
et il se débrouille.

---

## Agent de update

**Contexte mental : *"Où est-ce que je range cette information ?"***

### Input

L'agent de update reçoit toujours la même chose :
du contenu à intégrer dans le vault.

Ce contenu est composé de :
- **Du texte** — message de l'utilisateur, note, transcription, email converti,
  n'importe quelle forme de texte. C'est toujours du markdown
  quand ça arrive à l'agent — le processing pipeline en amont
  a déjà converti ce qui devait l'être.
- **Des images** — optionnellement. Passées au modèle vision tel quel,
  jamais converties en description texte.
- **Un `inbox_ref`** — optionnellement. Le path d'un folder inbox
  quand l'utilisateur répond à un item en attente.

L'invariant : à l'entrée de l'agent, tout est soit du texte, soit une image.
Le processing pipeline garantit cet invariant quelle que soit la source d'origine.

L'agent ne sait pas et n'a pas besoin de savoir d'où vient l'input —
interface web, Claude Code via MCP, script custom. Il traite ce qu'il reçoit.

### Ce que l'agent fait

L'agent de update a accès à tous les tools — lecture, écriture, search, navigation.
Il est le seul à pouvoir modifier le vault.

À partir de son contexte initial et de l'input reçu, il entre dans sa boucle agentique.
Ce qui se passe dans cette boucle dépend entièrement de la nature de l'input.
L'agent navigue le vault avec ses tools, décide du routing, agit sur les fichiers.

Ce qu'on sait de façon certaine sur son comportement,
parce que c'est inscrit dans le system prompt :

**Il cherche avant d'écrire.**
L'agent utilise le search tool pour vérifier si une information existe déjà
dans le vault, si elle contredit quelque chose, si elle complète une entrée existante.
Il ne crée pas de doublons, il ne contredit pas des décisions existantes
sans le signaler. Le vault est une source de vérité — l'agent la respecte.

**Il logue systématiquement ses actions.**
Chaque opération de update produit une entrée dans `changelog.md` global.
Une entrée par opération, pas par fichier touché. Si une opération
met à jour le state d'un projet, ajoute une tâche, et crée un item bucket,
c'est une seule entrée de changelog qui résume l'ensemble.
L'agent ne termine jamais sa boucle sans avoir loggé.

**Il route à trois niveaux.**

*Niveau 1 — Inférence par contenu.*
Le signal sémantique dans l'input est assez fort pour router sans demander.
"Le client de startup-x veut changer de prestataire" → le projet est identifiable,
l'agent route directement. L'utilisateur n'est pas dérangé.

*Niveau 2 — Inférence par contexte.*
Si l'input arrive avec un contexte qui identifie clairement un projet —
un `inbox_ref` qui pointe vers un folder inbox lié à un projet,
ou un contexte d'usage depuis Claude Code sur un repo précis —
le contexte suffit. Pas besoin de demander.

*Niveau 3 — Inbox.*
L'ambiguïté est trop forte. L'agent ne peut pas router avec confiance.
Il crée un folder inbox avec un `review.md` qui expose tout son raisonnement :
ce qu'il a cherché, dans quels projets, ce qu'il a trouvé ou pas,
ce qu'il propose, et la question précise qu'il pose.
L'utilisateur répondra plus tard via le mode answering de l'interface.
*Ce troisième niveau est optionnel pour la première version du MVP.*

### Cas spécial — `inbox_ref`

Quand l'input contient `inbox_ref: [folder-path]`,
l'agent sait qu'il s'agit d'une réponse à un item inbox en attente.
Il lit le folder inbox concerné en premier — le `review.md` avec son raisonnement
précédent et les fichiers d'input originaux — intègre la réponse de l'utilisateur,
route les fichiers vers leur destination dans le vault,
supprime le folder inbox, et logue dans le changelog global.

Ce mécanisme permet de résoudre les cas d'ambiguïté sans interrompre
la boucle agentique. L'agent qui a créé le folder inbox n'est pas
le même agent que celui qui le résout — ce sont deux sessions distinctes.
Le `review.md` fait le pont entre les deux : il porte le raisonnement
de la première session pour que la deuxième n'ait pas à tout reconstruire.

### Output

L'agent de update retourne un résumé de confirmation.
Ce résumé contient :
- Ce qui a été fait — en quelques lignes factuelles
- Les fichiers touchés — liste de paths

C'est ce que l'interface affiche dans la vue activité après un update.
C'est aussi ce que le client MCP reçoit en réponse.

Le résumé n'est pas le changelog — le changelog est écrit dans le vault
par l'agent pendant sa boucle. Le résumé est la réponse directe à l'appelant.

### Ce que l'agent de update ne fait pas

Il ne maintient pas les métadonnées des fichiers.
Les champs `tokens` et `updated` dans le frontmatter sont gérés
exclusivement par le background job — un processus programmatique
qui se déclenche automatiquement après chaque écriture.
L'agent de update écrit du contenu. La plomberie se fait toute seule derrière.

Il ne régénère pas `tree.md`.
Le background job s'en occupe après chaque modification du vault.
L'agent n'a pas à y penser.

Il ne ré-indexe pas les fichiers dans le search engine.
C'est le background job qui ré-indexe le fichier modifié après chaque écriture.
L'agent écrit, le système propage.

---

## Agent de search

**Contexte mental : *"Qu'est-ce que l'utilisateur a besoin de savoir ?"***

### Input

L'agent de search reçoit une question ou une requête textuelle.
C'est toujours du texte — jamais d'images, jamais de fichiers joints.

La question peut être :
- Précise : "Où en est le projet startup-x ?"
- Vague : "Ce truc qu'on avait décidé sur l'architecture de paiement"
- Cross-projet : "Quels projets sont bloqués ?"
- Temporelle : "Qu'est-ce qui s'est passé cette semaine ?"

L'agent ne reçoit aucune instruction sur comment chercher.
Il a la question, son contexte initial, et ses tools. Il se débrouille.

### Ce que l'agent fait

L'agent de search est **read-only**.
Il n'a accès qu'aux tools de lecture et de navigation.
Il ne peut pas modifier le vault — pas d'écriture, pas de suppression,
pas de déplacement. C'est une garantie architecturale :
la search peut tourner en parallèle des updates sans aucun risque
de conflit d'écriture.

À partir de son contexte initial et de la question reçue,
il entre dans sa boucle agentique.

Il commence par raisonner sur ce qu'il sait déjà.
L'overview lui dit quels projets existent et dans quel état ils sont.
Le tree lui dit où se trouvent les fichiers et combien ils pèsent.
Souvent, avant même d'appeler un tool, l'agent sait déjà
dans quels projets chercher et quels fichiers cibler.

Ensuite il utilise ses tools pour aller chercher le détail.
Le search tool pour identifier les chunks pertinents dans le vault indexé.
Le read tool pour charger les fichiers identifiés et construire du contexte complet.
Le tree tool pour explorer un sous-dossier s'il a besoin de plus de détail
sur la structure.

L'agent peut faire plusieurs passes.
Un premier search identifie des chunks dans un changelog.
L'agent lit le state du projet pour comprendre le contexte actuel.
Il fait un deuxième search avec des termes différents pour couvrir un autre angle.
Il lit un fichier bucket qui semble pertinent.
Chaque itération de la boucle affine sa compréhension.

Quand il estime avoir suffisamment de contexte pour répondre à la question,
il produit son output et la boucle s'arrête.

### Output

La sortie de l'agent de search est composée de deux parties :

**Partie 1 — L'overview de l'agent.**
Quelques lignes — deux à cinq — rédigées par l'agent.
Ce n'est pas une synthèse exhaustive. C'est une orientation :
ce qu'il a trouvé, dans quels fichiers, et en quoi c'est pertinent
par rapport à la question posée. Cette partie est produite par le LLM
au terme de son exploration.

**Partie 2 — Les fichiers assemblés.**
L'agent spécifie quels fichiers (ou quelles sections de fichiers)
sont pertinents pour répondre à la question.
Le `concat` tool — un outil mécanique, pas un LLM — assemble ces fichiers
en un document markdown structuré où chaque bloc est préfixé par le path
du fichier source.

Le résultat final est un seul document markdown :
l'overview en haut, un séparateur, puis les fichiers concaténés en dessous.
C'est ce que l'interface affiche dans la vue activité après un search.
C'est aussi ce que le client MCP reçoit en réponse.

Ce format est identique quel que soit le client — interface web ou MCP.
Le contenu brut des fichiers est retourné tel quel, pas résumé,
pas reformulé. L'utilisateur voit exactement ce qui est dans sa mémoire.

### Ce que l'agent de search ne fait pas

Il n'écrit rien dans le vault. Jamais. Sous aucune condition.
Il ne crée pas de fichiers, ne modifie pas de state, ne logue pas dans le changelog.
Il lit, il cherche, il assemble, il retourne.

Il ne résume pas les fichiers.
Les fichiers retournés dans la partie 2 de l'output sont le contenu brut.
L'overview de l'agent en partie 1 est une orientation, pas un résumé
qui remplacerait la lecture des fichiers. L'utilisateur a toujours
accès au matériau source.

---

## Les tools — vue d'ensemble

Les tools sont l'interface entre les agents et le vault.
Le détail de chaque tool — signature, paramètres, comportement,
edge cases — est documenté dans `tools/`.

Les deux agents partagent les tools de lecture et de navigation.
Seul l'agent de update a les tools d'écriture.
Le `concat` tool est exclusif à l'agent de search.

| Tool | Update | Search | Rôle |
|------|:------:|:------:|------|
| `tree` | ✅ | ✅ | Explorer la structure du vault |
| `read` | ✅ | ✅ | Lire des fichiers |
| `search` | ✅ | ✅ | Chercher dans le vault indexé |
| `write` | ✅ | ❌ | Créer ou réécrire un fichier |
| `edit` | ✅ | ❌ | Modifier une section précise |
| `append` | ✅ | ❌ | Insérer en début/fin sans lecture |
| `move` | ✅ | ❌ | Déplacer un fichier |
| `delete` | ✅ | ❌ | Supprimer un fichier ou dossier |
| `concat` | ❌ | ✅ | Assembler des fichiers en un document |

L'index et la vue d'ensemble des tools → `tools/overview.md`

---

## Parallélisme et séquentialité

Les updates sont séquentielles. La queue garantit qu'un seul agent de update
écrit dans le vault à la fois. Deux agents de update en parallèle
qui écrivent dans les mêmes fichiers créeraient des conflits d'écriture
impossibles à résoudre. Une update ne commence pas son processing
tant que la précédente n'est pas terminée.

Les searches sont parallèles. L'agent de search est read-only —
il ne modifie rien, il ne crée pas de conflits. Plusieurs recherches
peuvent tourner simultanément, y compris pendant qu'un update est en cours.
Un search qui tourne pendant un update lira les fichiers dans leur état
au moment de la requête — potentiellement avant qu'une mise à jour
soit complète. C'est acceptable. On ne cherche pas de la consistance
transactionnelle, on cherche de la mémoire humaine.

Le détail de la queue et du processing → `infra.md`

---

## Features supplémentaires

**Séparation orchestrateur / worker.**
Le MVP fait tourner un seul modèle qui fait tout — raisonnement et génération.
À terme, l'orchestrateur tournerait sur un modèle puissant (raisonnement,
routing, détection de contradictions) et déléguerait la génération de contenu
markdown à un worker cheap et rapide. Le worker recevrait le contexte complet —
jamais appauvri — pour produire du contenu cohérent avec le ton et le vocabulaire
existants dans le vault.

**Streaming des actions de l'agent.**
Le MVP retourne le résultat final en bloc — l'utilisateur ne voit pas
les étapes intermédiaires. À terme, un flux WebSocket pourrait pusher
chaque action de l'agent en temps réel vers l'interface :
`reading: state.md`, `searching: startup-x changelog`, `writing: tasks.md`.
C'est ce qui rendrait la boucle agentique visible et renforcerait
la confiance de l'utilisateur dans le système.