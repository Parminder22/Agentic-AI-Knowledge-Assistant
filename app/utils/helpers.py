import uuid
import time
from typing import Any


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


def generate_message_id() -> str:
    """Generate a unique message ID."""
    return str(uuid.uuid4())


def current_timestamp() -> int:
    """Return current Unix timestamp."""
    return int(time.time())


def truncate_text(text: str, max_chars: int = 500) -> str:
    """Truncate text for display/logging."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def safe_get(d: dict, *keys: str, default: Any = None) -> Any:
    """Safely navigate nested dicts."""
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
    return d
