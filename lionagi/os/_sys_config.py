from datetime import timezone
from lion_core.setting import LION_ID_CONFIG, LN_UNDEFINED


TIME_CONFIG = {
    "tz": timezone.utc,
}

BASE_LION_FIELDS = [
    "ln_id",
    "timestamp",
    "metadata",
    "extra_fields",
    "content",
    "created",
    "embedding",
]

__all__ = [
    "TIME_CONFIG",
    "LION_ID_CONFIG",
    "LN_UNDEFINED",
    "BASE_LION_FIELDS",
]
