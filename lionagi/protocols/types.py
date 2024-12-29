# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

from lionagi.utils import DataClass, HashableModel, Params

from .action.request_response_model import (
    ACTION_REQUESTS_FIELD,
    ACTION_RESPONSES_FIELD,
)
from .action.utils import (
    ACTION_REQUIRED_FIELD,
    ARGUMENTS_FIELD,
    FUNCTION_FIELD,
)


class ActionFieldModels(Enum):
    ACTION_REQUESTS = ACTION_REQUESTS_FIELD
    ACTION_RESPONSES = ACTION_RESPONSES_FIELD
    ACTION_REQUIRED = ACTION_REQUIRED_FIELD
    FUNCTION = FUNCTION_FIELD
    ARGUMENTS = ARGUMENTS_FIELD


from .action.function_calling import FunctionCalling
from .action.manager import ActionManager
from .action.request_response_model import (
    ActionRequestModel,
    ActionResponseModel,
)
from .action.tool import FuncTool, FuncToolRef, Tool, ToolRef
from .generic._id import ID, Collective, IDError, IDType, Ordering
from .generic.concepts import Manager, Observer
from .generic.element import E, Element, Observable
from .generic.event import Condition, Event, EventStatus, Execution
from .generic.exchange import Exchange
from .generic.log import Log, LogManager, LogManagerConfig
from .generic.pile import Pile, pile
from .generic.processor import Executor, Processor
from .generic.progression import Progression, prog
from .graph.edge import Edge, EdgeCondition
from .graph.graph import Graph
from .graph.node import Node, Relational
from .messages.action_request import ActionRequest
from .messages.action_response import ActionResponse
from .messages.assistant_response import AssistantResponse
from .messages.base import (
    MESSAGE_FIELDS,
    Communicatable,
    MessageField,
    MessageFlag,
    MessageRole,
    Sendable,
    SenderRecipient,
    validate_sender_recipient,
)
from .messages.instruction import Instruction
from .messages.manager import MessageManager
from .messages.message import MESSAGE_FIELDS, MessageRole, RoledMessage
from .messages.system import System
from .models.field_model import FieldModel
from .models.model_params import ModelParams
from .models.note import Note
from .models.operable_model import OperableModel
from .models.schema_model import SchemaModel

__all__ = (
    "ActionFieldModels",
    "ActionManager",
    "ActionRequest",
    "ActionRequestModel",
    "ActionResponse",
    "ActionResponseModel",
    "AssistantResponse",
    "Collective",
    "Condition",
    "DataClass",
    "E",
    "Edge",
    "EdgeCondition",
    "Element",
    "Event",
    "EventStatus",
    "Executor",
    "FieldModel",
    "FuncTool",
    "FuncToolRef",
    "FunctionCalling",
    "Graph",
    "ID",
    "IDError",
    "IDType",
    "Instruction",
    "Log",
    "LogManager",
    "LogManagerConfig",
    "MessageField",
    "MessageFlag",
    "MessageManager",
    "MessageRole",
    "ModelParams",
    "Node",
    "Observable",
    "Observer",
    "OperableModel",
    "Ordering",
    "Pile",
    "Params",
    "Processor",
    "Progression",
    "RoledMessage",
    "Relational",
    "SchemaModel",
    "Sendable",
    "System",
    "Tool",
    "ToolRef",
    "ValidateSenderRecipient",
    "validate_sender_recipient",
    "HashableModel",
    "Execution",
    "pile",
    "prog",
    "MESSAGE_FIELDS",
    "Communicatable",
    "Note",
    "SenderRecipient",
    "Manager",
    "Exchange",
)
