from typing import Union
from pathlib import Path

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import FullLoader as Loader

from .utils import iter_frontmatter_lines


def read_frontmatter(path: Union[str, Path]) -> dict:
    """Read and parse YAML frontmatter from a Markdown file.

    Returns an empty dict if no frontmatter block is found.
    """
    try:
        with open(path, encoding="utf-8") as f:
            first = f.readline()
            if first.rstrip("\n") != "---":
                print(f"[read_frontmatter] no frontmatter in {path}")
                return {}
            try:
                lines = list(iter_frontmatter_lines(f))
            except (EOFError, ValueError):
                return {}
        return yaml.load("".join(lines), Loader=Loader) or {}
    except Exception as e:
        print(f"[read_frontmatter] error reading {path}: {e}")
        return {}
