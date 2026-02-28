from pathlib import Path
from typing import Union

from .utils import _CONTENT_FIELD_MAP

def write_frontmatter(path: Union[str, Path], body: str = "") -> None:
    """Write YAML frontmatter skeleton and optional body to a Markdown file.

    Keys are derived from FM via _CONTENT_FIELD_MAP; values are left null.
    Overwrites the file entirely.
    """
    try:
        lines = ["---"]
        for _, yaml_key in sorted(_CONTENT_FIELD_MAP.items()):
            lines.append(f"{yaml_key}:")
        lines.append("---")
        content = "\n".join(lines) + "\n"
        if body:
            content += f"\n{body}"
        Path(path).write_text(content, encoding="utf-8")
        from ..created.update import update_created
        update_created(path)
    except Exception as e:
        print(f"[write_frontmatter] error writing {path}: {e}")
