from pathlib import Path
from typing import Union
from datetime import datetime

from ..io import update_frontmatter
from ..layout import FM


def update_created(path: Union[str, Path]) -> datetime:
    """Write the current datetime to the created line. Call once at file creation."""
    now = datetime.now()
    update_frontmatter(path, {FM.created_key: now}, line=FM.created)
    return now
