# Analyse Technique Exhaustive : Git-Context-Controller et l'Écosystème Aline / OneContext

Ce document présente une analyse détaillée du fonctionnement, de l'architecture technique et de la réalité opérationnelle du projet connu sous les noms de Git-Context-Controller (GCC), Aline et OneContext. L'objectif est de décortiquer précisément la mécanique de cette solution de gestion de mémoire pour agents IA.

## 1. Le Problème Fondamental : L'Amnésie et la Dégradation du Contexte

Les agents de codage basés sur les LLM (Large Language Models), tels que Claude Code, Gemini CLI ou Codex, font face à un goulot d'étranglement critique lors de l'exécution de workflows longs et complexes. Bien que les modèles récents disposent d'une fenêtre de contexte théorique allant jusqu'à un million de tokens, la fenêtre de contexte effective et optimale se situe en réalité entre 120 000 et 200 000 tokens.

Au fur et à mesure qu'une session se prolonge, l'accumulation de l'historique ralentit l'agent et augmente les coûts d'inférence. L'agent commence à perdre le fil de son raisonnement, répète des erreurs passées et oublie les tentatives précédentes. Pour contourner cela, les systèmes actuels utilisent deux stratégies imparfaites :
La première consiste à tronquer purement et simplement les anciens messages, ce qui détruit l'historique des décisions.
La seconde, utilisée par des outils comme Claude Code, consiste à compresser l'état du projet dans un fichier texte unique (souvent nommé `memory.md`). Cette approche par résumé écrase les détails granulaires du raisonnement étape par étape (les traces d'exécution). De plus, cette mémoire est éphémère et isolée : lorsqu'une session est fermée ou qu'un autre agent prend le relais sur une autre machine, le contexte est perdu, forçant l'utilisateur à réexpliquer continuellement l'état du projet.

## 2. La Mécanique Théorique : Le Framework Git-Context-Controller (GCC)

Pour résoudre ce problème, un papier de recherche introduit le Git-Context-Controller. Ce framework conceptuel élève la gestion du contexte d'un simple flux de tokens passif à un système de fichiers persistant, versionné et navigable, s'inspirant directement des systèmes de contrôle de version comme Git. L'agent interagit avec une structure de dossiers stricte via des commandes spécifiques.

### La Structure du Système de Fichiers
Le framework impose la création d'un répertoire racine nommé `.GCC/` qui organise la mémoire en trois niveaux de résolution :

