from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TreeNode:
    """Single node in the vault tree (file or directory)."""

    name: str  # "state.md" or "bucket/"
    path: str  # full filesystem path
    is_directory: bool
    tokens: int  # file: own count, dir: sum of all descendants
    mtime: Optional[datetime]  # None → empty dir, displays "—"
    children: list[TreeNode] = field(default_factory=list)
