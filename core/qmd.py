import asyncio
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

QMD_TIMEOUT_FAST = 30   # BM25 — always instant
QMD_TIMEOUT_DEEP = 120  # CPU inference — can be slow

def _run_qmd(args: list[str], timeout: int = QMD_TIMEOUT_FAST) -> str:
    cmd = ["qmd"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            logger.error(f"[qmd] Error: {result.stderr.strip()}")
            return ""
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"[qmd] Timeout after {timeout}s: {cmd}")
        return ""
    except FileNotFoundError:
        logger.error("[qmd] qmd binary not found in PATH")
        return ""

async def _run_qmd_async(args: list[str]) -> str:
    """Non-blocking wrapper for async context."""
    return await asyncio.to_thread(_run_qmd, args)


def _parse_json_output(raw: str) -> list[dict]:
    """Parse qmd --json output. Returns empty list on failure."""
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error(f"[qmd] Failed to parse JSON: {raw[:200]}")
        return []


def _apply_scope(results: list[dict], scope: str) -> list[dict]:
    """Post-filter results by project path prefix."""
    if not scope or not scope.startswith("project:"):
        return results
    project_name = scope.removeprefix("project:")
    prefix = f"projects/{project_name}/"
    return [r for r in results if r.get("docid", "").startswith(prefix)]


# --- Public API ---


async def search(
    query: str, mode: str = "fast", scope: str = "", limit: int = 5
) -> list[dict]:
    """
    mode="fast"  → BM25 only  (qmd search --json)
    mode="deep"  → semantic + rerank (qmd query --json)
    """
    fetch_limit = limit * 3 if scope else limit  # over-fetch when filtering by scope

    if mode == "deep":
        args = ["query", query, "--json", "-n", str(fetch_limit)]
    else:
        args = ["search", query, "--json", "-n", str(fetch_limit)]

    raw = await _run_qmd_async(args)
    results = _parse_json_output(raw)
    results = _apply_scope(results, scope)
    return results[:limit]


async def reindex() -> bool:
    """Call after vault writes. Fast (BM25 only, no model)."""
    raw = await _run_qmd_async(["update"])
    ok = raw is not None
    logger.info("[qmd] reindex done" if ok else "[qmd] reindex failed")
    return ok


async def reembed() -> bool:
    """Call periodically. Slow (runs GGUF model)."""
    raw = await _run_qmd_async(["embed"])
    ok = raw is not None
    logger.info("[qmd] reembed done" if ok else "[qmd] reembed failed")
    return ok
