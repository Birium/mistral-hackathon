import json
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Represents a tool call requested by the LLM."""

    tool_id: str
    id: str = ""
    name: str = ""
    arguments_str: str = ""
    arguments: Optional[Dict[str, Any]] = None
    result_str: Optional[str] = None
    result: Optional[Any] = None

    def parse_arguments(self):
        if self.arguments_str and not self.arguments:
            try:
                self.arguments = json.loads(self.arguments_str)
            except (json.JSONDecodeError, TypeError):
                self.arguments = {}

    def set_result(self, result: Any) -> None:
        if result is None:
            self.result = ""
            self.result_str = ""
        else:
            self.result = result
            self.result_str = (
                json.dumps(result) if isinstance(result, (dict, list)) else str(result)
            )

    def to_message(self) -> Dict[str, Any]:
        """Returns a tool result message dict for the LLM conversation."""
        return {
            "role": "tool",
            "tool_call_id": self.tool_id,
            "name": self.name,
            "content": self.result_str if self.result_str is not None else "",
        }