# Système de Mémoire des Agents IA — Documentation Complète
### Étude de cas : OpenClaw

> **Note sur les sources :** Ce document combine trois niveaux de sources.
> - ✅ **Doc officielle** OpenClaw
> - 📹 **Blog/YT** de Damian Galarza (analyse approfondie du système)
> - 🗂️ **Diagrammes** fournis dans la présentation

---

## Partie 1 — Fondations Théoriques

### 1.1 Le Problème de Base : Les LLMs sont Stateless

Les modèles de langage n'ont **aucune mémoire entre les appels**. Ce qui ressemble à une conversation n'est en réalité qu'une **fenêtre de contexte de plus en plus longue** qui est renvoyée intégralement à chaque nouveau message.

Chaque tour de conversation ajoute :
- Le message de l'utilisateur
- La réponse du modèle
- Les résultats des tool calls

Ce contexte grossit à chaque échange, et il est **entièrement recréé** à partir de zéro à chaque nouvelle session. Sans système de mémoire explicite, l'agent ne sait pas qui tu es, ce dont vous avez parlé hier, ni les décisions que vous avez prises ensemble.

---

### 1.2 La Taxonomie de la Mémoire Agentique
#### *(Framework Google — whitepaper "Context Engineering: Sessions & Memory", novembre 2025)*

📹 C'est la meilleure grille de lecture pour structurer ce qu'un agent doit retenir. Google identifie **trois types de mémoire** qui, ensemble, forment la mémoire complète d'un agent.

---

#### 🔵 Mémoire Épisodique
**Question clé : "Que s'est-il passé lors de nos dernières interactions ?"**

Ce sont les événements et interactions. Le contexte temporel d'une conversation passée. Si tu as passé une session à débugger un webhook, la mémoire épisodique permet à l'agent de savoir ça lors de la session suivante, sans que tu aies à le réexpliquer.

Exemples :
- "Hier on a discuté de la migration vers Redis"
- "La semaine dernière tu as refactorisé le module d'auth"
- "On a décidé d'abandonner l'approche GraphQL pour cette feature"

Caractéristiques : **temporelle, événementielle, se périme avec le temps.**

---

#### 🟢 Mémoire Sémantique
**Question clé : "Que sais-je sur cet utilisateur / ce projet ?"**

Ce sont les faits stables et les préférences. Les informations qui ne changent pas d'une session à l'autre ou qui évoluent lentement. C'est la connaissance de fond qui rend l'agent utile dès les premiers mots d'une conversation.

Exemples :
- "Utilise TypeScript"
- "Préfère le dark mode"
- "Travaille sur un projet d'API REST avec Node.js"
- "Utilise Vim keybindings"
- "A migré vers Cursor"

Caractéristiques : **stable, factuelle, toujours pertinente.**

---

#### 🟡 Mémoire Procédurale
**Question clé : "Comment est-ce qu'on accomplit cette tâche ?"**

Ce sont les workflows et les routines apprises. La compréhension qu'a l'agent de tes processus spécifiques.

Exemples :
- "Le processus de déploiement passe par X, Y, Z"
- "Les PR doivent être reviewées selon ce checklist"
- "Les tests s'exécutent avec cette commande avant chaque commit"

Caractéristiques : **procédurale, apprise, spécifique au contexte de travail.**

---

### 1.3 Ce qui Rend un Système de Mémoire Efficace
#### *(Principes issus du blog/YT)*

Avoir un endroit pour stocker les informations ne suffit pas. Trois défis doivent être résolus :

#### Problème 1 : L'Extraction (Qu'est-ce qui vaut la peine d'être retenu ?)
Toutes les informations d'une conversation ne méritent pas d'être persistées. Les détails banals, les hésitations, les formulations intermédiaires n'ont pas de valeur. Un bon système de mémoire fonctionne comme la mémoire humaine : on ne retient pas chaque mot d'une conversation, on retient les **faits clés et les décisions importantes**.

Le système doit appliquer un **filtrage ciblé** pour ne garder que ce qui est réellement utile lors des sessions futures.

---

