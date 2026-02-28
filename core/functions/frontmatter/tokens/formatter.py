def format_tokens(tokens: int) -> str:
    """Format token count per spec scale rules.

    < 1 000      → exact          420
    1k–999k      → one decimal    9.3k  (trailing .0 dropped → 9k)
    ≥ 1 000 000  → one decimal    1.3M  (trailing .0 dropped → 1M)
    """
    if tokens < 1_000:
        return str(tokens)

    if tokens < 1_000_000:
        value = tokens / 1_000
        if value == int(value):
            return f"{int(value)}k"
        return f"{value:.1f}k"

    value = tokens / 1_000_000
    if value == int(value):
        return f"{int(value)}M"
    return f"{value:.1f}M"
