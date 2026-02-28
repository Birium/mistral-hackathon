# Memory Manager — Vue d'ensemble du projet

## Le contexte

Ce projet est né d'un constat simple : la mémoire dans l'IA est aujourd'hui **locked**. Elle vit dans Claude Code, dans OpenClaw, dans Cursor, dans ChatGPT. Chaque outil a sa propre mémoire, dans son propre silo, incompatible avec le reste. Tu changes d'outil, tu repars de zéro. Tu veux utiliser deux outils ensemble, ils ne partagent rien.

Ce n'est pas un problème de qualité de mémoire. C'est un problème d'**architecture**.

Il y a déjà eu une première tentative avec un projet appelé MCPMEM — knowledge graphs, Neo4j, moteur de relations entre entités. L'idée était solide sur le papier. En pratique : trop complexe, trop atomique, pas utilisable au quotidien. Un knowledge graph, c'est un excellent outil pour ce qu'il fait. Mais un agent ne sait pas vraiment quoi faire avec. Tu envoies une requête, tu reçois un nœud, tu peux naviguer ses connexions — mais c'est trop déstructuré, trop fragmenté pour qu'un LLM construise une compréhension cohérente à partir de ça. Et pour un humain qui veut juste voir ce qu'il y a dans sa mémoire, c'est opaque.

Ce projet repart de zéro, avec tout ce qu'on a appris depuis.

---

## Ce qu'on veut construire

Un **service de mémoire autonome**, local-first, qui maintient une file structure de fichiers Markdown, et qui expose une interface simple pour y déposer des informations et en récupérer du contexte.

Deux opérations, c'est tout :

**→ Envoyer de l'information.** Tu donnes n'importe quoi en entrée — un résumé, une conversation, une note, un contexte de projet. Le service comprend, structure, et met la mémoire à jour. Tu reçois une confirmation que c'est intégré.

**→ Chercher du contexte.** Tu envoies une query. Le service te retourne du Markdown pertinent, extrait de ta mémoire, prêt à être utilisé où tu veux — dans un prompt, dans un terminal, dans une interface.

C'est un **outil à part entière**. Pas lié directement à un agent. Pas lié à un IDE. Pas lié à un outil en particulier. Il est sur le côté. Tu l'appelles quand tu en as besoin, depuis où tu veux. Tu poses une question depuis un CLI, tu reçois du Markdown. Tu l'appelles depuis un MCP, tu reçois du Markdown. C'est la même interaction, partout, toujours.

---

## Pourquoi des fichiers Markdown

C'est le choix central du projet, et il mérite d'être expliqué.

Les fichiers Markdown sont simples, portables, lisibles par un humain et par un LLM. Une file structure bien organisée, c'est quelque chose qu'un agent peut naviguer de façon **répétable et prévisible**. Il y a des patterns, des conventions, des endroits connus où chercher. Un agent qui connaît la structure sait exactement où aller chercher sans avoir à explorer à l'aveugle.

C'est ça la vraie puissance : la structure est toujours la même. Les informations dedans sont déstructurées et évoluent en permanence — mais la façon de les chercher, elle, est répétable. On peut construire des algorithmes de recherche précis, des checkpoints, des stratégies d'exploration. On sait qu'on cherche dans ce projet et pas dans les autres. On restreint le périmètre, on applique les bons outils (sémantique, keywords, navigation de fichiers), et on obtient du contexte pertinent sans avoir à tout lire.

Les fichiers sont aussi **accessibles directement**. Tu peux les ouvrir dans Obsidian, dans VS Code, dans un terminal. Tu vois exactement ce que le système a stocké. Pas de boîte noire. Pas d'interface propriétaire obligatoire pour consulter ta propre mémoire.

C'est un choix que l'écosystème est en train de converger vers. Claude Code a construit leur mémoire sur des markdown files. OpenClaw pareil. Letta Code aussi. Ce n'est pas un hasard — c'est simplement ce qui fonctionne.

---

## Pourquoi un process séparé et pas l'agent lui-même

Aujourd'hui, quand un agent veut retrouver quelque chose en mémoire, il utilise ses propres outils : grep, read, bash, tree. Il explore. Il lit des fichiers. Il cherche.

Le problème, ce n'est pas que ça coûte des tokens — même si c'est vrai. Le vrai problème, c'est que **tout ce travail d'exploration occupe de la place dans la context window de l'agent principal**. Et la context window, c'est sa capacité à réfléchir.

Un agent qui commence à saturer sa fenêtre de contexte devient de moins en moins efficace sur sa tâche principale. Vers 40 000 tokens occupés, la qualité du raisonnement commence à décliner. À 100 000, 120 000 tokens, l'agent n'arrive plus à tenir une pensée cohérente sur une tâche complexe. Si une partie significative de cette fenêtre est absorbée par la recherche en mémoire — lire des fichiers, les analyser, construire une représentation de ce qu'il y a dedans — il ne reste plus grand chose pour faire le vrai travail.

