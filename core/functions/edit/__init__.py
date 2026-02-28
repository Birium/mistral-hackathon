from functions.utils import _resolve_path
from .stripper import has_line_numbers, strip_line_numbers

def edit(path: str, old_content: str, new_content: str) -> str:
    # Validate inputs
    if not old_content:
        raise ValueError("old_content must not be empty")

    resolved = _resolve_path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: '{path}'")

    # Strip line-number prefixes if present
    cleaned_old = strip_line_numbers(old_content) if has_line_numbers(old_content) else old_content

    file_content = resolved.read_text(encoding="utf-8")

    if cleaned_old not in file_content:
        raise ValueError(f"old_content not found in '{path}'")

    # No-op check
    if cleaned_old == new_content:
        return f"[EDIT] No-op: old_content and new_content are identical in '{path}'"

    # Replace FIRST occurrence only
    new_file_content = file_content.replace(cleaned_old, new_content, 1)
    resolved.write_text(new_file_content, encoding="utf-8")

    return f"[EDIT] '{path}' updated successfully"