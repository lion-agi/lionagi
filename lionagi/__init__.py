"""
lionagi is an intelligent automation framework.
"""

import logging
from .version import __version__
from dotenv import load_dotenv


from lionagi.core.generic.abc import Field
from lionagi.core.generic import progression, flow, pile, Node, Model
from lionagi.core.work.worker import work, Worker
from lionagi.core.branch.branch import Branch


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()
