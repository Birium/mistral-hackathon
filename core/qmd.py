import asyncio
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

QMD_TIMEOUT_FAST = 30
QMD_TIMEOUT_DEEP = 300


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


def _extract_json(raw: str) -> str:
    """Slice from the first JSON array marker, skipping qmd progress lines."""
    idx = raw.find("[")
    if idx == -1:
        return ""
    return raw[idx:]


def _parse_json_output(raw: str) -> list[dict]:
    if not raw:
        return []
    try:
        return json.loads(_extract_json(raw))
    except json.JSONDecodeError:
        logger.error(f"[qmd] Failed to parse JSON: {raw[:300]}")
        return []


def _apply_scope(results: list[dict], scope: str) -> list[dict]:
    if not scope or not scope.startswith("project:"):
        return results
    project_name = scope.removeprefix("project:")
    prefix = f"projects/{project_name}/"
    return [r for r in results if r.get("docid", "").startswith(prefix)]


async def search(
    query: str, mode: str = "fast", scope: str = "", limit: int = 5
) -> list[dict]:
    fetch_limit = limit * 3 if scope else limit

    if mode == "deep":
        args = ["query", query, "--json", "-n", str(fetch_limit)]
        timeout = QMD_TIMEOUT_DEEP
    else:
        args = ["search", query, "--json", "-n", str(fetch_limit)]
        timeout = QMD_TIMEOUT_FAST

    raw = await asyncio.to_thread(_run_qmd, args, timeout)
    results = _parse_json_output(raw)
    results = _apply_scope(results, scope)
    return results[:limit]


async def reindex() -> bool:
    raw = await asyncio.to_thread(_run_qmd, ["update"], QMD_TIMEOUT_FAST)
    ok = bool(raw)
    logger.info("[qmd] reindex done" if ok else "[qmd] reindex failed")
    return ok


async def reembed() -> bool:
    raw = await asyncio.to_thread(_run_qmd, ["embed"], QMD_TIMEOUT_DEEP)
    ok = bool(raw)
    logger.info("[qmd] reembed done" if ok else "[qmd] reembed failed")
    return ok
