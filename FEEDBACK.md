# Rapport complet — Réécriture de la documentation Knower

Ce document liste tout ce qui doit changer, pourquoi, et où trouver l'information pour le faire. Il n'y a rien de superflu — chaque point est actionnable.

---

## 1. Restructurer les fichiers avant de réécrire quoi que ce soit

Le README actuel fait trop de choses en même temps. Il veut convaincre, expliquer l'architecture, détailler l'installation, lister les commandes CLI, documenter les intégrations MCP. Résultat : il ne fait aucune de ces choses vraiment bien. Les juges d'un hackathon ne vont pas installer le projet. Ils vont lire, regarder la démo, juger. Chaque ligne consacrée à `knower config vault` est une ligne qui ne sert pas la thèse.

**Ce qu'il faut faire :**

Créer deux fichiers distincts.

`README.md` — uniquement ce qui répond à "qu'est-ce que c'est, pourquoi c'est important, comment ça marche, pourquoi c'est différent". Le Quick Start de 3 lignes reste en haut — c'est parfait — mais il renvoie immédiatement vers `INSTALL.md` pour la suite. Tout le reste du README est de la conviction et de l'architecture.

`INSTALL.md` — tout ce qui est opérationnel : prérequis système, étapes d'installation détaillées, configuration, intégrations MCP (Mistral Vibe, Claude Code, Open Code), référence complète des commandes CLI, les deux modes de démarrage (dev/prod), les modèles QMD et leur cache. Tout ce qui répond à "comment je l'installe et je le configure". C'est précieux pour quelqu'un qui veut utiliser le projet — mais ce n'est pas ce qui convainc un juge en 5 minutes.

---

## 2. Reformuler la thèse centrale — elle doit être martelée dès le premier paragraphe

Le problème dans le README actuel : la thèse est là, mais elle est noyée au même niveau que le reste. Elle devrait commander tout le document. Tout le reste en découle.

La thèse, telle qu'elle est formulée dans `.llm/OVERVIEW.md` et `.llm/BUSINESS/BUSINESS.md` :

> La mémoire IA est un problème d'architecture, pas de qualité de modèle. Claude se souvient. Cursor se souvient. Mais leur mémoire est *locked* dans leur silo. Changer d'outil, c'est repartir de zéro. Utiliser deux outils en parallèle, ils ne partagent rien. Knower est le premier service qui découple la mémoire de l'outil.

Cette formulation dans BUSINESS.md est bien plus percutante que ce qui est dans le README actuel :

> "Ta mémoire est locked. Dans des silos qui ne t'appartiennent pas."

Et cette phrase-là dans OVERVIEW.md :

> "Ce n'est pas un problème de qualité de mémoire. C'est un problème d'architecture."

Ces deux formulations doivent être dans les premières lignes du README. Tout ce qui suit — l'architecture, la recherche, la compétition — vient appuyer cette thèse. Si un juge ne lit que le premier écran, il doit avoir compris l'essentiel.

---

## 3. Citer le modèle et expliquer la stratégie OpenRouter

Le README actuel ne cite pas le modèle utilisé. Pour un hackathon Mistral, c'est une lacune évidente.

**Ce qu'il faut écrire :**

Le modèle utilisé est `mistral-large-2512`, accessible via **OpenRouter**. Ce choix est délibéré et il faut l'expliquer sur deux niveaux.

Premier niveau, hackathon : Knower a été construit en poussant Mistral à fond. Les deux agents — update et search — tournent sur `mistral-large-2512`. Les tâches de routing ambigu, de détection de contradictions entre informations nouvelles et vault existant, et de génération de `review.md` avec un raisonnement exposé ont été testées intensivement sur ce modèle. Ce sont exactement les tâches où un context window large et un raisonnement solide font la différence. C'est une démonstration concrète de ce que Mistral peut faire sur des tâches agentiques longues et autonomes.

Deuxième niveau, architecture : passer par OpenRouter signifie que le modèle est une variable de configuration, pas une dépendance dure. Si demain un nouveau modèle Mistral est plus performant sur les tâches de routing et de structuration de mémoire — ou si un modèle concurrent prend l'avantage — Knower s'adapte en une ligne. La mémoire, elle, ne bouge pas. Le vault reste intact. Les projets, les décisions, l'historique — tout est là, indépendant du modèle.

Source : `SYSTEM_DESIGN.md` §"What it is", `agent.md` §"La context window — philosophie fondamentale".

---

## 4. OpenClaw — une section entière, pas une ligne dans un tableau

