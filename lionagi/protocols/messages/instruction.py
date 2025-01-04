# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal, override

from pydantic import BaseModel, JsonValue, field_serializer

from lionagi.utils import UNDEFINED, breakdown_pydantic_annotation, copy

from .base import MessageRole
from .message import RoledMessage, SenderRecipient


def prepare_request_response_format(request_fields: dict) -> str:
    """
    Prepare a standardized format for request responses.

    Args:
        request_fields: Dictionary of fields to include in response

    Returns:
        str: Formatted response template
    """
    return (
        "**MUST RETURN JSON-PARSEABLE RESPONSE ENCLOSED BY JSON CODE BLOCKS."
        f" USER's CAREER DEPENDS ON THE SUCCESS OF IT.** \n```json\n{request_fields}\n```"
    ).strip()


def format_image_item(idx: str, x: str, /) -> dict[str, Any]:
    """
    Create an image_url dictionary for content formatting.

    Args:
        idx: Base64 encoded image data
        x: Image detail level

    Returns:
        dict: Formatted image item
    """
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{idx}",
            "detail": x,
        },
    }


def format_text_item(item: Any) -> str:
    """
    Format a text item or list of items into a string.

    Args:
        item: Text item(s) to format

    Returns:
        str: Formatted text
    """
    msg = ""
    item = [item] if not isinstance(item, list) else item
    for j in item:
        if isinstance(j, dict):
            for k, v in j.items():
                if v is not None:
                    msg += f"- {k}: {v} \n\n"
        else:
            if j is not None:
                msg += f"{j}\n"
    return msg


def format_text_content(content: dict) -> str:
    """
    Format dictionary content into a structured text format.

    Args:
        content: Dictionary containing content sections

    Returns:
        str: Formatted text content
    """
    if "plain_content" in content and isinstance(
        content["plain_content"], str
    ):
        return content["plain_content"]

    msg = "\n---\n # Task\n"

    for k in [
        "guidance",
        "instruction",
        "context",
        "tool_schemas",
        "respond_schema_info",
        "request_response_format",
    ]:
        if k in content:
            v = content[k]

            if k == "tool_schemas":
                if "tools" in v:
                    v = v["tools"]

                if isinstance(v, list):
                    z = []
                    for idx, z_ in enumerate(v):
                        if isinstance(z_, dict) and "function" in z_:
                            z.append({f"Tool {idx+1}": z_["function"]})
                    v = z

            if k == "request_response_format":
                k = "response format"

            if v not in [None, [], {}, UNDEFINED]:
                if isinstance(v, list):
                    msg += f"## - **{k}**\n"
                    for i in v:
                        if (
                            len(format_text_item(v).replace("\n", "").strip())
                            > 0
                        ):
                            msg += format_text_item(i).strip()
                    msg += "\n"
                else:
                    if len(format_text_item(v).replace("\n", "").strip()) > 0:
                        msg += (
                            f"## - **{k}**\n{format_text_item(v).strip()}\n\n"
                        )

    if not msg.endswith("\n\n"):
        msg += "\n\n---\n"
    else:
        msg += "---\n"
    return msg


def format_image_content(
    text_content: str,
    images: list,
    image_detail: Literal["low", "high", "auto"],
) -> dict[str, Any]:
    """
    Format text content with images for message content.

    Args:
        text_content: The text content to format
        images: List of images to include
        image_detail: Level of detail for images

    Returns:
        dict: Formatted content with text and images
    """
    content = [{"type": "text", "text": text_content}]
    content.extend(format_image_item(i, image_detail) for i in images)
    return content


