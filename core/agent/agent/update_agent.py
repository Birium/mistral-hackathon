from agent.agent.base_agent import BaseAgent
from agent.agent.context import load_vault_context
from agent.llm.config import DEFAULT_MODEL
from agent.prompts.update_agent_prompt import UPDATE_SYSTEM_PROMPT

from agent.tools.tree_tool import TreeTool
from agent.tools.read_tool import ReadTool
from agent.tools.search_tool import SearchTool
from agent.tools.write_tool import WriteTool
from agent.tools.edit_tool import EditTool
from agent.tools.append_tool import AppendTool
from agent.tools.move_tool import MoveTool
from agent.tools.delete_tool import DeleteTool


class UpdateAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model=DEFAULT_MODEL,
            system_prompt=UPDATE_SYSTEM_PROMPT,
            tools=[
                TreeTool, ReadTool, SearchTool,
                WriteTool, EditTool, AppendTool,
                MoveTool, DeleteTool
            ],
        )

    def process(self, content: str, inbox_ref: str = None):
        vault_context = load_vault_context()
        payload = f"{vault_context}\n\n---\n\n{content}"
        if inbox_ref:
            payload += f"\n\ninbox_ref: {inbox_ref}"
        yield from self.run(payload)