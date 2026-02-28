"""
Parse QMD --line-numbers snippet strings into (lines_range, chunk_with_context).

Format with --line-numbers:
  "1: @@ -4,4 @@ (3 before, 0 after)\n2: \n3: # Profile\n4: \n5: No profile yet."

  Line 1  → header (strip it)
  Lines 2+ → content with snippet-relative numbers (strip "N: " prefix)

From @@ -start,total @@:
  file_line_of_content_i  = start_line + i          (0-indexed content lines)
  match_start_in_file     = start_line + before
  match_end_in_file       = start_line + total - after - 1
"""

import re

_HEADER_RE = re.compile(r"@@\s+-(\d+),(\d+)\s+@@\s+\((\d+)\s+before,\s+(\d+)\s+after\)")
_LINE_PREFIX_RE = re.compile(r"^\d+:\s?")


def _strip_prefix(line: str) -> str:
    """Remove the snippet-relative '3: ' prefix added by --line-numbers."""
    return _LINE_PREFIX_RE.sub("", line)


def parse_snippet(snippet: str) -> tuple[str, str]:
    """Return (lines_range, chunk_with_context).

    lines_range        — e.g. "7-10"  (match only, excluding context padding)
    chunk_with_context — file-absolute numbered lines, e.g. "4  | \\n5  | # Profile"

    Falls back to ("?", raw_snippet) if the header can't be parsed.
    """
    if not snippet:
        return ("?", "")

    raw_lines = snippet.split("\n")
    if not raw_lines:
        return ("?", snippet)

    # First line is always the header (possibly prefixed with "1: ")
    header = _strip_prefix(raw_lines[0]).strip()
    match = _HEADER_RE.search(header)

    if not match:
        body = "\n".join(_strip_prefix(l) for l in raw_lines)
        return ("?", body.strip())

    start_line = int(match.group(1))  # file-absolute line where snippet starts
    total = int(match.group(2))  # total lines in snippet content
    before = int(match.group(3))  # context lines before the match
    after = int(match.group(4))  # context lines after the match

    content_lines = raw_lines[1:]  # drop header line

    # Re-number with file-absolute line numbers
    numbered: list[str] = []
    for i, raw_line in enumerate(content_lines):
        file_lineno = start_line + i
        clean = _strip_prefix(raw_line)
        numbered.append(f"{file_lineno:>4}  | {clean}")

    # Compute the match range (excluding context padding)
    match_start = start_line + before
    match_end = start_line + total - after - 1
    if match_start <= match_end:
        lines_range = f"{match_start}-{match_end}"
    else:
        lines_range = str(match_start)

    return (lines_range, "\n".join(numbered))
