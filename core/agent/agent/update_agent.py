from agent.agent.base_agent import BaseAgent
from agent.agent.context import load_vault_context
from agent.llm.config import DEFAULT_MODEL
from agent.prompts.update_agent_prompt import UPDATE_SYSTEM_PROMPT
from agent.tools.tools import UPDATE_TOOLS


class UpdateAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model=DEFAULT_MODEL,
            system_prompt=UPDATE_SYSTEM_PROMPT,
            tools=UPDATE_TOOLS,
        )

    def process(self, content: str, inbox_ref: str = None):
        vault_context = load_vault_context()
        payload = f"{vault_context}\n\n---\n\n{content}"
        if inbox_ref:
            payload += f"\n\ninbox_ref: {inbox_ref}"
        yield from self.run(payload)