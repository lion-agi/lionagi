# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.core.generic.types import LogManager, Pile, Progression
from lionagi.core.typing import ID, Any, BaseModel, JsonValue, Literal

from .action_request import ActionRequest
from .action_response import ActionResponse
from .assistant_response import AssistantResponse
from .instruction import Instruction
from .message import RoledMessage
from .system import System

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


class MessageManager:
    """
    Manages messages within a communication system.

    This class provides functionality for creating, adding, and managing
    different types of messages in a conversation. It maintains message
    history, handles system messages, and provides access to specific
    message types.

    Attributes:
        messages (Pile[RoledMessage]): Collection of messages
        logger (LogManager): Logger for message history
        system (System): System message setting context
        save_on_clear (bool): Whether to save logs when clearing
    """

    def __init__(
        self, messages=None, logger=None, system=None, save_on_clear=True
    ):
        """
        Initialize a MessageManager instance.

        Args:
            messages: Initial list of messages
            logger: Logger instance for message history
            system: Initial system message
            save_on_clear: Whether to save logs when clearing
        """
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

    @property
    def progress(self) -> Progression:
        """Get the progression of messages."""
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
    ) -> Instruction:
        """
        Create an instruction message.

        Args:
            sender: Message sender
            recipient: Message recipient
            instruction: Instruction content
            context: Additional context
            guidance: Optional guidance
            plain_content: Plain text content
            request_fields: Fields to request
            request_model: Pydantic model for requests
            images: Optional images
            image_detail: Image detail level
            tool_schemas: Optional tool schemas
            **kwargs: Additional parameters

        Returns:
            Instruction: The created instruction
        """
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
        """
        Create an assistant response message.

        Args:
            sender: Message sender
            recipient: Message recipient
            assistant_response: Response content

        Returns:
            AssistantResponse: The created response
        """
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
        """
        Create an action request message.

        Args:
            sender: Message sender
            recipient: Message recipient
            function: Function to execute
            arguments: Function arguments
            action_request: Existing request to use

        Returns:
            ActionRequest: The created request

        Raises:
            ValueError: If action_request is not an ActionRequest instance
        """
        if action_request:
            if not isinstance(action_request, ActionRequest):
                raise ValueError(
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
        """
        Create an action response message.

        Args:
            action_request: The corresponding action request
            action_response: Response content

        Returns:
            ActionResponse: The created response

        Raises:
            ValueError: If action_request is invalid or already responded to
        """
        if not isinstance(action_request, ActionRequest):
            raise ValueError(
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
                    action_response.ln_id
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
        """
        Create a system message.

        Args:
            system: System message content
            sender: Message sender
            recipient: Message recipient
            system_datetime: Whether to include datetime

        Returns:
            System: The created system message
        """
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
        """
        Add a message to the manager.

        This method creates and adds a message of the specified type. Only
        one message type can be added at a time.

        Args:
            sender: Message sender
            recipient: Message recipient
            instruction: Instruction content
            context: Additional context
            guidance: Optional guidance
            plain_content: Plain text content
            request_fields: Fields to request
            request_model: Pydantic model for requests
            images: Optional images
            image_detail: Image detail level
            assistant_response: Assistant response content
            system: System message content
            system_datetime: Whether to include datetime
            function: Function for action request
            arguments: Arguments for action request
            action_request: Action request
            action_response: Action response
            metadata: Additional metadata

        Returns:
            RoledMessage: The added message

        Raises:
            ValueError: If multiple message types are specified
        """
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
            self.messages.exclude(_msg.ln_id)
            self.messages.insert(0, _msg)
        else:
            self.messages.include(_msg)

        self.logger.log(_msg.to_log())
        return _msg

    def clear_messages(self) -> None:
        """Clear all messages except the system message."""
        if self.save_on_clear:
            self.logger.dump(clear=True)

        self.messages.clear()
        self.progress.clear()
        if self.system:
            self.messages.include(self.system)
            self.progress.insert(0, self.system)

    @property
    def last_response(self) -> AssistantResponse | None:
        """Get the last assistant response message."""
        for i in reversed(self.messages.progress):
            if isinstance(self.messages[i], AssistantResponse):
                return self.messages[i]

    @property
    def last_instruction(self) -> Instruction | None:
        """Get the last instruction message."""
        for i in reversed(self.messages.progress):
            if isinstance(self.messages[i], Instruction):
                return self.messages[i]

    @property
    def assistant_responses(self) -> Pile[AssistantResponse]:
        """Get all assistant response messages."""
        return Pile(
            [
                self.messages[i]
                for i in self.messages.progress
                if isinstance(self.messages[i], AssistantResponse)
            ]
        )

    @property
    def action_requests(self) -> Pile[ActionRequest]:
        """Get all action request messages."""
        return Pile(
            [
                self.messages[i]
                for i in self.messages.progress
                if isinstance(self.messages[i], ActionRequest)
            ]
        )

    @property
    def action_responses(self) -> Pile[ActionResponse]:
        """Get all action response messages."""
        return Pile(
            [
                self.messages[i]
                for i in self.messages.progress
                if isinstance(self.messages[i], ActionResponse)
            ]
        )

    @property
    def instructions(self) -> Pile[Instruction]:
        """Get all instruction messages."""
        return Pile(
            [
                self.messages[i]
                for i in self.messages.progress
                if isinstance(self.messages[i], Instruction)
            ]
        )

    def to_chat_msgs(self, progress=None) -> list[dict]:
        """
        Convert messages to chat format.

        Args:
            progress: Optional specific progression to convert

        Returns:
            list[dict]: Messages in chat format

        Raises:
            ValueError: If requested messages are not in the message pile
        """
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
        """Check if there are any logs."""
        return not self.logger.logs.is_empty()
