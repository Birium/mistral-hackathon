import json
from typing import List

from llm.client import LLMClient
from llm.config import ModelConfig
from schemas.message import Message, HumanMessage, ToolMessage


class BaseAgent:
    def __init__(self, model: ModelConfig, system_prompt: str, tools: List = None):
        self.llm = LLMClient(
            model=model,
            system_prompt=system_prompt,
            tools=tools or [],
        )

    def run(self, content: str) -> str:
        """Run the agent loop on a single user input, return final answer."""
        messages = [HumanMessage(content=content)]
        return self._loop(messages)

    def _loop(self, messages: List[Message]) -> str:
        """
        N-round loop:
        1. Call LLM — may trigger tool calls (executed inline by LLMClient)
        2. If tools were called, add results to conversation and loop again
        3. If no tools were called, the agent has finished its task.
        """
        max_iterations = 15
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            full_answer = self._stream_and_collect(messages)

            tool_calls = self.llm.get_tool_calls()
            
            # If the LLM didn't call any tools, it means it decided to answer directly.
            # The loop ends here.
            if not tool_calls:
                return full_answer

            # Append assistant message (with tool_calls) + tool results to history
            messages.append(self.llm.get_full_response())
            for tc in tool_calls:
                messages.append(ToolMessage(
                    tool_call_id=tc.tool_id,
                    name=tc.name,
                    content=tc.result_str or "",
                ))

        print("\n[Warning] Max agent iterations reached. Forcing stop.", flush=True)
        return full_answer

    def _stream_and_collect(self, messages: List[Message]) -> str:
        """Stream one LLM call, display events, return accumulated text answer."""
        full_answer = ""
        for event_json in self.llm.stream(messages):
            event = json.loads(event_json)
            self._display(event)
            # Collect plain text answer (not the tool_calls wrapper)
            if event["type"] == "answer" and not event.get("tool_calls"):
                full_answer += event.get("content", "")
        return full_answer

    def _display(self, event: dict):
        """Print events to terminal in a readable way."""
        t = event.get("type")

        if t == "answer" and not event.get("tool_calls"):
            print(event.get("content", ""), end="", flush=True)

        elif t == "think":
            # Affiche la réflexion en gris clair
            print(f"\033[90m{event.get('content', '')}\033[0m", end="", flush=True)

        elif t == "tool":
            status = event.get("status")
            name = event.get("name", "")
            if status == "start":
                print(f"\n  🔧 {name}...", flush=True)
            elif status == "end":
                preview = str(event.get("result", ""))[:80].replace("\n", " ")
                print(f"  ✓ {name}: {preview}...", flush=True)
            elif status == "error":
                print(f"  ✗ {name}: {event.get('result', '')}", flush=True)

        elif t == "error":
            print(f"\n  ❌ {event.get('content', '')}", flush=True)

        elif t == "usage":
            print(
                f"\n  [{event.get('prompt_tokens', 0)}→"
                f"{event.get('completion_tokens', 0)} tokens | "
                f"${event.get('total_cost', 0):.5f}]",
                flush=True,
            )