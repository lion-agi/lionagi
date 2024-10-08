import inspect
from typing import Any, Literal

from lionabc.exceptions import LionTypeError
from lionfuncs import LN_UNDEFINED
from typing_extensions import override

from lion_core.communication.message import (
    MessageFlag,
    MessageRole,
    RoledMessage,
)
from lion_core.form.base import BaseForm
from lion_core.form.form import Form
from lion_core.generic.note import Note, note


def prepare_request_response_format(request_fields: dict) -> str:
    return (
        "MUST RETURN JSON-PARSEABLE RESPONSE ENCLOSED BY JSON CODE BLOCKS. "
        f"---\n```json\n{request_fields}\n```\n---"
    ).strip()


def _f(idx: str, x: str, /) -> dict[str, Any]:
    """Create an image_url dict for content formatting."""
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{idx}",
            "detail": x,
        },
    }


def format_image_content(
    text_content: str,
    images: list,
    image_detail: Literal["low", "high", "auto"],
) -> dict[str, Any]:
    """Format text content with images for message content."""
    content = [{"type": "text", "text": text_content}]
    content.extend(_f(i, image_detail) for i in images)
    return content


def prepare_instruction_content(
    guidance: str | None = None,
    instruction: str | None = None,
    context: str | dict | list | None = None,
    request_fields: dict | None = None,
    images: str | list | None = None,
    image_detail: Literal["low", "high", "auto"] | None = None,
) -> Note:
    """Prepare the content for an instruction message."""
    out_ = {}
    if guidance:
        out_["guidance"] = guidance

    out_["instruction"] = instruction or "N/A"
    if context:
        if not isinstance(context, str):
            out_["context"] = context
        else:
            out_["context"] = [context]
    if images:
        out_["images"] = images if isinstance(images, list) else [images]
        out_["image_detail"] = image_detail or "low"
    if request_fields:
        out_["request_fields"] = request_fields
        out_["request_response_format"] = prepare_request_response_format(
            request_fields=request_fields
        )

    return note(
        **{k: v for k, v in out_.items() if v not in [None, LN_UNDEFINED]},
    )


class Instruction(RoledMessage):
    """Represents an instruction message in the system."""

    @override
    def __init__(
        self,
        instruction: Any | MessageFlag,
        context: Any | MessageFlag = None,
        guidance: Any | MessageFlag = None,
        images: list | MessageFlag = None,
        sender: Any | MessageFlag = None,
        recipient: Any | MessageFlag = None,
        request_fields: dict | MessageFlag = None,
        image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
        protected_init_params: dict | None = None,
    ) -> None:
        """Initialize an Instruction instance."""
        message_flags = [
            instruction,
            context,
            images,
            sender,
            recipient,
            request_fields,
            image_detail,
        ]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
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
                image_detail=image_detail,
            ),
            sender=sender or "user",
            recipient=recipient or "N/A",
        )

    @property
    def guidance(self):
        """Return the guidance content."""
        return self.content.get(["guidance"], None)

    @property
    def instruction(self):
        """Return the main instruction content."""
        return self.content.get(["instruction"], None)

    def update_images(
        self,
        images: list | str,
        image_detail: Literal["low", "high", "auto"] = None,
    ) -> None:
        """Add new images and update the image detail level."""
        images = images if isinstance(images, list) else [images]
        _ima: list = self.content.get(["images"], [])
        _ima.extend(images)
        self.content["images"] = _ima

        if image_detail:
            self.content["image_detail"] = image_detail

    def update_guidance(self, guidance: str) -> None:
        """Update the guidance content of the instruction."""
        if guidance and isinstance(guidance, str):
            self.content["guidance"] = guidance
            return
        raise LionTypeError(
            "Invalid guidance. Guidance must be a string.",
        )

    def update_request_fields(self, request_fields: dict) -> None:
        """Update the requested fields in the instruction."""
        self.content["request_fields"].update(request_fields)
        format_ = prepare_request_response_format(
            request_fields=self.content["request_fields"],
        )
        self.content["request_response_format"] = format_

    def update_context(self, *args, **kwargs) -> None:
        """Add new context to the instruction."""
        self.content["context"] = self.content.get("context", [])
        if args:
            self.content["context"].extend(args)
        if kwargs:
            self.content["context"].append(kwargs)

    @override
    def _format_content(self) -> dict[str, Any]:
        """Format the content of the instruction."""
        _msg = super()._format_content()
        if isinstance(_msg["content"], str):
            return _msg

        else:
            content = _msg["content"]
            content.pop("images")
            content.pop("image_detail")
            text_content = str(content)
            content = format_image_content(
                text_content=text_content,
                images=self.content.get(["images"]),
                image_detail=self.content.get(["image_detail"]),
            )
            _msg["content"] = content
            return _msg

    @classmethod
    def from_form(
        cls,
        form: BaseForm | type[Form],
        *,
        sender: str | None = None,
        recipient: Any = None,
        images: str | None = None,
        image_detail: str | None = None,
        strict: bool = None,
        assignment: str = None,
        task_description: str = None,
        fill_inputs: bool = True,
        none_as_valid_value: bool = False,
        input_value_kwargs: dict = None,
    ) -> "Instruction":
        """Create an Instruction instance from a form."""
        try:
            if inspect.isclass(form) and issubclass(form, Form):
                form = form(
                    strict=strict,
                    assignment=assignment,
                    task_description=task_description,
                    fill_inputs=fill_inputs,
                    none_as_valid_value=none_as_valid_value,
                    **(input_value_kwargs or {}),
                )

            elif isinstance(form, BaseForm) and not isinstance(form, Form):
                form = Form.from_form(
                    form=form,
                    assignment=assignment or form.assignment,
                    strict=strict,
                    task_description=task_description,
                    fill_inputs=fill_inputs,
                    none_as_valid_value=none_as_valid_value,
                    **(input_value_kwargs or {}),
                )

            if isinstance(form, Form):
                self = cls(
                    guidance=form.guidance,
                    images=images,
                    sender=sender,
                    recipient=recipient,
                    image_detail=image_detail,
                    **form.instruction_dict,
                )
                self.metadata.set(["original_form"], form.ln_id)
                return self
        except Exception as e:
            raise LionTypeError(
                "Invalid form. The form must be a subclass or an instance "
                "of BaseForm."
            ) from e


__all__ = ["Instruction"]

# File: lion_core/communication/instruction.py
