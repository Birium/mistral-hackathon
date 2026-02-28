from agent.agent.base_agent import BaseAgent
from agent.llm.config import DEFAULT_MODEL
from agent.prompts.update_prompt import UPDATE_SYSTEM_PROMPT
from agent.tools.tools import UPDATE_TOOLS, read, tree


class UpdateAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model=DEFAULT_MODEL,
            system_prompt=UPDATE_SYSTEM_PROMPT,
            tools=UPDATE_TOOLS,
        )

    def process(self, content: str, inbox_ref: str = None):
        vault_context = self._load_vault_context()
        payload = f"{vault_context}\n\n---\n\n{content}"
        if inbox_ref:
            payload += f"\n\ninbox_ref: {inbox_ref}"
        yield from self.run(payload)

    def _load_vault_context(self) -> str:
        try:
            overview = read("overview.md")
            vault_tree = f"```tree.md\n{tree(depth=1)}\n```"
            profile = read("profile.md")
            return f"{overview}\n\n{vault_tree}\n\n{profile}"
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception while loading vault context: {e}")
            traceback.print_exc()
            return f"[vault context unavailable: {e}]"