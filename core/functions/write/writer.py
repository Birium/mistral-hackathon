from pathlib import Path


def write(resolved_path: Path, content: str) -> str:
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(content, encoding="utf-8")
    return f"Written: '{resolved_path}'"