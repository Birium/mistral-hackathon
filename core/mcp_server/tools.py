"""
MCP tool implementations.

search → SearchAgent (was: functions.search directly)
write  → raw atomic filesystem write (unchanged — MCP clients expect deterministic path)
update → UpdateAgent (new — intelligent vault routing for unstructured content)
"""

import asyncio
import os

VAULT = os.getenv("VAULT_PATH", "")
if not VAULT:
    raise RuntimeError("VAULT_PATH env var is not set")

# ---------------------------------------------------------------------------
# update — routes through UpdateAgent
# ---------------------------------------------------------------------------


async def update(content: str) -> str:
    """Send unstructured content to the update agent for intelligent vault routing.

    The agent decides where to store it, how to structure it, and logs to changelog.
    For direct deterministic writes, use `write` instead.
    """
    from agent.agent.update_agent import UpdateAgent
    from agent.logger import log_agent_event

    agent = UpdateAgent()

    def _run() -> str:
        parts = []
        for event in agent.process(content):
            log_agent_event(event)
            if event.get("type") == "answer" and not event.get("tool_calls"):
                parts.append(event.get("content", ""))
        return "".join(parts)

    result = await asyncio.to_thread(_run)
    return result or "Update agent processed the content."


# ---------------------------------------------------------------------------
# search — routes through SearchAgent
# ---------------------------------------------------------------------------


async def search(
    content: str
) -> str:
    """Search the vault using the search agent (BM25 or semantic pipeline).

    The agent runs the query, retrieves results, and formats them with context.
    """
    from agent.agent.search_agent import SearchAgent
    from agent.logger import log_agent_event

    agent = SearchAgent()

    def _run() -> str:
        parts = []
        for event in agent.process(content):
            log_agent_event(event)
            if event.get("type") == "answer" and not event.get("tool_calls"):
                parts.append(event.get("content", ""))
        return "".join(parts)

    try:
        result = await asyncio.to_thread(_run)
    except Exception as e:
        return f"[search error] {e}"

    return result or f"No answer returned for: {content}"
