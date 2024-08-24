from datetime import timezone
from lion_core import BASE_LION_FIELDS
from pydantic import BaseModel

TIME_CONFIG = {
    "tz": timezone.utc,
}


__all__ = [
    "TIME_CONFIG",
    "BASE_LION_FIELDS",
]
