from pathlib import Path
from typing import Union
from datetime import datetime

from ..io import read_frontmatter
from ..layout import FM


def read_updated(path: Union[str, Path]) -> Union[datetime, None]:
    """Read the updated timestamp from a markdown file's frontmatter."""
    return read_frontmatter(path, FM.updated).get(FM.updated_key, None)
