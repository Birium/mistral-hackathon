import os
from pathlib import Path
from typing import Union
from datetime import datetime

from ..io import update_frontmatter
from ..layout import FM


def update_created(path: Union[str, Path]) -> datetime:
    """Write the current datetime to the created line. Call once at file creation."""
    created = datetime.fromtimestamp(os.stat(path).st_birthtime)
    update_frontmatter(path, {FM.created_key: created}, line=FM.created)
    return created
