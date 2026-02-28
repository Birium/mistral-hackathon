from pathlib import Path


def expand_folder(resolved: Path) -> list[Path]:
    """Return direct files inside a folder, sorted. Subfolders are silently skipped."""
    return sorted(p for p in resolved.iterdir() if p.is_file())