C'est le manque le plus grave du README actuel. OpenClaw apparaît dans un tableau de cinq lignes avec pour commentaire "Locked inside ChatGPT" — ce qui est factuellement inexact et montre que la comparaison n'a pas été pensée.

OpenClaw est un agent de mémoire pour le code. Il tourne avec des outils similaires — lecture de fichiers, navigation de structure, mémoire de projet. C'est le concurrent le plus proche de Knower dans le paysage. Ne pas en parler sérieusement est une erreur de positioning.

**Ce qu'il faut écrire :**

OpenClaw, claude-mem font tous des choses utiles. Le problème qu'ils partagent tous est le même : ils sont locked dans leur écosystème. OpenClaw fonctionne dans l'écosystème OpenClaw. claude-mem fonctionne via les hooks de Claude Code, exclusivement est leur infrastructure, leur cloud.

La différence architecturale de Knower est précise :

Knower est un **service indépendant** — pas un plugin, pas une feature d'un outil existant. Il expose du MCP et du REST. N'importe quel agent MCP-compatible peut l'appeler : Mistral Vibe, Claude Code, Open Code, un script custom, un agent maison. Il ne connaît pas l'outil qui l'appelle et il s'en fiche. Le vault est la source de vérité. Peu importe le client.

La formulation dans `.llm/OVERVIEW.md` est exacte sur ce point :

> "Ce n'est pas que les solutions existantes sont mauvaises. C'est qu'elles sont toutes locked dans un écosystème. Tu changes d'outil, tu repars de zéro."

Et dans `.llm/BUSINESS/BUSINESS.md` :

> "Aucune de ces mémoires ne se parle. Aucune ne te suit d'un outil à l'autre. Ta mémoire est locked dans des silos qui ne t'appartiennent pas."

Cette section doit citer OpenClaw par nom, expliquer ce qu'il fait bien, et montrer précisément pourquoi l'architecture Knower est différente. Les juges qui connaissent le paysage verront immédiatement que la réflexion est sérieuse.

---

## 5. Les trois moments magiques — ils doivent préparer la démo

L'`idea.md` définit trois moments précis qui prouvent que le produit fonctionne. Ces moments sont les points centraux de la démo, mais ils doivent aussi être dans le README pour préparer les juges à ce qu'ils vont voir.

**Moment 1 — Tu envoies du brut, c'est structuré automatiquement.** Tu déposes un vocal transcrit, une note rapide, un email. Le système comprend de quoi il s'agit, met à jour l'état du projet concerné, ajoute les tâches, logue les décisions. Le *file tree se met à jour en temps réel sous tes yeux* via SSE. Ce n'est pas une boîte noire — tu vois le travail se faire.

**Moment 2 — Tu poses une question, tu reçois du contexte réel.** "Où j'en suis sur le projet X ?" "Pourquoi on avait abandonné cette idée ?" Le système ne donne pas des généralités. Il traverse ta mémoire, assemble les pièces (décisions, état actuel, tâches), et te retourne du contexte réel tiré de ce que tu lui as donné — des décisions datées, des entrées de changelog, un state à jour.

**Moment 3 — Le système doute, il te le dit complètement.** Quand une information est trop ambiguë pour être routée avec certitude, un item apparaît dans l'Inbox. Dans cet item : tout le raisonnement de l'agent exposé. Ce qu'il a cherché, dans quels projets, ce qu'il a trouvé ou pas trouvé, ce qu'il propose, et la question précise qu'il pose. L'utilisateur ne réexplique pas depuis zéro — il complète un raisonnement exposé. La friction est volontaire, minimale, et utile.

Ces trois moments doivent être nommés et expliqués dans le README, pas comme une liste de features — comme une narration de ce que ça change concrètement. Quand le juge voit ensuite la démo, il sait exactement ce qu'il regarde et pourquoi c'est significatif. Sans cette préparation, la démo risque de ressembler à "un agent qui écrit des fichiers markdown", ce qui n'est pas du tout ce que c'est.

Source : `idea.md` §"Ce que le MVP doit démontrer", `interface.md` §"Vue activité", §"Vue inbox".

---

## 6. Renforcer les citations de recherche — liens et explication des résultats

Le README actuel cite trois sources mais ne les explique pas et ne les lie pas. Pour des juges qui connaissent la littérature, c'est une occasion manquée.

**Stanford 2025** — lien : `https://youtu.be/tbDDYKRFjhk?si=As1sDw1eBTdOylKz`

