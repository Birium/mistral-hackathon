import shutil
from pathlib import Path

def delete(resolved_path: Path) -> str:
    if resolved_path.is_dir():
        shutil.rmtree(resolved_path)
        return f"Deleted folder: '{resolved_path}'"
    else:
        resolved_path.unlink()
        return f"Deleted file: '{resolved_path}'"