#### Problème 2 : La Consolidation (Comment éviter la redondance ?)
📹 Scénario concret :
- Session 1 : l'utilisateur dit *"Je préfère le dark mode"*
- Session 3 : l'utilisateur dit *"J'aime le dark mode"*
- Session 7 : l'utilisateur dit *"Je suis passé au dark mode"*

Sans consolidation, ces trois phrases coexistent en mémoire comme trois entrées distinctes disant la même chose. La mémoire devient du bruit.

Un bon système **fusionne** ces trois entrées en une seule : `"L'utilisateur préfère le dark mode"`.

---

#### Problème 3 : La Mise à Jour (Comment gérer le changement ?)
Ce qui est vrai aujourd'hui ne l'est pas forcément demain. Si l'utilisateur passe du dark mode au light mode, le système doit **écraser** l'ancienne entrée, pas en ajouter une contradictoire. Sans gestion des mises à jour, la mémoire devient **bruyante et contradictoire** avec le temps, ce qui est pire que pas de mémoire du tout.

---

### 1.4 Les Deux Grandes Catégories de Stockage
📹 Avant d'entrer dans l'implémentation concrète, il faut distinguer les deux espaces où vit l'information :

**La Session (le bureau)**
L'historique de la conversation en cours. Tout y est visible, tout est accessible. Mais l'espace est limité (la fenêtre de contexte), et quand la session se termine, tout ce qui n'a pas été rangé disparaît.

**La Mémoire Long-Terme (le classeur)**
Les fichiers persistants sur disque. Organisés, catégorisés. Ce qui survit à la fin d'une session et est rechargé au démarrage de la suivante.

Le vrai problème de la mémoire agentique, c'est de **déplacer les bonnes choses du bureau vers le classeur, au bon moment.**

---

## Partie 2 — La Session et la Compaction

### 2.1 Cycle de Vie d'une Session
✅ Une session est l'historique complet d'une conversation avec le LLM. À chaque nouveau message, cet historique est passé intégralement au modèle. Plus la conversation avance, plus le contexte grossit.

L'état de chaque session est stocké sur le gateway :
- **Store** : `~/.openclaw/agents/<agentId>/sessions/sessions.json` (map sessionKey → metadata)
- **Transcript** : `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`

Chaque session a un `sessionKey` (ex: `agent:main:main` pour la session principale DM) et un `sessionId` unique.

---

### 2.2 La Compaction
✅ Quand une session **approche ou dépasse la context window du modèle**, OpenClaw déclenche automatiquement la **compaction**.

