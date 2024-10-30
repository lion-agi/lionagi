from lionagi.core.collections.abc import SYSTEM_FIELDS, LionIDable
from lionagi.core.message.message import MessageRole, RoledMessage
from lionagi.core.report.form import Form


class Instruction(RoledMessage):
    """
    Represents an instruction message with additional context and requested fields.

    Inherits from `RoledMessage` and provides methods to manage context and
    requested fields specific to instructions.

    Attributes:
        instruction (str): The instruction content.
        context (dict or str): Additional context for the instruction.
        sender (LionIDable): The sender of the instruction.
        recipient (LionIDable): The recipient of the instruction.
        requested_fields (dict): Fields requested in the instruction.
    """

    def __init__(
        self,
        instruction: str | None = None,
        context: dict | str | None = None,
        images: list | None = None,
        sender: LionIDable | None = None,
        recipient: LionIDable | None = None,
        requested_fields: dict | None = None,  # {"field": "description"}
        additional_context: dict | None = None,
        image_detail: str | None = None,
        **kwargs,
    ):
        """
        Initializes the Instruction message.

        Args:
            instruction (str, optional): The instruction content.
            context (dict or str, optional): Additional context for the instruction.
            image (str, optional): The image content in base64 encoding.
            sender (LionIDable, optional): The sender of the instruction.
            recipient (LionIDable, optional): The recipient of the instruction.
            requested_fields (dict, optional): Fields requested in the instruction.
            **kwargs: Additional context fields to be added to the message content, must be JSON serializable.
        """
        if not instruction:
            if "metadata" in kwargs and "instruction" in kwargs["metadata"]:
                instruction = kwargs["metadata"].pop("instruction")

        super().__init__(
            role=MessageRole.USER,
            sender=sender or "user",
            content={"instruction": instruction or "N/A"},
            recipient=recipient or "N/A",
            **kwargs,
        )

        additional_context = additional_context or {}
        self._initiate_content(
            context=context,
            requested_fields=requested_fields,
            images=images,
            image_detail=image_detail or "low",
            **additional_context,
        )

    @property
    def instruct(self):
        """Returns the instruction content."""
        return self.content["instruction"]

    def _check_chat_msg(self):
        text_msg = super()._check_chat_msg()
        if "images" not in self.content:
            return text_msg

        text_msg["content"].pop("images", None)
        text_msg["content"].pop("image_detail", None)
        text_msg["content"] = [
            {"type": "text", "text": text_msg["content"]},
        ]

        for i in self.content["images"]:
            text_msg["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{i}",
                        "detail": self.content["image_detail"],
                    },
                }
            )
        return text_msg

    def _add_context(self, context: dict | str | None = None, **kwargs):
        if "context" not in self.content:
            self.content["context"] = {}
        if isinstance(context, dict):
            self.content["context"].update({**context, **kwargs})
        elif isinstance(context, str):
            self.content["context"]["additional_context"] = context

    def _update_requested_fields(self, requested_fields: dict):
        if "context" not in self.content:
            self.content["context"] = {}
            self.content["context"]["requested_fields"] = {}
        self.content["context"]["requested_fields"].update(requested_fields)

    def _initiate_content(
        self, context, requested_fields, images, image_detail, **kwargs
    ):
        if context:
            context = (
                {"context": context}
                if not isinstance(context, dict)
                else context
            )
            if (
                additional_context := {
                    k: v for k, v in kwargs.items() if k not in SYSTEM_FIELDS
                }
            ) != {}:
                context["additional_context"] = additional_context
            self.content.update(context)

        if not requested_fields in [None, {}]:
            self.content["requested_fields"] = self._format_requested_fields(
                requested_fields
            )

        if images:
            self.content["images"] = (
                images if isinstance(images, list) else [images]
            )
            self.content["image_detail"] = image_detail

    def clone(self, **kwargs):
        """
        Creates a copy of the current Instruction object with optional additional arguments.

        This method clones the current object, preserving its content.
        It also retains the original metadata, while allowing
        for the addition of new attributes through keyword arguments.

        Args:
            **kwargs: Optional keyword arguments to be included in the cloned object.

        Returns:
            Instruction: A new instance of the object with the same content and additional keyword arguments.
        """
        import json

        content = json.dumps(self.content)
        instruction_copy = Instruction(**kwargs)
        instruction_copy.content = json.loads(content)
        instruction_copy.metadata["origin_ln_id"] = self.ln_id
        return instruction_copy

    @staticmethod
    def _format_requested_fields(requested_fields):
        format_ = f"""
        MUST RETURN JSON-PARSEABLE RESPONSE ENCLOSED BY JSON CODE BLOCKS. ----
        ```json
        {requested_fields}
        ```---
        """
        return {"response_format": format_.strip()}

    @classmethod
    def from_form(
        cls,
        form: Form,
        sender: str | None = None,
        recipient=None,
        image=None,
    ):
        """
        Creates an Instruction instance from a form.

        Args:
            form (Form): The form containing instruction details.
            sender (str, optional): The sender of the instruction.
            recipient (LionIDable, optional): The recipient of the instruction.

        Returns:
            Instruction: The created Instruction instance.
        """
        return cls(
            instruction=form._instruction_prompt,
            context=form._instruction_context,
            requested_fields=form._instruction_requested_fields,
            image=image,
            sender=sender,
            recipient=recipient,
        )
