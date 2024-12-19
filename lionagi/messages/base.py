# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


from enum import Enum


class MessageRole(str, Enum):
    """Message participant roles in conversations."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    UNSPECIFIED = "unspecified"


class MessageFlag(str, Enum):
    """Internal flags for message construction control."""

    MESSAGE_CLONE = "MESSAGE_CLONE"
    MESSAGE_LOAD = "MESSAGE_LOAD"


class MessageField(str, Enum):
    """Standard message field identifiers."""

    TIMESTAMP = "timestamp"
    LION_CLASS = "lion_class"
    ROLE = "role"
    CONTENT = "content"
    id = "id"
    SENDER = "sender"
    RECIPIENT = "recipient"
    METADATA = "metadata"