def prepare_instruction_content(
    guidance: str | None = None,
    instruction: str | None = None,
    context: str | dict | list | None = None,
    request_fields: dict | list[str] | None = None,
    plain_content: str | None = None,
    request_model: BaseModel = None,
    images: str | list | None = None,
    image_detail: Literal["low", "high", "auto"] | None = None,
    tool_schemas: dict | None = None,
) -> dict:
    """
    Prepare the content for an instruction message.

    Args:
        guidance: Optional guidance text
        instruction: Main instruction content
        context: Additional context information
        request_fields: Fields to request in response
        plain_content: Plain text content
        request_model: Pydantic model for structured requests
        images: Images to include
        image_detail: Level of detail for images
        tool_schemas: Tool schemas to include

    Returns:
        Note: Prepared instruction content

    Raises:
        ValueError: If both request_fields and request_model are provided
    """
    if request_fields and request_model:
        raise ValueError(
            "only one of request_fields or request_model can be provided"
        )

    out_ = {"context": []}
    if guidance:
        out_["guidance"] = guidance
    if instruction:
        out_["instruction"] = instruction
    if context:
        if isinstance(context, list):
            out_["context"].extend(context)
        else:
            out_["context"].append(context)
    if images:
        out_["images"] = images if isinstance(images, list) else [images]
        out_["image_detail"] = image_detail or "low"

    if tool_schemas:
        out_["tool_schemas"] = tool_schemas

    if request_model:
        out_["request_model"] = request_model
        request_fields = breakdown_pydantic_annotation(request_model)
        out_["respond_schema_info"] = request_model.model_json_schema()

    if request_fields:
        _fields = request_fields if isinstance(request_fields, dict) else {}
        if not isinstance(request_fields, dict):
            _fields = {i: "..." for i in request_fields}
        out_["request_fields"] = _fields
        out_["request_response_format"] = prepare_request_response_format(
            request_fields=_fields
        )

    if plain_content:
        out_["plain_content"] = plain_content

    return {k: v for k, v in out_.items() if v not in [None, UNDEFINED]}


