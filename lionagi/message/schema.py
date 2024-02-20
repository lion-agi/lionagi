from enum import Enum


class MessageField(str, Enum):
    NODE_ID = 'node_id'
    TIMESTAMP = 'timestamp'
    ROLE = 'role'
    SENDER = 'sender'
    RECIPIENT = 'recipient'
    CONTENT = 'content'


class MessageRoleType(str, Enum):
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'


class MessageSenderType(str, Enum):
    USER = 'user'
    INSTRUCTION = 'instruction'
    SYSTEM = 'system'
    ACTION_REQUEST = 'action_request'
    ACTION_RESPONSE = 'action_response'
    RESPONSE = 'response'


class MessageContentKey(str, Enum):
    INSTRUCTION = 'instruction'
    SYSTEM = 'system_info'
    ACTION_REQUEST = 'action_list'
    ACTION_RESPONSE = 'action_response'
    RESPONSE = 'response'
