from typing import Any

from lionabc import Communicatable
from lionabc.exceptions import LionIDError, LionValueError
from pydantic import Field, field_validator

from lion_core.generic.element import Element
from lion_core.sys_utils import SysUtil


def validate_sender_recipient(value: Any, /) -> str:
    """Validate the sender and recipient fields for mail-like communication."""
    if value in ["system", "user", "N/A", "assistant"]:
        return value

    if value is None:
        return "N/A"

    try:
        return SysUtil.get_id(value)
    except LionIDError as e:
        raise LionValueError("Invalid sender or recipient") from e


class BaseMail(Element, Communicatable):
    """Base class for mail-like communication in the LION system.

    Attributes:
        sender: The ID of the sender node.
        recipient: The ID of the recipient node.
    """

    sender: str = Field(
        default="N/A",
        title="Sender",
        description="The ID of the sender node, or 'system', 'user', "
        "or 'assistant'.",
    )

    recipient: str = Field(
        default="N/A",
        title="Recipient",
        description="The ID of the recipient node, or 'system', 'user', "
        "or 'assistant'.",
    )

    @field_validator("sender", "recipient", mode="before")
    @classmethod
    def _validate_sender_recipient(cls, value: Any) -> str:
        """Validate the sender and recipient fields.

        Args:
            value: The value to validate for the sender or recipient.

        Returns:
            The validated sender or recipient ID.

        Raises:
            LionValueError: If the value is not a valid sender or recipient.
        """
        return validate_sender_recipient(value)


# File: lion_core/communication/base.py