Et à ça s'ajoute un deuxième problème : un agent généraliste n'a pas les bons outils pour interagir avec une file structure de mémoire spécifique. Il peut faire du grep, mais il ne connaît pas la structure interne, les conventions, les endroits stratégiques où chercher. Il explore à l'aveugle alors qu'un process spécialisé, lui, connaît parfaitement la carte.

**L'idée, c'est la séparation des responsabilités :**

L'agent principal fait le travail — il code, il répond, il raisonne, il produit.

Le memory service, lui, est expert dans une seule chose : maintenir et requêter cette file structure. Il a des outils faits exprès pour ça, une connaissance intime de la structure, et il peut être invoqué comme un tool. L'agent principal l'appelle, récupère du contexte propre et pertinent, et continue sa tâche — sa context window à peine entamée.

---

## Local-first

La mémoire vit localement. Comme Obsidian. C'est un volume de fichiers sur ta machine, géré par un service qui tourne en local.

Les fichiers t'appartiennent. Tu peux les lire directement, les modifier, les versionner sur un repo privé. Rien n'est chez quelqu'un d'autre.

Si un jour tu veux accéder à ta mémoire depuis un outil cloud — ChatGPT, Gemini — tu exposes le service sur une URL publique. Si tu veux syncer ta mémoire pour ne pas la perdre, tu la verses dans un repo. Mais c'est optionnel. La base, c'est local.

---

## La connectivité

Ce service est conçu pour être **pluggé partout**. La même mémoire, accessible depuis tous les outils que tu utilises.

Via MCP (Model Context Protocol), n'importe quel agent compatible peut appeler le service — Claude Code, Cursor, un agent custom, un script. Via une API locale, n'importe quel programme peut interagir avec. Via un CLI, toi directement, sans aucun intermédiaire.

C'est ça le vrai differentiateur par rapport aux solutions existantes. Elles sont toutes locked dans un écosystème. Toi tu veux une mémoire qui te suit, peu importe l'outil que tu utilises aujourd'hui ou demain.

---

## Ce que cette mémoire contient

On a une intuition de ce qu'elle doit contenir — et cette intuition est déjà assez claire. Mais la structure exacte de la mémoire, comment elle s'organise, ce qu'elle stocke précisément et comment, c'est quelque chose qui n'est pas encore défini. C'est en fait l'une des questions centrales du projet.

Ce qu'on sait déjà, c'est que la mémoire doit pouvoir accueillir des choses très différentes :

Une **mémoire globale sur toi** — qui tu es, tes préférences, tes habitudes, la façon dont tu travailles, tes contraintes récurrentes. Des choses stables qui évoluent lentement mais qui doivent toujours être disponibles en contexte.

Des **projets** — chaque projet avec sa propre logique, son état, son historique, ce qui y a été décidé, ce qui reste à faire. Un projet peut être énorme ou minuscule. Créer une startup ou organiser un anniversaire. Développer une feature ou trouver un nouvel appart. Un projet est un projet.

Une **mémoire épisodique** — ce qui s'est passé, les interactions importantes, les idées qui ont émergé, les recherches qui ont été faites. Du contexte temporel qui a une valeur à un moment donné.

Des **tâches** — liées à un projet ou standalone, avec des priorités qui changent.

Mais au-delà de ces catégories intuitives, la vraie structure — comment les fichiers s'organisent, ce que contient chaque type de fichier, comment un agent sait où chercher quoi — c'est ce qui reste à définir et à tester.

---

## Ce qu'on ne fait pas

Ce n'est pas un product SAAS. Pas encore, et peut-être jamais. C'est d'abord un outil qui marche pour soi.

Ce n'est pas un agent autonome qui tourne en background et prend des initiatives. La mémoire se met à jour quand on lui demande, pas toute seule.

Ce n'est pas un project manager avec une interface élaborée. L'interface, si elle existe, est une fenêtre optionnelle sur ce qui se passe — pas le produit lui-même.

Et ce n'est pas un knowledge graph. Pas parce que les knowledge graphs sont mauvais — ils ont leur utilité pour d'autres choses. Mais pour cet usage, une file structure Markdown qu'un agent peut naviguer de façon structurée et prévisible est infiniment plus adaptée.

---

## Ce qui n'existe pas encore et pourquoi on le fait

Les solutions existantes ont toutes le même problème fondamental : elles sont locked. claude-mem fonctionne avec Claude Code et ses hooks. OpenClaw, c'est son propre écosystème. Letta Code, c'est leur infrastructure. OneContext, c'est un cloud proxy fermé.

Ce qu'elles font bien, on va le prendre. Les algorithmes de recherche hybride (sémantique + keywords). Le concept de progressive disclosure dans la navigation de fichiers. La séparation entre mémoire épisodique et sémantique. L'idée d'un agent observateur qui extrait du contexte structuré.

Mais tout ça, on va le mettre dans un outil qui **t'appartient**, qui tourne **chez toi**, et qui **se connecte partout**.

C'est ça qui n'existe pas.