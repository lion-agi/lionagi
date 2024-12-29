"""The LION framework."""

import logging

from dotenv import load_dotenv

from .protocols import types as types
from .service import iModel
from .session.session import Branch, Session
from .settings import Settings
from .version import __version__

load_dotenv()


__all__ = (
    "Settings",
    "__version__",
    "iModel",
    "Branch",
    "Session",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
