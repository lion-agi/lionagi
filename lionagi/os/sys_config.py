from datetime import timezone
from lion_core import BASE_LION_FIELDS


TIME_CONFIG = {
    "tz": timezone.utc,
}


__all__ = [
    "TIME_CONFIG",
    "BASE_LION_FIELDS",
]