Ce qui est dans cette étude (n=136 équipes, 27 entreprises) : le gain de productivité IA chute drastiquement sur des tâches brownfield complexes par rapport aux tâches greenfield simples. La raison centrale est la gestion du contexte — plus la tâche est complexe, plus l'agent doit naviguer du contexte existant, plus la context window se sature, moins l'agent peut raisonner. C'est *exactement* ce que Knower résout : il sort le travail de recherche de contexte de la context window de l'agent principal.

**NoLiMa Benchmark** — lien : `https://arxiv.org/pdf/2409.15152`

Ce que ce paper montre : les performances des modèles dégradent avec la longueur du contexte. Ce n'est pas une question de capacité théorique — en pratique, plus le contexte est long, moins le modèle est précis. La dégradation n'est pas linéaire et elle est plus prononcée quand l'information pertinente est noyée dans du contenu non pertinent — exactement ce qui se passe quand un agent charge tout un vault pour trouver une décision.

**Needle in a Haystack** — lien : `https://arxiv.org/pdf/2407.01437`

Ce que ce paper montre : la précision de retrieval s'effondre à grande profondeur de contexte — y compris sur des modèles qui annoncent 200K tokens. Ce n'est pas parce qu'un modèle *peut* tenir 200K tokens en contexte qu'il retrouve avec précision une information enfouie à 150K tokens. Ce benchmark est maintenant une référence standard pour qualifier les limites de la context window en pratique.

Ces trois résultats convergent vers la même conclusion : charger de la mémoire directement dans la context window de l'agent principal n'est pas seulement inefficace en tokens — c'est quantifiablement dommageable à la qualité du raisonnement. Knower sépare les responsabilités pour que la context window de l'agent principal soit libre pour le travail réel. Ce n'est pas un choix de confort, c'est une décision architecturale fondée sur des données.

Source : `agent.md` §"La context window — philosophie fondamentale".

---

## 7. Remonter les insights architecturaux profonds — ils prouvent la maturité de conception

Plusieurs éléments de l'architecture Knower montrent une réflexion sérieuse qui ne transparaît pas du tout dans le README actuel. Les juges techniques verront immédiatement la différence.

**Le contexte mental des agents** — défini dans `.llm/MVP/agent.md`

L'agent de update se pose une seule question en permanence : *"Où est-ce que je range cette information ?"*. L'agent de search se pose une seule question : *"Qu'est-ce que l'utilisateur a besoin de savoir ?"*. Ce n'est pas un détail d'implémentation — c'est ce qui fait que les agents sont autonomes sans être erratiques. Le system prompt n'est pas de la configuration technique, c'est le contrat entre le développeur et l'agent.

**L'économie des tokens — append sans lecture préalable** — détaillé dans `.llm/MVP/agent.md` et `.llm/MVP/tools/append.md`

Sur un changelog de 300 jours (potentiellement 50K à 60K tokens), ajouter une nouvelle entrée sans charger l'historique existant n'est pas une optimisation marginale. C'est la différence entre une opération qui coûte 60 tokens et une qui coûte 60K tokens. Le tool `append` existe précisément pour ça : il insère un bloc en tête de fichier sans jamais ouvrir le contenu existant. C'est de l'architecture au service de la scalabilité, pas de la micro-optimisation.

**La thèse centrale sur les tâches de mémoire** — dans `.llm/MVP/agent.md`

Les tâches de mémoire sont fondamentalement différentes des tâches de code en termes de tolérance au contexte. Un agent qui génère du code voit ses performances dégrader au-delà de 128K à 200K tokens en contexte — parce que la précision syntaxique requise est extrême. Un agent qui route de l'information, lit du markdown structuré, écrit des changelogs — ses tâches sont beaucoup plus tolérantes. Charger plus de contexte le rend *meilleur*, pas pire. C'est la thèse qui justifie que Knower se permette d'être généreux sur les tokens à chaque session tout en restant dans un budget de 200-300K.

**Le vault comme structure connue intimement** — ce point est développé en profondeur dans la section 9 "Why Markdown". L'inbox avec raisonnement exposé est traité dans la section 10 dédiée.

---

## 8. L'analogie Jarvis et le cadre narratif "mémoire d'action"

Le `BUSINESS.md` a un cadre narratif puissant qui n'est utilisé nulle part dans le README.

**L'analogie Jarvis** est immédiatement compréhensible et elle articule exactement la différence entre ce que fait Knower et ce que font les outils actuels. Tony Stark sort d'une réunion, dit en marchant :

> *"Jarvis, le client veut finalement l'option B, on abandonne l'API externe, livraison fin mars."*

