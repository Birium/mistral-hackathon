from dataclasses import dataclass


@dataclass
class SearchResult:
    path: str  # e.g. "projects/startup-x/changelog.md"
    score: float  # 0.0 – 1.0
    lines: str  # e.g. "9-14"
    chunk_with_context: str  # numbered lines: "7  | ...\n8  | ..."
