from pathlib import Path
from typing import Union
from datetime import datetime

from ..io import update_frontmatter
from ..layout import FM


def update_updated(path: Union[str, Path]) -> datetime:
    """Write the current datetime to the updated line."""
    now = datetime.now()
    update_frontmatter(path, {FM.updated_key: now}, line=FM.updated)
    return now
