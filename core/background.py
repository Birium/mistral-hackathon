import asyncio
import logging
import qmd as qmd_client

logger = logging.getLogger(__name__)

# Set once at startup by watcher.py
_loop: asyncio.AbstractEventLoop | None = None

def set_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _loop
    _loop = loop

def run(path: str) -> None:
    """Called from watchdog thread — must not block."""
    if _loop is None:
        logger.error("[background] event loop not set, skipping")
        return
    logger.info(f"[background] triggered for {path}")
    asyncio.run_coroutine_threadsafe(_handle(path), _loop)

async def _handle(path: str) -> None:
    # TODO: token count + frontmatter update
    await qmd_client.reindex()
    logger.info(f"[background] reindex done for {path}")