*   **main.md** : Situé à la racine, ce fichier maintient la feuille de route globale du projet. Il contient l'intention de haut niveau, les jalons principaux et l'état de la planification partagée entre toutes les branches.
*   **branches/** : Un répertoire contenant des sous-dossiers pour chaque piste explorée. Chaque branche agit comme un espace de travail isolé permettant à l'agent de tester des hypothèses architecturales sans polluer la trajectoire principale. Chaque dossier de branche contient trois fichiers :
    *   **commit.md** : Un journal structuré des jalons. Il capture l'objectif de la branche, un résumé à gros grains de l'historique précédent, et une description détaillée de la contribution du commit actuel.
    *   **log.md** : La trace d'exécution à grain fin. Ce fichier enregistre en temps réel chaque cycle OTA (Observation-Thought-Action) de l'agent. C'est la mémoire brute de bas niveau.
    *   **metadata.yaml** : Un fichier structuré capturant le contexte architectural, tel que la structure actuelle des fichiers, les responsabilités des modules et les configurations d'environnement.

### Les Commandes Agentiques
Le framework expose quatre commandes que l'agent est instruit d'utiliser via son prompt système :

*   **COMMIT <summary>** : Invoquée lorsque l'agent détecte qu'il a atteint un jalon cohérent (ex: implémentation d'une fonction, passage d'un test). Cette commande met à jour le fichier `commit.md`, propose une révision du `main.md` si la feuille de route a évolué, et fige l'état sous forme de commit Git.
*   **BRANCH <name>** : Invoquée lorsque l'agent souhaite explorer une approche alternative. Elle initialise un nouveau dossier avec des fichiers `log.md` et `commit.md` vierges, isolant ainsi le nouveau raisonnement.
*   **MERGE <branch>** : Invoquée pour synthétiser les résultats d'une branche terminée dans la trajectoire principale. Elle fusionne les entrées des fichiers `commit.md`, combine les fichiers `log.md` en conservant des balises d'origine, et met à jour le `main.md`.
*   **CONTEXT <options>** : Permet à l'agent de récupérer l'historique à la demande. L'agent peut cibler sa requête avec des arguments tels que `--branch` pour lire un résumé, `--commit` pour lire une entrée spécifique, `--log` pour inspecter la trace brute, ou `--metadata` pour l'architecture.

## 3. L'Implémentation Technique Réelle : L'Architecture Aline / OneContext

La théorie du GCC est matérialisée par un outil logiciel distribué sous les noms de OneContext ou Aline (via les paquets `onecontext-ai` ou `aline-ai`). L'implémentation technique s'écarte de la simple manipulation de fichiers texte pour reposer sur une architecture logicielle robuste de type client-serveur hybride, fonctionnant en arrière-plan.

### Découverte des Sessions et Détection des Tours
Le système fonctionne de manière agnostique vis-à-vis des sessions. Il déploie un service d'observation (Watcher) qui scanne automatiquement les chemins connus sur la machine locale pour détecter l'activité des agents (par exemple, `~/.claude/projects/{project-name}/` pour Claude ou des répertoires spécifiques pour Codex). Les chemins des projets sont transformés pour le stockage interne (ex: `/Users/alice/MyApp` devient `-Users-alice-MyApp`).

La détection de l'activité repose sur un système de déclencheurs enfichables (TurnTrigger ABC) avec des implémentations spécifiques pour chaque plateforme (Claude, Codex, Gemini). Ce mécanisme détecte précisément quand un "tour" (turn) de conversation est terminé. Il extrait alors les informations du tour : le numéro, le message de l'utilisateur, l'horodatage, et génère un hash MD5 du contenu. Ce hash MD5 est crucial car il sert de mécanisme de déduplication pour empêcher l'importation multiple des mêmes données.

### Base de Données Locale et Gestion de la Concurrence
Toute la mémoire est persistée localement dans une base de données SQLite située dans `~/.aline/db/aline.db` (pouvant atteindre environ 3 Go). Le schéma de cette base de données est complexe, actuellement à la version 27, et comprend plus de 13 tables couvrant les sessions, les tours, les événements, les agents, les tâches, les verrous, les utilisateurs et les contextes d'agents.

Pour gérer l'exécution asynchrone et sécuriser l'accès aux données lorsque plusieurs agents ou processus tournent simultanément, le système intègre :
Une table de tâches durables (Job Queue) qui gère les opérations de synthèse (`turn_summary`, `session_summary`, `agent_description`). Cette file d'attente utilise un algorithme de "exponential backoff" avec un maximum de 10 tentatives, plafonné à 300 secondes.
Un système de verrouillage distribué (Distributed Locking) basé sur des baux (lease-based locks) avec un temps de vie (TTL) de 10 minutes, stocké dans une table `locks`, garantissant la sécurité multi-processus.

### Le Proxy Cloud et la Synthèse LLM
Contrairement à une approche purement locale, l'outil délègue la lourde tâche de résumer le contexte à un serveur distant géré par l'entreprise Aline. Ce choix architectural (Cloud-proxied LLM) permet de générer des résumés sans nécessiter de clés API locales de la part de l'utilisateur.

Pour protéger cette API cloud contre le spam lors d'une activité rapide de l'agent, le système applique un "debounce" strict de 10 secondes. Une fois les données envoyées au proxy, le LLM distant génère plusieurs niveaux d'information : des résumés par tour (titre et description), des résumés agrégés au niveau de la session, des descriptions de profils pour les entités "Agent", et des résumés d'événements formatés pour des plateformes de messagerie (avec des questions pré-générées).

### Le Moteur de Recherche et de Récupération
Lorsque l'outil est interrogé par un agent (via la commande `aline search` ou via le protocole MCP - Model Context Protocol), la recherche opère selon deux modes distincts sur la base SQLite locale :
Le premier mode est une correspondance exacte d'extraits (Exact snippet matching) qui renvoie des morceaux de code ou de dialogue précis.
Le second mode utilise FTS5 (SQLite full-text search) via une table virtuelle nommée `fts_events`. Cette table est maintenue à jour par des déclencheurs automatiques (triggers) lors des insertions, mises à jour ou suppressions.
Les résultats de ces recherches peuvent être filtrés de manière granulaire par ID de session, ID d'événement, ID de tour, ou par la portée de l'agent (via la variable d'environnement `ALINE_AGENT_ID`). Les requêtes peuvent également être affinées en utilisant des préfixes d'ID (les 8 à 12 premiers caractères).

## 4. La Réalité du Projet : État des Lieux et Contradictions

L'analyse des documents met en évidence un décalage significatif entre la présentation académique de la solution et sa distribution réelle, ainsi que des frictions opérationnelles.

### Le Statut "Closed Source"
Le papier de recherche indique que le code est publié sur un dépôt GitHub public (`github.com/theworldofagents/GCC`). L'analyse révèle que ce dépôt est en réalité vide de tout code source fonctionnel. Il ne contient qu'un fichier d'instructions pour installer des paquets précompilés. L'architecture décrite ci-dessus (le Watcher, la base de données SQLite complexe, et surtout le Cloud Proxy gérant les LLM) est entièrement fermée et propriétaire, contrôlée par l'entreprise Aline.

### La Confusion de la Nomenclature
Le projet souffre d'une fragmentation de ses noms qui complexifie l'identification de ses composants. La théorie s'appelle Git-Context-Controller (GCC). Le paquet npm d'installation s'appelle `onecontext-ai`. Le paquet Python sous-jacent et la commande CLI s'appellent `aline-ai` ou `aline`. L'entreprise derrière l'infrastructure cloud s'appelle Aline.

### Frictions avec la Mémoire Native des Agents
Une contradiction technique émerge lors de l'utilisation pratique avec des agents commerciaux existants. Des outils comme Claude Code possèdent déjà leur propre mécanisme de mémoire interne (le fichier `memory.md`). Lors de l'exécution, l'agent a naturellement tendance à interroger et à écrire dans sa propre mémoire native plutôt que d'utiliser l'outil externe Aline. L'utilisateur est fréquemment contraint d'intervenir manuellement dans le prompt (par exemple en écrivant "use aline" ou en ordonnant explicitement à l'agent d'ignorer sa mémoire native) pour forcer le routage du contexte vers la base de données SQLite d'Aline.

### Persistance et Partage du Contexte
Malgré ces frictions, l'architecture technique permet une véritable persistance découplée. Puisque la mémoire est gérée par un processus externe (le Watcher) et stockée indépendamment de la session de l'agent, elle survit à la fermeture du terminal. De plus, l'outil permet d'exporter ce contexte. Lorsqu'un développeur pousse son code sur GitHub, la mémoire accumulée par Aline peut être partagée. Un autre développeur, ou un autre agent sur une machine différente, peut récupérer ce contexte, interroger les sessions passées, ou même exposer cette mémoire via une URL publique agissant comme un chatbot interrogatif sur l'historique du projet.