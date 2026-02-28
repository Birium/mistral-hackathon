import json
import uuid
import job_queue as queue
import qmd
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
from watcher import subscribe, unsubscribe

router = APIRouter()


class UpdatePayload(BaseModel):
    content: str


class SearchPayload(BaseModel):
    query: str
    mode: str = Field(default="fast", pattern="^(fast|deep)$")
    scope: str = ""
    limit: int = Field(default=5, ge=1, le=20)


@router.post("/update")
async def update(payload: UpdatePayload):
    update_id = f"update-{uuid.uuid4().hex[:8]}"
    await queue.put({"id": update_id, "payload": payload})
    return {"status": "accepted", "id": update_id}


@router.post("/search")
async def search(payload: SearchPayload):
    results = await qmd.search(
        query=payload.query,
        mode=payload.mode,
        scope=payload.scope,
        limit=payload.limit,
    )
    return {"query": payload.query, "results": results}


@router.get("/sse")
async def sse(request: Request):
    async def event_stream():
        q = subscribe()
        try:
            while True:
                if await request.is_disconnected():
                    break
                event = await q.get()
                yield {"data": json.dumps(event)}
        finally:
            unsubscribe(q)

    return EventSourceResponse(event_stream())


@router.get("/tree")
async def tree():
    return {"tree": ""}
