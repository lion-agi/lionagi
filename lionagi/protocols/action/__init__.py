# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

from .request_response_model import (
    ACTION_REQUESTS_FIELD,
    ACTION_RESPONSES_FIELD,
)
from .utils import ACTION_REQUIRED_FIELD, ARGUMENTS_FIELD, FUNCTION_FIELD


class ActionFieldModels(Enum):
    ACTION_REQUESTS = ACTION_REQUESTS_FIELD
    ACTION_RESPONSES = ACTION_RESPONSES_FIELD
    ACTION_REQUIRED = ACTION_REQUIRED_FIELD
    FUNCTION = FUNCTION_FIELD
    ARGUMENTS = ARGUMENTS_FIELD


from .function_calling import FunctionCalling
from .manager import ActionManager
from .request_response_model import ActionRequestModel, ActionResponseModel
from .tool import FuncTool, FuncToolRef, Tool, ToolRef

__all__ = (
    "ActionFieldModels",
    "ActionManager",
    "FunctionCalling",
    "ActionRequestModel",
    "ActionResponseModel",
    "Tool",
    "FuncTool",
    "FuncToolRef",
    "ToolRef",
)
