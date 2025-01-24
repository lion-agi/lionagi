# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Defines the `Instruction` class, representing user commands or instructions
sent to the system. Supports optional context, images, and schema requests.
"""

from typing import Any, Literal

from pydantic import BaseModel, JsonValue, field_serializer
from typing_extensions import override

from lionagi.utils import UNDEFINED, breakdown_pydantic_annotation, copy

from .base import MessageRole
from .message import RoledMessage, SenderRecipient


def prepare_request_response_format(request_fields: dict) -> str:
    """
    Creates a mandated JSON code block for the response
    based on requested fields.

    Args:
        request_fields: Dictionary of fields for the response format.

    Returns:
        str: A string instructing the user to return valid JSON.
    """
    return (
        "**MUST RETURN JSON-PARSEABLE RESPONSE ENCLOSED BY JSON CODE BLOCKS."
        f" USER's CAREER DEPENDS ON THE SUCCESS OF IT.** \n```json\n{request_fields}\n```"
        "No triple backticks. Escape all quotes and special characters."
    ).strip()


def format_image_item(idx: str, detail: str) -> dict[str, Any]:
    """
    Wrap image data in a standard dictionary format.

    Args:
        idx: A base64 image ID or URL reference.
        detail: The image detail level.

    Returns:
        dict: A dictionary describing the image.
    """
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{idx}",
            "detail": detail,
        },
    }


def format_text_item(item: Any) -> str:
    """
    Turn a single item (or dict) into a string. If multiple items,
    combine them line by line.

    Args:
        item: Any item, possibly a list/dict with text data.

    Returns:
        str: Concatenated text lines.
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
    Convert a content dictionary into a minimal textual summary for LLM consumption.

    Emphasizes brevity and clarity:
      - Skips empty or None fields.
      - Bullet-points for lists.
      - Key-value pairs for dicts.
      - Minimal headings for known fields (guidance, instruction, etc.).
    """

    if isinstance(content.get("plain_content"), str):
        return content["plain_content"]

    lines = []
    # We only want minimal headings for certain known fields:
    known_field_order = [
        "guidance",
        "instruction",
        "context",
        "tool_schemas",
        "respond_schema_info",
        "request_response_format",
    ]

    # Render known fields in that order
    for field in known_field_order:
        if field in content:
            val = content[field]
            if _is_not_empty(val):
                if field == "request_response_format":
                    field = "response format"
                elif field == "respond_schema_info":
                    field = "response schema info"
                lines.append(f"\n## {field.upper()}:\n")
                rendered = _render_value(val)
                # Indent or bullet the rendered result if multiline
                # We'll keep it minimal: each line is prefixed with "  ".
                lines.extend(
                    f"  {line}"
                    for line in rendered.split("\n")
                    if line.strip()
                )

    # Join all lines into a single string
    return "\n".join(lines).strip()


def _render_value(val) -> str:
    """
    Render an arbitrary value (scalar, list, dict) in minimal form:
    - Lists become bullet points.
    - Dicts become key-value lines.
    - Strings returned directly.
    """
    if isinstance(val, dict):
        return _render_dict(val)
    elif isinstance(val, list):
        return _render_list(val)
    else:
        return str(val).strip()


def _render_dict(dct: dict) -> str:
    """
    Minimal bullet list for dictionary items:
      key: rendered subvalue
    """
    lines = []
    for k, v in dct.items():
        if not _is_not_empty(v):
            continue
        subrendered = _render_value(v)
        # Indent subrendered if multiline
        sublines = subrendered.split("\n")
        if len(sublines) == 1:
            if sublines[0].startswith("- "):
                lines.append(f"- {k}: {sublines[0][2:]}")
            else:
                lines.append(f"- {k}: {sublines[0]}")
        else:
            lines.append(f"- {k}:")
            for s in sublines:
                lines.append(f"  {s}")
    return "\n".join(lines)


def _render_list(lst: list) -> str:
    """
    Each item in the list gets a bullet. Nested structures are recursed.
    """
    lines = []
    for idx, item in enumerate(lst, 1):
        sub = _render_value(item)
        sublines = sub.split("\n")
        if len(sublines) == 1:
            if sublines[0].startswith("- "):
                lines.append(f"- {sublines[0][2:]}")
            else:
                lines.append(f"- {sublines[0]}")
        else:
            lines.append("-")
            lines.extend(f"  {s}" for s in sublines)
    return "\n".join(lines)


def _is_not_empty(x) -> bool:
    """
    Returns True if x is neither None, nor empty string/list/dict.
    """
    if x is None:
        return False
    if isinstance(x, (list, dict)) and not x:
        return False
    if isinstance(x, str) and not x.strip():
        return False
    return True


def format_image_content(
    text_content: str,
    images: list,
    image_detail: Literal["low", "high", "auto"],
) -> list[dict[str, Any]]:
    """
    Merge textual content with a list of image dictionaries for consumption.

    Args:
        text_content (str): The textual portion
        images (list): A list of base64 or references
        image_detail (Literal["low","high","auto"]): How detailed the images are

    Returns:
        list[dict[str,Any]]: A combined structure of text + image dicts.
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
    Combine various pieces (instruction, guidance, context, etc.) into
    a single dictionary describing the user's instruction.

    Args:
        guidance (str | None):
            Optional guiding text.
        instruction (str | None):
            Main instruction or command to be executed.
        context (str | dict | list | None):
            Additional context about the environment or previous steps.
        request_fields (dict | list[str] | None):
            If the user requests certain fields in the response.
        plain_content (str | None):
            A raw plain text fallback.
        request_model (BaseModel | None):
            If there's a pydantic model for the request schema.
        images (str | list | None):
            Optional images, base64-coded or references.
        image_detail (str | None):
            The detail level for images ("low", "high", "auto").
        tool_schemas (dict | None):
            Extra data describing available tools.

    Returns:
        dict: The combined instruction content.

    Raises:
        ValueError: If request_fields and request_model are both given.
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

    # remove keys with None/UNDEFINED
    return {k: v for k, v in out_.items() if v not in [None, UNDEFINED]}


