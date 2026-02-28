from contextlib import asynccontextmanager
import asyncio
import logging

import job_queue
import qmd as qmd_client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from mcp_server.server import mcp
from watcher import start_watcher
from vault_init import init_vault

logger = logging.getLogger(__name__)

EMBED_INTERVAL_SECONDS = 5 * 60


async def _embed_loop() -> None:
    while True:
        await asyncio.sleep(EMBED_INTERVAL_SECONDS)
        logger.info("[embed-loop] running scheduled reembed")
        await qmd_client.reembed()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_vault()
    asyncio.create_task(job_queue.worker())
    await start_watcher()

    # Embed on mount (models already downloaded by start.sh first-boot path)
    logger.info("[startup] running initial reembed")
    await qmd_client.reembed()

    # Embed on timer
    asyncio.create_task(_embed_loop())

    yield


app = FastAPI(title="Knower Core", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.mount("/mcp", mcp.sse_app())
