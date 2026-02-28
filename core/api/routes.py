import asyncio
import json
import os
from pathlib import Path
from typing import Optional

import frontmatter
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from watcher import subscribe, unsubscribe
from agent.utils.logger import log_agent_event

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


@router.post("/update")
async def update(payload: UpdatePayload):
    from agent.agent.update_agent import UpdateAgent

    agent = UpdateAgent()

    def _run() -> str:
        parts = []
        for event in agent.process(payload.user_query, inbox_ref=payload.inbox_ref):
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

    # Validate no path traversal
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
