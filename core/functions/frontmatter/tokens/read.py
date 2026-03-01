from pathlib import Path
from typing import Union

from ..io import read_frontmatter
from ..layout import FM


def read_tokens(path: Union[str, Path]) -> int:
    """Read token count from a markdown file's frontmatter."""
    readed = read_frontmatter(path, FM.tokens)
    if readed == {}:
        return 0
    # if readed is not of type dict:
    #     raise TypeError(f"Expected dict, got {type(readed)}")
    if not isinstance(readed, dict):
        return 0
    return readed.get(FM.tokens_key, 0)
