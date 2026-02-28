## Implémentation des Outils et Tests

- [ ] Implémenter le wrapper d'outils personnalisé
    Le client LLM a besoin d'un schéma JSON pour chaque outil et d'une méthode d'invocation. Comme la dépendance LangChain a été retirée pour garder le projet léger, il faut créer une classe ou un mécanisme dans `agent/vault_tools.py` capable d'inspecter les signatures des fonctions Python existantes (via le module `inspect`) pour générer automatiquement le format attendu par l'API OpenRouter. L'idée est de commencer avec des "dummy tools" pour valider la mécanique de parsing et d'exécution avant de brancher les vrais outils du vault présents dans `mcp_server/tools.py`.

- [ ] Connecter les outils aux agents Update et Search
    Actuellement, `UpdateAgent` et `SearchAgent` sont instanciés avec une liste d'outils vide (`tools=[]`). Une fois le wrapper d'outils fonctionnel, il faudra importer les instances d'outils et les injecter dans les agents respectifs. L'agent Update doit avoir accès à l'ensemble des capacités (lecture, écriture, navigation), tandis que l'agent Search doit être strictement restreint aux outils en lecture seule pour éviter tout effet de bord.

- [ ] Tester la boucle d'exécution complète via le terminal
    Le code de base (client LLM, schémas, agents, CLI) a été écrit mais n'a pas encore été exécuté. Il faut lancer `terminal.py`, vérifier que la connexion à OpenRouter avec le modèle Gemini s'établit correctement, s'assurer que le streaming des événements (réflexion, génération de texte, appels d'outils) s'affiche proprement dans la console, et corriger les éventuels crashs liés au parsing des réponses JSON du modèle.

## Amélioration de la Logique Agentique

- [ ] Étendre la boucle de l'agent pour supporter N itérations
    La méthode `_loop` dans `BaseAgent` est actuellement codée en dur pour effectuer exactement deux passes : un premier appel LLM qui peut déclencher des outils, suivi d'un second appel pour formuler la réponse finale. Selon les spécifications du MVP, l'agent doit être autonome et pouvoir boucler autant de fois que nécessaire (ex: chercher, puis lire un fichier, puis écrire) jusqu'à ce qu'il décide de lui-même qu'il a terminé sa tâche.

- [ ] Enrichir les System Prompts avec l'architecture du vault
    Les prompts actuels dans `prompts/update_prompt.py` et `prompts/search_prompt.py` sont de simples placeholders. Ils doivent être remplacés par les véritables instructions détaillées dans la documentation du MVP. Ces prompts doivent transmettre au modèle la compréhension de la structure des fichiers (`overview.md`, `state.md`, `changelog.md`), les règles de routing à 3 niveaux, et les directives strictes sur l'utilisation économique des outils (par exemple, privilégier `append` plutôt que de lire et réécrire un long historique).