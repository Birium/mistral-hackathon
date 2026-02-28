from pathlib import Path


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split file text into (frontmatter_block, body).

    frontmatter_block includes both --- delimiters and the trailing newline.
    If no frontmatter is found, returns ("", text).
    """
    if not text.startswith("---"):
        return "", text

    end = text.find("\n---", 3)
    if end == -1:
        return "", text

    # include the closing --- line + newline
    close = end + len("\n---")
    # consume optional trailing newline after closing ---
    if close < len(text) and text[close] == "\n":
        close += 1

    return text[:close], text[close:]


def append(resolved: Path, content: str, position: str) -> str:
    if not resolved.exists():
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return f"Created: '{resolved}'"

    if position == "bottom":
        with resolved.open("a", encoding="utf-8") as f:
            if not resolved.read_bytes().endswith(b"\n"):
                f.write("\n")
            f.write("\n")
            f.write(content)
        return f"Appended to bottom of '{resolved}'"

    # position == "top": must read to preserve frontmatter
    existing = resolved.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(existing)

    new_text = (
        frontmatter + content + "\n\n" + body if body else frontmatter + content + "\n"
    )
    resolved.write_text(new_text, encoding="utf-8")
    return f"Prepended to top of '{resolved}'"
