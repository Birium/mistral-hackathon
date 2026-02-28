import json
import traceback
from typing import List, Optional, Generator

from openai import OpenAI

from schemas.message import Message, SystemMessage, AIMessage
from schemas.tool import ToolCall
from schemas.event import (
    BaseEvent, ThinkEvent, AnswerEvent, ToolEvent, UsageEvent, ErrorEvent
)
from llm.config import ModelConfig


class LLMClient:
    def __init__(
        self,
        model: ModelConfig,
        system_prompt: str = "",
        tools: Optional[List] = None,
        reasoning_effort: str = "low",
        api_key: str = None,
    ):
        from env import env  # lazy import to avoid circular
        self.client = OpenAI(
            base_url=model.base_url,
            api_key=api_key or env.OPENROUTER_API_KEY,
        )
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.reasoning_effort = reasoning_effort

        # State reset on each stream() call
        self.thinking: str = ""
        self.content: str = ""
        self.tool_calls: List[ToolCall] = []
        self.last_event_type: Optional[str] = None
        self.is_thinking_started: bool = False

    def stream(self, messages: List[Message]) -> Generator[str, None, None]:
        """
        Stream LLM responses as JSON event strings.
        Handles tool calls inline — executes them and appends results.
        """
        self._reset_state()

        try:
            all_messages = [SystemMessage(content=self.system_prompt)] + messages
            serialized = [m.to_dict() for m in all_messages]

            stream_params = {
                "model": self.model.model_id,
                "messages": serialized,
                "stream": True,
                "reasoning_effort": self.reasoning_effort,
            }

            if self.tools:
                stream_params["tools"] = [t.to_schema() for t in self.tools]

            stream = self.client.chat.completions.create(**stream_params)

            message_id = ""
            for chunk in stream:
                event = self._process_chunk(chunk)
                if event:
                    if hasattr(event, "id"):
                        message_id = event.id
                    yield json.dumps(event.model_dump())

            # If tool calls were requested — execute them and yield results
            if self.tool_calls:
                # Emit the assistant message with tool_calls
                tool_calls_data = [
                    {
                        "id": tc.tool_id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": tc.arguments_str},
                    }
                    for tc in self.tool_calls
                ]
                yield json.dumps(
                    AnswerEvent(id=message_id, content="", tool_calls=tool_calls_data).model_dump()
                )

                # Execute each tool and yield events
                for tc in self.tool_calls:
                    yield from self._execute_tool(tc)

        except Exception as e:
            traceback.print_exc()
            yield json.dumps(
                ErrorEvent(id="error", content=f"LLM stream error: {e}").model_dump()
            )

    def _execute_tool(self, tc: ToolCall) -> Generator[str, None, None]:
        """Find the matching tool, run it, yield events."""
        tool = next((t for t in self.tools if t.name == tc.name), None)

        yield json.dumps(
            ToolEvent(id=tc.id, tool_id=tc.tool_id, name=tc.name,
                      arguments=tc.arguments_str, status="start").model_dump()
        )

        if tool is None:
            tc.set_result(f"Tool '{tc.name}' not found.")
            yield json.dumps(
                ToolEvent(id=tc.id, tool_id=tc.tool_id, name=tc.name,
                          arguments=tc.arguments_str, status="error",
                          result=tc.result_str).model_dump()
            )
            return

        try:
            tc.parse_arguments()
            result = tool.invoke(tc.arguments or {})
            tc.set_result(result)
            yield json.dumps(
                ToolEvent(id=tc.id, tool_id=tc.tool_id, name=tc.name,
                          arguments=tc.arguments_str, status="end",
                          result=tc.result_str).model_dump()
            )
        except Exception as e:
            tc.set_result(f"Error: {e}")
            yield json.dumps(
                ToolEvent(id=tc.id, tool_id=tc.tool_id, name=tc.name,
                          arguments=tc.arguments_str, status="error",
                          result=tc.result_str).model_dump()
            )

    def _process_chunk(self, chunk) -> Optional[BaseEvent]:
        """Parse one streaming chunk into an event."""
        message_id = getattr(chunk, "id", "id_")

        # Usage chunk
        if hasattr(chunk, "usage") and chunk.usage:
            cost = self.model.calculate_cost(
                chunk.usage.prompt_tokens, chunk.usage.completion_tokens
            )
            return UsageEvent(
                id=message_id,
                prompt_tokens=cost.prompt_tokens,
                completion_tokens=cost.completion_tokens,
                input_cost=cost.input_cost,
                output_cost=cost.output_cost,
                total_cost=cost.total_cost,
                usage_type="chat",
            )

        if not chunk.choices:
            return None

        delta = chunk.choices[0].delta

        # Thinking / reasoning
        if hasattr(delta, "reasoning") and delta.reasoning:
            thinking_chunk = delta.reasoning
            self.thinking += thinking_chunk
            if not self.is_thinking_started:
                self.is_thinking_started = True
                thinking_chunk = f"<think>\n{thinking_chunk}"
            return ThinkEvent(content=thinking_chunk, id=message_id)

        # Close thinking block if we were thinking
        if self.is_thinking_started and not (hasattr(delta, "reasoning") and delta.reasoning):
            self.is_thinking_started = False
            return ThinkEvent(content="\n</think>\n", id=message_id)

        # Text content
        if hasattr(delta, "content") and delta.content:
            self.content += delta.content
            return AnswerEvent(content=delta.content, id=message_id)

        # Tool calls
        if hasattr(delta, "tool_calls") and delta.tool_calls:
            for tc_delta in delta.tool_calls:
                # Extend tool_calls list if needed
                while len(self.tool_calls) <= tc_delta.index:
                    self.tool_calls.append(
                        ToolCall(
                            tool_id=f"call_{len(self.tool_calls)}",
                            id=message_id,
                        )
                    )
                current = self.tool_calls[tc_delta.index]
                if tc_delta.id:
                    current.tool_id = tc_delta.id
                if hasattr(tc_delta, "function") and tc_delta.function:
                    if tc_delta.function.name:
                        current.name = tc_delta.function.name
                    if tc_delta.function.arguments:
                        current.arguments_str += tc_delta.function.arguments

        return None

    def get_tool_calls(self) -> List[ToolCall]:
        return self.tool_calls

    def get_full_response(self) -> AIMessage:
        return AIMessage(
            content=self.content or None,
            tool_calls=[
                {
                    "id": tc.tool_id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments_str},
                }
                for tc in self.tool_calls
            ] if self.tool_calls else [],
        )

    def _reset_state(self):
        self.thinking = ""
        self.content = ""
        self.tool_calls = []
        self.last_event_type = None
        self.is_thinking_started = False