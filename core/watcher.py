import os
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import background
from background import run as run_background

_subscribers: list[asyncio.Queue] = []


def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    try:
        _subscribers.remove(q)
    except ValueError:
        pass


def broadcast(message: dict) -> None:
    for q in _subscribers:
        q.put_nowait(message)


class VaultHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory or background.is_background_write(event.src_path):
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


async def start_watcher() -> None:
    vault_path = os.getenv("VAULT_PATH", "")
    if not vault_path:
        raise RuntimeError("VAULT_PATH env var is not set")

    # Hand the running loop to background so it can submit coroutines safely
    background.set_loop(asyncio.get_running_loop())

    observer = Observer()
    observer.schedule(VaultHandler(), vault_path, recursive=True)
    observer.start()
    print(f"[watcher] started watching {vault_path}")