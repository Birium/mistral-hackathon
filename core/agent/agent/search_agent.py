from agent.base_agent import BaseAgent
from llm.config import DEFAULT_MODEL
from prompts.search_prompt import SEARCH_SYSTEM_PROMPT
from tools.dummy_tools import TreeTool, ReadTool


class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model=DEFAULT_MODEL,
            system_prompt=SEARCH_SYSTEM_PROMPT,
            tools=[TreeTool, ReadTool],
        )

    def process(self, query: str):
        vault_context = self._load_vault_context()
        payload = f"{vault_context}\n\n---\n\n{query}"
        yield from self.run(payload)

    def _load_vault_context(self) -> str:
        from tools.dummy_tools import read
        try:
            overview = read("overview.md")
            tree_content = read("tree.md")
            profile = read("profile.md")
            return (
                f"## overview.md\n{overview}\n\n"
                f"## tree.md\n{tree_content}\n\n"
                f"## profile.md\n{profile}"
            )
        except Exception as e:
            return f"[vault context unavailable: {e}]"