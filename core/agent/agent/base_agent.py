import json
from typing import List, Generator

from llm.client import LLMClient
from llm.config import ModelConfig
from schemas.message import Message, HumanMessage, ToolMessage


class BaseAgent:
    """
    Core agentic loop for Knower.

    Runs an LLM in a tool-calling loop: the model reasons, calls tools,
    receives results, and loops until it produces a final text answer
    (i.e. a response with no tool_calls).

    The agent is pure logic — it yields event dicts and never prints.
    Display is the caller's responsibility (terminal, API, etc.).

    Events follow the schemas defined in schemas/event.py:
      - "think"   : reasoning tokens from the model
      - "answer"  : streamed text content, or tool_calls wrapper
      - "tool"    : tool start / end / error with name, args, result
      - "usage"   : token counts and cost for one LLM call
      - "error"   : LLM-level errors
    """

    def __init__(self, model: ModelConfig, system_prompt: str, tools: List = None):
        self.llm = LLMClient(
            model=model,
            system_prompt=system_prompt,
            tools=tools or [],
        )

    def run(self, content: str) -> Generator[dict, None, None]:
        messages = [HumanMessage(content=content)]
        yield from self._loop(messages)

    def _loop(self, messages: List[Message]) -> Generator[dict, None, None]:
        max_iterations = 15
        iteration = 0

        while iteration < max_iterations:
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

        yield {"type": "error", "id": "max_iter", "content": "max agent iterations reached, stopping."}