from pathlib import Path
from typing import Union

from ..io import read_frontmatter
from ..layout import FM


def read_tokens(path: Union[str, Path]) -> int:
    """Read token count from a markdown file's frontmatter."""
    return read_frontmatter(path, FM.tokens).get(FM.tokens_key, 0)
