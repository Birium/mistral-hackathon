from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FrontMatterLayout:
    """Zero-indexed line positions and YAML key names for a fixed front matter layout.

    ---          # 0  (opening delimiter)
    tokens: ...  # 1
    ---          # 2  (closing delimiter)
    """
    # Line positions
    delimiter_start: int = 0
    tokens: int = 1
    delimiter_end: int = 2

    # YAML key names
    tokens_key: str = "tokens"


# Single instance — treat as a constant
FM = FrontMatterLayout()
