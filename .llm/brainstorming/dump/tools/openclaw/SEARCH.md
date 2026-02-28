# Comment fonctionne la recherche dans la mémoire d'un agent IA — Documentation technique exhaustive

---

## Introduction et philosophie générale

La mémoire d'un agent IA dans OpenClaw est constituée de **fichiers Markdown ordinaires sur le disque**. Ces fichiers sont la source de vérité absolue. L'agent ne "sait" que ce qui est écrit dedans. Tout le reste — les index, les embeddings, les bases SQLite — n'est qu'une infrastructure pour retrouver le bon contenu au bon moment.

Il est utile de noter que l'équipe de Claude Code a initialement construit leur système de mémoire autour d'une base de données vectorielle, puis a finalement **fait marche arrière vers des outils comme grep**. Leur constat : la recherche agentique par grep simple, combinée à une exploration itérative par l'agent lui-même, s'est révélée plus performante et considérablement plus simple à maintenir que l'infrastructure vectorielle. C'est une observation importante sur les compromis réels de ces approches — la sophistication n'est pas toujours synonyme de meilleure qualité dans la pratique.

OpenClaw choisit une voie intermédiaire : garder les fichiers Markdown comme source de vérité (simple, portable, lisible), mais construire une infrastructure de recherche hybride sophistiquée par-dessus.

OpenClaw organise la mémoire autour de deux types de fichiers dans le workspace de l'agent :

Le **journal quotidien** `memory/YYYY-MM-DD.md`, en écriture append-only. Au démarrage d'une session, OpenClaw charge automatiquement aujourd'hui et hier dans le contexte.

Le fichier `MEMORY.md`, optionnel, pour les faits durables, les préférences stables, les décisions importantes. Chargé uniquement dans la session principale privée — jamais dans des contextes de groupe.

Ces fichiers vivent dans `~/.openclaw/workspace` par défaut.

---

## La structure de stockage de l'index

### La base de données SQLite par agent

OpenClaw maintient une base de données SQLite dédiée par agent à `~/.openclaw/memory/<agentId>.sqlite`. Plusieurs tables y travaillent ensemble.

La table **files** est le registre de tous les fichiers mémoire indexés. Elle stocke le chemin, la source, un **hash du contenu**, le timestamp de dernière modification, et la taille. Le hash de contenu est la clé de la synchronisation incrémentielle : il suffit de comparer ce hash au hash actuel du fichier sur disque pour savoir si quelque chose a changé, sans lire le contenu entier.

La table **chunks** est là où les documents découpés vivent. Chaque chunk stocke son id, son chemin vers le fichier parent, sa **ligne de début et sa ligne de fin** dans le fichier original, le hash de son texte, le modèle d'embedding utilisé, le texte brut, le vecteur d'embedding, et un timestamp. La ligne de début et de fin est fondamentale : c'est ce qui permet à l'agent, après avoir trouvé un chunk pertinent, de demander exactement la bonne section du fichier via `memory_get`.

Deux **tables virtuelles** alimentent les deux types de recherche :

`chunks_fts` est une table virtuelle **FTS5** de SQLite. Elle indexe le texte de chaque chunk en construisant un index inversé pour la recherche BM25 par mots-clés.

`chunks_vec` est une table virtuelle fournie par l'extension **sqlite-vec**. Elle stocke les vecteurs d'embedding en tableaux float32 et permet de calculer des distances cosinus directement dans SQLite via `vec_distance_cosine()`. Quand sqlite-vec n'est pas disponible, OpenClaw charge tous les embeddings en mémoire JavaScript et effectue la comparaison manuellement — plus lent, mais fonctionnel.

La table **embedding_cache** indexe les embeddings par hash du texte, fournisseur, et modèle. Avant de générer un embedding pour un chunk, on calcule son hash et on vérifie la cache. Si l'embedding existe déjà (cache hit), on le réutilise sans aucun appel. Si non (cache miss), on le génère et on le stocke. Cette optimisation est particulièrement précieuse pour les transcriptions de session qui s'accumulent rapidement mais où la majorité du contenu existant ne change pas.

---

## Le découpage en chunks

### Le chunking d'OpenClaw

OpenClaw découpe les fichiers Markdown en chunks d'environ **400 tokens**, avec **80 tokens de chevauchement** entre chunks consécutifs. Ce chevauchement garantit qu'une information à cheval sur la frontière naturelle entre deux chunks sera entièrement représentée dans au moins l'un d'eux. Chaque chunk stocke sa ligne de début et de fin dans le fichier original.

### Le chunking avancé de QMD

