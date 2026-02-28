from agent.agent.base_agent import BaseAgent
from agent.llm.config import DEFAULT_MODEL
from agent.prompts.search_prompt import SEARCH_SYSTEM_PROMPT
from agent.tools.tools import SEARCH_TOOLS, read, tree


class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model=DEFAULT_MODEL,
            system_prompt=SEARCH_SYSTEM_PROMPT,
            tools=SEARCH_TOOLS,
        )

    def process(self, query: str):
        vault_context = self._load_vault_context()
        payload = f"{vault_context}\n\n---\n\n{query}"
        yield from self.run(payload)

    def _load_vault_context(self) -> str:
        try:
            overview = read("overview.md")
            vault_tree = f"```tree.md\n{tree(depth=1)}\n```"
            profile = read("profile.md")
            return f"{overview}\n\n{vault_tree}\n\n{profile}"
        except Exception as e:
            return f"[vault context unavailable: {e}]"