**Ce que fait la compaction :**
- Prend l'historique ancien de la conversation
- Le **résume** en une entrée compacte (summary)
- Conserve les **messages récents intacts** après le point de compaction
- Persiste ce résumé dans le JSONL de la session (c'est permanent)

La requête originale est retentée avec le contexte compacté.

**Ce qu'on voit :**
- En mode verbose : `🧹 Auto-compaction complete`
- Via `/status` : `🧹 Compactions: <count>`

**Déclenchement manuel :**
```
/compact Focus on decisions and open questions
```

---

### 2.3 Session Pruning vs Compaction
✅ Ce sont deux mécanismes distincts qui opèrent à des niveaux différents.

| | **Compaction** | **Session Pruning** |
|---|---|---|
| **Quand** | Session proche de la context window | Avant **chaque** appel LLM |
| **Quoi** | Résume tout l'historique ancien | Supprime les vieux **tool results** uniquement |
| **Sur disque** | ✅ Persisté dans le JSONL | ❌ En mémoire uniquement, jamais sur disque |
| **Déclenché** | Token-based (auto) ou `/compact` (manuel) | Automatiquement selon TTL |
| **Messages user/assistant** | Résumés | **Jamais touchés** |

**Détails du Session Pruning :**
- Ne s'applique qu'aux `toolResult` messages
- Les derniers `keepLastAssistants` (défaut : 3) messages assistant sont protégés
- Les tool results contenant des **blocs image** ne sont jamais prunés
- **Soft-trim** (par défaut) : conserve tête + queue, insère `...` au milieu
- **Hard-clear** : remplace tout le contenu par `[Old tool result content cleared]`
- Mode `cache-ttl` : ne prune que si le dernier appel Anthropic est plus vieux que le TTL configuré

---

### 2.4 Gestion des Sessions : Reset et Lifecycle
✅ Une session est réutilisée jusqu'à expiration. L'expiration est évaluée au prochain message entrant.

**Modes de reset :**
- **Daily** (défaut) : reset à 4h00 du matin (heure locale du gateway)
- **Idle** : reset après N minutes d'inactivité
- **Combiné** : le premier des deux qui expire l'emporte

**Déclencheurs manuels :**
- `/new` → nouveau `sessionId`, l'agent lance un court greeting de confirmation
- `/reset` → idem
- `/new <modèle>` → démarre une nouvelle session avec un modèle spécifique

**Scoping des DMs :**
- `main` (défaut) : tous les DMs partagent la session principale (continuité)
- `per-channel-peer` : isolation par canal + expéditeur (recommandé en multi-utilisateur)
- `per-account-channel-peer` : isolation par compte + canal + expéditeur

⚠️ En configuration multi-utilisateurs sans scoping, les utilisateurs **partagent le même contexte**, ce qui peut faire fuiter des informations privées entre eux.

---

## Partie 3 — L'Architecture Mémoire d'OpenClaw

### 3.1 Philosophie Centrale
✅📹 La mémoire d'OpenClaw repose sur un principe radical de simplicité :

> **"Plain Markdown in the agent workspace. The files are the source of truth."**

Pas de base de données vectorielle, pas de pipeline RAG complexe, pas d'infrastructure dédiée. Juste des fichiers Markdown locaux que l'agent peut lire et écrire.

Le workspace par défaut est `~/.openclaw/workspace/`.

---

### 3.2 Structure des Fichiers

```
~/.openclaw/workspace/
├── MEMORY.md                    ← Mémoire sémantique long-terme
└── memory/
    ├── 2026-02-07.md            ← Log quotidien
    ├── 2026-02-08.md
    ├── 2026-02-09.md
    ├── 2026-02-09-refactor.md   ← Snapshot de session (blog/YT)
    └── 2026-02-09-memory-system.md
```

---

### 3.3 Couche 1 : `MEMORY.md` (Mémoire Sémantique Long-Terme)

✅ Rôle : stocker les **faits durables, préférences et informations d'identité**.

**Caractéristiques techniques (doc officielle) :**
- Chargé uniquement dans la **session principale privée** — jamais dans les contextes de groupe
- C'est la source des faits stables que l'agent doit toujours connaître
- Limite de **~200 lignes** pour ne pas saturer le contexte
- Organisé en sections structurées

**Exemples de contenu :**
```markdown
## Preferences
- Préfère le dark mode
- Utilise TypeScript
- Vim keybindings

## Context
- Travaille sur une API REST avec Node.js
- A migré vers Cursor

## Decisions
- Choix de PostgreSQL plutôt que MongoDB pour ce projet
```

**Règle de routage :**
> *"Decisions, preferences, and durable facts go to MEMORY.md"* ✅

---

### 3.4 Couche 2 : Les Logs Quotidiens (Mémoire Épisodique Continue)

✅ **Chemin :** `memory/YYYY-MM-DD.md`

**Caractéristiques techniques :**
- **Append-only** : les nouvelles entrées sont ajoutées à la fin, rien n'est jamais supprimé
- Portée **journalière**
- Les fichiers d'**aujourd'hui et d'hier** sont chargés au démarrage de chaque session
- `memory_get` gère gracieusement l'absence du fichier du jour (retourne `{ text: "", path }` au lieu de lancer une erreur `ENOENT`)

**Règle de routage :**
> *"Day-to-day notes and running context go to memory/YYYY-MM-DD.md"* ✅

---

### 3.5 Couche 3 : Les Session Snapshots (Mémoire Épisodique Ponctuelle)

📹 **Source : blog et vidéo YouTube uniquement. Non documenté officiellement.**

**Déclencheur :** commandes `/new` ou `/reset` uniquement. Fermer le navigateur ou l'application ne déclenche rien.

**Mécanisme :**
1. Un hook (`on_session_start`) capture les **15 derniers messages**
2. Filtrage strict : uniquement les messages `user` et `assistant`
3. Exclus : tool calls, messages système, slash commands
4. L'agent génère un **slug descriptif** pour le nom de fichier
5. Le texte brut filtré est sauvegardé

**Important :** ce n'est **pas un résumé généré par l'IA**. C'est le texte brut de la conversation, tel quel.

**Exemple de fichier créé :** `memory/2026-02-09-api-design.md`

**Portée :** conversation-scoped (lié à la conversation qui vient de se terminer).

---

## Partie 4 — Les 4 Mécanismes qui Font Tout Fonctionner

Les fichiers seuls ne servent à rien. Ce sont les mécanismes de lecture/écriture au bon moment qui donnent vie au système.

---

### Mécanisme 1 : Bootstrap Loading au Démarrage de Session

✅📹 **Quand :** au début de chaque nouvelle session.

**Ce qui se passe :**
1. Le système **injecte automatiquement** `MEMORY.md` dans le prompt — l'agent commence la conversation en sachant déjà qui est l'utilisateur, sans avoir rien à chercher
2. Les **instructions de l'agent** lui ordonnent de lire lui-même les logs de today et yesterday pour récupérer le contexte récent

**Distinction importante :**
- `MEMORY.md` → **poussé par le système** (injection automatique dans le prompt)
- Logs quotidiens → **tirés par l'agent** (l'agent suit ses propres instructions)

