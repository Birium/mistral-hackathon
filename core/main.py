from contextlib import asynccontextmanager
import asyncio

import job_queue
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from mcp_server.server import mcp
from watcher import start_watcher
from vault_init import init_vault


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_vault()
    asyncio.create_task(job_queue.worker())
    await start_watcher()
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