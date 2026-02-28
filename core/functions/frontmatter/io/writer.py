from pathlib import Path
from typing import Union

import yaml

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


def write_frontmatter(path: Union[str, Path], data: dict, body: str = "") -> None:
    """Write YAML frontmatter and optional body to a Markdown file.

    Overwrites the file entirely.
    """
    try:
        block = yaml.dump(data, Dumper=Dumper, allow_unicode=True, default_flow_style=False)
        content = f"---\n{block}---\n"
        if body:
            content += f"\n{body}"
        Path(path).write_text(content, encoding="utf-8")
    except Exception as e:
        print(f"[write_frontmatter] error writing {path}: {e}")
