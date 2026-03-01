import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp.utilities.lifespan import combine_lifespans

import job_queue
import qmd as qmd_client
from api.routes import router
from mcp_server.server import mcp
from vault_init import init_vault
from watcher import start_watcher

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    init_vault()
    asyncio.create_task(job_queue.worker())
    await start_watcher()
    logger.info("[startup] running initial reembed")
    await qmd_client.reembed()
    yield


mcp_app = mcp.http_app(path="/mcp")

app = FastAPI(
    title="Knower Core",
    lifespan=combine_lifespans(app_lifespan, mcp_app.lifespan),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for route in mcp_app.routes:
    app.router.routes.append(route)

app.include_router(router)
