# Search — Vue d'ensemble de la situation

## Contrainte fondamentale

Le vector search est non-négociable. C'est le cœur de la valeur du produit — retrouver de l'information par sens et non par mots-clés exacts. Toute solution qui l'élimine est hors-jeu.

## Ce qu'on ne veut pas

Les modèles locaux via GGUF et node-llama-cpp. QMD dans sa configuration par défaut télécharge ~2GB de modèles (embedding, reranker, query expansion) et les tourne via node-llama-cpp. Sur des petites machines c'est lent, lourd, et ça bloque le démarrage. La philosophie du projet c'est tout par API — OpenRouter couvre les embeddings, le reranking, n'importe quel modèle.

## Ce que QMD apporte réellement

QMD c'est trois choses distinctes :
- Un **algorithme de chunking markdown** qui découpe intelligemment aux breakpoints H1/H2/code fences
- Un **BM25 via SQLite FTS5** — aucun modèle, pur SQLite, millisecondes
- Un **pipeline vector + reranking** qui dépend des modèles locaux GGUF

Les deux premières pièces n'ont aucune dépendance modèle. La troisième est le problème.

Bima est en train de tester QMD sur sa machine pour évaluer ce que ça demande concrètement.

---

## Les options

### Option A — Tout construire en Python

Chunking H1/H2 maison, SQLite FTS5 pour le BM25, embeddings via OpenRouter stockés en SQLite, cosine similarity en Python, fusion RRF. Zéro dépendance externe autre que httpx.

**Pour** : stack 100% Python, cohérent avec le backend FastAPI, aucun subprocess, aucun fork à maintenir, contrôle total.

**Contre** : on recodie des choses qui existent déjà. Le chunking en particulier a des edge cases (code fences, overlap, fichiers très longs). C'est faisable mais c'est du travail — et du travail qui n'est pas spécifique au produit.

---

### Option B — QMD comme subprocess, couche vector maison

On utilise QMD uniquement pour son BM25 (aucun modèle impliqué, SQLite pur). Pour le vector search, on construit notre propre couche en Python avec OpenRouter pour les embeddings. On fusionne les deux avec RRF.

**Pour** : on récupère le chunking et le BM25 de QMD sans toucher aux modèles locaux. On reste sur API pour tout ce qui est ML.

**Contre** : Node/Bun comme dépendance dans un projet Python. Deux systèmes d'indexation à garder synchronisés — QMD doit chunker les fichiers pour le BM25, notre couche Python doit chunker les mêmes fichiers pour les embeddings, et les chunks doivent s'aligner pour que la fusion marche. C'est un problème de coordination permanent. Si les chunks divergent, la fusion mélange des pommes et des oranges.

---

### Option C — QMD tel quel, modèles locaux assumés

On prend QMD comme il est, modèles GGUF inclus. Le mode `fast` (BM25) reste sans modèle. Le mode `deep` (query expansion + vector + reranking) charge les modèles localement. C'est ce que Bima est en train de tester.

**Pour** : zéro travail d'intégration custom. QMD est prêt à l'emploi, bien documenté, les trois modes fonctionnent out of the box.

**Contre** : contraire à la philosophie API du projet. ~2GB de modèles à télécharger. node-llama-cpp qui peut ne pas builder proprement selon la machine. Performance dégradée sur petit hardware. Le premier `qmd query` peut prendre 30-60 secondes le temps de télécharger et charger les modèles.

---

### Option D — Fork QMD, remplacer les modèles par des API calls

Modifier le codebase Node de QMD pour remplacer les appels node-llama-cpp par des appels HTTP vers OpenRouter. Même logique, même pipeline, mais les modèles tournent en cloud.

**Pour** : on garde toute la logique QMD (chunking, fusion, reranking) avec des modèles API.

**Contre** : c'est le plus de travail. Il faut lire et comprendre le codebase QMD, localiser tous les points d'appel aux modèles, remplacer, tester. On maintient un fork d'un projet tiers. Si QMD évolue, on est découplés.

---

## Ce que le test de Bima détermine

Si QMD tourne correctement sur sa machine — install propre, `qmd search` fonctionnel, `qmd embed` qui tourne — ça valide que l'Option C est au moins techniquement viable. Si c'est galère à installer ou si les modèles locaux posent problème, ça ferme l'Option C et ça renforce l'argument pour A ou D.

La question ouverte reste : est-ce qu'on accepte les modèles locaux (Option C), ou est-ce qu'on investit du temps pour s'en passer (Option A ou D) ?