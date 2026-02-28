from pathlib import Path
from typing import Union

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import FullLoader as Loader


def read_frontmatter(path: Union[str, Path]) -> dict:
    """Read and parse YAML frontmatter from a Markdown file.

    Returns an empty dict if no frontmatter block is found.
    """
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    return yaml.load(block, Loader=Loader) or {}