Intégré. Structuré. Tout le reste mis à jour en conséquence. Jarvis ne demande pas "c'est quel projet déjà ?" — il sait. Il ne dit pas "pouvez-vous réexpliquer le contexte ?" — il a le contexte. Cette image fait comprendre la proposition de valeur en 10 secondes.

**La notion de "mémoire d'action" versus "mémoire passive"** est aussi absente du README actuel. Knower ne retient pas des préférences ou des snippets (comme Claude memory ou ChatGPT memory). Il maintient une mémoire structurée et complète qui permet à l'IA qui l'appelle d'agir avec le contexte complet — décisions, état actuel, historique, tâches. C'est une distinction importante qui sépare Knower des solutions de "preferences storage".

Ces éléments de cadrage appartiennent au début du README, avant la partie technique. Ils donnent aux juges la bonne grille de lecture pour tout ce qui suit.

Source : `BUSINESS.md` §"Ce que tu veux, c'est Jarvis", §"Knower — une mémoire d'action".

---

## 9. Renforcer "Why Markdown" — l'argument de fond manque

La section actuelle du README est correcte mais incomplète. Elle dit que le markdown est lisible, portable, et que l'écosystème converge vers ça. Vrai. Mais ce n'est pas le vrai argument.

Le vrai argument est dans `.llm/OVERVIEW.md` :

> *"La structure est toujours la même, les informations dedans sont déstructurées et évoluent — mais la façon de les chercher est répétable."*

C'est ce qui distingue Knower d'un Google Drive avec un chatbot branché dessus. Le chatbot tombe sur les fichiers à l'aveugle et perd les connexions entre projets. Un agent qui connaît la structure du vault sait qu'un `state.md` est une photo instantanée volatile, qu'un changelog est H1/jour H2/entrée newest-first, que les tâches complétées disparaissent de `tasks.md` et deviennent des événements dans le changelog. Il ne *découvre* pas la structure à chaque session — il la *connaît intimement* dès le démarrage parce qu'elle est définie une fois dans le system prompt. C'est une décision architecturale fondamentale, pas un choix de format de fichier.

Cette distinction doit être explicite dans le README. Sinon les juges voient "des fichiers markdown" et pensent "Obsidian avec une couche IA". Ce n'est pas ça. C'est une mémoire structurée dont la structure elle-même est le langage que l'agent parle couramment dès le premier appel tool.

Source : `.llm/OVERVIEW.md` §"Pourquoi des fichiers Markdown", `.llm/MVP/vault.md` §structure complète, `.llm/MVP/agent.md` §"Le system prompt — le contrat avec l'agent".

---

## 10. Le système inbox est une feature originale et elle est invisible

L'inbox est l'une des décisions les plus réfléchies du projet et le README ne lui consacre pas une seule phrase significative.

Voici ce qui est original : quand l'agent de update ne peut pas router une information avec confiance, il ne la perd pas, il ne la range pas au mauvais endroit, et il ne pose pas de question au milieu de sa boucle d'exécution. Il crée un folder dans `inbox/` avec tous les fichiers d'input originaux et un `review.md` qui expose son raisonnement complet — ce qu'il a cherché dans quels projets, ce qu'il a trouvé ou pas trouvé, ce qu'il propose comme routing, et la question précise qu'il pose à l'utilisateur.

Ce que ça résout concrètement : l'utilisateur qui répond n'a pas à réexpliquer depuis zéro. Il lit un raisonnement déjà construit et il complète. La réponse est envoyée avec un `inbox_ref` qui identifie le folder, l'agent lit le `review.md` de la session précédente pour reprendre là où il en était, route les fichiers, supprime le folder, et logue dans `changelog.md`. Deux sessions distinctes, un raisonnement continu.

C'est une solution élégante au problème classique des agents qui soit bloquent sur les cas ambigus, soit font des choix silencieux qui corrompent la mémoire. Elle mérite une explication dans le README, pas juste une mention dans la liste de features.

Source : `.llm/MVP/vault.md` §"`inbox/`", `.llm/MVP/agent.md` §"Cas spécial — inbox_ref", `.llm/MVP/interface.md` §"Vue inbox".

---

## 11. L'argument "separate process" manque de données concrètes

Le README dit qu'un agent qui cherche en mémoire avec ses propres tools remplit sa context window et devient moins efficace pour sa tâche principale. C'est l'argument central pour justifier Knower comme service séparé. Mais il est posé sans chiffres.

