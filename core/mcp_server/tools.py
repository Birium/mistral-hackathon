import asyncio
import os

VAULT = os.getenv("VAULT_PATH", "")
if not VAULT:
    raise RuntimeError("VAULT_PATH env var is not set")


async def update(content: str) -> str:
    """Send unstructured content to the update agent for intelligent vault routing."""
    from agent.agent.update_agent import UpdateAgent
    from agent.utils.logger import RequestLogger

    agent = UpdateAgent()

    def _run() -> str:
        log = RequestLogger("update")
        try:
            parts = []
            for event in agent.process(content):
                log.log(event)
                if event.get("type") == "answer" and not event.get("tool_calls"):
                    parts.append(event.get("content", ""))
            return "".join(parts)
        finally:
            log.save()

    result = await asyncio.to_thread(_run)
    return result or "Update agent processed the content."


async def search(content: str) -> str:
    """Search the vault using the search agent."""
    from agent.agent.search_agent import SearchAgent
    from agent.utils.logger import RequestLogger

    agent = SearchAgent()

    def _run() -> str:
        log = RequestLogger("search")
        try:
            parts = []
            for event in agent.process(content):
                log.log(event)
                if event.get("type") == "answer" and not event.get("tool_calls"):
                    parts.append(event.get("content", ""))
            return "".join(parts)
        finally:
            log.save()

    try:
        result = await asyncio.to_thread(_run)
    except Exception as e:
        return f"[search error] {e}"

    return result or f"No answer returned for: {content}"