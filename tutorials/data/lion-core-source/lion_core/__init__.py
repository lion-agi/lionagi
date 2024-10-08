"""lion-core."""

import logging

from .log_manager import LogManager
from .setting import BASE_LION_FIELDS, DEFAULT_LION_ID_CONFIG, LN_UNDEFINED
from .version import __version__

event_log_manager = LogManager(
    persist_dir="./data/logs",
    subfolder="events",
    file_prefix="event_",
)

__all__ = [
    "BASE_LION_FIELDS",
    "DEFAULT_LION_ID_CONFIG",
    "LN_UNDEFINED",
    "LogManager",
    "event_log_manager",
    "__version__",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
