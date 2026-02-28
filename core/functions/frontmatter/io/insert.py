from pathlib import Path
from typing import Union

from .writer import write_frontmatter


def insert_frontmatter(path: Union[str, Path]) -> None:
    """Prepend a frontmatter skeleton to an existing file, using its current content as body."""
    p = Path(path)
    body = p.read_text(encoding="utf-8")
    write_frontmatter(p, body=body)
