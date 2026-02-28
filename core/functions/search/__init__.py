"""
search(queries, mode, scopes) — public entry point.

from functions.search import search
results = await search(["décision", "API"], mode="fast", scopes=["vault/projects/startup-x/*"])
"""

from .models import SearchResult
from .query import run


async def search(
    queries: list[str],
    mode: str = "fast",
    scopes: list[str] | None = None,
    limit: int = 10,
) -> list[SearchResult]:
    if mode not in ("fast", "deep"):
        raise ValueError(f"Invalid mode: {mode!r}. Use 'fast' or 'deep'.")
    if not queries:
        raise ValueError("queries must be a non-empty list")
    return await run(queries=queries, mode=mode, scopes=scopes, limit=limit)
