import asyncio
import json

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from watcher import subscribe, unsubscribe
from agent.utils.logger import log_agent_event

router = APIRouter()


class UpdatePayload(BaseModel):
    user_query: str


class SearchPayload(BaseModel):
    user_query: str


@router.post("/update")
async def update(payload: UpdatePayload):
    from agent.agent.update_agent import UpdateAgent

    agent = UpdateAgent()

    def _run() -> str:
        parts = []
        for event in agent.process(payload.user_query):
            log_agent_event(event)
            if event.get("type") == "answer" and not event.get("tool_calls"):
                parts.append(event.get("content", ""))
        return "".join(parts)

    result = await asyncio.to_thread(_run)
    return {"status": "done", "result": result}


@router.post("/search")
async def search(payload: SearchPayload):
    from agent.agent.search_agent import SearchAgent

    agent = SearchAgent()

    def _run() -> str:
        parts = []
        for event in agent.process(payload.user_query):
            log_agent_event(event)
            if event.get("type") == "answer" and not event.get("tool_calls"):
                parts.append(event.get("content", ""))
        return "".join(parts)

    answer = await asyncio.to_thread(_run)
    return {"queries": [payload.user_query], "answer": answer}


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