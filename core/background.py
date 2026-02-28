import asyncio
import logging
from functions.frontmatter import write_frontmatter
import qmd as qmd_client

logger = logging.getLogger(__name__)

# Set once at startup by watcher.py
_loop: asyncio.AbstractEventLoop | None = None
_locked: bool = False

def set_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _loop
    _loop = loop

def lock() -> None:
    global _locked
    _locked = True

def unlock() -> None:
    global _locked
    _locked = False

def run(path: str) -> None:
    """Called from watchdog thread — must not block."""
    if _locked:
        logger.debug(f"[background] locked, skipping {path}")
        return
    if _loop is None:
        logger.error("[background] event loop not set, skipping")
        return
    logger.info(f"[background] triggered for {path}")
    asyncio.run_coroutine_threadsafe(_handle(path), _loop)

async def _handle(path: str) -> None:
    lock()
    write_frontmatter(path)

    ok = await qmd_client.reindex()
    if not ok:
        logger.error(f"[background] reindex failed for {path}, skipping reembed")
        return

    logger.info(f"[background] reindex done for {path}")
    unlock()

    # Uncomment to run full reembed on file change (slow, but ensures embeddings are always up to date)
    # ok = await qmd_client.reembed()
    # if not ok:
    #     logger.error(f"[background] reembed failed for {path}")
    # logger.info(f"[background] reembed done for {path}")
