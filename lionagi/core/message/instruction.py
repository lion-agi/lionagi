from ..generic.abc import LionIDable, SYSTEM_FIELDS
from .message import RoledMessage, MessageRole


class Instruction(RoledMessage):

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
        kwargs are additional context fields to be added to the
        message content have to be JSON serializable
        """
        super().__init__(
            role=MessageRole.USER,
            sender=sender or "N/A",
            content={"instruction": instruction or "N/A"},
            recipient=recipient or "N/A",
        )

        self._initiate_content(context, requested_fields, **kwargs)

    def _add_context(self, context: dict | str | None = None, **kwargs):
        if "context" not in self.content:
            self.content["context"] = {}
        if isinstance(context, dict):
            self.content["context"].update(context)
        elif isinstance(context, str):
            self.content["context"]["additional_context"] = context

    def _update_requested_fields(self, requested_fields: dict):
        if "context" not in self.content:
            self.content["context"] = {}
            self.content["context"]["requested_fields"] = {}
        self.content["context"]["requested_fields"].update(requested_fields)

    def _initiate_content(self, context, requested_fields, **kwargs):
        """
        Processes context and output fields to update message content.
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
        format_ = f"""
        MUST EXACTLY FOLLOW THE RESPONSE FORMAT NO ADDITIONAL COMMENTS ALLOWED!
        ```json
        {requested_fields}
        ```
        """
        return {"response_format": format_.replace("        ", "")}

    # TODO: add from_form method
    def from_form(self, form):
        pass
