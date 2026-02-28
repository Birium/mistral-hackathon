from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FrontMatterLayout:
    """Zero-indexed line positions and YAML key names for a fixed front matter layout.

    ---                  # 0  (opening delimiter)
    created: ...           # 1
    updated: ...          # 2
    tokens: ...            # 3
    ---                  # 4  (closing delimiter)
    """
    # Line positions
    delimiter_start: int = 0
    created: int = 1
    updated: int = 2
    tokens: int = 3
    delimiter_end: int = 4

    # YAML key names
    created_key: str = "created"
    updated_key: str = "updated"
    tokens_key: str = "tokens"


# Single instance — treat as a constant
FM = FrontMatterLayout()
