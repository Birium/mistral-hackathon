import json
import traceback
from typing import List, Optional, Generator

from openai import OpenAI

from agent.schemas.message import Message, SystemMessage, AIMessage
from agent.schemas.tool import ToolCall
from agent.schemas.event import (
    BaseEvent, ThinkEvent, AnswerEvent, ToolEvent, UsageEvent, ErrorEvent
)
from agent.llm.config import ModelConfig
from agent.utils.raw_logger import object_logger


class LLMClient:
    def __init__(
        self,
        model: ModelConfig,
        system_prompt: str = "",
        tools: Optional[List] = None,
        reasoning: Optional[str] = None,  # "low" | "medium" | "high" | None
        api_key: str = None,
    ):
        from env import env
        self.client = OpenAI(
            base_url=model.base_url,
            api_key=api_key or env.OPENROUTER_API_KEY,
        )
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.reasoning = reasoning

        self.thinking: str = ""
        self.content: str = ""
        self.tool_calls: List[ToolCall] = []
        self.is_thinking_started: bool = False

    def stream(self, messages: List[Message]) -> Generator[str, None, None]:
        self._reset_state()
        usage_event = None

        try:
            all_messages = [SystemMessage(content=self.system_prompt)] + messages
            serialized = [m.to_dict() for m in all_messages]

            stream_params = {
                "model": self.model.model_id,
                "messages": serialized,
                "stream": True,
            }

            if self.tools:
                stream_params["tools"] = [t.to_schema() for t in self.tools]

            if self.reasoning is not None:
                stream_params["extra_body"] = {"reasoning": {"effort": self.reasoning}}

            object_logger.log_object(stream_params)

            stream = self.client.chat.completions.create(**stream_params)

            message_id = ""
            for chunk in stream:
                object_logger.log_event(chunk.model_dump_json())

                for event in self._process_chunk(chunk):
                    if hasattr(event, "id"):
                        message_id = event.id
                    if isinstance(event, UsageEvent):
                        usage_event = event
                    else:
                        yield json.dumps(event.model_dump())

            if self.tool_calls:
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

                for tc in self.tool_calls:
                    yield from self._execute_tool(tc)

            if usage_event:
                yield json.dumps(usage_event.model_dump())

        except Exception as e:
            traceback.print_exc()
            yield json.dumps(
                ErrorEvent(id="error", content=f"LLM stream error: {e}").model_dump()
            )
        finally:
            object_logger.save()

    def _execute_tool(self, tc: ToolCall) -> Generator[str, None, None]:
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

    def _process_chunk(self, chunk) -> Generator[BaseEvent, None, None]:
        message_id = getattr(chunk, "id", "id_")

        if hasattr(chunk, "usage") and chunk.usage:
            cost = self.model.calculate_cost(
                chunk.usage.prompt_tokens, chunk.usage.completion_tokens
            )
            yield UsageEvent(
                id=message_id,
                prompt_tokens=cost.prompt_tokens,
                completion_tokens=cost.completion_tokens,
                input_cost=cost.input_cost,
                output_cost=cost.output_cost,
                total_cost=cost.total_cost,
                usage_type="chat",
            )
            return

        if not chunk.choices:
            return

        delta = chunk.choices[0].delta

        # 1. Handle reasoning tokens
        if hasattr(delta, "reasoning") and delta.reasoning:
            thinking_chunk = delta.reasoning
            self.thinking += thinking_chunk
            if not self.is_thinking_started:
                self.is_thinking_started = True
                thinking_chunk = f"<think>\n{thinking_chunk}"
            yield ThinkEvent(content=thinking_chunk, id=message_id)

        # 2. Handle transition: if we were thinking, and now we get content, close the think block
        if self.is_thinking_started and hasattr(delta, "content") and delta.content:
            self.is_thinking_started = False
            yield ThinkEvent(content="\n</think>\n", id=message_id)

        # 3. Handle actual content tokens
        if hasattr(delta, "content") and delta.content:
            self.content += delta.content
            yield AnswerEvent(content=delta.content, id=message_id)

        # 4. Handle tool calls
        if hasattr(delta, "tool_calls") and delta.tool_calls:
            for tc_delta in delta.tool_calls:
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
        self.is_thinking_started = False