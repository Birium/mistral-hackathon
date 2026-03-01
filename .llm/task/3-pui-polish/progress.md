### ✅ **Phase 4 : Refonte de l'Activity View & Intégration du Chain of Thought Réel**

-   **Architecture & Parsing de Flux (`src/lib/parseStreamEvents.ts`) :**
    -   **Extraction de la logique :** Création d'une fonction pure `parseStreamEvents` pour transformer les événements NDJSON bruts (`AgentEvent[]`) en une structure d'affichage typée (`DisplayItem[]`).
    -   **Gestion des types d'items :**
        -   `ThinkItem` : Agrégation des fragments de pensée consécutifs et nettoyage des balises `<think>`.
        -   `ToolItem` : Suivi du cycle de vie complet (start → running → done/error) avec réconciliation des événements de début et de fin.
        -   `UsageItem` : Parsing des statistiques de tokens (conservé mais masqué dans l'UI pour l'instant).
    -   **Helpers utilitaires :**
        -   `parseArgs` : Parsing sécurisé des arguments JSON des outils pour un affichage structuré.
        -   `extractFilePaths` : Extraction automatique des chemins de fichiers depuis les résultats d'outils (via regex sur les code fences).
        -   `deriveHeaderText` : Génération dynamique du texte du header (ex: "Reading tasks.md") basée sur le dernier item significatif, assurant une continuité visuelle entre les états.

-   **Composants UI & Intégration (`src/components/central/`) :**
    -   **`StreamChainOfThought.tsx` :** Nouveau composant dédié encapsulant toute la logique d'affichage du raisonnement.
        -   **Gestion de l'état :** Fermé par défaut (`defaultOpen={false}`), l'activité est communiquée via le header dynamique.
        -   **Header Icon :** Logique robuste pour l'icône du header qui reflète toujours le *dernier* item significatif (Think ou Tool), ignorant les items `usage` pour éviter les clignotements en fin de stream.
        -   **Rendu des Steps :**
            -   *Reasoning* : Utilisation de `MarkdownRenderer` avec des overrides CSS (`text-xs`) pour une intégration fluide du markdown dans les steps.
            -   *Tools* : Affichage des arguments complets (sans troncation) et des fichiers impactés sous forme de badges cliquables.
    -   **`ActivityView.tsx` :** Refonte complète pour composer `StreamChainOfThought` et `MarkdownRenderer`. Gestion des états de chargement, d'erreur, et d'auto-collapse du CoT à la fin du stream.
    -   **`src/hooks/useStreamParser.ts` :** Hook réactif faisant le pont entre le `ChatContext` et l'UI, mémoïsant le parsing pour la performance.

-   **Système de Fichiers & Navigation (`src/components/shared/`) :**
    -   **`FileLink.tsx` :** Création d'un composant "chip" cliquable qui utilise `useFileNavigation` pour ouvrir les fichiers vault directement depuis le flux de pensée ou la réponse finale.
    -   **Intégration Markdown (`MarkdownRenderer.tsx`) :**
        -   **Interception des Code Blocks :** Les blocs de code dont le langage est un nom de fichier (ex: ````tasks.md`) sont remplacés par un simple `FileLink`, masquant le contenu brut pour alléger l'affichage.
        -   **Liens Intelligents :** Détection automatique des chemins vault dans les liens markdown `[lien](path)` pour les rendre navigables en interne via `FileLink`.

-   **Nettoyage & Optimisations :**
    -   Suppression de l'ancien composant `EventStream.tsx` devenu obsolète.
    -   Correction des styles pour le code inline dans les blocs de pensée (force `text-xs` pour éviter les incohérences de taille).
    -   Affichage des arguments d'outils en format clé-valeur complet pour une meilleure lisibilité technique.