from pathlib import Path
from typing import Union

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import FullLoader as Loader, Dumper


def update_frontmatter(path: Union[str, Path], updates: dict) -> None:
    """Merge updates into the existing YAML frontmatter of a Markdown file.

    Body content is preserved unchanged.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")

    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            block = text[3:end]
            data = yaml.load(block, Loader=Loader) or {}
            body = text[end + 3:]
        else:
            data = {}
            body = text
    else:
        data = {}
        body = text

    data.update(updates)
    block = yaml.dump(data, Dumper=Dumper, allow_unicode=True, default_flow_style=False)
    content = f"---\n{block}---\n{body}"
    p.write_text(content, encoding="utf-8")
