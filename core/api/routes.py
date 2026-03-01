import asyncio
import json
import os
import queue as stdlib_queue
import threading
from pathlib import Path
from typing import Optional

import frontmatter
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from watcher import subscribe, unsubscribe
from agent.utils.logger import RequestLogger

router = APIRouter()


class UpdatePayload(BaseModel):
    user_query: str
    inbox_ref: Optional[str] = None


class SearchPayload(BaseModel):
    user_query: str


def _node_to_dict(node) -> dict:
    return {
        "name": node.name,
        "path": str(node.path),
        "type": "directory" if node.is_directory else "file",
        "tokens": node.tokens,
        "updated_at": node.mtime.isoformat() if node.mtime else None,
        "children": [_node_to_dict(c) for c in node.children] if node.is_directory else None,
    }


# ---------------------------------------------------------------------------
# Streaming bridge: sync agent generator → async NDJSON stream
# ---------------------------------------------------------------------------

async def _stream_agent(agent_iter, request_name: str):
    """
    Run a synchronous agent generator in a dedicated thread and yield
    each event as a NDJSON line (one JSON object per line).

    Uses a stdlib queue to bridge the sync thread → async generator
    safely. A None sentinel signals the end of the stream.
    """
    q = stdlib_queue.Queue()

    def _worker():
        log = RequestLogger(request_name)
        try:
            for event in agent_iter:
                log.log(event)
                q.put(event)
        except Exception as e:
            q.put({"type": "error", "id": "stream_error", "content": str(e)})
        finally:
            log.save()
            q.put(None)  # sentinel

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

    while True:
        # await on a thread so we don't block the event loop
        event = await asyncio.to_thread(q.get)
        if event is None:
            break
        yield json.dumps(event) + "\n"

    yield json.dumps({"type": "done"}) + "\n"


def _streaming_response(agent_iter, request_name: str) -> StreamingResponse:
    """Build a StreamingResponse with anti-buffering headers."""
    return StreamingResponse(
        _stream_agent(agent_iter, request_name),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/update")
async def update(payload: UpdatePayload):
    from agent.agent.update_agent import UpdateAgent

    agent = UpdateAgent()
    return _streaming_response(
        agent.process(payload.user_query, inbox_ref=payload.inbox_ref),
        "update",
    )


@router.post("/search")
async def search(payload: SearchPayload):
    from agent.agent.search_agent import SearchAgent

    agent = SearchAgent()
    return _streaming_response(
        agent.process(payload.user_query),
        "search",
    )


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
    from functions.tree.scanner import scan

    vault_path = Path(os.getenv("VAULT_PATH", ""))
    try:
        node = scan(vault_path)
        return {"tree": _node_to_dict(node)}
    except FileNotFoundError:
        return {"tree": None}


@router.get("/file")
async def get_file(path: str):
    vault_path = Path(os.getenv("VAULT_PATH", ""))

    try:
        resolved = (vault_path / path).resolve()
        resolved.relative_to(vault_path.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path")

    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        post = frontmatter.load(str(resolved))
        content = post.content
    except Exception:
        content = resolved.read_text(encoding="utf-8")

    return {"path": path, "content": content}


@router.get("/inbox/{name}")
async def get_inbox(name: str):
    vault_path = Path(os.getenv("VAULT_PATH", ""))
    inbox_dir = vault_path / "inbox" / name

    if not inbox_dir.exists() or not inbox_dir.is_dir():
        raise HTTPException(status_code=404, detail="Inbox item not found")

    review_path = inbox_dir / "review.md"
    review_content = ""
    if review_path.exists():
        try:
            post = frontmatter.load(str(review_path))
            review_content = post.content
        except Exception:
            review_content = review_path.read_text(encoding="utf-8")

    input_files = [
        f.name
        for f in inbox_dir.iterdir()
        if f.is_file() and f.name != "review.md" and not f.name.startswith(".")
    ]

    return {"name": name, "review": review_content, "input_files": sorted(input_files)}


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    import httpx
    from env import env

    api_key = env.ELEVENLABS_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not set")

    content = await audio.read()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={"xi-api-key": api_key},
            files={"file": (audio.filename or "audio.webm", content, audio.content_type or "audio/webm")},
            data={"model_id": "scribe_v1"},
            timeout=30.0,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return {"text": resp.json().get("text", "")}