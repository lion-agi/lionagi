"""
lionagi is an intelligent automation framework.
"""

import logging
from .version import __version__
from dotenv import load_dotenv


from .libs import *
from .core import *
from .integrations import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()
