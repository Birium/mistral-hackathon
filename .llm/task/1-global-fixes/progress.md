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

### ✅ **Phase 2 : Intégration du Contenu Fichier dans la Réponse SearchAgent**

-   **Logique d'Accumulation et de Buffering :**
    -   **Modification du flux de réponse :** Le `SearchAgent` a été refactorisé pour ne plus émettre les chunks `answer` textuels (l'overview) en temps réel. Ces fragments sont désormais interceptés et accumulés dans une liste interne (`answer_parts`) tout au long de l'exécution.
    -   **Préservation du Streaming Technique :** Les événements de type `think`, `tool` (start/end/error), `usage` et `error` continuent d'être streamés normalement pour assurer le feedback visuel et le logging en temps réel.

-   **Gestion du Tool `concat` :**
    -   **Interception du Résultat :** Mise en place d'une écoute spécifique sur les événements `tool` dans la boucle d'exécution. Lorsqu'un événement `concat` avec le statut `end` est détecté, son résultat (qui contient déjà les fichiers formatés en blocs markdown) est capturé et stocké (`concat_result`).
    -   **Assemblage Final :** À la fin du processus, l'agent construit une réponse unique en concaténant l'overview accumulé et le contenu des fichiers capturé.

-   **Émission de la Réponse Unique :**
    -   **Event Final Unifié :** L'agent émet un seul et unique événement `answer` (`id="final"`) contenant la totalité de la réponse (Texte explicatif + Contenu brut des fichiers).
    -   **[`core/agent/agent/search_agent.py`] :** Implémentation de la logique de filtrage, d'accumulation et d'assemblage dans la méthode `process`. Cela garantit que l'API et le frontend reçoivent un payload markdown complet et cohérent, simplifiant grandement le traitement côté client.

### ✅ **Phase 3 : Nettoyage et Standardisation du Format de Sortie `concat`**

-   **Raffinement de l'Affichage des Tools :**
    -   **Simplification des En-têtes de Blocs :** Modification de la logique de génération des code fences dans le tool `concat`. Suppression de l'annotation dynamique `(lines N-M)` dans le header du bloc markdown. Désormais, seul le chemin du fichier est utilisé comme identifiant de langage, ce qui garantit une compatibilité maximale avec les parseurs markdown et évite la redondance d'information (les numéros de ligne étant déjà explicites dans le contenu).
    -   **Harmonisation Visuelle :** Ajustement du formatage des numéros de ligne dans `_format_lines`. Passage de 1 à 2 espaces avant le séparateur vertical (`|`), alignant ainsi strictement le style visuel de `concat` sur celui du tool `read`. Cela assure une cohérence parfaite de la présentation des fichiers, quelle que soit la méthode d'accès utilisée par l'agent.
    -   **[`core/functions/concat/concat.py`] :** Mise à jour des fonctions `_format_lines` et `concat` pour implémenter ces changements de formatage.

### ✅ **Phase 4 : Refonte et Unification du Système de Logs par Requête**

-   **Architecture du Logging :**
    -   **Log par requête (Per-Request Logging) :** Abandon de l'approche hybride (un log global pour le serveur + un log par appel LLM) au profit d'un système unifié où chaque requête API (ex: `/search` ou `/update`) génère un et un seul fichier de log. Ce fichier regroupe chronologiquement tous les événements streamés par l'agent (`think`, `tool`, `answer`, `usage`, `error`).
    -   **Isolation des contextes :** En passant d'une fonction globale à une classe instanciée localement, on garantit que les requêtes concurrentes sur le serveur FastAPI ne mélangent plus leurs événements dans le même fichier.
    -   **Gate de Développement (`DEV`) :** L'écriture des fichiers JSONL sur le disque est désormais strictement conditionnée à l'activation du mode développement. L'affichage humain dans le terminal (stdout) reste quant à lui toujours actif pour le monitoring en production.

-   **Implémentation du RequestLogger :**
    -   **[`core/agent/utils/logger.py`] :** Réécriture complète du module. Création de la classe `RequestLogger` qui gère un buffer en mémoire (`self.events`). La méthode `log()` affiche dans le terminal et ajoute l'événement au buffer. La méthode `save()` écrit le buffer dans `logs/requests/{name}_{timestamp}.jsonl` uniquement si `env.DEV` est vrai. Le chemin du dossier de logs a été hardcodé pour simplifier le code et retirer la dépendance à `os.getenv`.
    -   **[`core/agent/utils/raw_logger.py`] :** Fichier supprimé. La journalisation des chunks bruts de l'API LLM (qui générait un dossier par appel LLM et spammait le disque) a été retirée, les événements structurés de l'agent étant amplement suffisants pour le débogage.

-   **Nettoyage et Intégration aux Points d'Entrée :**
    -   **[`core/agent/llm/client.py`] :** Purge de toutes les références à `object_logger`. Le client LLM retrouve un rôle pur : il génère et `yield` des événements structurés sans aucune responsabilité d'écriture sur le disque.
    -   **[`core/api/routes.py`] & [`core/mcp_server/tools.py`] :** Intégration du nouveau logger dans les routes `/search`, `/update` et les outils MCP. Mise en place d'un pattern robuste : instanciation de `log = RequestLogger("nom")` au début de la fonction `_run()`, appel de `log.log(event)` dans la boucle de l'agent, et garantie de l'écriture via un bloc `finally: log.save()`. Nettoyage d'un import `uuid` mort dans les tools MCP.
    -   **[`core/env.py`] & [`.env.example`] :** Ajout de la variable `DEV: bool = False` dans le schéma Pydantic `EnvVariables` pour centraliser la configuration, avec mise à jour du fichier d'exemple.