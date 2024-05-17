"""
lionagi is an intelligent automation framework.
"""

import logging
from .version import __version__
from dotenv import load_dotenv


from lionagi.core.generic.abc import Field
from lionagi.core.generic import progression, flow, pile, Node, iModel
from lionagi.core.work.worker import work, Worker
from lionagi.core.session.branch import Branch
from lionagi.core.report import Form, Report
from lionagi.integrations.provider.services import Services
import lionagi.core.agent.director.direct as direct


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()
