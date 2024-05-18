from lionagi.core.collections.abc import LionIDable, SYSTEM_FIELDS
from lionagi.core.report.form import Form
from lionagi.core.message.message import RoledMessage, MessageRole


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
        sender: LionIDable | None = None,
        recipient: LionIDable | None = None,
        requested_fields: dict | None = None,  # {"field": "description"}
        **kwargs,
    ):
        """
        Initializes the Instruction message.

        Args:
            instruction (str, optional): The instruction content.
            context (dict or str, optional): Additional context for the instruction.
            sender (LionIDable, optional): The sender of the instruction.
            recipient (LionIDable, optional): The recipient of the instruction.
            requested_fields (dict, optional): Fields requested in the instruction.
            **kwargs: Additional context fields to be added to the message content, must be JSON serializable.
        """
        super().__init__(
            role=MessageRole.USER,
            sender=sender or "user",
            content={"instruction": instruction or "N/A"},
            recipient=recipient or "N/A",
        )

        self._initiate_content(context, requested_fields, **kwargs)

    @property
    def instruct(self):
        return self.content["instruction"]

    def _add_context(self, context: dict | str | None = None, **kwargs):
        """
        Adds context to the instruction message.

        Args:
            context (dict or str, optional): Additional context to be added.
            **kwargs: Additional context fields to be added.
        """
        if "context" not in self.content:
            self.content["context"] = {}
        if isinstance(context, dict):
            self.content["context"].update({**context, **kwargs})
        elif isinstance(context, str):
            self.content["context"]["additional_context"] = context

    def _update_requested_fields(self, requested_fields: dict):
        """
        Updates the requested fields in the instruction message.

        Args:
            requested_fields (dict): The fields requested in the instruction.
        """
        if "context" not in self.content:
            self.content["context"] = {}
            self.content["context"]["requested_fields"] = {}
        self.content["context"]["requested_fields"].update(requested_fields)

    def _initiate_content(self, context, requested_fields, **kwargs):
        """
        Processes context and requested fields to update the message content.

        Args:
            context (dict or str, optional): Additional context for the instruction.
            requested_fields (dict, optional): Fields requested in the instruction.
            **kwargs: Additional context fields to be added.
        """
        if context:
            context = {"context": context} if not isinstance(context, dict) else context
            if (
                additional_context := {
                    k: v for k, v in kwargs.items() if k not in SYSTEM_FIELDS
                }
            ) != {}:
                context["additional_context"] = additional_context
            self.content.update(context)

        if requested_fields:
            self.content["requested_fields"] = self._format_requested_fields(
                requested_fields
            )

    @staticmethod
    def _format_requested_fields(requested_fields):
        """
        Formats the requested fields into a JSON-parseable response format.

        Args:
            requested_fields (dict): The fields requested in the instruction.

        Returns:
            dict: The formatted requested fields.
        """
        format_ = f"""
        MUST EXACTLY FOLLOW THE RESPONSE GUIDE BELOW RETURN IN JSON PARSEABLED FORMAT:
        ```json
        {requested_fields}
        ```
        """
        return {"response_format": format_.replace("        ", "")}

    @classmethod
    def from_form(
        cls,
        form: Form,
        sender: str | None = None,
        recipient=None,
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
            sender=sender,
            recipient=recipient,
        )
