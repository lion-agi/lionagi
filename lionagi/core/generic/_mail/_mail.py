from pydantic import Field, field_validator

from ..abc import Component, get_lion_id, LionTypeError


class Mail(Component):

    sender: str = Field(
        "N/A",
        title="Sender",
        description="The id of the sender node, or 'system', 'user', or 'assistant'.",
    )

    recipient: str = Field(
        "N/A",
        title="Recipient",
        description="The id of the recipient node, or 'system', 'user', or 'assistant'.",
    )

    @field_validator("sender", "recipient", mode="before")
    def _validate_sender_recipient(cls, value):
        if value in ["system", "user", "assistant", "N/A"]:
            return value

        a = get_lion_id(value)
        if not isinstance(a, str) and len(a) == 32:
            raise LionTypeError
        return a
