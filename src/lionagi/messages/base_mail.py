# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from pydantic import Field, field_validator

from lionagi.protocols.types import ID, Communicatable, Element

from .utils import validate_sender_recipient


class BaseMail(Element, Communicatable):

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
