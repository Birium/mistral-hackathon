import os
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from background import run as run_background

_background_writes: set = set()   # paths being written by background job

# Simple SSE Pub/Sub
_subscribers = []

async def subscribe():
    q = asyncio.Queue()
    _subscribers.append(q)
    try:
        yield q
    finally:
        _subscribers.remove(q)

def broadcast(message: dict):
    for q in _subscribers:
        q.put_nowait(message)

class VaultHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path in _background_writes:
            return
        if event.is_directory:
            return
        
        broadcast({"type": "file_changed", "path": event.src_path})
        run_background(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        broadcast({"type": "file_created", "path": event.src_path})

    def on_deleted(self, event):
        if event.is_directory:
            return
        broadcast({"type": "file_deleted", "path": event.src_path})

async def start_watcher():
    vault_path = os.getenv("VAULT_PATH", "/vault")
    observer = Observer()
    handler = VaultHandler()
    observer.schedule(handler, vault_path, recursive=True)
    observer.start()
    print(f"[watcher] started watching {vault_path}")
