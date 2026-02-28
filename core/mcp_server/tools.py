import os
from typing import Optional
import asyncio
import qmd as qmd_client

VAULT = os.getenv("VAULT_PATH", "/vault")

def _resolve_path(path: str) -> str:
    # Ensure path stays within vault
    full_path = os.path.normpath(os.path.join(VAULT, path))
    if not full_path.startswith(os.path.normpath(VAULT)):
        raise ValueError("Path must be within vault")
    return full_path

def tree(path: str = "", depth: int = 3) -> str:
    target_path = _resolve_path(path)
    if not os.path.exists(target_path):
        return f"Path not found: {path}"
    
    output = []
    base_level = target_path.count(os.sep)
    
    for root, dirs, files in os.walk(target_path):
        level = root.count(os.sep) - base_level
        if level > depth:
            dirs.clear() # Stop deeper traversal
            continue
        
        indent = "  " * level
        basename = os.path.basename(root)
        if level == 0:
            basename = path or "/"
        
        output.append(f"{indent}{basename}/")
        for f in files:
            output.append(f"{indent}  {f}")
            
    return "\n".join(output)

def read(path: str) -> str:
    target_path = _resolve_path(path)
    if not os.path.exists(target_path):
        return f"File not found: {path}"
    with open(target_path, "r") as f:
        return f.read()

def write(path: str, content: str) -> str:
    target_path = _resolve_path(path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        f.write(content)
    return f"written: {path}"

def search(query: str, mode: str = "fast", scope: str = "") -> str:
    """
    Search the vault using QMD.
    mode: "fast" (BM25) or "deep" (semantic + rerank)
    scope: "" (whole vault) or "project:<name>"
    """
    try:
        results = asyncio.run(qmd_client.search(query, mode=mode, scope=scope))
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

def edit(path: str, old_content: str, new_content: str) -> str:
    target_path = _resolve_path(path)
    if not os.path.exists(target_path):
        return f"File not found: {path}"
    with open(target_path, "r") as f:
        content = f.read()
    if old_content not in content:
        return "old_content not found in file"
    content = content.replace(old_content, new_content, 1)
    with open(target_path, "w") as f:
        f.write(content)
    return f"edited: {path}"

def append(path: str, content: str, position: str = "bottom") -> str:
    target_path = _resolve_path(path)
    if not os.path.exists(target_path):
        return f"File not found: {path}"
    with open(target_path, "r") as f:
        existing = f.read()
    with open(target_path, "w") as f:
        if position == "top":
            f.write(content + "\n" + existing)
        else:
            if existing and not existing.endswith("\n"):
                f.write(existing + "\n" + content)
            else:
                f.write(existing + content)
    return f"appended to: {path}"

def delete(path: str) -> str:
    target_path = _resolve_path(path)
    if not os.path.exists(target_path):
        return f"File not found: {path}"
    os.remove(target_path)
    return f"deleted: {path}"

def move(from_path: str, to_path: str) -> str:
    src = _resolve_path(from_path)
    dst = _resolve_path(to_path)
    if not os.path.exists(src):
        return f"File not found: {from_path}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.rename(src, dst)
    return f"moved {from_path} to {to_path}"