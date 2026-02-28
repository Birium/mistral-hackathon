from pathlib import Path
from typing import Union

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import FullLoader as Loader, Dumper

from .utils import iter_frontmatter_lines


def update_frontmatter(path: Union[str, Path], updates: dict) -> None:
    """Merge updates into the existing YAML frontmatter of a Markdown file.

    Body content is preserved unchanged.
    """
    try:
        p = Path(path)
        with open(p, encoding="utf-8") as f:
            first = f.readline()
            if first.rstrip("\n") != "---":
                body = first + f.read()
                data = updates
            else:
                try:
                    lines = list(iter_frontmatter_lines(f))
                except EOFError:
                    print(f"[update_frontmatter] unclosed frontmatter in {path}")
                    return
                except ValueError:
                    print(f"[update_frontmatter] frontmatter cap exceeded in {path}")
                    return
                body = f.read()
                data = yaml.load("".join(lines), Loader=Loader) or {}
                data.update(updates)

        block = yaml.dump(data, Dumper=Dumper, allow_unicode=True, default_flow_style=False)
        p.write_text(f"---\n{block}---\n{body}", encoding="utf-8")
    except Exception as e:
        print(f"[update_frontmatter] error updating {path}: {e}")
