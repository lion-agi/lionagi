"""
lionagi is an intelligent automation framework.
"""

import logging

from dotenv import load_dotenv

from .core import *
from .integrations import *
from .libs import *
from .version import __version__

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()
