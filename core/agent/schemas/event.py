from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class BaseEvent(BaseModel):
    type: str
    id: str
    
class ThinkEvent(BaseEvent):
    type: str = "think"
    content: str
    
class AnswerEvent(BaseEvent):
    type: str = "answer"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
class ToolEvent(BaseEvent):
    type: str = "tool"
    tool_id: str
    name: str
    arguments: str
    status: str  # "start", "pending", "end", ou "error"
    result: Optional[str] = None
    
class ToolEventStream(ToolEvent):
    content: Optional[str] = None
    
class UsageEvent(BaseEvent):
    type: str = "usage"
    usage_type: str # "tool" ou "chat"
    prompt_tokens: int
    completion_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float

class ErrorEvent(BaseEvent):
    type: str = "error"
    content: str