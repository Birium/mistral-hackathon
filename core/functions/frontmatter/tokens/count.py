"""
Token counter.

Drop-in replacement point: swap the body of count_tokens()
with a real tokenizer (tiktoken, etc.) when ready.
The signature MUST stay: (str) -> int.
"""


def count_tokens(content: str) -> int:
    """Approximate token count. Replace with real tokenizer later."""
    if not content:
        return 0
    # Rough heuristic: ~4 characters per token
    return max(1, len(content) // 4)
