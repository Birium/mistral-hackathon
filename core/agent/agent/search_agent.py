from agent.agent.base_agent import BaseAgent
from agent.agent.context import load_vault_context
from agent.llm.config import DEFAULT_MODEL
from agent.prompts.search_prompt import SEARCH_SYSTEM_PROMPT
from agent.tools.tools import SEARCH_TOOLS


class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model=DEFAULT_MODEL,
            system_prompt=SEARCH_SYSTEM_PROMPT,
            tools=SEARCH_TOOLS,
        )

    def process(self, query: str):
        vault_context = load_vault_context()
        payload = f"{vault_context}\n\n---\n\n{query}"

        answer_parts = []
        concat_result = None

        for event in self.run(payload):
            event_type = event.get("type")

            if event_type == "answer" and not event.get("tool_calls"):
                answer_parts.append(event.get("content", ""))
                continue

            if (
                event_type == "tool"
                and event.get("name") == "concat"
                and event.get("status") == "end"
            ):
                concat_result = event.get("result", "")

            yield event

        content = "".join(answer_parts)
        if concat_result:
            content += "\n" + concat_result

        yield {"type": "answer", "id": "final", "content": content}