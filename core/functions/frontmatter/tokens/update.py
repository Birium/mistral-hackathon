from typing import Union
from pathlib import Path

from functions.frontmatter.tokens.count import count_tokens

from ..io import update_frontmatter
from ..layout import FM


def update_tokens(path: Union[str, Path]) -> int:
    """Update token count in a markdown file's frontmatter. Returns the new count."""
    content = Path(path).read_text(encoding="utf-8")
    tokens = count_tokens(content)
    update_frontmatter(path, {FM.tokens_key: tokens}, line=FM.tokens)
    return tokens
