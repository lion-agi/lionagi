from enum import Enum

from lionagi.core.schema import BaseNode


class MessageField(str, Enum):
    NODE_ID = "node_id"
    TIMESTAMP = "timestamp"
    ROLE = "role"
    SENDER = "sender"
    RECIPIENT = "recipient"
    CONTENT = "content"
    METADATA = "metadata"
    RELATIONSHIP = "relationship"


class MessageRoleType(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageContentKey(str, Enum):
    INSTRUCTION = "instruction"
    CONTEXT = "context"
    SYSTEM = "system_info"
    ACTION_REQUEST = "action_request"
    ACTION_RESPONSE = "action_response"
    RESPONSE = "response"


class MessageType(dict, Enum):
    SYSTEM = (
        {
            MessageField.ROLE.value: MessageRoleType.SYSTEM.value,
            MessageField.SENDER.value: MessageRoleType.SYSTEM.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.SYSTEM.value,
        },
    )

    INSTRUCTION = (
        {
            MessageField.ROLE.value: MessageRoleType.USER.value,
            MessageField.SENDER.value: MessageRoleType.USER.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.INSTRUCTION.value,
        },
    )

    CONTEXT = (
        {
            MessageField.ROLE.value: MessageRoleType.USER.value,
            MessageField.SENDER.value: MessageRoleType.USER.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.CONTEXT.value,
        },
    )

    ACTION_REQUEST = (
        {
            MessageField.ROLE.value: MessageRoleType.ASSISTANT.value,
            MessageField.SENDER.value: MessageRoleType.ASSISTANT.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.ACTION_REQUEST.value,
        },
    )

    ACTION_RESPONSE = (
        {
            MessageField.ROLE.value: MessageRoleType.ASSISTANT.value,
            MessageField.SENDER.value: MessageRoleType.ASSISTANT.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.ACTION_RESPONSE.value,
        },
    )

    RESPONSE = {
        MessageField.ROLE.value: MessageRoleType.ASSISTANT.value,
        MessageField.SENDER.value: MessageRoleType.ASSISTANT.value,
        MessageField.RECIPIENT.value: "null",
        "content_key": MessageContentKey.RESPONSE.value,
    }


class MessageTemplate(BaseNode): ...
