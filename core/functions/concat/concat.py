from pathlib import Path
from typing import Optional


def _parse_range(lines: str, total: int) -> tuple[int, int] | str:
    """
    Parse "N-M" into (start, end) — 1-indexed, inclusive.
    Returns an error string if the format is invalid.
    Clamps end to total if out of bounds.
    """
    parts = lines.split("-")
    if len(parts) != 2:
        return f"[CONCAT ERROR] Invalid line range format '{lines}' — expected 'N-M'"

    try:
        start = int(parts[0])
        end = int(parts[1])
    except ValueError:
        return f"[CONCAT ERROR] Invalid line range format '{lines}' — expected integers"

    if start < 1 or end < start:
        return f"[CONCAT ERROR] Invalid line range '{lines}' — start must be >= 1 and <= end"

    end = min(end, total)  # clamp silently
    return (start, end)


def _format_lines(file_lines: list[str], start: int, end: int) -> str:
    """
    Format lines[start-1 : end] with original line numbers.
    Width is based on the largest line number in the selection.
    Two spaces before the pipe — consistent with read/reader.py.
    """
    width = len(str(end))
    chunks = []
    for i in range(start - 1, end):  # 0-indexed slice, 1-indexed output
        lineno = i + 1
        chunks.append(f"{lineno:<{width}}  | {file_lines[i]}")
    return "\n".join(chunks)


def concat(path: str, resolved: Path, lines: Optional[str]) -> str:
    """
    Build a single fenced code block for one file entry.
    `path` is the original vault path (used in the block header).
    `resolved` is the absolute filesystem path.
    `lines` is the raw range string or None.
    """
    if not resolved.exists() or not resolved.is_file():
        return f"[CONCAT ERROR] File not found: '{path}'"

    try:
        content = resolved.read_text(encoding="utf-8")
    except (OSError, PermissionError) as e:
        return f"[CONCAT ERROR] Could not read '{path}': {e}"

    file_lines = content.splitlines()
    total = len(file_lines)

    if lines is None:
        body = _format_lines(file_lines, start=1, end=total)
    else:
        result = _parse_range(lines, total)
        if isinstance(result, str):
            return result  # error string
        start, end = result
        body = _format_lines(file_lines, start=start, end=end)

    return f"```{path}\n{body}\n```"