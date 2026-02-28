import json
from typing import Optional, Any, Dict, Union, Callable
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.tools import tool, BaseTool as LangChainBaseTool

class BaseTool(BaseModel):
    """
    Base class for tools that can be used with LLM models.
    Wraps a Python function using LangChain's @tool decorator to automatically
    generate JSON schemas for the LLM.
    """
    
    tool: LangChainBaseTool = Field()
    result: Optional[str] = Field(default=None)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, func: Callable, **kwargs):
        # Automatically wrap the provided function with LangChain's @tool
        tool_obj = tool(func)
        super().__init__(tool=tool_obj, **kwargs)
        
    @property
    def name(self) -> str:
        """Expose the tool name directly for the LLMClient."""
        return self.tool.name
    
    def to_schema(self) -> Dict[str, Any]:
        """Convert the LangChain tool schema to the OpenAI/OpenRouter format."""
        parameters = {"type": "object", "properties": {}}
        if self.tool.args_schema:
            parameters = self.tool.args_schema.model_json_schema()
            
        return {
            "type": "function",
            "function": {
                "name": self.tool.name,
                "description": self.tool.description,
                "parameters": parameters
            }
        }
    
    def invoke(self, args: Union[str, Dict]) -> str:
        """Execute the tool with the given arguments and return the result as a string."""
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}
        
        # Invoke the underlying LangChain tool
        result = self.tool.invoke(args)
        
        # Store and return the result as a string
        self.result = str(result)
        return self.result