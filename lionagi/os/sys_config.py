from datetime import timezone
from lion_core import BASE_LION_FIELDS, LION_ID_CONFIG

TIME_CONFIG = {
    "tz": timezone.utc,
}

__all__ = [
    "TIME_CONFIG",
    "LION_ID_CONFIG",
    "BASE_LION_FIELDS",
]
