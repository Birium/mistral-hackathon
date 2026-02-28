import asyncio
import logging
import qmd as qmd_client

logger = logging.getLogger(__name__)


def run(path: str):
    logger.info(f"[background] triggered for {path}")
    asyncio.run(_handle(path))


async def _handle(path: str):
    # TODO: token count + frontmatter update here
    await qmd_client.reindex()
    logger.info(f"[background] reindex done for {path}")
