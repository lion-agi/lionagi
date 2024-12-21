# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from datetime import UTC, datetime

from pydantic import JsonValue
from typing_extensions import override

from .message import ID, MessageRole, RoledMessage
from .utils import validate_sender_recipient

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


def format_system_content(
    system_datetime: bool | str | None,
    system_message: str,
) -> dict:
    content = {"system": system_message or DEFAULT_SYSTEM}
    if system_datetime:
        if isinstance(system_datetime, str):
            content["system_datetime"] = system_datetime
        else:
            content["system_datetime"] = datetime.now(UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    return content


class System(RoledMessage):

    @classmethod
    def create(
        cls,
        system: JsonValue = None,
        sender: ID.SenderRecipient = None,
        recipient: ID.SenderRecipient = None,
        system_datetime: bool | JsonValue = None,
    ):
        return System(
            role=MessageRole.SYSTEM,
            content=format_system_content(
                system_datetime=system_datetime, system_message=system
            ),
            sender=sender,
            recipient=recipient,
        )

    def update(
        self,
        system: JsonValue = None,
        sender: ID.SenderRecipient = None,
        recipient: ID.Ref = None,
        system_datetime: bool | str = None,
    ) -> None:
        if system:
            self.content = format_system_content(
                system_datetime=system_datetime, system_message=system
            )
        if sender:
            self.sender = validate_sender_recipient(sender)
        if recipient:
            self.recipient = validate_sender_recipient(recipient)

    @property
    def system_info(self) -> str:
        """
        Get the complete system information.

        Returns:
            str: The formatted system information including datetime if present
        """
        if "system_datetime" in self.content:
            msg = f"System datetime: {self.content['system_datetime']}\n\n"
            return msg + f"{self.content['system']}"

        return str(self.content["system"])

    @override
    def _format_content(self) -> dict[str, str]:
        return {"role": self.role.value, "content": self.system_info}
