from pathlib import Path
from typing import Union

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import FullLoader as Loader, Dumper

from .utils import iter_frontmatter_lines


def update_frontmatter(
    path: Union[str, Path],
    updates: dict,
    line: Union[int, None] = None,
) -> None:
    """Merge updates into the existing YAML frontmatter of a Markdown file.

    If `line` is given (zero-indexed, matching FrontMatterSchema), replaces only
    that line with the serialized `updates` dict — no YAML parsing of the rest.

    Without `line`, merges updates into the full frontmatter block.
    Body content is preserved unchanged in both cases.
    """
    try:
        p = Path(path)
        if line is not None:
            lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
            if line >= len(lines):
                print(f"[update_frontmatter] line {line} out of range in {path}")
                return
            lines[line] = yaml.dump(
                updates, Dumper=Dumper, allow_unicode=True, default_flow_style=False
            )
            p.write_text("".join(lines), encoding="utf-8")
            return
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
