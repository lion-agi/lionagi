"""
lionagi is an intelligent automation framework.
"""

import logging
from .version import __version__
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()
