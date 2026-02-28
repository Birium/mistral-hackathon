from typing import Union
from pathlib import Path

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import FullLoader as Loader

from .utils import iter_frontmatter_lines


def read_frontmatter(path: Union[str, Path], line: Union[int, None] = None) -> dict:
    """Read and parse YAML frontmatter from a Markdown file.

    If `line` is given (zero-indexed, matching FrontMatterSchema), reads only
    that line and returns a single-key dict. Returns {} if the line is not found.

    Without `line`, returns the full frontmatter as a dict (empty dict if none).
    """
    try:
        if line is not None:
            with open(path, encoding="utf-8") as f:
                for i, raw in enumerate(f):
                    if i == line:
                        return yaml.load(raw, Loader=Loader) or {}
            return {}
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