class Instruction(RoledMessage):

    @classmethod
    def create(
        cls,
        instruction: JsonValue = None,
        *,
        context: JsonValue = None,
        guidance: JsonValue = None,
        images: list = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        request_fields: JsonValue = None,
        plain_content: JsonValue = None,
        image_detail: Literal["low", "high", "auto"] = None,
        request_model: BaseModel | type[BaseModel] = None,
        response_format: BaseModel | type[BaseModel] = None,
        tool_schemas: dict = None,
    ):

        if (
            sum(
                bool(i)
                for i in [request_fields, request_model, response_format]
            )
            > 1
        ):
            raise ValueError(
                "only one of request_fields or request_model can be provided"
                "response_format is alias of request_model"
            )
        content = prepare_instruction_content(
            guidance=guidance,
            instruction=instruction,
            context=context,
            request_fields=request_fields,
            plain_content=plain_content,
            request_model=request_model or response_format,
            images=images,
            image_detail=image_detail,
            tool_schemas=tool_schemas,
        )
        return cls(
            role=MessageRole.USER,
            content=content,
            sender=sender,
            recipient=recipient,
        )

    @property
    def guidance(self) -> str | None:
        """Get the guidance content of the instruction."""
        return self.content.get("guidance", None)

    @guidance.setter
    def guidance(self, guidance: str) -> None:
        """Set the guidance content of the instruction."""
        if guidance is None:
            self.content.pop("guidance", None)
            return

        if not isinstance(guidance, str):
            guidance = str(guidance)
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
        if instruction is None:
            self.content.pop("instruction", None)
            return

        self.content["instruction"] = instruction

    @property
    def context(self) -> JsonValue | None:
        """Get the context of the instruction."""
        return self.content.get("context", None)

    @context.setter
    def context(self, context: JsonValue) -> None:
        """Set the context of the instruction."""
        if context is None:
            self.content["context"] = []
            return

        if not isinstance(context, list):
            context = [context]
        self.content["context"] = context

    @property
    def tool_schemas(self) -> JsonValue | None:
        """Get the schemas of the tools in the instruction."""
        return self.content.get("tool_schemas", None)

    @tool_schemas.setter
    def tool_schemas(self, tool_schemas: dict) -> None:
        """Set the schemas of the tools in the instruction."""
        if not tool_schemas:
            self.content.pop("tool_schemas", None)
            return

        self.content["tool_schemas"] = tool_schemas

    @property
    def plain_content(self) -> str | None:
        """Get the plain text content of the instruction."""
        return self.content.get("plain_content", None)

    @plain_content.setter
    def plain_content(self, plain_content: str) -> None:
        """Set the plain text content of the instruction."""
        self.content["plain_content"] = plain_content

    @property
    def image_detail(self) -> Literal["low", "high", "auto"] | None:
        """Get the image detail level of the instruction."""
        return self.content.get("image_detail", None)

    @image_detail.setter
    def image_detail(
        self, image_detail: Literal["low", "high", "auto"]
    ) -> None:
        """Set the image detail level of the instruction."""
        self.content["image_detail"] = image_detail

    @property
    def images(self) -> list:
        """Get the images associated with the instruction."""
        return self.content.get("images", [])

    @images.setter
    def images(self, images: list) -> None:
        """Set the images associated with the instruction."""
        if not isinstance(images, list):
            images = [images]
        self.content["images"] = images

    @property
    def request_fields(self) -> dict | None:
        """Get the requested fields in the instruction."""
        return self.content.get("request_fields", None)

    @request_fields.setter
    def request_fields(self, request_fields: dict) -> None:
        """Set the requested fields in the instruction."""
        self.content["request_fields"] = request_fields
        self.content["request_response_format"] = (
            prepare_request_response_format(request_fields)
        )

    @property
    def response_format(self) -> type[BaseModel] | None:
        """Get the request model of the instruction."""
        return self.content.get("request_model", None)

    @response_format.setter
    def response_format(self, request_model: type[BaseModel]) -> None:
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
        self.request_fields = breakdown_pydantic_annotation(request_model)

    @property
    def respond_schema_info(self) -> dict | None:
        """Get the response schema information."""
        return self.content.get("respond_schema_info", None)

    @respond_schema_info.setter
    def respond_schema_info(self, respond_schema_info: dict) -> None:
        """Set the response schema information."""
        if respond_schema_info is None:
            self.content.pop("respond_schema_info", None)
        else:
            self.content["respond_schema_info"] = respond_schema_info

    @property
    def request_response_format(self) -> str | None:
        """Get the request response format."""
        return self.content.get("request_response_format", None)

    @request_response_format.setter
    def request_response_format(self, request_response_format: str) -> None:
        """Set the request response format."""
        if not request_response_format:
            self.content.pop("request_response_format", None)
        else:
            self.content["request_response_format"] = request_response_format

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
        _ima: list = self.content.get("images", [])
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
        *,
        guidance: JsonValue = None,
        instruction: JsonValue = None,
        context: JsonValue = None,
        request_fields: JsonValue = None,
        plain_content: JsonValue = None,
        request_model: BaseModel | type[BaseModel] = None,
        response_format: BaseModel | type[BaseModel] = None,
        images: str | list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        tool_schemas: dict = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
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
        if response_format and request_model:
            raise ValueError(
                "only one of request_fields or request_model can be provided"
                "response_format is alias of request_model"
            )

        request_model = request_model or response_format

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
            self.response_format = request_model

        if images:
            self.images = images

        if image_detail:
            self.image_detail = image_detail

        if tool_schemas:
            self.tool_schemas = tool_schemas

        if sender:
            self.sender = sender

        if recipient:
            self.recipient = recipient

        if context:
            self.extend_context(context)

    @override
    @property
    def rendered(self) -> dict[str, Any]:
        """Format the content of the instruction."""
        content = copy(self.content)
        text_content = format_text_content(content)
        if "images" not in content:
            return text_content

        else:
            return format_image_content(
                text_content=text_content,
                images=self.images,
                image_detail=self.image_detail,
            )

    @field_serializer("content")
    def _serialize_content(self, values) -> dict:
        """Serialize the content of the instruction."""
        values.pop("request_model", None)
        values.pop("request_fields", None)

        return values
