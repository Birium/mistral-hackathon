import json
import re
import inspect
from typing import get_type_hints, Any, Dict, Callable, Union

from pydantic import BaseModel, Field, ConfigDict, create_model


def _parse_docstring(func: Callable) -> tuple[str, dict[str, str]]:
    """
    Extract description and per-param descriptions from a Google-style docstring.

    Returns:
        (description, {param_name: param_description})

    Raises:
        ValueError: If the function has no docstring or an empty description.
    """
    doc = inspect.getdoc(func)
    if not doc:
        raise ValueError(
            f"Function '{func.__name__}' has no docstring. "
            f"A docstring is required for tool schema generation."
        )

    # Split on the "Args:" section
    parts = re.split(r"\n\s*Args:\s*\n", doc, maxsplit=1)
    description = parts[0].strip()

    if not description:
        raise ValueError(
            f"Function '{func.__name__}' has an empty description in its docstring."
        )

    param_descs: dict[str, str] = {}
    if len(parts) > 1:
        current_param: str | None = None
        current_lines: list[str] = []

        for line in parts[1].splitlines():
            # Match "param_name: desc" or "param_name (type): desc"
            match = re.match(r"\s+(\w+)\s*(?:\(.*?\))?\s*:\s*(.*)", line)
            if match:
                # Save previous param before starting a new one
                if current_param:
                    param_descs[current_param] = " ".join(current_lines).strip()
                current_param = match.group(1)
                first_line = match.group(2).strip()
                current_lines = [first_line] if first_line else []
            elif current_param and line.strip():
                # Continuation line for the current param
                current_lines.append(line.strip())

        # Save the last param
        if current_param:
            param_descs[current_param] = " ".join(current_lines).strip()

    return description, param_descs


def _build_args_schema(func: Callable, param_docs: dict[str, str]) -> type[BaseModel]:
    """
    Build a Pydantic model from function signature + docstring param descriptions.

    Uses type hints for field types, inspect.signature for defaults,
    and parsed docstring for Field descriptions.
    """
    hints = get_type_hints(func)
    hints.pop("return", None)

    sig = inspect.signature(func)

    fields: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        annotation = hints.get(name, Any)
        description = param_docs.get(name, "")
        default = ... if param.default is inspect.Parameter.empty else param.default
        fields[name] = (annotation, Field(default=default, description=description))

    return create_model(f"{func.__name__}_args", **fields)


class BaseTool(BaseModel):
    """
    Tool wrapper that generates OpenAI-compatible schemas from plain Python functions.

    Requires the wrapped function to have a Google-style docstring with:
      - A description line (becomes the tool description in the API schema)
      - An Args section with per-param descriptions (becomes parameter descriptions)

    Usage:
        ReadTool = BaseTool(read_function)
        schema = ReadTool.to_schema()    # OpenAI tool schema dict
        result = ReadTool.invoke({"paths": ["file.md"]})
    """

    name: str = ""
    description: str = ""
    args_schema: Any = None
    fn: Callable = lambda: None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, func: Callable, **kwargs):
        description, param_docs = _parse_docstring(func)
        schema = _build_args_schema(func, param_docs)

        super().__init__(
            name=func.__name__,
            description=description,
            args_schema=schema,
            fn=func,
            **kwargs,
        )

    def to_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI/OpenRouter tool schema format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema(),
            },
        }

    def invoke(self, args: Union[str, Dict]) -> str:
        """Execute the tool with the given arguments and return the result as a string."""
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except (json.JSONDecodeError, TypeError):
                args = {}

        result = self.fn(**args)
        return str(result) if result is not None else ""