📹 *"C'est le pattern le plus simple et le plus important. L'agent n'a pas à chercher le contexte. Il est juste là."*

---

### Mécanisme 2 : Pre-Compaction Memory Flush (Write-Ahead Log)

✅ **Quand :** juste avant qu'une session atteigne la limite de sa context window.

**Ce qui se passe techniquement :**
1. OpenClaw calcule en continu l'estimation des tokens utilisés
2. Quand le seuil est atteint (`contextWindow - reserveTokensFloor - softThresholdTokens`), il injecte un **tour agentique silencieux**
3. Ce tour est composé de deux prompts simultanés :

**System prompt injecté :**
```
"Session nearing compaction. Store durable memories now."
```

**User prompt injecté :**
```
"Write any lasting notes to memory/YYYY-MM-DD.md; create memory/ if needed. 
Reply with NO_REPLY if nothing to store."
```

4. L'agent analyse la session en cours, écrit ce qui mérite d'être conservé dans le log du jour, puis répond `NO_REPLY`
5. La réponse `NO_REPLY` garantit que **rien n'apparaît dans le chat de l'utilisateur**

**Contraintes techniques :**
- **Un seul flush par cycle de compaction** (tracké dans `sessions.json` pour éviter les doublons)
- **Skippé** si le workspace est en lecture seule (`workspaceAccess: "ro"` ou `"none"`)

**Configuration :**
```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "reserveTokensFloor": 20000,
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 4000,
          "systemPrompt": "Session nearing compaction. Store durable memories now.",
          "prompt": "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store."
        }
      }
    }
  }
}
```

**Pattern sous-jacent :**
📹 Ce mécanisme applique le pattern **Write-Ahead Log** des bases de données : sauvegarder avant de perdre. Ce qui était une opération destructrice (perdre le contexte à la compaction) devient un **point de sauvegarde**. La compaction se transforme en checkpoint plutôt qu'en perte d'information.

---

### Mécanisme 3 : Session Snapshot au `/new`

📹 **Source : blog/YT uniquement.**

**Quand :** uniquement sur déclenchement explicite `/new` ou `/reset`.

**Ce qui se passe :**
1. Hook `on_session_start` intercepte la fin de conversation
2. Capture les **15 derniers messages** de l'historique
3. **Filtre** : conserve uniquement `user` + `assistant`
4. **Exclut** : tool_calls, messages système, slash commands
5. L'agent génère un slug descriptif basé sur le contenu
6. Sauvegarde en fichier `memory/YYYY-MM-DD-slug.md`

**Différence clé avec le flush de pré-compaction :**
- Le flush écrit des **notes distillées** → c'est de l'extraction
- Le snapshot conserve **les messages bruts** → c'est une archive de conversation

---

### Mécanisme 4 : Commande Utilisateur Explicite "Remember this"

✅ **Le mécanisme le plus simple.**

**Quand :** l'utilisateur demande explicitement à l'agent de retenir quelque chose.

**Ce qui se passe :**
L'agent applique un arbre de décision simple :

