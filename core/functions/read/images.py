from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def load_image(path: Path) -> str:
    # MVP stub — real impl will inject into multimodal session context
    return f"[IMAGE] '{path.name}' (multimodal loading not yet implemented)"
