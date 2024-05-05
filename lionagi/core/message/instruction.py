from ..generic.abc import LionIDable
from .message import RoledMessage, MessageRole, SYSTEM_FIELDS


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

    def _initiate_content(self, context, output_fields, **kwargs):
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

        if output_fields:
            self.content["output_fields"] = self._format_output_field(output_fields)

    @staticmethod
    def _format_output_field(output_fields):
        format_ = f"""
        MUST EXACTLY FOLLOW THE RESPONSE FORMAT NO ADDITIONAL COMMENTS ALLOWED!
        ```json
        {output_fields}
        ```
        """
        return {"response_format": format_.replace("        ", "")}
