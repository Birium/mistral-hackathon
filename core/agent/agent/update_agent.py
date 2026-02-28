from agent.base_agent import BaseAgent
from llm.config import DEFAULT_MODEL
from prompts.update_prompt import UPDATE_SYSTEM_PROMPT
from tools.dummy_tools import TreeTool, ReadTool


class UpdateAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model=DEFAULT_MODEL,
            system_prompt=UPDATE_SYSTEM_PROMPT,
            tools=[TreeTool, ReadTool],
        )

    def process(self, content: str, inbox_ref: str = None):
        vault_context = self._load_vault_context()
        payload = f"{vault_context}\n\n---\n\n{content}"
        if inbox_ref:
            payload += f"\n\ninbox_ref: {inbox_ref}"
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