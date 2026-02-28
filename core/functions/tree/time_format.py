from datetime import datetime, timezone
from typing import Optional


def format_time_ago(dt: Optional[datetime]) -> str:
    """Convert a datetime to a human-readable relative string.

    Returns "—" if dt is None (empty directory).
    """
    if dt is None:
        return "—"

    now = datetime.now(timezone.utc)

    # Ensure timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    seconds = int((now - dt).total_seconds())
    if seconds < 0:
        seconds = 0

    if seconds < 60:
        return f"{seconds}s ago"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"

    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"

    days = hours // 24
    if days < 30:
        return f"{days}d ago"

    months = days // 30
    if months < 12:
        return f"{months}mo ago"

    years = days // 365
    return f"{years}y ago"
