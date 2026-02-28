# Vision & Démonstration — Knower MVP

Ce document définit l'intention derrière le MVP. Il explique le problème précis qu'on cherche à résoudre avec cette première version et les moments clés qui doivent prouver que la solution fonctionne.

---

## Le problème ciblé par le MVP

Aujourd'hui, quand tu utilises l'IA (Claude, ChatGPT, Cursor), tu dois systématiquement réexpliquer ton contexte. Tes projets, tes décisions passées, tes contraintes actuelles sont éparpillés dans des notes, des vocaux, des emails ou simplement dans ta tête. 

La conséquence : tu perds un temps fou à re-contextualiser l'IA à chaque session, tu oublies des détails cruciaux, et tu obtiens des réponses génériques parce que l'IA ne connaît pas la réalité de ce que tu construis.

Le MVP s'attaque directement à ce problème : **créer une mémoire d'action qui te suit**. Un endroit unique où tu déposes ton contexte en vrac, et où un système intelligent se charge de le structurer pour qu'il soit toujours prêt à être utilisé par toi ou par tes outils IA.

---

## Ce que le MVP doit démontrer

Le succès de ce MVP ne se mesure pas au nombre de features, mais à sa capacité à délivrer trois moments "magiques" qui prouvent la thèse du produit :

**1. Tu envoies de l'information brute → elle est structurée automatiquement.**
Tu déposes un vocal transcrit, une note rapide ou un email sans te soucier de la mise en forme ou du classement. Le système comprend de quoi il s'agit, met à jour l'état du projet concerné, ajoute les tâches, logue les décisions. Le file tree se met à jour en temps réel sous tes yeux. Ce n'est pas une boîte noire, tu vois le travail se faire.

**2. Tu poses une question → tu reçois du contexte réel tiré de ta mémoire.**
Tu demandes "Où en est-on sur le projet X ?" ou "Pourquoi a-t-on abandonné cette idée ?". Le système ne te donne pas des généralités. Il traverse ta mémoire, assemble les pièces du puzzle (décisions, état actuel, tâches) et te construit une réponse précise basée uniquement sur ce que tu lui as confié.

**3. Le système a un doute → il te le dit clairement.**
Quand une information est trop ambiguë pour être rangée avec certitude, le système ne la perd pas et ne la range pas au hasard. Un item apparaît dans ton Inbox. Le système t'expose son raisonnement ("J'ai cherché X, je n'ai pas trouvé Y, je propose Z"). Tu confirmes ou corriges avec une simple réponse. La friction est volontaire, minimale et utile.

---

## La promesse

La valeur fondamentale de ce MVP réside dans le transfert de la charge mentale. 

Tu n'as plus besoin d'être discipliné. Tu n'as plus besoin de maintenir des dossiers parfaits ou des documents de référence à jour. **Tu te contentes de déposer de l'information et de demander du contexte.** Le système s'occupe de toute la charge de maintenance, de structuration et de recherche.