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
    queries: list[str] = Field(min_length=1)
    mode: str = Field(default="fast", pattern="^(fast|deep)$")
    scopes: list[str] | None = None
    limit: int = Field(default=10, ge=1, le=50)


@router.post("/search")
async def search(payload: SearchPayload):
    from functions.search import search as search_fn
    from dataclasses import asdict

    results = await search_fn(
        queries=payload.queries,
        mode=payload.mode,
        scopes=payload.scopes,
        limit=payload.limit,
    )
    return {"queries": payload.queries, "results": [asdict(r) for r in results]}


@router.post("/update")
async def update(payload: UpdatePayload):
    update_id = f"update-{uuid.uuid4().hex[:8]}"
    await queue.put({"id": update_id, "payload": payload})
    return {"status": "accepted", "id": update_id}


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
