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


async def search(query: str, mode: str = "fast", scope: str = "") -> str:
    """
    Search the vault using QMD.
    mode: "fast" (BM25) or "deep" (semantic + rerank)
    scope: "" (whole vault) or "project:<name>"
    """
    if mode not in ("fast", "deep"):
        return f"[search error] invalid mode '{mode}'; use 'fast' or 'deep'"

    try:
        results = await qmd_client.search(query, mode=mode, scope=scope)
    except Exception as e:
        return f"[search error] {e}"

    if not results:
        return f"No results found for: {query}"

    lines = [f"## Search results for `{query}`\n"]
    for r in results:
        docid = r.get("docid", "?")
        snippet = r.get("snippet") or r.get("context", "")
        score = r.get("score", "")
        lines.append(f"**{docid}** (score: {score})\n{snippet}\n")

    return "\n".join(lines)