QMD implémente un chunking beaucoup plus sophistiqué basé sur la détection de **points de rupture naturels** dans la structure Markdown. La taille cible est de **900 tokens** avec **15% de chevauchement**.

Chaque type de rupture potentielle reçoit un score qui reflète son poids sémantique :

`# Titre` (H1) → 100. C'est la rupture la plus significative possible, marque le début d'une section majeure.

`## Titre` (H2) → 90.

`### Titre` (H3) → 80.

`#### Titre` (H4) → 70.

`##### Titre` (H5) → 60.

`###### Titre` (H6) → 50.

Délimiteur de bloc de code (```) → 80. Le code est une unité sémantique cohérente qu'on ne veut pas couper en plein milieu.

Ligne horizontale (`---` ou `***`) → 60.

Ligne vide (séparation de paragraphe) → 20.

Item de liste (`- item` ou `1. item`) → 5.

Simple retour à la ligne → 1.

Quand on approche de la limite de 900 tokens, QMD examine une **fenêtre de 200 tokens avant ce point**. Pour chaque rupture potentielle dans cette fenêtre, il calcule un score final qui combine le score de base du type de rupture avec une pénalité de distance : `scoreFinal = scoreBase × (1 - (distance/tailleF enêtre)² × 0.7)`. On coupe au point qui a le score final le plus élevé.

La décroissance est **quadratique** avec la distance. Un H1 à 200 tokens de la limite obtient un score final d'environ 30 — ce qui bat encore un simple retour à la ligne exactement à la limite (score = 1). En revanche, un H1 proche de la limite battra toujours un H1 éloigné. Cela signifie que la priorité est donnée aux ruptures sémantiquement fortes proches de la limite, avec une dégradation progressive pour les ruptures plus éloignées.

**Protection des blocs de code** : les points de rupture à l'intérieur d'un bloc de code sont complètement ignorés. On ne coupe jamais du code en plein milieu. Si un bloc de code dépasse la taille maximale, il est gardé entier même si ça dépasse la limite imposée.

---

## La recherche par mots-clés : BM25 et FTS5

### Comment ça fonctionne concrètement

La table virtuelle `chunks_fts` est une table FTS5 de SQLite. À l'insertion d'un chunk, SQLite tokenise le texte et construit un index inversé : pour chaque terme, la liste de tous les chunks qui le contiennent et combien de fois. BM25 combine la fréquence du terme dans le chunk (TF, avec saturation logarithmique) et la rareté du terme dans l'ensemble du corpus (IDF) pour produire un score de pertinence.

SQLite retourne les scores BM25 comme valeurs **négatives** par convention interne. OpenClaw et QMD les convertissent en positifs avec `Math.abs(score)`. Les scores bruts vont de 0 à ~25+ selon la richesse du match.

### Les limites

BM25 est excellent pour les tokens exacts — identifiants comme `a828e60`, variables de code comme `useState`, chaînes d'erreur précises comme "sqlite-vec unavailable". Mais il est aveugle aux synonymes et aux paraphrases. "Configurer le réseau" et "network setup" sont sémantiquement identiques mais BM25 les traite comme complètement différents si aucun token ne se recoupe.

---

## La recherche sémantique par vecteurs

### Ce que fait concrètement QMD

Pour générer ses embeddings, QMD utilise le modèle local GGUF `embeddinggemma-300M-Q8_0` (~300 Mo) via `node-llama-cpp`. Le format d'entrée est **spécifique et différencié selon le type de contenu** :

Pour les requêtes de recherche : `"task: search result | query: {texte_de_la_requête}"`

Pour les documents : `"title: {titre_du_document} | text: {contenu_du_chunk}"`

Ce formatage asymétrique est délibéré — le modèle a été entraîné à différencier les requêtes des documents pour améliorer la qualité des correspondances. Les embeddings sont générés par lots via `embedBatch()` de `node-llama-cpp`, avec un identifiant composite `hash_document:sequence_chunk` comme clé dans la table `content_vectors`.

La recherche retrouve les chunks les plus proches en distance cosinus. SQLite stocke la distance cosinus (pas la similarité), qu'OpenClaw convertit en score de 0 à 1 avec `similarité = 1 - distance`.

### Les limites

La recherche vectorielle est aveugle aux identifiants exacts et aux tokens très spécifiques. Elle peut rapprocher `useState` et `useEffect` parce que ce sont tous deux des hooks React — mais si on cherche `useState` précisément, cette proximité sémantique est une erreur. De même, elle peut retourner des résultats sémantiquement proches dans leur domaine mais factuellement inutiles pour la requête réelle.

---

## La recherche hybride : fusion des deux approches

### L'approche d'OpenClaw : Weighted Score Fusion

OpenClaw lance **deux recherches en parallèle** pour chaque requête. Chaque recherche utilise un **multiplicateur de candidats de 4x** : pour 6 résultats demandés, chaque backend retourne 24 candidats, ce qui donne à la fusion plus de matière à travailler.

Les scores BM25 bruts sont d'abord normalisés **par rang** (pas par score absolu) : `textScore = 1 / (1 + max(0, rang_bm25))`. Le premier résultat BM25 vaut 0.5, le deuxième 0.33, le troisième 0.25, et ainsi de suite.

Les deux pools de candidats sont fusionnés par identifiant de chunk et un score final pondéré est calculé : `scoreTotal = 0.7 × scoreVecteur + 0.3 × scoreTexte`. Ces poids (70% vecteur, 30% texte) sont les valeurs par défaut d'OpenClaw, normalisés automatiquement pour toujours sommer à 1.

Un chunk qui apparaît dans les deux listes cumule les deux scores. Un chunk présent uniquement dans les résultats vectoriels obtient zéro pour le score texte. Un chunk présent uniquement dans les résultats BM25 obtient zéro pour le score vecteur.

Au final, tout est trié par score décroissant, filtré par le seuil minimum de **0.35** (valeur par défaut), et les N meilleurs sont retournés.

### L'approche de QMD : Reciprocal Rank Fusion (RRF)

QMD utilise la **Reciprocal Rank Fusion**. Au lieu de travailler sur des scores absolus, RRF travaille uniquement sur les **positions** des résultats dans chaque liste.

La formule : pour chaque document, `scoreRRF = Σ 1 / (k + rang_dans_liste_i)` pour chaque liste où le document apparaît. La constante `k = 60` est un paramètre d'amortissement qui empêche le premier résultat d'une liste de dominer excessivement.

Un document classé 2e en vectoriel et 3e en BM25 obtient `1/(60+2) + 1/(60+3) = 0.0161 + 0.0159 = 0.032`. Un document classé 1er uniquement en vectoriel obtient `1/(60+1) = 0.0164`.

La différence fondamentale avec la weighted score fusion d'OpenClaw : RRF ignore la force du score — un document avec un score vectoriel de 0.99 est traité identiquement à un document avec 0.61 s'ils sont tous les deux premiers dans leur liste. La weighted score fusion préserve cette information de magnitude mais nécessite une normalisation préalable des scores entre backends. RRF est plus robuste aux différences d'amplitude entre systèmes mais perd l'information de confiance absolue.

---

## L'expansion de requête dans QMD

QMD utilise un LLM spécialisé fine-tuné pour générer des reformulations : `qmd-query-expansion-1.7B-q4_k_m.gguf` (~1.1 Go, quantifié à 4 bits). Pour une requête donnée, il génère **2 variantes alternatives** qui capturent différentes façons de formuler le même besoin de recherche.

On se retrouve donc avec 3 requêtes : originale + variante 1 + variante 2. Chacune lance ses propres recherches BM25 et vectorielle en parallèle — soit **6 listes de résultats** à fusionner.

La requête originale reçoit un **poids double** dans la fusion RRF. Concrètement, sa contribution dans le calcul du score RRF compte deux fois plus que celle des variantes. Ceci garantit que si un document correspond parfaitement à la requête exacte de l'utilisateur, il ne sera pas dilué par des variantes potentiellement moins précises.

Les réponses du LLM d'expansion sont **mises en cache** dans la table `llm_cache`. Si la même requête arrive une seconde fois, les variantes sont récupérées instantanément sans ré-invoquer le modèle.

---

## Le re-ranking LLM dans QMD

### Le modèle et son fonctionnement

Après la fusion RRF, QMD sélectionne les **30 meilleurs candidats** pour le re-ranking. QMD utilise `Qwen3-Reranker-0.6B` quantifié à 8 bits (~640 Mo), via l'API `createRankingContext()` et `rankAndSort()` de `node-llama-cpp`.

Le modèle évalue chaque candidat avec une logique binaire yes/no (le document est-il pertinent pour la requête ?) et utilise les **log-probabilités** de ces tokens pour produire un score de confiance continu entre 0 et 1. Un score proche de 1 signifie que le modèle est très confiant que le document est pertinent. Un score proche de 0 signifie qu'il est très confiant qu'il ne l'est pas. Le scoring se fait toujours par rapport à la **requête originale** de l'utilisateur — pas les variantes expansées.

Les scores du re-ranker (0 à 10 nativement selon Qwen3) sont normalisés en divisant par 10 pour obtenir une plage de 0 à 1.

Les scores de re-ranking sont aussi **mis en cache** dans `llm_cache` par couple (requête, document). Si le même couple (requête, document) revient — ce qui arrive quand les mêmes documents ressortent pour des requêtes proches — le score est récupéré instantanément sans ré-invoquer le modèle.

### Le mélange position-aware : le cœur de l'algorithme final

C'est là que QMD fait un choix architectural particulièrement réfléchi. Après le re-ranking, on dispose de deux scores pour chaque candidat : le score RRF issu de la fusion des recherches hybrides, et le score du re-ranker LLM. QMD n'en choisit pas un au détriment de l'autre — il les **mélange dans des proportions qui varient selon la position du document dans le classement RRF**.

La logique fondamentale derrière ce choix est la suivante : le classement RRF reflète la confiance des algorithmes de recherche. Plus un document est haut dans ce classement, plus les signaux mathématiques (distances vectorielles, scores BM25) sont concordants et forts. Plus il est bas, plus c'est ambigu.

**Pour les positions 1 à 3 dans le classement RRF** : le mélange est 75% score RRF et 25% score re-ranker. Ces documents sont arrivés premiers selon plusieurs critères de recherche simultanément. Il y a de très bonnes raisons mathématiques pour lesquelles ils sont là — une correspondance exacte dans l'index BM25, un vecteur très proche, ou les deux. Introduire trop de poids de re-ranker à ces positions risque de dégrader des correspondances fortes et évidentes que le LLM du re-ranker pourrait mal interpréter pour des raisons de formulation ou de style. On laisse donc les algorithmes de recherche maîtriser le résultat final, avec le re-ranker comme correction mineure.

**Pour les positions 4 à 10 dans le classement RRF** : le mélange devient 60% score RRF et 40% score re-ranker. On est dans une zone intermédiaire où les algorithmes de recherche ont identifié des documents pertinents mais avec moins de certitude que pour le top 3. Le re-ranker commence à avoir une influence substantielle — il peut corriger des erreurs de classement où un document sémantiquement très pertinent aurait été légèrement pénalisé par des différences de vocabulaire.

**Pour les positions 11 et au-delà dans le classement RRF** : le mélange s'inverse à 40% score RRF et 60% score re-ranker. Ces documents n'étaient pas clairement dans les meilleurs selon les algorithmes de recherche hybride. Les signaux mathématiques sont ambigus et faibles. C'est exactement là où le re-ranker LLM, avec sa capacité de compréhension sémantique profonde, peut identifier des **gemmes cachées** — des documents réellement pertinents que les métriques de distance et de fréquence de termes ont sous-évalués à cause de différences de formulation, de contexte, ou de structure. On lui fait donc majoritairement confiance dans cette zone.

Ce mélange position-aware résout un problème connu des systèmes qui appliquent le re-ranking en remplacement complet du classement initial : le re-ranker peut parfois détruire des correspondances exactes très fortes placées en tête par les algorithmes, en sur-pondérant des aspects sémantiques subtils. Et inversement, si on ne donne jamais assez d'autorité au re-ranker, les documents en queue de classement ne bénéficient pas de sa capacité à identifier la pertinence nuancée. Le mélange position-aware est la solution pragmatique à ce dilemme.

### Le bonus top-rank

En plus du mélange position-aware, QMD applique un bonus sur le score RRF aux documents qui se classent premiers dans n'importe quelle liste individuelle (avant la fusion) :

Le premier résultat dans n'importe quelle liste reçoit **+0.05** sur son score RRF.

Les deuxième et troisième résultats dans n'importe quelle liste reçoivent **+0.02**.

Ce bonus compense un effet de dilution intrinsèque au RRF : quand on fusionne 6 listes (3 requêtes × 2 backends), un document parfaitement premier pour la requête originale voit sa contribution diluée par les 5 autres listes où il n'est pas forcément premier. Sans ce bonus, des correspondances exactes très fortes au score idéal peuvent se retrouver déclassées par des documents moyennement bons dans plusieurs listes. Le bonus préserve la visibilité des véritables correspondances dominantes.

---

## Le pipeline complet de QMD query

Voici le flux exhaustif d'un appel `qmd query` :

**Étape 1 — Expansion de requête** : `qmd-query-expansion-1.7B` génère 2 variantes. On dispose de 3 requêtes — l'originale comptant double dans la fusion.

**Étape 2 — Recherche parallèle** : pour chacune des 3 requêtes, BM25 dans `documents_fts` et recherche vectorielle dans `vectors_vec` (après conversion de la requête en embedding avec `embeddinggemma-300M`). Résultat : 6 listes de résultats.

**Étape 3 — Fusion RRF** : k=60, poids double pour l'originale, bonus +0.05 pour les premiers rangs et +0.02 pour les deuxième et troisième de chaque liste individuelle. On conserve les **30 meilleurs candidats** pour le re-ranking.

**Étape 4 — Re-ranking** : `Qwen3-Reranker-0.6B` évalue chaque candidat par rapport à la requête originale. Score yes/no avec logprob de confiance. Normalisation par /10 pour obtenir 0 à 1.

**Étape 5 — Mélange position-aware** : ratios 75/25 pour les positions 1-3, 60/40 pour les positions 4-10, 40/60 pour les positions 11+.

**Étape 6 — Résultats finaux** : N meilleurs résultats après le mélange final, avec leurs scores, chemins, docids, et contextes documentaires.

### Les différentes commandes et leur sémantique

`qmd search` : BM25 pur uniquement. Très rapide, aucun modèle requis à l'exécution. Adapté pour les recherches par tokens exacts.

`qmd vsearch` : vectoriel pur. Nécessite les embeddings pré-générés. Pas d'expansion de requête, pas de re-ranking.

`qmd query` : le pipeline complet décrit ci-dessus. Le plus lent, le plus précis.

`qmd get <chemin>` : récupère un document entier par chemin relatif ou par docid (`#abc123`). Supporte la récupération à partir d'une ligne précise (`notes/meeting.md:50`) et un nombre maximum de lignes (`-l 100`). Si le chemin est approximatif, QMD propose des correspondances proches par fuzzy matching.

`qmd multi-get "pattern/*.md"` : récupère plusieurs documents en une seule commande, selon un pattern glob, une liste séparée par des virgules, ou une liste de docids. Un paramètre `--max-bytes` permet d'ignorer les fichiers dépassant une certaine taille.

`qmd embed` : génère les embeddings pour tous les documents indexés qui n'en ont pas encore. L'option `-f` force la re-génération de tous les embeddings existants.

`qmd update` : re-scanne les collections et ré-indexe les fichiers modifiés. L'option `--pull` permet de faire un `git pull` avant le re-scan, utile pour des repos distants.

`qmd status` : affiche la santé de l'index et le détail des collections avec leurs contextes associés.

---

## Le schéma complet de la base de données QMD

QMD maintient sa propre SQLite à `~/.cache/qmd/index.sqlite` (ou dans le répertoire XDG cache configuré). Son schéma :

`collections` : les répertoires indexés avec leur nom et leurs patterns glob pour filtrer quels fichiers inclure.

`path_contexts` : les descriptions textuelles associées aux chemins virtuels `qmd://...`. Quand QMD retourne un résultat, il inclut le contexte associé au chemin. Ce contexte est remonté dans chaque résultat et aide considérablement les agents LLM à jauger la pertinence d'un résultat avant de le lire en entier.

`documents` : contenu Markdown avec métadonnées. Chaque document a un `docid` — un **hash de 6 caractères** dérivé du contenu du fichier, utilisable directement dans `qmd get #abc123`. Le titre est extrait automatiquement (premier heading H1 ou nom de fichier si aucun heading).

`documents_fts` : table virtuelle FTS5 pour BM25 sur tous les documents.

`content_vectors` : chunks avec leur position dans le document original. Clé composite `(hash_document, sequence_chunk)`. Chaque chunk fait ~900 tokens. Le champ `pos` stocke la position en caractères dans le document original.

`vectors_vec` : table virtuelle sqlite-vec stockant les vecteurs pour la recherche rapide par proximité cosinus.

`llm_cache` : cache des réponses LLM — aussi bien les variantes de requête générées par l'expansion que les scores de re-ranking. Un couple (requête, document) scoré une fois ne sera jamais re-scoré si la même paire revient. Une requête expansée une fois ne sera jamais ré-expansée si elle revient à l'identique.

---

## Le système de contexte documentaire de QMD

QMD introduit un mécanisme de **contexte documentaire** qui n'existe pas dans la recherche classique. Ce sont des métadonnées descriptives attachées à des chemins virtuels dans les collections, ajoutées via `qmd context add qmd://notes "Notes personnelles et idées"`.

Ces contextes fonctionnent de manière **hiérarchique comme un arbre** : le contexte d'un répertoire parent s'applique à tous les fichiers enfants, sauf si un sous-répertoire a son propre contexte plus spécifique défini. Le contexte global s'applique à tout le corpus.

Chaque résultat de recherche remonte ce contexte au niveau du snippet retourné. Un agent qui reçoit des résultats voit donc non seulement le texte et les scores mais aussi la nature du répertoire dont vient le résultat. Cela lui permet de prendre des décisions de sélection bien plus informées — préférer un résultat venant de "Documentation de travail" à un résultat venant de "Vieilles notes personnelles" si la tâche en cours est technique, même si les deux ont des scores de pertinence proches.

---

## Les outils exposés à l'agent

### memory_search

Présenté à l'agent comme une **étape de rappel obligatoire**. Le prompt système d'OpenClaw indique explicitement à l'agent de chercher en mémoire avant de répondre à des questions sur des travaux antérieurs, des décisions, des dates, des personnes, des préférences, ou des tâches à faire.

L'outil retourne pour chaque résultat : le chemin du fichier, les numéros de lignes (début et fin du chunk), le score de pertinence, et un aperçu textuel du chunk **limité à ~700 caractères**. Des informations de citation précises sont incluses — chemin exact et numéros de lignes — pour que l'agent puisse référencer la source.

Ce que l'outil ne retourne **pas** : le contenu complet des fichiers. C'est intentionnel — on veut que l'agent ait juste assez pour décider si un résultat est pertinent, sans inonder le contexte.

Quand le backend QMD est actif, les snippets incluent un pied de page `Source: <chemin#ligne>` si `memory.citations = "auto"` (le défaut) ou `= "on"`. Si `memory.citations = "off"`, le chemin reste disponible pour l'agent en interne (pour `memory_get`), mais n'est pas inclus dans le texte du snippet.

### memory_get

Le suivi naturel de `memory_search`. Après avoir identifié des snippets pertinents, l'agent lit la section précise d'un fichier.

Paramètres : chemin de fichier, ligne de début optionnelle, nombre de lignes à lire optionnel. OpenClaw lit exactement cette plage de lignes et la retourne.

**L'impact sur la fenêtre de contexte est concret** : un fichier complet peut faire 2400 tokens. Une lecture ciblée via `memory_get` peut récupérer 180 tokens de contexte précisément localisé. Facteur d'économie : ~13x.

`memory_get` refuse de lire des fichiers en dehors de `MEMORY.md` et du répertoire `memory/` — restriction de sécurité pour empêcher l'agent de lire des fichiers arbitraires du système.

Quand un fichier n'existe pas (journal du jour pas encore créé), `memory_get` retourne gracieusement `{ text: "", path }` au lieu de lever une erreur. L'agent peut continuer sans try/catch.

Ce **two-step pattern** — chercher avec `memory_search`, lire avec `memory_get` — est entièrement délibéré et constitue le pattern central du système. La recherche retourne des snippets compacts pour trier ce qui est pertinent. La lecture ciblée récupère ensuite uniquement le contenu nécessaire, sans charger des fichiers entiers en contexte.

---

## Le post-traitement des résultats dans OpenClaw

### MMR : Maximal Marginal Relevance

Après la fusion pondérée, OpenClaw peut appliquer un re-ranking MMR pour éliminer les résultats redondants. Le problème qu'il résout : si 30 journaux quotidiens mentionnent tous "routeur Omada" dans des formulations quasi-identiques, une recherche retourne 5 snippets pratiquement identiques qui gaspillent des tokens de contexte en répétant la même information.

MMR construit itérativement un ensemble de résultats en maximisant à chaque étape : `λ × pertinence - (1-λ) × similarité_max_avec_déjà_sélectionnés`. On sélectionne le candidat avec le score le plus élevé, on l'ajoute à l'ensemble, et on recommence jusqu'à avoir N résultats.

La similarité entre deux chunks est calculée par **similarité de Jaccard sur le texte tokenisé** — chevauchement de vocabulaire, pas de distance vectorielle. Intentionnellement simple pour garder le post-traitement léger.

λ = 0.7 par défaut — légère préférence pour la pertinence avec une pénalité significative pour la redondance. λ = 1.0 est identique à un classement normal sans MMR (pertinence pure). λ = 0.0 est une diversité maximale sans regard pour la pertinence.

MMR est **désactivé par défaut**. Il est recommandé quand on observe des snippets répétitifs dans les résultats, notamment avec des journaux quotidiens qui répètent souvent les mêmes informations au fil des jours.

### Temporal Decay : décroissance temporelle

Sans décroissance, une note très bien rédigée de 6 mois peut avoir un excellent score sémantique et déclasser des notes récentes plus pertinentes sur le même sujet — simplement parce qu'elle est mieux formulée ou plus dense en information. La temporal decay applique un multiplicateur exponentiel basé sur l'âge : `scoreAjusté = score × e^(-λ × ageEnJours)` où `λ = ln(2) / halfLifeDays`.

Avec halfLifeDays = 30 (valeur par défaut) :

Aujourd'hui → multiplicateur 1.0 (aucune pénalité).

Il y a 7 jours → ~0.84.

Il y a 30 jours → 0.5 exactement (la moitié du score original).

Il y a 90 jours → ~0.125.

Il y a 180 jours → ~0.016.

Les fichiers **evergreen** ne sont jamais décayés : `MEMORY.md` et tous les fichiers non-datés dans `memory/` comme `memory/projets.md` ou `memory/réseau.md`. Ces fichiers contiennent des informations de référence durables qui doivent toujours être classées normalement, indépendamment de leur ancienneté.

La date utilisée est extraite du nom du fichier pour les journaux datés (`memory/YYYY-MM-DD.md`). Pour d'autres sources comme les transcriptions de session, c'est le `mtime` (date de modification) du fichier qui sert de référence.

La temporal decay est **désactivée par défaut**. Elle est recommandée pour les agents avec des mois de journaux quotidiens où les informations récentes sont généralement plus pertinentes que les anciennes.

---

## La synchronisation incrémentielle

OpenClaw utilise un **file watcher** qui monitore `MEMORY.md` et `memory/` en temps réel. Dès qu'une modification est détectée, un **debounce de 1,5 seconde** est appliqué avant de marquer l'index comme dirty et de déclencher la sync. Cela évite de re-indexer à chaque frappe quand un utilisateur édite un fichier.

Lors de la sync, OpenClaw compare le hash du contenu actuel de chaque fichier au hash stocké dans la table `files`. Si les hashes correspondent : le fichier est ignoré entièrement. Si différents : le fichier est découpé en chunks, chaque chunk est comparé à la cache d'embeddings par son hash de texte, les anciens chunks du fichier sont supprimés de toutes les tables (chunks, chunks_fts, chunks_vec), les nouveaux chunks avec leurs embeddings sont insérés. Le hash et le mtime du fichier sont mis à jour dans `files`.

Une **ré-indexation complète** est déclenchée si le fournisseur d'embeddings, le modèle, ou les paramètres de chunking changent. OpenClaw détecte ces changements via une empreinte de configuration stockée en métadonnées. La ré-indexation se fait dans une **base de données temporaire** avec échange atomique final — l'index n'est jamais dans un état incohérent, l'agent peut continuer à chercher dans l'ancien index pendant que le nouveau est en cours de construction.

Les transcriptions de session utilisent des **seuils delta** au lieu d'un file watcher, pour éviter de synchroniser à chaque message : par défaut, la sync se déclenche quand 100 000 octets ou 50 messages se sont accumulés depuis la dernière sync.

---

## Le backend QMD dans OpenClaw

Quand `memory.backend = "qmd"` est configuré, OpenClaw remplace son système de recherche interne par QMD comme sidecar externe. Les fichiers Markdown restent la source de vérité — OpenClaw continue d'y écrire. Mais toutes les opérations de recherche passent par le binaire QMD via des appels en ligne de commande.

OpenClaw crée un environnement QMD **isolé par agent** sous `~/.openclaw/agents/<agentId>/qmd/`, avec `XDG_CONFIG_HOME` et `XDG_CACHE_HOME` ajustés automatiquement :

Config : `~/.openclaw/agents/<agentId>/qmd/xdg-config`

Cache et modèles : `~/.openclaw/agents/<agentId>/qmd/xdg-cache`

Base de données SQLite : à l'intérieur du cache XDG ci-dessus.

Deux agents distincts ont chacun leur propre index QMD, leurs propres modèles chargés en mémoire, et leurs propres configurations.

Au démarrage, OpenClaw crée les collections QMD via `qmd collection add`, puis exécute `qmd update` (re-scan des fichiers modifiés) et `qmd embed` (génération des embeddings pour les nouveaux documents). Ces opérations se font **en arrière-plan par défaut** — elles ne bloquent pas le démarrage de la session de chat. Un rafraîchissement périodique toutes les 5 minutes maintient l'index à jour.

OpenClaw peut configurer quel mode de recherche QMD utiliser : `search` (BM25 pur), `vsearch` (vectoriel pur), ou `query` (pipeline complet). Si le mode sélectionné échoue sur la version installée de QMD, OpenClaw retente avec `qmd query`. Si QMD échoue entièrement (binaire manquant, erreur de parsing JSON, timeout), OpenClaw bascule sur son backend SQLite intégré — transparent pour l'agent, les outils `memory_search` et `memory_get` continuent de fonctionner.

Quand `memory.qmd.sessions.enabled = true`, OpenClaw exporte des transcriptions de session sanitisées (uniquement les tours user/assistant) dans `~/.openclaw/agents/<id>/qmd/sessions/`. QMD indexe ce répertoire comme une collection séparée. `memory_search` peut ainsi retrouver des conversations passées, pas uniquement des notes écrites explicitement.

Les snippets venant de collections QMD hors workspace apparaissent avec le préfixe `qmd/<collection>/<chemin-relatif>` dans les résultats. `memory_get` comprend ce préfixe et lit depuis la racine de la collection QMD correspondante.

La **scope de recherche** est configurable par type de session — on peut par exemple autoriser `memory_search` uniquement dans les conversations directes et le désactiver dans les canaux de groupe, pour des raisons de confidentialité des données mémoire.

---

## Le flush automatique avant compaction

Quand une session approche de sa limite de tokens, OpenClaw déclenche un **tour agentic silencieux** avant la compaction. Ce tour envoie un message à l'agent lui demandant d'écrire les informations durables dans ses fichiers mémoire avant que le contexte soit résumé et tronqué. Si l'agent n'a rien à sauvegarder, il répond `NO_REPLY` et rien n'est visible pour l'utilisateur.

Le seuil de déclenchement : par défaut, le flush se déclenche quand la session a moins de `contextWindow - reserveTokensFloor - softThresholdTokens` tokens restants — les valeurs par défaut sont 20 000 et 4 000, soit 24 000 tokens de réserve avant compaction.

Un seul flush par cycle de compaction, suivi dans `sessions.json`. Si la session s'exécute en mode workspace read-only ou sans accès workspace, le flush est simplement ignoré.

---

## La normalisation des scores

QMD normalise les scores de chaque backend différemment pour les rendre comparables dans le pipeline de fusion :

Scores BM25 bruts SQL (valeurs négatives par convention SQLite) → `Math.abs(score)`, plage résultante 0 à ~25+.

Distances cosinus vectorielles → `1 / (1 + distance)`, plage résultante 0.0 à 1.0.

Scores du re-ranker Qwen3 (0 à 10 nativement) → `score / 10`, plage résultante 0.0 à 1.0.

Les scores finaux après le pipeline complet de QMD s'interprètent ainsi :

0.8 à 1.0 : hautement pertinent — le document répond directement à la requête.

0.5 à 0.8 : modérément pertinent — le document est lié au sujet.

0.2 à 0.5 : partiellement pertinent — connexion indirecte.

0.0 à 0.2 : faiblement pertinent — à exclure dans la plupart des cas.

---

## La chaîne complète de bout en bout

**Écriture** → L'agent écrit dans `memory/2025-05-20.md`. Le file watcher détecte le changement. Après 1.5s de debounce, sync déclenchée. Hash du fichier comparé au hash stocké → différent. Découpage en chunks de 400 tokens avec 80 tokens de chevauchement. Pour chaque chunk : calcul du hash de texte, vérification dans `embedding_cache`. Cache hit : embedding réutilisé. Cache miss : embedding généré. Insertion dans `chunks_fts` et `chunks_vec`. Mise à jour du hash et mtime dans `files`.

**Recherche via OpenClaw (backend natif)** → L'agent appelle `memory_search("processus de déploiement")`. La requête est convertie en embedding. BM25 dans `chunks_fts` (24 candidats) et vectorielle dans `chunks_vec` (24 candidats) en parallèle. Scores BM25 normalisés par rang avec `1/(1+rang)`. Fusion pondérée 70% vecteur + 30% texte par identifiant de chunk. Filtrage à 0.35. Retour des N meilleurs : chemin, lignes debut/fin, score, snippet de 700 caractères.

**Recherche via QMD query** → L'agent appelle `memory_search` ou directement `qmd query`. Expansion de requête via `qmd-query-expansion-1.7B` → 3 requêtes (originale ×2). 6 recherches parallèles (3 requêtes × BM25 + vectorielle). Fusion RRF k=60 avec poids double pour l'originale et bonus top-rank +0.05/+0.02. 30 candidats pour `Qwen3-Reranker-0.6B`. Mélange position-aware : 75/25 pour positions 1-3, 60/40 pour 4-10, 40/60 pour 11+. Résultats finaux avec contextes documentaires intégrés.

**Lecture ciblée** → L'agent identifie un snippet pertinent dans `memory/projet-alpha.md` à la ligne 42. Il appelle `memory_get("memory/projet-alpha.md", startLine: 42, lineCount: 30)`. OpenClaw retourne exactement ces 30 lignes — ~180 tokens au lieu de ~2400 pour le fichier complet. Facteur d'économie : ~13x sur la fenêtre de contexte.