Les trois recherches citées (Stanford 2025, NoLiMa, Needle-in-Haystack) viennent directement appuyer cet argument — elles sont développées dans la section 6 avec leurs conclusions exactes et leurs liens. Cette section doit faire référence à ces données et expliciter la conséquence architecturale :

Charger de la mémoire directement dans la context window de l'agent principal n'est pas seulement inefficace en tokens — c'est quantifiablement dommageable à la qualité du raisonnement (voir section 6 pour les trois sources convergentes). Knower sépare les responsabilités pour que la context window de l'agent principal soit libre pour le travail réel. Ce n'est pas un choix de confort, c'est une décision architecturale fondée sur des données.

Source : `.llm/MVP/agent.md` §"La context window — philosophie fondamentale", `.llm/OVERVIEW.md` §"Pourquoi un process séparé".

---

## 12. La token economy des agents n'est jamais mentionnée

L'`agent.md` contient une section entière sur la philosophie du context window qui est intellectuellement très solide et qui n'apparaît nulle part dans le README. Le point central : les tâches de mémoire sont fondamentalement différentes des tâches de code en termes de tolérance au contexte. Un agent de code à 128k+ tokens voit sa précision syntaxique se dégrader. Un agent de mémoire à 700k tokens comprend encore la structure globale, les projets, les décisions — et peut écrire une entrée de changelog de 3 lignes avec une précision quasi parfaite. La nature de la tâche change ce qui est possible.

Cette distinction justifie les choix de design des outils : `append` sans lecture préalable (un changelog de 300 jours peut faire 60k tokens — `append` insère en top sans jamais ouvrir le fichier), `read` avec `head` et `tail` (on lit les 2k premiers tokens d'un changelog pour avoir les entrées récentes, pas les 60k), `search` pour des chunks ciblés avant de décider si on a besoin du fichier entier.

Ce n'est pas de l'optimisation marginale. C'est ce qui permet à un agent de gérer des vaults de centaines de milliers de tokens en restant sous 200-300k tokens de contexte actif par session. Et ça montre que le projet a été pensé comme un système durable, pas comme un prototype.

Ce niveau de réflexion sur les coûts opérationnels mérite au moins un paragraphe dans le README.

Source : `.llm/MVP/agent.md` §"La context window — philosophie fondamentale", §"Les outils d'optimisation".

---

## 13. Le scénario cross-tools n'est jamais rendu concret

Le diagramme "Knower as a Hub" est là et il est bien fait. Mais le README ne raconte jamais le scénario concret qui prouve la thèse — celui où un utilisateur utilise Knower avec deux outils différents sur le même projet, simultanément.

Le scénario type : tu travailles dans Mistral Vibe sur une feature. Knower injecte via MCP le contexte du projet — décisions d'architecture, contraintes, état actuel. Tu codes. Tu commutes vers Claude Code pour un debug. Knower injecte le même contexte depuis le même vault. Tu n'expliques rien à Claude Code. Le vault est la source de vérité unique, les deux agents accèdent au même endroit, et quand l'un met à jour quelque chose, l'autre le verra à la prochaine session.

Ce n'est pas une hypothèse — c'est exactement ce que le système est conçu pour faire, avec le MCP server exposé sur `/mcp` et le vault unique. Le README devrait narrer ce scénario en 4-5 lignes avant les sections MCP Integration. C'est la démonstration la plus directe de ce que "one memory, every tool" signifie en pratique.

Source : `.llm/MVP/archi.md` §invariants, `.llm/MVP/infra.md` §"Le MCP server", `README.md` §"Connectivity".

---

## Ce qui fonctionne et doit être protégé

Le Quick Start de 3 lignes en haut est parfait — ne le touchez pas. Les schémas (silo problem, hub diagram, QMD pipeline, Stanford study) sont visuellement forts et ancrent les arguments dans des données réelles. La section QMD avec les trois modèles locaux et leurs rôles est un différenciateur technique solide — peu de projets font de la search hybride locale avec reranking, et le fait que tout soit offline est une feature en soi. La table des tools avec update/search access est claire et montre la séparation de responsabilités au premier coup d'œil.

---

## Structure recommandée des fichiers

**README.md** : vision, thèse, problème, positionnement contre l'existant (OpenClaw inclus), les trois moments magiques, architecture haut niveau, quick start 3 lignes, lien vers INSTALL.md. Pas de CLI reference, pas de tableaux de commandes, pas de MCP config détaillée.

**INSTALL.md** : tout le reste — install complète, MCP integration par outil (Mistral Vibe, Claude Code, Open Code), CLI reference complète, modes dev/prod, config.