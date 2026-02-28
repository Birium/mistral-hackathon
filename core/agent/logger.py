"""
Server-side agent event logger.
Same events as Display, but uses Python logging → appears in uvicorn stdout.
Import and call log_agent_event(event) wherever agents run outside the terminal.
"""

import json
import logging

logger = logging.getLogger("knower.agent")


def _fmt_args(args_str: str) -> str:
    if not args_str:
        return ""
    try:
        args = json.loads(args_str)
        return ", ".join(f'{k}="{v}"' for k, v in args.items())
    except (json.JSONDecodeError, TypeError):
        return args_str


def log_agent_event(event: dict) -> None:
    t = event.get("type")

    if t == "think":
        logger.debug("[think] %s", event.get("content", "")[:120])

    elif t == "answer" and not event.get("tool_calls"):
        logger.info("[answer] %s", event.get("content", "")[:200])

    elif t == "tool":
        status = event.get("status")
        name = event.get("name", "")
        if status == "start":
            logger.info("[tool→] %s(%s)", name, _fmt_args(event.get("arguments", "")))
        elif status == "end":
            result = str(event.get("result", ""))
            logger.info("[tool←] %s → %s", name, result[:120])
        elif status == "error":
            logger.warning("[tool✗] %s: %s", name, event.get("result", ""))

    elif t == "usage":
        logger.info(
            "[usage] %d in / %d out | $%.5f",
            event.get("prompt_tokens", 0),
            event.get("completion_tokens", 0),
            event.get("total_cost", 0),
        )

    elif t == "error":
        logger.error("[error] %s", event.get("content", ""))
