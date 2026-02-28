import asyncio
import logging
import os
import qmd as qmd_client

from functions.frontmatter.tokens import update_tokens

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
    # if it's not a new file, update file frontmatter
    # use OS tools to avoid concurrency issues
    if os.stat(path).st_birthtime != os.path.getmtime(path):
        update_tokens(path)

    ok = await qmd_client.reindex()
    if not ok:
        logger.error(f"[background] reindex failed for {path}, skipping reembed")
        return

    logger.info(f"[background] reindex done for {path}")

    # Uncomment to run full reembed on file change (slow, but ensures embeddings are always up to date)
    # ok = await qmd_client.reembed()
    # if not ok:
    #     logger.error(f"[background] reembed failed for {path}")
    # logger.info(f"[background] reembed done for {path}")
