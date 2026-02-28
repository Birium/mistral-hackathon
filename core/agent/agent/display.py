"""
Terminal display for agent events.

Consumes the event stream from agents and formats everything
for human-readable terminal output. The agent itself never prints —
this is the only place where events become visible text.

Events handled: answer, think, tool (start/end/error), usage, error.
"""

import json


def _format_tool_args(args_str: str) -> str:
    if not args_str:
        return ""
    try:
        args = json.loads(args_str)
        if not args:
            return ""
        return ", ".join(f'{k}="{v}"' for k, v in args.items())
    except (json.JSONDecodeError, TypeError):
        return args_str


def _indent_result(result: str) -> str:
    if not result:
        return "   (empty)"
    lines = result.splitlines()
    return "\n".join(f"   {line}" for line in lines)


class Display:
    def __init__(self):
        self.agent_started = False

    def event(self, data: dict):
        t = data.get("type")

        if t == "answer" and not data.get("tool_calls"):
            if not self.agent_started:
                print("\nAgent: ", end="", flush=True)
                self.agent_started = True
            print(data.get("content", ""), end="", flush=True)

        elif t == "think":
            print(f"\033[90m{data.get('content', '')}\033[0m", end="", flush=True)

        elif t == "tool":
            status = data.get("status")
            name = data.get("name", "")
            args_str = data.get("arguments", "")

            if status == "start":
                formatted = _format_tool_args(args_str)
                print(f"\nToolCall -> {name}({formatted})", flush=True)
            elif status == "end":
                result = str(data.get("result", ""))
                print(f"ToolResult:\n```\n{_indent_result(result)}\n```", flush=True)
            elif status == "error":
                print(f"ToolError -> {name}: {data.get('result', '')}", flush=True)

        elif t == "error":
            print(f"\nError: {data.get('content', '')}", flush=True)

        elif t == "usage":
            prompt = data.get("prompt_tokens", 0)
            completion = data.get("completion_tokens", 0)
            cost = data.get("total_cost", 0)
            print(f"\nTokens: [{prompt} in / {completion} out | ${cost:.5f}]", flush=True)