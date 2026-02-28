import asyncio
import json
import uuid

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from watcher import subscribe, unsubscribe

router = APIRouter()


class UpdateAndSearchPayload(BaseModel):
    user_query: str


@router.post("/search")
async def search(payload: UpdateAndSearchPayload):
    from agent.agent.search_agent import SearchAgent
    from agent.logger import log_agent_event

    agent = SearchAgent()
    query_str = payload.user_query

    def _run() -> str:
        parts = []
        for event in agent.process(query_str):
            log_agent_event(event)
            if event.get("type") == "answer" and not event.get("tool_calls"):
                parts.append(event.get("content", ""))
        return "".join(parts)

    answer = await asyncio.to_thread(_run)
    return {"queries": [query_str], "answer": answer}


@router.post("/update")
async def update(payload: UpdateAndSearchPayload):
    from agent.agent.update_agent import UpdateAgent
    from agent.logger import log_agent_event

    agent = UpdateAgent()

    def _run() -> str:
        parts = []
        for event in agent.process(payload.user_query):
            log_agent_event(event)
            if event.get("type") == "answer" and not event.get("tool_calls"):
                parts.append(event.get("content", ""))
        return "".join(parts)

    result = await asyncio.to_thread(_run)
    return {"status": "processed", "result": result}


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
