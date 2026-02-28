from pathlib import Path
from typing import Union

from venv import logger

from .io import insert_frontmatter
from .io import validate_frontmatter
from .tokens import update_tokens
from .updated import update_updated
from .created import update_created

def write_frontmatter(
    path: Union[Path, str],
) -> None:
    """Write or update YAML frontmatter in a Markdown file.

    - File does not exist: creates it with `data` as frontmatter and `body` as content.
    - File exists, first line is '---': merges `data` into existing frontmatter, body preserved.
    - File exists, no '---' in first 3 lines: prepends new frontmatter, existing content preserved.
    """

    p = Path(path)

    if not p.exists():
        logger.warning(f'[write_frontmatter] path does not exist: {p}')
        return

    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    first_3 = [line.rstrip("\n") for line in lines[:3]]

    if not first_3 and not first_3[0] == "---":
        insert_frontmatter(p)

    valid = validate_frontmatter(p)
    if not valid:
        insert_frontmatter(p)

    update_updated(p)
    update_tokens(p)
    update_created(p)
    return
