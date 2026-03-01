### ✅ **Phase 1 : Refactoring du Contexte Vault et Injection de la Date**

-   **Centralisation et Formatage du Contexte :**
    -   **Mutualisation de la logique :** Création d'un nouveau module dédié pour gérer le contexte du vault partagé entre les différents agents, éliminant ainsi la duplication de code existante.
    -   **Injection de la date du jour :** Ajout systématique de la date actuelle au format `YYYY-MM-DD` via `datetime.now()`. Cela permet aux agents (notamment l'`UpdateAgent`) d'avoir un repère temporel fiable pour la rédaction des changelogs, corrigeant le bug des dates inventées ou incorrectes.
    -   **Suppression de la référence `tree.md` :** Retrait du bloc markdown factice ````tree.md` qui enveloppait l'arborescence. L'output de `tree(depth=1)` est désormais injecté directement, évitant la confusion du modèle avec un fichier physique inexistant.
    -   **Structuration en XML :** Refonte du format de sortie du contexte en utilisant des balises XML explicites (`<date>`, `<overview>`, `<vault-structure>`, `<profile>`). Cette approche améliore grandement la capacité du LLM à parser et isoler les différentes sections du contexte.
    -   **[`core/agent/agent/context.py`] :** Implémentation de la fonction `load_vault_context()`. Utilisation de constantes de templates (`VAULT_CONTEXT_TEMPLATE` et `VAULT_CONTEXT_ERROR_TEMPLATE`) formatées via `.format()` avec des arguments nommés (kwargs), remplaçant les f-strings concaténées pour un code beaucoup plus propre et lisible. Gestion des erreurs conservée avec un template XML de fallback (`<vault-context-error>`).

-   **Mise à jour des Agents :**
    -   **Nettoyage et intégration :** Les agents de recherche et de mise à jour ont été allégés de leur logique de chargement de contexte interne.
    -   **[`core/agent/agent/search_agent.py`] & [`core/agent/agent/update_agent.py`] :** Suppression de la méthode `_load_vault_context()` dans les deux classes. Remplacement des imports directs des outils `read` et `tree` par l'import de la nouvelle fonction `load_vault_context`. Le payload principal reste inchangé dans sa structure globale (`vault_context\n\n---\n\nquery`), mais bénéficie désormais du nouveau formatage XML et de la date.
