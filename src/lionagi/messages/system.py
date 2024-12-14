# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import JsonValue
from typing_extensions import override

from lionagi.utils import time

from ..protocols.base import ID, MessageRole, validate_sender_recipient
from .message import MessageFlag, MessageRole, RoledMessage, Template, env


class System(RoledMessage):

    template: Template = env.get_template("system_message.jinja2")

    @override
    def __init__(
        self,
        system: JsonValue = None,
        sender: ID.Ref | MessageRole = None,
        recipient: ID.Ref | MessageRole = None,
        system_datetime: bool | JsonValue = None,
        protected_init_params: dict | None = None,
    ):
        """
        Initialize a System message instance.

        Args:
            system: The content of the system message
            sender: The sender of the system message
            recipient: The recipient of the message
            system_datetime: Flag to include system datetime
            protected_init_params: Protected initialization parameters

        Raises:
            ValueError: If invalid combination of parameters is provided
        """
        if all(
            x == MessageFlag.MESSAGE_LOAD
            for x in [system, sender, recipient, system_datetime]
        ):
            super().__init__(**protected_init_params)
            return

        if all(
            x == MessageFlag.MESSAGE_CLONE
            for x in [system, sender, recipient, system_datetime]
        ):
            super().__init__(role=MessageRole.SYSTEM)
            return

        if system_datetime is True:
            system_datetime = time(type_="iso", timespec="minutes")
        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content={
                "system_datetime": system_datetime,
                "system_message": system,
            },
            recipient=recipient or "N/A",
        )

    def update(
        self,
        system: JsonValue = None,
        sender: ID.Ref | MessageRole = None,
        recipient: ID.Ref | MessageRole = None,
        system_datetime: bool | str = None,
    ) -> None:
        """
        Update the system message components.

        Args:
            system: New system message content
            sender: New sender
            recipient: New recipient
            system_datetime: New datetime flag or string
        """
        if system:
            self.content = {
                "system_datetime": system_datetime,
                "system_message": system,
            }
        if sender:
            self.sender = validate_sender_recipient(sender)
        if recipient:
            self.recipient = validate_sender_recipient(recipient)

    def _format_content(self):
        return {
            "role": self.role.value,
            "content": self.template.render(self.content),
        }
