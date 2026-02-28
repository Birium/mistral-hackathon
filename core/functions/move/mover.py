from pathlib import Path


def move(from_path: Path, to_path: Path) -> str:
    if from_path == to_path:
        return f"[MOVE] No-op: source and destination are identical '{from_path}'"

    to_path.parent.mkdir(parents=True, exist_ok=True)
    from_path.rename(to_path)

    return f"Moved: '{from_path}' → '{to_path}'"
