from datetime import timezone
from lion_core.setting import LION_ID_CONFIG, LN_UNDEFINED


TIME_CONFIG = {
    "tz": timezone.utc,
}


__all__ = [
    "TIME_CONFIG",
    "LION_ID_CONFIG",
    "LN_UNDEFINED",
]
