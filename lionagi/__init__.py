"""The LION framework."""

import logging

from dotenv import load_dotenv

from .integrations.litellm_.imodel import LiteiModel
from .operatives.step import Step
from .service import iModel
from .session.session import Branch, Session
from .settings import Settings
from .version import __version__

load_dotenv()


__all__ = [
    "Settings",
    "__version__",
    "iModel",
    "LiteiModel",
    "Branch",
    "Step",
    "Session",
    "LiteiModel",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
