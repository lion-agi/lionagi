# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from pydantic import BaseModel, JsonValue
from typing_extensions import Self, override

from lionagi.protocols.log import Log
from lionagi.utils import break_down_pydantic_annotation, copy

from .message import ID, MessageFlag, MessageRole, RoledMessage, Template
from .utils import (
    format_image_content,
    format_text_content,
    prepare_instruction_content,
    prepare_request_response_format,
)


class Instruction(RoledMessage):

    @classmethod
    def create(
        cls,
        instruction: JsonValue = None,
        context: JsonValue = None,
        guidance: JsonValue = None,
        images: list = None,
        sender: ID.SenderRecipient = None,
        recipient: ID.SenderRecipient = None,
        request_fields: JsonValue = None,
        plain_content: JsonValue = None,
        image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
        request_model: BaseModel | type[BaseModel] | MessageFlag = None,
        tool_schemas: dict | None = None,
        template: Template = None,
    ) -> Self:
        return Instruction(
            template=template,
            sender=sender,
            recipient=recipient,
            role=MessageRole.USER,
            content=prepare_instruction_content(
                instruction=instruction,
                context=context,
                guidance=guidance,
                images=images,
                request_fields=request_fields,
                plain_content=plain_content,
                image_detail=image_detail,
                request_model=request_model,
                tool_schemas=tool_schemas,
            ),
        )

    @property
    def guidance(self) -> str | None:
        """Get the guidance content of the instruction."""
        return self.content.get("guidance", None)

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
            return self.content.get("instruction", None)

    @instruction.setter
    def instruction(self, instruction: JsonValue) -> None:
        """Set the main instruction content."""
        self.content["instruction"] = instruction

    @property
    def context(self) -> JsonValue | None:
        """Get the context of the instruction."""
        return self.content.get("context", None)

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
        content: dict = dict_.pop("content")
        content.pop("request_model", None)
        content.pop("request_fields", None)
        content.pop("tool_schemas", None)
        content.pop("request_response_format", None)
        for i in content["context"]:
            if "respond_schema_info" in i and isinstance(i, dict):
                i.pop("respond_schema_info")
        return Log.create(content)


__all__ = ["Instruction"]
