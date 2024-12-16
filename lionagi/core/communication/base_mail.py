# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.core.generic.types import Element
from lionagi.core.typing import ID, Any, Communicatable, Field, field_validator

from .utils import validate_sender_recipient


class BaseMail(Element, Communicatable):
    """
    Base class for mail-like communication in the LION system.

    This class provides the foundation for all message-based communication,
    implementing sender and recipient functionality with proper validation.
    It inherits from Element for core functionality and Communicatable for
    communication capabilities.

    Attributes:
        sender (ID.SenderRecipient): The ID of the sender node or role.
            Can be a specific node ID or one of: "system", "user", "assistant", "N/A"
        recipient (ID.SenderRecipient): The ID of the recipient node or role.
            Can be a specific node ID or one of: "system", "user", "assistant", "N/A"

    Example:
        >>> mail = BaseMail(sender="user", recipient="assistant")
        >>> print(mail.sender)
        'user'
        >>> print(mail.recipient)
        'assistant'
    """

    sender: ID.SenderRecipient = Field(
        default="N/A",
        title="Sender",
        description="The ID of the sender node or a role.",
    )

    recipient: ID.SenderRecipient = Field(
        default="N/A",
        title="Recipient",
        description="The ID of the recipient node or a role.",
    )

    @field_validator("sender", "recipient", mode="before")
    @classmethod
    def _validate_sender_recipient(cls, value: Any) -> ID.SenderRecipient:
        return validate_sender_recipient(value)
