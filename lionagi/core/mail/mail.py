from typing import Any
from enum import Enum

from pydantic import Field, field_validator

from lionagi.core.generic.abc import Component


class MailPackageCategory(str, Enum):
    MESSAGES = "messages"
    TOOL = "tool"
    SERVICE = "service"
    MODEL = "model"
    NODE = "node"
    NODE_LIST = "node_list"
    NODE_ID = "node_id"
    START = "start"
    END = "end"
    CONDITION = "condition"


class MailPackage(Component):
    category: MailPackageCategory = Field(
        ..., title="Category", description="The category of the mail package."
    )

    package: Any = Field(
        ..., title="Package", description="The package to send in the mail."
    )


class Mail(Component):
    sender: str = Field(
        "N/A",
        title="Sender",
        description="The id of the sender node.",
    )

    recipient: str = Field(
        "N/A",
        title="Recipient",
        description="The id of the recipient node.",
    )

    package: MailPackage = Field(
        title="Packages",
        default_factory=dict,
        description="The packages to send in the mail.",
    )

    @field_validator("sender", "recipient", mode="before")
    def _validate_sender_recipient(cls, value):
        if isinstance(value, Component):
            return value.id_
        return value
