# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from jinja2 import Template
from pydantic import BaseModel, JsonValue

from .._concepts import Manager
from ..generic.log import Log
from ..generic.pile import Pile
from ..generic.progression import Progression
from .action_request import ActionRequest
from .action_response import ActionResponse
from .assistant_response import AssistantResponse
from .instruction import Instruction
from .message import RoledMessage, SenderRecipient
from .system import System

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


class MessageManager(Manager):

    def __init__(
        self,
        messages: list[RoledMessage] | None = None,
        progression: Progression | None = None,
        system: System | None = None,
    ):
        super().__init__()
        m_ = []
        if isinstance(messages, list):
            for i in messages:
                if isinstance(i, dict):
                    i = RoledMessage.from_dict(i)
                if isinstance(i, RoledMessage):
                    m_.append(i)
        if isinstance(messages, dict):
            self.messages = Pile.from_dict(messages)
        else:
            self.messages: Pile[RoledMessage] = Pile(
                collections=m_,
                item_type={RoledMessage},
                strict_type=False,
                progression=progression,
            )
        if system and not isinstance(system, System):
            raise ValueError("System message must be a System instance.")
        self.system = system  # system must be the first message
        if self.system:
            self.add_message(system=self.system)

    @property
    def progression(self) -> Progression:
        return self.messages.progression

    def set_system(self, system: System) -> None:
        """
        Set or update the system message.

        Args:
            system: The new system message to set
        """
        if not self.system:
            self.system = system
            self.messages.insert(0, self.system)
        else:
            old_system = self.system
            self.system = system
            self.messages.insert(0, self.system)
            self.messages.exclude(old_system)

    async def aclear_messages(self):
        """Asynchronously clear all messages except system message."""
        async with self.messages:
            self.clear_messages()

    async def a_add_message(self, **kwargs):
        """
        Asynchronously add a message.

        Args:
            **kwargs: Message creation parameters
        """
        async with self.messages:
            return self.add_message(**kwargs)

    @staticmethod
    def create_instruction(
        *,
        instruction: JsonValue = None,
        context: JsonValue = None,
        guidance: JsonValue = None,
        images: list = None,
        request_fields: JsonValue = None,
        plain_content: JsonValue = None,
        image_detail: Literal["low", "high", "auto"] = None,
        request_model: BaseModel | type[BaseModel] = None,
        response_format: BaseModel | type[BaseModel] = None,
        tool_schemas: dict = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
    ) -> Instruction:

        params = {k: v for k, v in locals().items() if v is not None}

        if isinstance(instruction, Instruction):
            params.pop("instruction")
            instruction.update(**params)
            return instruction
        else:
            return Instruction.create(**params)

    @staticmethod
    def create_assistant_response(
        *,
        sender: Any = None,
        recipient: Any = None,
        assistant_response: AssistantResponse | Any = None,
        template: Template | str = None,
        template_context: dict[str, Any] = None,
    ) -> AssistantResponse:

        params = {k: v for k, v in locals().items() if v is not None}
        template_context = params.pop("template_context", {})
        params.update(template_context)

        if isinstance(assistant_response, AssistantResponse):
            params.pop("assistant_response")
            assistant_response.update(**params)
            return assistant_response

        return AssistantResponse.create(**params)

    @staticmethod
    def create_action_request(
        *,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        function: str = None,
        arguments: dict[str, Any] = None,
        action_request: ActionRequest | None = None,
        template: Template | str = None,
        template_context: dict[str, Any] = None,
    ) -> ActionRequest:

        params = {
            "sender": sender,
            "recipient": recipient,
            "function": function,
            "arguments": arguments,
            "template": template,
            **(template_context or {}),
        }

        if isinstance(action_request, ActionRequest):
            action_request.update(**params)
            return action_request

        return ActionRequest.create(**params)

    @staticmethod
    def create_action_response(
        *,
        action_request: ActionRequest,
        action_output: Any = None,
        action_response: ActionResponse | Any = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
    ) -> ActionResponse:

        if not isinstance(action_request, ActionRequest):
            raise ValueError(
                "Error: please provide a corresponding action request for an "
                "action response."
            )

        params = {
            "action_request": action_request,
            "output": action_output,
            "sender": sender,
            "recipient": recipient,
        }

        if isinstance(action_response, ActionResponse):
            action_response.update(**params)
            return action_response

        return ActionResponse.create(**params)

    @staticmethod
    def create_system(
        *,
        system: Any = None,
        system_datetime: bool | str = None,
        sender: Any = None,
        recipient: Any = None,
        template: Template | str = None,
        template_context: dict[str, Any] = None,
    ) -> System:
        params = {
            "system_datetime": system_datetime,
            "sender": sender,
            "recipient": recipient,
            "template": template,
            **(template_context or {}),
        }
        if isinstance(system, System):
            system.update(**params)
            return system

        if system:
            params["system_message"] = system

        return System.create(**params)

    def add_message(
        self,
        *,
        # common
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        template: Template | str = None,
        template_context: dict[str, Any] = None,
        metadata: dict[str, Any] = None,
        # instruction
        instruction: JsonValue = None,
        context: JsonValue = None,
        guidance: JsonValue = None,
        request_fields: JsonValue = None,
        plain_content: JsonValue = None,
        request_model: BaseModel | type[BaseModel] = None,
        response_format: BaseModel | type[BaseModel] = None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        tool_schemas: dict = None,
        # system
        system: Any = None,
        system_datetime: bool | str = None,
        # assistant_response
        assistant_response: AssistantResponse | Any = None,
        # actions
        action_function: str = None,
        action_arguments: dict[str, Any] = None,
        action_output: Any = None,
        action_request: ActionRequest | None = None,
        action_response: ActionResponse | Any = None,
    ) -> tuple[RoledMessage, Log]:

        _msg = None
        if (
            sum(
                bool(x)
                for x in (
                    instruction,
                    assistant_response,
                    system,
                    action_request,
                )
            )
            > 1
        ):
            raise ValueError("Only one message type can be added at a time.")

        if system:
            _msg = self.create_system(
                system=system,
                system_datetime=system_datetime,
                sender=sender,
                recipient=recipient,
                template=template,
                template_context=template_context,
            )
            self.set_system(_msg)

        elif action_output:
            _msg = self.create_action_response(
                action_request=action_request,
                action_output=action_output,
                action_response=action_response,
                sender=sender,
                recipient=recipient,
            )

        elif action_request or (action_function and action_arguments):
            _msg = self.create_action_request(
                sender=sender,
                recipient=recipient,
                function=action_function,
                arguments=action_arguments,
                action_request=action_request,
                template=template,
                template_context=template_context,
            )

        elif assistant_response:
            _msg = self.create_assistant_response(
                sender=sender,
                recipient=recipient,
                assistant_response=assistant_response,
                template=template,
                template_context=template_context,
            )

        else:
            _msg = self.create_instruction(
                instruction=instruction,
                context=context,
                guidance=guidance,
                images=images,
                request_fields=request_fields,
                plain_content=plain_content,
                image_detail=image_detail,
                request_model=request_model,
                response_format=response_format,
                tool_schemas=tool_schemas,
                sender=sender,
                recipient=recipient,
            )

        if metadata:
            _msg.metadata.setdefault("extra", {})
            _msg.metadata["extra"].update(metadata)

        if _msg in self.messages:
            idx = self.messages.progression.index(_msg.id)
            self.messages.exclude(_msg.id)
            self.messages.insert(idx, _msg)
        else:
            self.messages.include(_msg)

        return _msg

    def clear_messages(self):
        self.messages.clear()
        if self.system:
            self.messages.insert(0, self.system)

    @property
    def last_response(self) -> AssistantResponse | None:
        """Get the last assistant response message."""
        for i in reversed(self.messages.progression):
            if isinstance(self.messages[i], AssistantResponse):
                return self.messages[i]

    @property
    def last_instruction(self) -> Instruction | None:
        """Get the last instruction message."""
        for i in reversed(self.messages.progression):
            if isinstance(self.messages[i], Instruction):
                return self.messages[i]

    @property
    def assistant_responses(self) -> Pile[AssistantResponse]:
        """Get all assistant response messages."""
        return Pile(
            collections=[
                self.messages[i]
                for i in self.messages.progression
                if isinstance(self.messages[i], AssistantResponse)
            ]
        )

    @property
    def action_requests(self) -> Pile[ActionRequest]:
        """Get all action request messages."""
        return Pile(
            collections=[
                self.messages[i]
                for i in self.messages.progression
                if isinstance(self.messages[i], ActionRequest)
            ]
        )

    @property
    def action_responses(self) -> Pile[ActionResponse]:
        """Get all action response messages."""
        return Pile(
            collections=[
                self.messages[i]
                for i in self.messages.progression
                if isinstance(self.messages[i], ActionResponse)
            ]
        )

    @property
    def instructions(self) -> Pile[Instruction]:
        """Get all instruction messages."""
        return Pile(
            collections=[
                self.messages[i]
                for i in self.messages.progression
                if isinstance(self.messages[i], Instruction)
            ]
        )

    def remove_last_instruction_tool_schemas(self) -> None:
        id_ = self.last_instruction.id
        self.messages[id_].tool_schemas = None

    def concat_recent_action_responses_to_instruction(
        self, instruction: Instruction
    ) -> None:
        for i in reversed(self.messages.progression):
            if isinstance(self.messages[i], ActionResponse):
                instruction.context.append(self.messages[i].content)
            else:
                break

    def to_chat_msgs(self, progression=None) -> list[dict]:
        if progression == []:
            return []
        try:
            return [
                self.messages[i].chat_msg
                for i in (progression or self.progression)
            ]
        except Exception as e:
            raise ValueError(
                "Invalid progress, not all requested messages are in the message pile"
            ) from e

    def __bool__(self):
        return bool(self.messages)

    def __contains__(self, message: RoledMessage) -> bool:
        return message in self.messages
