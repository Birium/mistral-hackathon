"""
Per-request agent event logger.

Handles two outputs:
  1. Human-readable → uvicorn stdout (always active)
  2. Structured NDJSON → logs/requests/{name}_{timestamp}.jsonl (DEV mode only)

Usage in routes/tools:
  logger = RequestLogger("search")
  try:
      for event in agent.process(...):
          logger.log(event)
  finally:
      logger.save()
"""

import json
import logging
from env import env
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Human-readable logger setup
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
# Request Logger Class
# ---------------------------------------------------------------------------

class RequestLogger:
    def __init__(self, request_name: str):
        """
        Initialize a new logger for a specific API request.
        
        Args:
            request_name: Identifier for the request (e.g., "search", "update")
        """
        self.request_name = request_name
        self.events = []
        self.is_dev = env.DEV
        self.start_time = datetime.now(timezone.utc)

    def log(self, event: dict) -> None:
        """Log event to stdout (human-readable) and buffer it for the JSONL file."""
        
        # --- 1. Buffer for structured JSON (DEV only) ---
        if self.is_dev:
            record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                **event
            }
            self.events.append(record)

        # --- 2. Human-readable stdout (Always active) ---
        t = event.get("type")

        if t == "think":
            logger.debug("[think] %s", event.get("content", "")[:120].replace("\n", " "))

        elif t == "answer" and not event.get("tool_calls"):
            logger.info("[answer] %s", event.get("content", "")[:200].replace("\n", " "))

        elif t == "tool":
            status = event.get("status")
            name = event.get("name", "")
            if status == "start":
                logger.info("[tool→] %s(%s)", name, _fmt_args(event.get("arguments", "")))
            elif status == "end":
                result = str(event.get("result", ""))
                logger.info("[tool←] %s → %s", name, result[:120].replace("\n", " "))
            elif status == "error":
                logger.warning("[tool✗] %s: %s", name, event.get("result", "").replace("\n", " "))

        elif t == "usage":
            logger.info(
                "[usage] %d in / %d out | $%.5f",
                event.get("prompt_tokens", 0),
                event.get("completion_tokens", 0),
                event.get("total_cost", 0),
            )

        elif t == "error":
            logger.error("[error] %s", event.get("content", ""))

    def save(self) -> None:
        """Write all buffered events to a single JSONL file if DEV mode is enabled."""
        if not self.is_dev or not self.events:
            return

        log_dir = Path("logs/requests")
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = self.start_time.strftime("%m-%d-%H-%M-%S")
        filename = f"{self.request_name}_{timestamp}.jsonl"
        filepath = log_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for record in self.events:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            logger.debug(f"[logger] Saved request logs to {filepath}")
        except Exception as e:
            logger.error(f"[logger] Failed to save request logs: {e}")