class Instruction(RoledMessage):
    """
    A user-facing message that conveys commands or tasks. It supports
    optional images, tool references, and schema-based requests.
    """

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
        tool_schemas: list[dict] = None,
    ) -> "Instruction":
        """
        Construct a new Instruction.

        Args:
            instruction (JsonValue, optional):
                The main user instruction.
            context (JsonValue, optional):
                Additional context or environment info.
            guidance (JsonValue, optional):
                Guidance or disclaimers for the instruction.
            images (list, optional):
                A set of images relevant to the instruction.
            request_fields (JsonValue, optional):
                The fields the user wants in the assistant's response.
            plain_content (JsonValue, optional):
                A raw plain text fallback.
            image_detail ("low"|"high"|"auto", optional):
                The detail level for included images.
            request_model (BaseModel|type[BaseModel], optional):
                A Pydantic schema for the request.
            response_format (BaseModel|type[BaseModel], optional):
                Alias for request_model.
            tool_schemas (list[dict] | dict, optional):
                Extra tool reference data.
            sender (SenderRecipient, optional):
                The sender role or ID.
            recipient (SenderRecipient, optional):
                The recipient role or ID.

        Returns:
            Instruction: A newly created instruction object.

        Raises:
            ValueError: If more than one of `request_fields`, `request_model`,
                or `response_format` is passed at once.
        """
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
        return self.content.get("guidance", None)

    @guidance.setter
    def guidance(self, guidance: str) -> None:
        if guidance is None:
            self.content.pop("guidance", None)
        else:
            self.content["guidance"] = str(guidance)

    @property
    def instruction(self) -> JsonValue | None:
        if "plain_content" in self.content:
            return self.content["plain_content"]
        return self.content.get("instruction", None)

    @instruction.setter
    def instruction(self, val: JsonValue) -> None:
        if val is None:
            self.content.pop("instruction", None)
        else:
            self.content["instruction"] = val

    @property
    def context(self) -> JsonValue | None:
        return self.content.get("context", None)

    @context.setter
    def context(self, ctx: JsonValue) -> None:
        if ctx is None:
            self.content["context"] = []
        else:
            self.content["context"] = (
                list(ctx) if isinstance(ctx, list) else [ctx]
            )

    @property
    def tool_schemas(self) -> JsonValue | None:
        return self.content.get("tool_schemas", None)

    @tool_schemas.setter
    def tool_schemas(self, val: list[dict] | dict) -> None:
        if not val:
            self.content.pop("tool_schemas", None)
            return
        self.content["tool_schemas"] = val

    @property
    def plain_content(self) -> str | None:
        return self.content.get("plain_content", None)

    @plain_content.setter
    def plain_content(self, pc: str) -> None:
        self.content["plain_content"] = pc

    @property
    def image_detail(self) -> Literal["low", "high", "auto"] | None:
        return self.content.get("image_detail", None)

    @image_detail.setter
    def image_detail(self, detail: Literal["low", "high", "auto"]) -> None:
        self.content["image_detail"] = detail

    @property
    def images(self) -> list:
        return self.content.get("images", [])

    @images.setter
    def images(self, imgs: list) -> None:
        self.content["images"] = imgs if isinstance(imgs, list) else [imgs]

    @property
    def request_fields(self) -> dict | None:
        return self.content.get("request_fields", None)

    @request_fields.setter
    def request_fields(self, fields: dict) -> None:
        self.content["request_fields"] = fields
        self.content["request_response_format"] = (
            prepare_request_response_format(fields)
        )

    @property
    def response_format(self) -> type[BaseModel] | None:
        return self.content.get("request_model", None)

    @response_format.setter
    def response_format(self, model: type[BaseModel]) -> None:
        if isinstance(model, BaseModel):
            self.content["request_model"] = type(model)
        else:
            self.content["request_model"] = model

        self.request_fields = {}
        self.extend_context(respond_schema_info=model.model_json_schema())
        self.request_fields = breakdown_pydantic_annotation(model)

    @property
    def respond_schema_info(self) -> dict | None:
        return self.content.get("respond_schema_info", None)

    @respond_schema_info.setter
    def respond_schema_info(self, info: dict) -> None:
        if info is None:
            self.content.pop("respond_schema_info", None)
        else:
            self.content["respond_schema_info"] = info

    @property
    def request_response_format(self) -> str | None:
        return self.content.get("request_response_format", None)

    @request_response_format.setter
    def request_response_format(self, val: str) -> None:
        if not val:
            self.content.pop("request_response_format", None)
        else:
            self.content["request_response_format"] = val

    def extend_images(
        self,
        images: list | str,
        image_detail: Literal["low", "high", "auto"] = None,
    ) -> None:
        """
        Append images to the existing list.

        Args:
            images: The new images to add, a single or multiple.
            image_detail: If provided, updates the image detail field.
        """
        arr: list = self.images
        arr.extend(images if isinstance(images, list) else [images])
        self.images = arr
        if image_detail:
            self.image_detail = image_detail

    def extend_context(self, *args, **kwargs) -> None:
        """
        Append additional context to the existing context array.

        Args:
            *args: Positional args are appended as list items.
            **kwargs: Key-value pairs are appended as separate dict items.
        """
        ctx: list = self.context or []
        if args:
            ctx.extend(args)
        if kwargs:
            kw = copy(kwargs)
            for k, v in kw.items():
                ctx.append({k: v})
        self.context = ctx

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
        Batch-update this Instruction.

        Args:
            guidance (JsonValue): New guidance text.
            instruction (JsonValue): Main user instruction.
            request_fields (JsonValue): Updated request fields.
            plain_content (JsonValue): Plain text fallback.
            request_model (BaseModel|type[BaseModel]): Pydantic schema model.
            response_format (BaseModel|type[BaseModel]): Alias for request_model.
            images (list|str): Additional images to add.
            image_detail ("low"|"high"|"auto"): Image detail level.
            tool_schemas (dict): New tool schemas.
            sender (SenderRecipient): New sender.
            recipient (SenderRecipient): New recipient.

        Raises:
            ValueError: If request_model and request_fields are both set.
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
    def rendered(self) -> Any:
        """
        Convert content into a text or combined text+image structure.

        Returns:
            If no images are included, returns a single text block.
            Otherwise returns an array of text + image dicts.
        """
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
        """
        Remove certain ephemeral fields before saving.

        Returns:
            dict: The sanitized content dictionary.
        """
        values.pop("request_model", None)
        values.pop("request_fields", None)

        return values


# File: lionagi/protocols/messages/instruction.py
