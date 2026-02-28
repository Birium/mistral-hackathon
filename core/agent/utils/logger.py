"""
Server-side agent event logger.

Two outputs:
  1. Human-readable → uvicorn stdout (unchanged)
  2. Structured NDJSON → AGENT_LOG_PATH (default: logs/agent_events.jsonl)

Each JSON line shape:
  { "ts": "...", "event": { ...raw event dict... } }

Import and call:
  log_agent_event(event)              — human log only
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Human-readable logger (unchanged)
# ---------------------------------------------------------------------------

logger = logging.getLogger("knower.agent")


def _fmt_args(args_str: str) -> str:
    if not args_str:
        return ""
    try:
        args = json.loads(args_str)
        return ", ".join(f'{k}="{v}"' for k, v in args.items())
    except (json.JSONDecodeError, TypeError):
        return args_str


# ---------------------------------------------------------------------------
# JSON file logger
# ---------------------------------------------------------------------------

_STARTED_AT = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

_LOG_DIR = Path(os.getenv("AGENT_LOG_DIR", "logs"))
_LOG_PATH = _LOG_DIR / f"agent_events_{_STARTED_AT}.jsonl"

_json_logger: logging.Logger | None = None


def _get_json_logger() -> logging.Logger:
    """Lazy singleton — creates file + handler once."""
    global _json_logger
    if _json_logger is not None:
        return _json_logger

    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(_LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))  # raw line only

    jl = logging.getLogger("knower.agent.json")
    jl.setLevel(logging.DEBUG)
    jl.addHandler(handler)
    jl.propagate = False  # don't bubble to uvicorn stdout

    _json_logger = jl
    return _json_logger


def log_raw_event(event: dict) -> None:
    """Write one event as a JSON line to AGENT_LOG_PATH."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
    }
    _get_json_logger().debug(json.dumps(record, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def log_agent_event(event: dict) -> None:
    """Log event to stdout (human-readable) and optionally to NDJSON file."""

    # --- structured JSON ---
    log_raw_event(event)

    # --- human-readable (unchanged) ---
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
