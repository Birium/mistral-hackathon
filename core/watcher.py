import asyncio
import os
from pathlib import Path

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

import background
from background import run as run_background
from env import env

_subscribers: list[asyncio.Queue] = []

IGNORE_PATTERNS = []
IGNORE_DIRECTORIES = []


def _is_ignored_directory(path: str) -> bool:
    """Check if the event path is inside any ignored directory."""
    parts = Path(path).parts
    return any(ignored in parts for ignored in IGNORE_DIRECTORIES)


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
    loop = background._loop
    if loop is None:
        return
    for q in _subscribers:
        loop.call_soon_threadsafe(q.put_nowait, message)


class VaultHandler(PatternMatchingEventHandler):
    def __init__(self) -> None:
        super().__init__(
            patterns=["*"],
            ignore_patterns=IGNORE_PATTERNS,
            ignore_directories=False,
            case_sensitive=True,
        )

    def _should_ignore(self, event) -> bool:
        """Extra filtering for directory-based ignores."""
        return event.is_directory or _is_ignored_directory(event.src_path)

    def on_modified(self, event):
        if self._should_ignore(event):
            return
        broadcast({"type": "file_changed", "path": event.src_path})
        run_background(event.src_path)

    def on_created(self, event):
        if self._should_ignore(event):
            return
        broadcast({"type": "file_created", "path": event.src_path})

    def on_deleted(self, event):
        if self._should_ignore(event):
            return
        broadcast({"type": "file_deleted", "path": event.src_path})


async def start_watcher() -> None:
    vault_path = env.VAULT_PATH

    # Hand the running loop to background so it can submit coroutines safely
    background.set_loop(asyncio.get_running_loop())

    observer = Observer()
    observer.schedule(VaultHandler(), vault_path, recursive=True)
    observer.start()
    print(f"[watcher] started watching {vault_path}")
