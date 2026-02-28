import asyncio
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

QMD_TIMEOUT_FAST = 30
QMD_TIMEOUT_SLOW = 600


def _run_qmd(args: list[str], timeout: int = QMD_TIMEOUT_FAST) -> str:
    cmd = ["qmd"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            logger.error(f"[qmd] stderr: {result.stderr.strip()}")
            return ""
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"[qmd] timeout after {timeout}s: {cmd}")
        return ""
    except FileNotFoundError:
        logger.error("[qmd] qmd binary not found in PATH")
        return ""


async def _run_qmd_async(args: list[str], timeout: int = QMD_TIMEOUT_FAST) -> str:
    return await asyncio.to_thread(_run_qmd, args, timeout)


def _parse_json(raw: str) -> list[dict]:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error(f"[qmd] JSON parse failed: {raw[:200]}")
        return []


async def raw_search(query: str, mode: str = "fast", limit: int = 10) -> list[dict]:
    """Return raw QMD result dicts. Callers own filtering and mapping."""
    if mode == "deep":
        args = ["query", query, "--json", "--line-numbers", "-n", str(limit)]
    else:
        args = ["search", query, "--json", "--line-numbers", "-n", str(limit)]

    raw = await _run_qmd_async(args)
    return _parse_json(raw)


async def reindex() -> bool:
    raw = await _run_qmd_async(["update"])
    ok = bool(raw)
    logger.info("[qmd] reindex done" if ok else "[qmd] reindex failed")
    return ok


async def reembed() -> bool:
    raw = await asyncio.to_thread(_run_qmd, ["embed"], QMD_TIMEOUT_SLOW)
    ok = bool(raw)
    logger.info("[qmd] reembed done" if ok else "[qmd] reembed failed")
    return ok
