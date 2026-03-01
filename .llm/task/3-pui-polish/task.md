# task.md — Refactor : Stream Events → Chain of Thought + Réponse finale avec liens fichiers

---

## 1. État actuel — Ce qui existe

### L'architecture de streaming

L'application repose sur un système de streaming ligne-par-ligne (NDJSON) via deux appels API :
- `streamSearch(query, onEvent)` — pour les recherches dans le vault
- `streamUpdate(query, onEvent, inboxRef?)` — pour les mises à jour

Ces deux fonctions se trouvent dans `src/api.ts` et consomment le stream via `consumeStream()`. Chaque ligne du stream est parsée en `AgentEvent`, un type union défini dans `src/types.ts` :

```
AgentThinkEvent     → type: 'think'   — raisonnement interne de l'agent (balises <think>)
AgentAnswerEvent    → type: 'answer'  — soit un appel tool (avec tool_calls), soit la réponse finale (sans tool_calls)
AgentToolEvent      → type: 'tool'    — début/fin/erreur d'un outil (status: 'start' | 'end' | 'error')
AgentUsageEvent     → type: 'usage'   — statistiques de tokens
AgentErrorEvent     → type: 'error'   — erreur de l'agent
AgentDoneEvent      → type: 'done'    — signal de fin
```

### Le state management du stream

`src/contexts/ChatProvider.tsx` collecte tous les événements dans un tableau `streamEvents: AgentEvent[]` et les expose via `ChatContext`. À la fin du stream, il extrait la réponse finale (dernier `answer` sans `tool_calls`) pour la stocker dans `activityResult`.

Le contexte expose aussi :
- `isLoading` — vrai pendant le stream
- `pendingMessage` — la question envoyée
- `activityResult` — `{ type, content, query }`

### L'affichage actuel — `ActivityView.tsx`

`src/components/central/ActivityView.tsx` est la vue affichée à `/activity`. Elle montre :
1. Pendant le loading : un `LoadingState` spinner générique + le message pending + une liste brute des événements (via `StreamEventLine`)
2. Après le loading : le `activityResult.content` passé à `MarkdownRenderer`

La fonction `StreamEventLine` locale est extrêmement rudimentaire : elle affiche juste le `content` si `event.type === 'answer'`, sinon un dump JSON tronqué. **C'est le vrai problème.**

### Le parseur qui existait — `EventStream.tsx`

`src/components/central/EventStream.tsx` contient un parseur bien plus élaboré (`processEvents`) qui transforme les `AgentEvent[]` bruts en `DisplayItem[]` typés :

- `ThinkItem` — agrège les blocs `think` consécutifs, strip les balises `<think>`, affiche un aperçu des 4 dernières lignes
- `ToolItem` — trace le cycle de vie d'un outil : `running → done | error`, avec les args parsés et le résultat tronqué
- `UsageItem` — tokens in/out et coût
- `ErrorItem` — message d'erreur

Ce composant existe dans la codebase mais **n'est plus utilisé** — il a été découplé de `ActivityView.tsx` lors d'un refactor antérieur et est tombé en déshérence.

### Les composants AI disponibles

La librairie `src/components/ai-elements/` contient des composants de haut niveau non encore utilisés dans le contexte du stream :

- **`chain-of-thought.tsx`** : `ChainOfThought`, `ChainOfThoughtHeader`, `ChainOfThoughtContent`, `ChainOfThoughtStep`, `ChainOfThoughtSearchResults`, `ChainOfThoughtSearchResult` — un collapsible structuré pour afficher le raisonnement pas à pas
- **`shimmer.tsx`** : `Shimmer` — animation de texte pour les états de chargement
- **`message.tsx`** : `Message`, `MessageContent`, `MessageResponse` (utilise Streamdown pour le markdown)

La sandbox (`src/components/ai-components/`) démontre comment combiner `ChainOfThought` avec `Shimmer` dans `ai-loader.tsx` et `ai-chain-of-thought.tsx` — c'est précisément le pattern voulu.

### La navigation fichiers

`src/hooks/useFileNavigation.ts` expose `navigateToFile(rawPath)` qui normalise un chemin absolu de vault vers un chemin relatif et navigue vers `/file/<relPath>`. C'est le hook à utiliser pour transformer les références fichiers en liens cliquables.

---

## 2. Le WHY — Pourquoi refactorer

### Problème 1 : L'expérience pendant le stream est nulle

