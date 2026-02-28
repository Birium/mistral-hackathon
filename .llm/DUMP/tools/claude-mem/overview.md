# `claude-mem` — Overview

## Le Problème

Les LLMs n'ont pas de mémoire persistante. Chaque session repart de zéro. Pour un agent de code comme Claude Code, ça signifie qu'il ne se souvient pas du bug corrigé la semaine dernière, de la décision architecturale prise hier, ou du refactor en cours ce matin.

La solution naïve — coller tout l'historique de chat dans le contexte — ne scale pas. Trop de tokens, trop de bruit.

## Ce que fait `claude-mem`

`claude-mem` ne sauvegarde pas les conversations. **Il sauvegarde la connaissance extraite des conversations.**

La distinction est fondamentale : au lieu de stocker "ce qui a été dit", il stocke "ce qui a été appris et pourquoi".

## Comment ça se plug

`claude-mem` s'installe comme un plugin Claude Code en deux commandes. Il n'y a aucun fichier de config à toucher, aucune API key à gérer.

Une fois installé, il s'intègre via des **lifecycle hooks** de l'IDE :
- **SessionStart** — initialise la session mémoire
- **PostToolUse** — déclenché après chaque action de l'agent (lecture de fichier, exécution bash, écriture de code...)
- **Stop** — génère un résumé global quand l'agent a fini de répondre

Ces hooks envoient les données à un **worker Node.js qui tourne en arrière-plan** sur `localhost:37777`. Ce worker est invisible et non-bloquant : si il tombe, l'IDE continue de fonctionner normalement.

## Ce qui se passe en background

À chaque action de l'agent principal, le worker réveille un **Agent Observateur** (un second LLM) qui analyse l'action et en extrait une observation structurée :

- Le **type** de l'action (`bugfix`, `feature`, `refactor`, `decision`, `discovery`)
- Un **titre** et un **résumé narratif** de ce qui s'est passé
- Des **faits concrets** extraits (ex: "JWT expire après 24h")
- Les **fichiers touchés**
- La **raison** derrière l'action

Ces observations sont persistées localement dans deux bases :
- **SQLite** — source de vérité, stocke toutes les métadonnées
- **ChromaDB** — base vectorielle pour la recherche sémantique

En fin de session, l'Agent Observateur génère un **résumé global** : ce qui a été investigué, découvert, complété, et les prochaines étapes suggérées.

## Comment la mémoire revient

À la session suivante, les observations pertinentes sont réinjectées automatiquement dans le contexte via :
- Le fichier `CLAUDE.md` à la racine du projet (lu automatiquement par Claude Code)
- Des **outils MCP** que l'agent peut appeler explicitement

Les types de recherche disponibles :
- **Structurée** — par type (`bugfix`, `decision`...), par fichier, par date
- **Sémantique** — en langage naturel ("comment est gérée l'auth ?")
- **Hybride** — combinaison des deux pour des résultats précis et pertinents

L'agent peut d'abord récupérer un index compact (~50 tokens/résultat), puis aller chercher le détail complet uniquement sur les observations qui l'intéressent. Ce système de **progressive disclosure** fait que `claude-mem` consomme ~10x moins de tokens qu'un historique brut.

## En une phrase

`claude-mem` est un agent observateur asynchrone qui s'accroche aux hooks de l'IDE, transforme chaque action de l'agent principal en connaissance structurée persistante, et la restitue intelligemment à n'importe quelle session future.

---

> Pour comprendre l'implémentation technique en détail : voir [`HOW-IT-WORKS.md`](./HOW-IT-WORKS.md)