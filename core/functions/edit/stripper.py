import re

_PREFIX_RE = re.compile(r"^\s*\d+\s+\| ?")


def has_line_numbers(text: str) -> bool:
    lines = text.split("\n")
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return False
    return all(_PREFIX_RE.match(l) for l in non_empty)


def strip_line_numbers(text: str) -> str:
    return "\n".join(_PREFIX_RE.sub("", line) for line in text.split("\n"))
