from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: str
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

class SystemMessage(Message):
    role: str = "system"

class HumanMessage(Message):
    role: str = "user"

class AIMessage(Message):
    role: str = "assistant"
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "role": self.role,
            "content": self.content,
        }
        
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
            
        return result

class ToolMessage(Message):
    role: str = "tool"
    tool_call_id: str
    name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "tool_call_id": self.tool_call_id,
            "name": self.name,
            "content": self.content if self.content is not None else ""
        }