Actuellement, l'utilisateur voit un spinner générique et une liste JSON illisible pendant que l'agent travaille. Il n'y a aucune visibilité sur ce que l'agent fait réellement :
- Quels outils appelle-t-il ?
- Sur quels fichiers travaille-t-il ?
- Où en est-il dans son raisonnement ?

C'est une boîte noire. L'utilisateur attend sans comprendre.

### Problème 2 : Le parseur est mort dans la codebase

`EventStream.tsx` a tout le logic de parsing correct mais n'est branché nulle part. La logique de `processEvents` est solide (gestion du cycle de vie des tools, agrégation des thinks) mais elle est orpheline.

### Problème 3 : La réponse finale ignore le contexte fichiers

L'agent, dans sa réponse finale en markdown, peut referencer des fichiers du vault (par exemple dans le JSONL exemple, l'agent propose de traiter un item du vault). Ces références sont actuellement passées brutes à `MarkdownRenderer` — elles s'affichent comme du texte mort, sans lien vers les vrais fichiers du vault.

### Problème 4 : Le design ne correspond pas à la vision

La sandbox démontre un pattern `ChainOfThought` + `Shimmer` très soigné, aligné sur le design system de l'app. L'implémentation actuelle de l'`ActivityView` est un placeholder fonctionnel, pas un vrai écran produit.

---

## 3. La vision — Ce qu'on veut construire

### 3.1 Un `ActivityView` en deux phases

**Phase 1 — Pendant le stream (isLoading: true)**

On affiche un composant `ChainOfThought` ouvert par défaut, avec :
- Un **header** animé (via `Shimmer`) qui reflète l'action courante (ex: "Recherche dans le vault...", "Appel de l'outil `read`...", "Rédaction de la réponse...")
- Un **contenu collapsible** qui liste les steps progressivement au fur et à mesure qu'ils arrivent dans le stream :
  - Les blocs `think` → un step "Raisonnement" avec une icône cerveau, statut `active` pendant le streaming, `complete` après
  - Les appels `tool` → un step par appel d'outil avec le nom de l'outil + arguments formatés, statut `active` quand `status: 'start'`, `complete` quand `status: 'end'`, et les résultats comme `ChainOfThoughtSearchResult` badges
  - Les `usage` → un step discret en bas du collapsible (optionnel, peut être masqué par défaut)

**Phase 2 — Après le stream (isLoading: false)**

- Le `ChainOfThought` se referme automatiquement (ou passe en mode "résumé")
- La réponse finale en markdown apparaît en dessous
- Les références fichiers dans le markdown sont converties en liens cliquables

### 3.2 Le parsing des événements — State machine propre

On s'appuie sur la logique existante de `EventStream.tsx` mais on la restructure en un **hook dédié** ou une **fonction utilitaire pure** `parseStreamEvents(events: AgentEvent[]): DisplayItem[]` — découplée de tout JSX pour être testable et réutilisable.

Le parsing doit gérer :
- **Agrégation des `think`** : les événements `think` consécutifs sont fusionnés en un seul item, les balises `<think>...</think>` sont strippées
- **Cycle de vie des `tool`** : un `tool start` crée un ToolItem `running`, le `tool end` correspondant (même `name`) le passe à `done` + attache le résultat
- **L'`answer` final** : l'`AgentAnswerEvent` sans `tool_calls` est la réponse finale markdown — il ne fait **pas** partie des `DisplayItem[]`, il est traité séparément
- **Les `answer` avec `tool_calls`** : ce sont des étapes intermédiaires d'orchestration, ils peuvent être ignorés ou comptabilisés comme steps

### 3.3 Les liens fichiers dans la réponse finale

Dans la réponse markdown de l'agent, les fichiers du vault peuvent être référencés sous plusieurs formes :
- Chemins relatifs : `vault/projects/freelance-fintech/blockers.md`
- Liens wiki-style : `[[meeting-notes]]`
- Liens markdown standard : `[blockers.md](vault/projects/freelance-fintech/blockers.md)`

On veut un système qui **détecte ces patterns** et les convertit en éléments cliquables. Quand on clique, `navigateToFile()` (de `src/hooks/useFileNavigation.ts`) est appelé, ce qui navigue vers `/file/<relPath>` et affiche le fichier dans le `FileView`.

