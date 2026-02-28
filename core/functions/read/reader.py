from pathlib import Path


def read_file(
    resolved: Path, head: int | None, tail: int | None
) -> list[tuple[int, str]]:
    """Read a file and return (1-based line number, text) pairs.

    Line numbers always reflect position in the full file, even for partial reads.
    """
    all_lines = resolved.read_text(encoding="utf-8").splitlines()
    total = len(all_lines)

    if head is not None:
        budget = head * 4
        pairs: list[tuple[int, str]] = []
        consumed = 0
        for i, line in enumerate(all_lines):
            consumed += len(line) + 1
            if consumed > budget:
                break
            pairs.append((i + 1, line))
        return pairs

    if tail is not None:
        budget = tail * 4
        selected: list[tuple[int, str]] = []
        consumed = 0
        for i, line in enumerate(reversed(all_lines)):
            consumed += len(line) + 1
            if consumed > budget:
                break
            # real 1-based line number from the full file
            selected.insert(0, (total - i, line))
        return selected

    return [(i + 1, line) for i, line in enumerate(all_lines)]


def format_pairs(pairs: list[tuple[int, str]]) -> str:
    """Format (lineno, text) pairs into the numbered block body."""
    if not pairs:
        return ""
    width = len(str(pairs[-1][0]))  # widest line number in this slice
    return "\n".join(f"{lineno:<{width}}  | {text}" for lineno, text in pairs)
