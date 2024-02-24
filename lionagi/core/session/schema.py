from enum import Enum


class MessageField(str, Enum):
    NODE_ID = 'node_id'
    TIMESTAMP = 'timestamp'
    ROLE = 'role'
    SENDER = 'sender'
    RECIPIENT = 'recipient'
    CONTENT = 'content'
    METADATA = 'metadata'
    RELATION = 'relation'




