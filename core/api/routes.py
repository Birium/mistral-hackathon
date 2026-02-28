import json
import uuid
import job_queue as queue
from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from watcher import subscribe, unsubscribe

router = APIRouter()

class UpdatePayload(BaseModel):
    content: str

@router.post("/update")
async def update(payload: UpdatePayload):
    update_id = f"update-{uuid.uuid4().hex[:8]}"
    await queue.put({"id": update_id, "payload": payload})
    return {"status": "accepted", "id": update_id}

@router.post("/search")
async def search(payload: dict):
    # return hardcoded markdown string
    return {"result": f"## Search Results\n\nFound mocked results for `{payload.get('query', '')}`."}

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
    # Return vault directory tree as string/json (using mcp tool's tree function for simplicity, or we can structure it)
    return {"tree": ""}
