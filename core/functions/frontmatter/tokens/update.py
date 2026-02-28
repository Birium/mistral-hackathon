from typing import Union
from pathlib import Path

from .count import count_tokens
from ..updated.update import update_updated

from ..io import read_frontmatter, update_frontmatter
from ..layout import FM


def update_tokens(path: Union[str, Path]) -> int:
    """Update token count in a markdown file's frontmatter. Returns the new count."""
    content = Path(path).read_text(encoding="utf-8")
    tokens = count_tokens(content)
    existing = read_frontmatter(path, line=FM.tokens).get(FM.tokens_key)
    if existing == tokens:
        return tokens
    update_frontmatter(path, {FM.tokens_key: tokens}, line=FM.tokens)
    update_updated(path)
    return tokens
