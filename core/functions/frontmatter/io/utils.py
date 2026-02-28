from typing import Generator, IO

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