L'implémentation ne doit **pas** afficher le contenu du fichier inline dans la réponse — juste un chip / badge / lien discret qui permet de sauter vers le fichier.

Le `MarkdownRenderer` actuel (`src/components/MarkdownRenderer.tsx`) utilise `react-markdown` avec des composants custom. C'est là qu'il faudra intercepter les liens et les patterns fichiers pour les router via `useFileNavigation`.

### 3.4 L'iconographie des steps

Chaque type de step dans le `ChainOfThought` doit avoir une icône Lucide appropriée :
- Raisonnement / Think → `Brain` ou `Lightbulb`
- Appel d'outil `read` → `FileText`
- Appel d'outil `tree` → `FolderTree`
- Appel d'outil `write` / `patch` → `Pencil`
- Appel d'outil générique → `Wrench`
- Usage → `BarChart2`

### 3.5 Comportement du collapsible

- **Pendant le stream** : le `ChainOfThought` est **ouvert** automatiquement pour que l'utilisateur voie le progrès
- **À la fin du stream** : après un délai (~1s), le `ChainOfThought` se **referme** automatiquement pour laisser la place à la réponse finale
- **L'utilisateur peut le rouvrir** manuellement pour inspecter les steps
- L'en-tête quand c'est fermé et terminé affiche un résumé : "Traité en X steps" ou le nombre d'outils appelés

---

## 4. Fichiers concernés par ce refactor

### Fichiers à réécrire intégralement
- `src/components/central/ActivityView.tsx` — complète réécriture, c'est le cœur du refactor

### Fichiers à refactorer / étendre
- `src/components/central/EventStream.tsx` — transformer `processEvents` en utilitaire pur, supprimer le JSX existant ou le remplacer par les composants `ai-elements`
- `src/components/MarkdownRenderer.tsx` — ajouter la détection et le rendu des références fichiers
- `src/contexts/ChatProvider.tsx` — potentiellement exposer plus de state granulaire (step courant, etc.) si le hook dédié ne suffit pas

### Fichiers à créer
- Un hook ou utilitaire de parsing : `src/hooks/useStreamParser.ts` (ou `src/lib/parseStreamEvents.ts`) — transforme `AgentEvent[]` en `DisplayItem[]` de façon réactive
- Un composant pour les liens fichiers dans le markdown : `src/components/shared/FileLink.tsx` (ou intégré directement dans `MarkdownRenderer`)

### Fichiers utilisés en lecture (composants AI)
- `src/components/ai-elements/chain-of-thought.tsx` — composants `ChainOfThought*`
- `src/components/ai-elements/shimmer.tsx` — `Shimmer` pour le header animé
- `src/hooks/useFileNavigation.ts` — navigation vers les fichiers

### Fichiers de référence (types, API)
- `src/types.ts` — les types `AgentEvent` (ne pas modifier)
- `src/api.ts` — `streamSearch`, `streamUpdate` (ne pas modifier)
- `src/contexts/ChatContext.tsx` — `streamEvents`, `isLoading`, `activityResult` (potentiellement étendre l'interface si nécessaire)

---

## 5. Contraintes et principes

- **Ne pas toucher à `api.ts`** — le streaming fonctionne correctement
- **Ne pas toucher aux types dans `types.ts`** — les types d'événements sont corrects et stables
- **Réutiliser les composants `ai-elements`** existants (`chain-of-thought.tsx`, `shimmer.tsx`) sans les modifier — ils ont été conçus pour exactement ce use case
- **Le parsing doit être découplé du rendu** — une fonction pure `AgentEvent[] → DisplayItem[]` facilement testable
- **Progressive disclosure** — les steps apparaissent progressivement au fil du stream, pas tous d'un coup à la fin
- **Performance** — les `think` events peuvent être très fréquents (fragments), l'agrégation doit être faite de façon à ne pas re-render à chaque fragment
- **Design system** — utiliser uniquement les tokens CSS (`--background`, `--muted-foreground`, etc.) et les classes Tailwind du design system en place (pas de couleurs hardcodées)


src/components/central/ActivityView.tsx
src/components/central/EventStream.tsx
src/components/MarkdownRenderer.tsx
src/hooks/useStreamParser.ts
src/components/shared/FileLink.tsx
src/contexts/ChatProvider.tsx
src/components/ai-elements/chain-of-thought.tsx
src/components/ai-elements/shimmer.tsx
src/hooks/useFileNavigation.ts
src/types.ts