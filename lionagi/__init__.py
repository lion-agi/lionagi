"""
lionagi is an intelligent automation framework.
"""

import logging
from .version import __version__
from dotenv import load_dotenv

from .libs import (
    to_df,
    to_dict,
    to_num,
    lcall,
    alcall,
    mcall,
    bcall,
    rcall,
    tcall,
    nget,
    nset,
    ninsert,
    nmerge,
    flatten,
    unflatten,
    nfilter,
    get_flattened_keys,
    to_readable_dict,
)
from . import CallDecorator

from .core import Session, Branch

from .integrations.provider.services import Services


__all__ = [
    "to_df",
    "to_dict",
    "to_num",
    "lcall",
    "alcall",
    "mcall",
    "bcall",
    "rcall",
    "tcall",
    "nget",
    "nset",
    "ninsert",
    "nmerge",
    "flatten",
    "unflatten",
    "nfilter",
    "get_flattened_keys",
    "Session",
    "Branch",
    "Services",
    "to_readable_dict",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()
