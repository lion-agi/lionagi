"""The LION framework."""

import logging

from dotenv import load_dotenv

from .core.session.types import Branch
from .integrations.litellm_.imodel import LiteiModel
from .protocols.operatives.step import Step
from .service import iModel
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
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
