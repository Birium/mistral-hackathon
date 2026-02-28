from pathlib import Path
from typing import Union
from datetime import datetime

from ..io import read_frontmatter
from ..layout import FM


def read_created(path: Union[str, Path]) -> Union[datetime, None]:
    """Read the created timestamp from a markdown file's frontmatter."""
    return read_frontmatter(path, FM.created).get(FM.created_key, None)
