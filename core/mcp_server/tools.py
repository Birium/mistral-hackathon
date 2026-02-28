import os
import qmd as qmd_client

VAULT = os.getenv("VAULT_PATH", "")
if not VAULT:
    raise RuntimeError("VAULT_PATH env var is not set")


def _resolve_path(path: str) -> str:
    full_path = os.path.normpath(os.path.join(VAULT, path))
    if not full_path.startswith(os.path.normpath(VAULT)):
        raise ValueError("Path must be within vault")
    return full_path


def write(path: str, content: str) -> str:
    target_path = _resolve_path(path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        f.write(content)
    return f"written: {path}"


async def search(
    queries: list[str],
    mode: str = "fast",
    scopes: list[str] | None = None,
) -> str:
    """Search the vault. mode: fast (BM25) or deep (semantic+rerank)."""
    from functions.search import search as search_fn

    if mode not in ("fast", "deep"):
        return f"[search error] invalid mode '{mode}'"
    if not queries:
        return "[search error] queries must be a non-empty list"

    try:
        results = await search_fn(queries=queries, mode=mode, scopes=scopes)
    except Exception as e:
        return f"[search error] {e}"

    if not results:
        return f"No results found for: {queries}"

    lines = [f"## Search results for `{queries}`\n"]
    for r in results:
        lines.append(f"### {r.path} (score: {r.score}, lines: {r.lines})")
        lines.append(f"```\n{r.chunk_with_context}\n```\n")

    return "\n".join(lines)
