from pathlib import Path


def read_file(resolved: Path) -> list[tuple[int, str]]:
    """Read a file and return (1-based line number, text) pairs."""
    all_lines = resolved.read_text(encoding="utf-8").splitlines()
    return [(i + 1, line) for i, line in enumerate(all_lines)]


def format_pairs(pairs: list[tuple[int, str]]) -> str:
    """Format (lineno, text) pairs into the numbered block body."""
    if not pairs:
        return ""
    width = len(str(pairs[-1][0]))
    return "\n".join(f"{lineno:<{width}}  | {text}" for lineno, text in pairs)