from agent.base_agent import BaseAgent
from llm.config import DEFAULT_MODEL
from prompts.search_prompt import SEARCH_SYSTEM_PROMPT
from tools.tools import SEARCH_TOOLS, read


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
            tree_content = read("tree.md")
            profile = read("profile.md")
            return f"{overview}\n\n{tree_content}\n\n{profile}"
        except Exception as e:
            return f"[vault context unavailable: {e}]"