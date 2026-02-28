import json
from typing import List, Generator

from agent.llm.client import LLMClient
from agent.llm.config import ModelConfig
from agent.schemas.message import Message, HumanMessage, ToolMessage


MAX_ITERATIONS = 25

FORCE_FINISH_MESSAGE = (
    "You have reached the maximum number of agent iterations. "
    "You MUST respond now with your final answer. "
    "Summarize what you accomplished, what remains incomplete if anything, "
    "and provide the best response you can with the context you have. "
    "Do NOT attempt to call any tools."
)


class BaseAgent:
    """
    Core agentic loop for Knower.

    Runs an LLM in a tool-calling loop: the model reasons, calls tools,
    receives results, and loops until it produces a final text answer
    (i.e. a response with no tool_calls).

    The agent is pure logic — it yields event dicts and never prints.
    Display is the caller's responsibility (terminal, API, etc.).

    Safety: if the loop reaches MAX_ITERATIONS without natural exit,
    _force_finish injects a directive and makes one last LLM call
    with no tools available — structurally guaranteeing text output.

    Events follow the schemas defined in schemas/event.py:
      - "think"   : reasoning tokens from the model
      - "answer"  : streamed text content, or tool_calls wrapper
      - "tool"    : tool start / end / error with name, args, result
      - "usage"   : token counts and cost for one LLM call
      - "error"   : LLM-level errors
    """

    def __init__(self, model: ModelConfig, system_prompt: str, tools: List = None):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.llm = LLMClient(
            model=model,
            system_prompt=system_prompt,
            tools=self.tools,
            reasoning="high",
        )
    def run(self, content: str) -> Generator[dict, None, None]:
        messages = [HumanMessage(content=content)]
        yield from self._loop(messages)

    def _loop(self, messages: List[Message]) -> Generator[dict, None, None]:
        iteration = 0

        while iteration < MAX_ITERATIONS:
            iteration += 1

            for event_json in self.llm.stream(messages):
                yield json.loads(event_json)

            tool_calls = self.llm.get_tool_calls()

            if not tool_calls:
                return

            messages.append(self.llm.get_full_response())
            for tc in tool_calls:
                messages.append(ToolMessage(
                    tool_call_id=tc.tool_id,
                    name=tc.name,
                    content=tc.result_str or "",
                ))

        yield from self._force_finish(messages)

    def _force_finish(self, messages: List[Message]) -> Generator[dict, None, None]:
        yield {"type": "error", "id": "max_iterations",
            "content": f"Max iterations ({MAX_ITERATIONS}) reached. Forcing final response."}

        messages.append(HumanMessage(content=FORCE_FINISH_MESSAGE))

        final_llm = LLMClient(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=[],
            reasoning="high",
        )

        for event_json in final_llm.stream(messages):
            yield json.loads(event_json)