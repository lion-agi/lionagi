"""
lionagi is an intelligent automation framework.
"""

import logging
from .version import __version__
from dotenv import load_dotenv

from .util import (
    to_df,
    to_dict,
    str_to_num,
    lcall,
    alcall,
    mcall,
    bcall,
    rcall,
    tcall,
    to_list,
    nget,
    nset,
    ninsert,
    nmerge,
    flatten,
    unflatten,
    nfilter,
    get_flattened_keys,
    CallDecorator,
    to_readable_dict,
)

from .core import ActionNode, ChatFlow, Session, Branch, func_to_tool

from .integrations.provider.services import Services


__all__ = [
    "to_df",
    "to_dict",
    "str_to_num",
    "lcall",
    "alcall",
    "mcall",
    "bcall",
    "rcall",
    "tcall",
    "to_list",
    "nget",
    "nset",
    "ninsert",
    "nmerge",
    "flatten",
    "unflatten",
    "nfilter",
    "get_flattened_keys",
    "CallDecorator",
    "ActionNode",
    "ChatFlow",
    "Session",
    "Branch",
    "func_to_tool",
    "Services",
    "to_readable_dict",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()
