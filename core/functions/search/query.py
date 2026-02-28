"""
Multi-query fan-out, merge, dedup, exclusion, scope, sort.
"""

import asyncio
import logging

import qmd as qmd_client
from .models import SearchResult
from .exclusions import is_excluded
from .scope import matches_scopes
from .snippet import parse_snippet

logger = logging.getLogger(__name__)

VAULT_URI_PREFIX = "qmd://vault/"


def _strip_path(file_uri: str) -> str:
    """'qmd://vault/projects/x/state.md' → 'projects/x/state.md'"""
    if file_uri.startswith(VAULT_URI_PREFIX):
        return file_uri[len(VAULT_URI_PREFIX) :]
    return file_uri


async def run(
    queries: list[str],
    mode: str,
    scopes: list[str] | None,
    limit: int = 10,
) -> list[SearchResult]:
    if not queries:
        raise ValueError("queries must be a non-empty list")

    logger.info(f"[search] running search with queries={queries}, mode={mode}, scopes={scopes}, limit={limit}")
    # Fan out all queries concurrently
    tasks = [qmd_client.raw_search(q, mode=mode, limit=limit * 2) for q in queries]
    per_query_results: list[list[dict]] = await asyncio.gather(*tasks)

    # Merge: key=file URI, keep highest score
    merged: dict[str, dict] = {}
    for results in per_query_results:
        for r in results:
            key = r.get("file", r.get("docid", ""))
            if key not in merged or r.get("score", 0) > merged[key].get("score", 0):
                merged[key] = r

    # Build SearchResult objects, apply exclusions + scope
    output: list[SearchResult] = []
    for raw in merged.values():
        path = _strip_path(raw.get("file", ""))
        if not path:
            continue
        if is_excluded(path):
            logger.debug(f"[search] excluded: {path}")
            continue
        if not matches_scopes(path, scopes):
            continue

        score = round(float(raw.get("score", 0.0)), 4)
        snippet = raw.get("snippet", "")
        lines_range, chunk_with_context = parse_snippet(snippet)

        output.append(
            SearchResult(
                path=path,
                score=score,
                lines=lines_range,
                chunk_with_context=chunk_with_context,
            )
        )

    print(f"SEARCH DEBUG: merged number = {len(merged)}, after exclusions/scopes = {len(output)}")
    output.sort(key=lambda r: r.score, reverse=True)
    return output[:limit]
