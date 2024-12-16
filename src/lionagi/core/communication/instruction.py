# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.core.generic.log import Log
from lionagi.core.typing import (
    ID,
    Any,
    BaseModel,
    JsonValue,
    Literal,
    override,
)
from lionagi.integrations.pydantic_ import break_down_pydantic_annotation
from lionagi.libs.parse import to_str
from lionagi.libs.utils import copy

from .message import MessageFlag, MessageRole, RoledMessage
from .utils import (
    format_image_content,
    format_text_content,
    prepare_instruction_content,
    prepare_request_response_format,
)


class Instruction(RoledMessage):
    """
    Represents an instruction message in the system.

    This class encapsulates various components of an instruction, including
    the main instruction content, guidance, context, and request fields.
    It supports both text and image content, and can handle structured
    request specifications through Pydantic models.

    Attributes:
        instruction: The main instruction content
        context: Additional context information
        guidance: Optional guidance for instruction execution
        images: Optional list of images
        request_fields: Fields requested in the response
        plain_content: Plain text content
        image_detail: Level of detail for images
        request_model: Optional Pydantic model for structured requests
        tool_schemas: Optional tool schemas
    """

    @override
    def __init__(
        self,
        instruction: JsonValue | MessageFlag,
        context: JsonValue | MessageFlag = None,
        guidance: JsonValue | MessageFlag = None,
        images: list | MessageFlag = None,
        sender: ID.Ref | MessageFlag = None,
        recipient: ID.Ref | MessageFlag = None,
        request_fields: JsonValue | MessageFlag = None,
        plain_content: JsonValue | MessageFlag = None,
        image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
        request_model: BaseModel | type[BaseModel] | MessageFlag = None,
        tool_schemas: dict | None = None,
        protected_init_params: dict | None = None,
    ) -> None:
        """
        Initialize an Instruction instance.

        Args:
            instruction: The main instruction content
            context: Additional context for the instruction
            guidance: Guidance information
            images: List of images
            sender: The sender of the instruction
            recipient: The recipient of the instruction
            request_fields: Fields requested in the response
            plain_content: Plain text content
            image_detail: Level of detail for images
            request_model: A Pydantic model for structured requests
            tool_schemas: Tool schemas
            protected_init_params: Protected initialization parameters
        """
        message_flags = [
            instruction,
            context,
            guidance,
            images,
            sender,
            recipient,
            request_fields,
            plain_content,
            image_detail,
            tool_schemas,
            request_model,
        ]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            protected_init_params = protected_init_params or {}
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.USER)
            return

        super().__init__(
            role=MessageRole.USER,
            content=prepare_instruction_content(
                guidance=guidance,
                instruction=instruction,
                context=context,
                images=images,
                request_fields=request_fields,
                plain_content=plain_content,
                image_detail=image_detail,
                request_model=request_model,
                tool_schemas=tool_schemas,
            ),
            sender=sender or "user",
            recipient=recipient or "N/A",
        )

    @property
    def guidance(self) -> str | None:
        """Get the guidance content of the instruction."""
        return self.content.get(["guidance"], None)

    @guidance.setter
    def guidance(self, guidance: str) -> None:
        """Set the guidance content of the instruction."""
        if not isinstance(guidance, str):
            guidance = to_str(guidance)
        self.content["guidance"] = guidance

    @property
    def instruction(self) -> JsonValue | None:
        """Get the main instruction content."""
        if "plain_content" in self.content:
            return self.content["plain_content"]
        else:
            return self.content.get(["instruction"], None)

    @instruction.setter
    def instruction(self, instruction: JsonValue) -> None:
        """Set the main instruction content."""
        self.content["instruction"] = instruction

    @property
    def context(self) -> JsonValue | None:
        """Get the context of the instruction."""
        return self.content.get(["context"], None)

    @context.setter
    def context(self, context: JsonValue) -> None:
        """Set the context of the instruction."""
        if not isinstance(context, list):
            context = [context]
        self.content["context"] = context

    @property
    def tool_schemas(self) -> JsonValue | None:
        """Get the schemas of the tools in the instruction."""
        return self.content.get(["tool_schemas"], None)

    @tool_schemas.setter
    def tool_schemas(self, tool_schemas: dict) -> None:
        """Set the schemas of the tools in the instruction."""
        self.content["tool_schemas"] = tool_schemas

    @property
    def plain_content(self) -> str | None:
        """Get the plain text content of the instruction."""
        return self.content.get(["plain_content"], None)

    @plain_content.setter
    def plain_content(self, plain_content: str) -> None:
        """Set the plain text content of the instruction."""
        self.content["plain_content"] = plain_content

    @property
    def image_detail(self) -> Literal["low", "high", "auto"] | None:
        """Get the image detail level of the instruction."""
        return self.content.get(["image_detail"], None)

    @image_detail.setter
    def image_detail(
        self, image_detail: Literal["low", "high", "auto"]
    ) -> None:
        """Set the image detail level of the instruction."""
        self.content["image_detail"] = image_detail

    @property
    def images(self) -> list:
        """Get the images associated with the instruction."""
        return self.content.get(["images"], [])

    @images.setter
    def images(self, images: list) -> None:
        """Set the images associated with the instruction."""
        if not isinstance(images, list):
            images = [images]
        self.content["images"] = images

    @property
    def request_fields(self) -> dict | None:
        """Get the requested fields in the instruction."""
        return self.content.get(["request_fields"], None)

    @request_fields.setter
    def request_fields(self, request_fields: dict) -> None:
        """Set the requested fields in the instruction."""
        self.content["request_fields"] = request_fields
        self.content["request_response_format"] = (
            prepare_request_response_format(request_fields)
        )

    @property
    def request_model(self) -> type[BaseModel] | None:
        """Get the request model of the instruction."""
        return self.content.get(["request_model"], None)

    @request_model.setter
    def request_model(self, request_model: type[BaseModel]) -> None:
        """
        Set the request model of the instruction.

        This also updates request fields and context based on the model.
        """
        if isinstance(request_model, BaseModel):
            self.content["request_model"] = type(request_model)
        else:
            self.content["request_model"] = request_model

        self.request_fields = {}
        self.extend_context(
            respond_schema_info=request_model.model_json_schema()
        )
        self.request_fields = break_down_pydantic_annotation(request_model)

    def extend_images(
        self,
        images: list | str,
        image_detail: Literal["low", "high", "auto"] = None,
    ) -> None:
        """
        Add new images to the instruction.

        Args:
            images: New images to add
            image_detail: Optional new image detail level
        """
        images = images if isinstance(images, list) else [images]
        _ima: list = self.content.get(["images"], [])
        _ima.extend(images)
        self.images = _ima

        if image_detail:
            self.image_detail = image_detail

    def extend_context(self, *args, **kwargs) -> None:
        """
        Add new context to the instruction.

        Args:
            *args: Positional arguments to add to context
            **kwargs: Keyword arguments to add to context
        """
        context: list = self.content.get("context", [])

        if args:
            context.extend(args)
        if kwargs:
            kwargs = copy(kwargs)
            for k, v in kwargs.items():
                context.append({k: v})

        self.context = context

    def update(
        self,
        *args,
        guidance: JsonValue = None,
        instruction: JsonValue = None,
        request_fields: JsonValue = None,
        plain_content: JsonValue = None,
        request_model: BaseModel | type[BaseModel] = None,
        images: str | list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        tool_schemas: dict = None,
        **kwargs,
    ):
        """
        Update multiple aspects of the instruction.

        Args:
            *args: Positional arguments for context update
            guidance: New guidance content
            instruction: New instruction content
            request_fields: New request fields
            plain_content: New plain text content
            request_model: New request model
            images: New images to add
            image_detail: New image detail level
            tool_schemas: New tool schemas
            **kwargs: Additional keyword arguments for context update

        Raises:
            ValueError: If both request_model and request_fields are provided
        """
        if request_model and request_fields:
            raise ValueError(
                "You cannot pass both request_model and request_fields "
                "to create_instruction"
            )
        if guidance:
            self.guidance = guidance

        if instruction:
            self.instruction = instruction

        if plain_content:
            self.plain_content = plain_content

        if request_fields:
            self.request_fields = request_fields

        if request_model:
            self.request_model = request_model

        if images:
            self.images = images

        if image_detail:
            self.image_detail = image_detail

        if tool_schemas:
            self.tool_schemas = tool_schemas

        self.extend_context(*args, **kwargs)

    @override
    def _format_content(self) -> dict[str, Any]:
        """Format the content of the instruction."""
        content = self.content.to_dict()
        text_content = format_text_content(content)
        if "images" not in content:
            return {"role": self.role.value, "content": text_content}
        else:
            content = format_image_content(
                text_content=text_content,
                images=self.images,
                image_detail=self.image_detail,
            )
            return {"role": self.role.value, "content": content}

    @override
    def to_log(self) -> Log:
        """
        Convert the message to a Log object.

        Creates a Log instance containing the message content and additional
        information as loginfo.

        Returns:
            Log: A Log object representing the message.
        """
        dict_ = self.to_dict()
        content = dict_.pop("content")
        content.pop("request_model", None)
        content.pop("request_fields", None)
        _log = Log(
            content=content,
            loginfo=dict_,
        )
        return _log


__all__ = ["Instruction"]
