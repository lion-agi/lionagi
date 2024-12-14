# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging

from dotenv import load_dotenv
from lion_service import iModel

from .protocols import types
from .session.session import Branch, Session
from .settings import Settings
from .version import __version__

__all__ = [
    "Branch",
    "Session",
    "types",
    "iModel",
    "Settings",
    "__version__",
]


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv(Settings.Config.ENV_FILE)
