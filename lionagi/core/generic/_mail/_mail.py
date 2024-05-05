from pydantic import Field, field_validator

from ..abc import Component, get_lion_id, LionTypeError


class Mail(Component):
    """Represents a mail component with sender and recipient information."""

    sender: str = Field(
        "N/A",
        title="Sender",
        description=("The id of the sender node, or 'system', 'user', or 'assistant'."),
    )

    recipient: str = Field(
        "N/A",
        title="Recipient",
        description=(
            "The id of the recipient node, or 'system', 'user', or 'assistant'."
        ),
    )

    @field_validator("sender", "recipient", mode="before")
    def _validate_sender_recipient(cls, value):
        """Validate the sender and recipient fields."""
        if value in ["system", "user", "assistant", "N/A"]:
            return value

        a = get_lion_id(value)
        if not isinstance(a, str) or len(a) != 32:
            raise LionTypeError(
                "Invalid sender or recipient value. "
                "Expected a valid node id or one of "
                "'system', 'user', or 'assistant'."
            )
        return a
