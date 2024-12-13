# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from pydantic import BaseModel, JsonValue

from ..base import ID
from ..log import LogManager
from ..pile import Pile
from ..progression import Progression
from .action_request import ActionRequest
from .action_response import ActionResponse
from .assistant_response import AssistantResponse
from .instruction import Instruction
from .message import RoledMessage
from .system import System

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


class MessageManager:

    def __init__(
        self, messages=None, logger=None, system=None, save_on_clear=True
    ):
        super().__init__()
        self.messages: Pile[RoledMessage] = Pile(
            items=messages, item_type={RoledMessage}
        )
        self.logger = logger or LogManager()
        self.system = system
        self.save_on_clear = save_on_clear
        if self.system:
            self.add_message(system=self.system)

    def set_system(self, system: System) -> None:
        if not self.system:
            self.system = system
            self.messages.insert(0, self.system)
        else:
            old_system = self.system
            self.system = system
            self.messages.insert(0, self.system)
            self.messages.exclude(old_system)

    async def aclear_messages(self):
        """async clear messages, check clear_messages for details"""
        async with self.messages:
            self.clear_messages()

    async def a_add_message(self, **kwargs):
        """async add a message, check add_message for details"""
        async with self.messages:
            return self.add_message(**kwargs)

    @property
    def progress(self) -> Progression:
        return Progression(order=list(self.messages))

    @staticmethod
    def create_instruction(
        *,
        sender: ID.SenderRecipient = None,
        recipient: ID.SenderRecipient = None,
        instruction: Instruction | JsonValue = None,
        context: JsonValue = None,
        guidance: JsonValue = None,
        plain_content: str = None,
        request_fields: list[str] | dict[str, Any] = None,
        request_model: type[BaseModel] | BaseModel = None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        tool_schemas: dict | None = None,
        **kwargs,
    ):
        if isinstance(instruction, Instruction):
            instruction.update(
                context,
                guidance=guidance,
                request_fields=request_fields,
                plain_content=plain_content,
                request_model=request_model,
                images=images,
                image_detail=image_detail,
                tool_schemas=tool_schemas,
                **kwargs,
            )
            if sender:
                instruction.sender = sender
            if recipient:
                instruction.recipient = recipient
            return instruction
        else:
            return Instruction(
                sender=sender,
                recipient=recipient,
                instruction=instruction,
                context=context,
                guidance=guidance,
                request_fields=request_fields,
                request_model=request_model,
                plain_content=plain_content,
                images=images,
                image_detail=image_detail,
                tool_schemas=tool_schemas,
                **kwargs,
            )

    @staticmethod
    def create_assistant_response(
        *,
        sender: Any = None,
        recipient: Any = None,
        assistant_response: AssistantResponse | Any = None,
    ) -> AssistantResponse:

        if isinstance(assistant_response, AssistantResponse):
            if sender:
                assistant_response.sender = sender
            if recipient:
                assistant_response.recipient = recipient
            return assistant_response

        return AssistantResponse(
            assistant_response=assistant_response,
            sender=sender,
            recipient=recipient,
        )

    @staticmethod
    def create_action_request(
        *,
        sender: ID.SenderRecipient = None,
        recipient: ID.SenderRecipient = None,
        function: str = None,
        arguments: dict[str, Any] = None,
        action_request: ActionRequest | None = None,
    ) -> ActionRequest:
        if action_request:
            if not isinstance(action_request, ActionRequest):
                raise LionValueError(
                    "Error: action request must be an instance of ActionRequest."
                )
            if sender:
                action_request.sender = sender
            if recipient:
                action_request.recipient = recipient
            return action_request

        return ActionRequest(
            function=function,
            arguments=arguments,
            sender=sender,
            recipient=recipient,
        )

    @staticmethod
    def create_action_response(
        *,
        action_request: ActionRequest,
        action_response: ActionResponse | Any = None,
    ) -> ActionResponse:
        if not isinstance(action_request, ActionRequest):
            raise LionValueError(
                "Error: please provide a corresponding action request for an "
                "action response."
            )

        if action_response:
            if isinstance(action_response, ActionResponse):
                if action_request.is_responded:
                    raise ValueError(
                        "Error: action request already has a response."
                    )
                action_request.content["action_response_id"] = (
                    action_response.id
                )
                return action_response

        return ActionResponse(
            action_request=action_request,
            output=action_response,
        )

    @staticmethod
    def create_system(
        *,
        system: Any = None,
        sender: Any = None,
        recipient: Any = None,
        system_datetime: bool | str = None,
    ) -> System:

        system = system or DEFAULT_SYSTEM

        if isinstance(system, System):
            system.update(
                sender=sender,
                recipient=recipient,
                system_datetime=system_datetime,
            )
            return system

        return System(
            system=system,
            sender=sender,
            recipient=recipient,
            system_datetime=system_datetime,
        )

    def add_message(
        self,
        *,
        sender: ID.SenderRecipient = None,
        recipient: ID.SenderRecipient = None,
        instruction: Instruction | JsonValue = None,
        context: JsonValue = None,
        guidance: JsonValue = None,
        plain_content: str = None,
        request_fields: list[str] | dict[str, Any] = None,
        request_model: type[BaseModel] | BaseModel = None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        assistant_response: AssistantResponse | Any = None,
        system: System | Any = None,
        system_datetime: bool | str = None,
        function: str = None,
        arguments: dict[str, Any] = None,
        action_request: ActionRequest | None = None,
        action_response: ActionResponse | Any = None,
        metadata: dict = None,
    ) -> RoledMessage:
        """Adds a message to the branch. Only use this to add a message"""

        _msg = None
        if sum(bool(x) for x in (instruction, assistant_response, system)) > 1:
            raise ValueError("Only one message type can be added at a time.")

        if system:
            _msg = self.create_system(
                system=system,
                sender=sender,
                recipient=recipient,
                system_datetime=system_datetime,
            )
            self.set_system(_msg)

        elif action_response:
            if not action_request:
                raise ValueError(
                    "Error: Action response must have an action request."
                )
            _msg = self.create_action_response(
                action_request=action_request,
                action_response=action_response,
            )

        elif action_request or (function and arguments):
            _msg = self.create_action_request(
                sender=sender,
                recipient=recipient,
                function=function,
                arguments=arguments,
                action_request=action_request,
            )

        elif assistant_response:
            _msg = self.create_assistant_response(
                sender=sender,
                recipient=recipient,
                assistant_response=assistant_response,
            )

        else:
            _msg = self.create_instruction(
                sender=sender,
                recipient=recipient,
                instruction=instruction,
                context=context,
                guidance=guidance,
                plain_content=plain_content,
                request_fields=request_fields,
                request_model=request_model,
                images=images,
                image_detail=image_detail,
            )

        if metadata:
            _msg.metadata.update(["extra"], metadata)

        if _msg in self.messages:
            self.messages[_msg] = _msg
        else:
            self.messages.include(_msg)

        self.logger.log(_msg.to_log())
        return _msg

    def clear_messages(self) -> None:
        """Clears all messages from the branch except the system message."""
        if self.save_on_clear:
            self.logger.dump(clear=True)

        self.messages.clear()
        self.progress.clear()
        if self.system:
            self.messages.include(self.system)
            self.progress.insert(0, self.system)

    @property
    def last_response(self) -> AssistantResponse | None:
        for i in reversed(self.messages.progress):
            if isinstance(self.messages[i], AssistantResponse):
                return self.messages[i]

    @property
    def last_instruction(self) -> Instruction | None:
        for i in reversed(self.messages.progress):
            if isinstance(self.messages[i], Instruction):
                return self.messages[i]

    @property
    def assistant_responses(self) -> Pile[AssistantResponse]:
        return Pile(
            [
                self.messages[i]
                for i in self.messages.progress
                if isinstance(self.messages[i], AssistantResponse)
            ]
        )

    @property
    def action_requests(self) -> Pile[ActionRequest]:
        return Pile(
            [
                self.messages[i]
                for i in self.messages.progress
                if isinstance(self.messages[i], ActionRequest)
            ]
        )

    @property
    def action_responses(self) -> Pile[ActionResponse]:
        return Pile(
            [
                self.messages[i]
                for i in self.messages.progress
                if isinstance(self.messages[i], ActionResponse)
            ]
        )

    @property
    def instructions(self) -> Pile[Instruction]:
        return Pile(
            [
                self.messages[i]
                for i in self.messages.progress
                if isinstance(self.messages[i], Instruction)
            ]
        )

    def to_chat_msgs(self, progress=None) -> list[dict]:
        if progress == []:
            return []
        try:
            return [
                self.messages[i].chat_msg for i in (progress or self.progress)
            ]
        except Exception as e:
            raise ValueError(
                "Invalid progress, not all requested messages are in the message pile"
            ) from e

    def __bool__(self):
        return not self.messages.is_empty()

    def has_logs(self):
        return not self.logger.logs.is_empty()