```
L'information est-elle un fait durable ?
        │
   ┌────┴────┐
  OUI       NON
   │         │
MEMORY.md  Daily Log
```

Aucun hook spécial nécessaire. L'agent a juste besoin :
- Des capacités d'écriture de fichiers
- D'instructions claires sur comment router l'information

---

## Partie 5 — Vue d'Ensemble du Cycle de Vie Complet

```
═══════════════════════════════════════════════════════
  DÉMARRAGE DE SESSION
═══════════════════════════════════════════════════════

  [Système] Injecte MEMORY.md dans le prompt
      │
  [Agent] Lit memory/today.md + memory/yesterday.md
      │
  [Conversation démarre]
      │
      ▼

═══════════════════════════════════════════════════════
  PENDANT LA SESSION
═══════════════════════════════════════════════════════

  [Message utilisateur]
      │
  [Session Pruning] supprime vieux tool results
  en mémoire avant l'appel LLM (pas sur disque)
      │
  [Appel LLM avec contexte épuré]
      │
  [Utilisateur dit "remember this"]
      │
  [Agent route] → MEMORY.md ou Daily Log
      │
      ▼

═══════════════════════════════════════════════════════
  APPROCHE DE LA LIMITE DE CONTEXTE
═══════════════════════════════════════════════════════

  [Tokens proches de la limite]
      │
  [Silent agentic turn injecté]
  "Write lasting notes to memory/YYYY-MM-DD.md"
      │
  [Agent écrit dans le Daily Log]
  [Agent répond NO_REPLY → invisible pour l'utilisateur]
      │
  [Compaction] résume l'historique ancien
  Le résumé est persisté dans le JSONL de session
      │
      ▼

═══════════════════════════════════════════════════════
  FIN DE SESSION (via /new ou /reset)
═══════════════════════════════════════════════════════

  [Hook session] capture les 15 derniers messages
  [Filtre] user + assistant uniquement
  [Génère slug descriptif]
  [Sauvegarde] memory/YYYY-MM-DD-slug.md
      │
  [Nouveau sessionId créé]
      │
  [Retour au démarrage de session →]

═══════════════════════════════════════════════════════
```

---

## Partie 6 — Les 3 Questions Fondamentales

📹 Toute l'architecture, ramenée à l'essentiel :

| Question | Réponse OpenClaw |
|---|---|
| **Qu'est-ce qui vaut la peine d'être retenu ?** | Faits durables + decisions + préférences (semantic) / Contexte récent + événements (épisodique) |
| **Où ça va ?** | `MEMORY.md` pour le durable / `memory/YYYY-MM-DD.md` pour le quotidien |
| **Quand est-ce que ça s'écrit ?** | Bootstrap (lecture), pré-compaction (flush automatique), `/new` (snapshot), demande explicite |

---

## Partie 7 — Ce qui Confirme que c'est un Pattern qui Devient Standard

📹 Claude Code a récemment sorti une feature de mémoire native. Elle utilise également des fichiers Markdown. Ce n'est pas une coïncidence — c'est la même conclusion : **pour la mémoire agentique locale, les fichiers Markdown et les bons déclencheurs sont la solution pragmatique.**

La complexité n'est pas dans le stockage. Elle est dans les mécanismes de cycle de vie qui savent **quand lire, quand écrire, et quoi garder.**

---

## Annexe — Récapitulatif des Fichiers et Chemins

| Fichier | Chemin | Type | Accès |
|---|---|---|---|
| Mémoire long-terme | `~/.openclaw/workspace/MEMORY.md` | Sémantique | Chargé à chaque session (privée) |
| Log quotidien | `~/.openclaw/workspace/memory/YYYY-MM-DD.md` | Épisodique | Append-only, today+yesterday au démarrage |
| Snapshot session | `~/.openclaw/workspace/memory/YYYY-MM-DD-slug.md` | Épisodique | Écrit au `/new`, lu via memory_search |
| Index vectoriel | `~/.openclaw/memory/<agentId>.sqlite` | Index | Interne au système |
| Sessions store | `~/.openclaw/agents/<agentId>/sessions/sessions.json` | Système | Gateway uniquement |
| Transcript | `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl` | Système | Gateway uniquement |