from dataclasses import fields
from pathlib import Path
from typing import Generator, IO

from ..layout import FM

_CAP = 200


def iter_frontmatter_lines(f: IO[str], cap: int = _CAP) -> Generator[str, None, None]:
    """Yield raw frontmatter lines from an open file handle.

    The caller must already have consumed the opening `---` line.
    Raises EOFError  if the file ends before the closing `---`.
    Raises ValueError if more than `cap` lines are read without a closing `---`.
    """
    for _ in range(cap):
        line = f.readline()
        if not line:
            raise EOFError("EOF before closing ---")
        if line.rstrip("\n") == "---":
            return
        yield line
    raise ValueError(f"frontmatter exceeds {cap} lines")


def _build_content_field_map() -> dict[int, str]:
    """Build {relative_line_index: expected_yaml_key} from FM dynamically.

    An int field `x` is a content field if `x_key` also exists as a field.
    Delimiter fields (`delimiter_start`, `delimiter_end`) have no `_key`
    counterpart and are skipped automatically.
    """
    all_field_names = {f.name for f in fields(FM)}
    index_to_key: dict[int, str] = {}
    for f in fields(FM):
        val = getattr(FM, f.name)
        if isinstance(val, int):
            key_field = f.name + "_key"
            if key_field in all_field_names:
                rel = val - (FM.delimiter_start + 1)
                index_to_key[rel] = getattr(FM, key_field)
    return index_to_key


_CONTENT_FIELD_MAP: dict[int, str] = _build_content_field_map()


def validate_frontmatter(path: Path) -> bool:
    """Return True if the file's frontmatter has exactly the keys defined in FM
    at the correct positions. Returns False on any mismatch or IO error.
    """
    try:
        with open(path, encoding="utf-8") as f:
            first = f.readline()
            if first.rstrip("\n") != "---":
                return False
            count = 0
            for line in iter_frontmatter_lines(f):
                expected_key = _CONTENT_FIELD_MAP.get(count)
                if expected_key is None:
                    return False  # more lines than FM defines
                if not line.startswith(f"{expected_key}:"):
                    return False  # wrong key at this position
                count += 1
            return count == len(_CONTENT_FIELD_MAP)
    except (EOFError, ValueError):
        return False
    except Exception:
        return False
