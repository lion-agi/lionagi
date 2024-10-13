import logging

from dotenv import load_dotenv

from .version import __version__

__all__ = [
    "__version__",
]


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()
