import json
from typing import Dict, Any

import pandas as pd

from lionagi.core.schema import BaseNode
from lionagi.core.session.message.schema import MessageField


class BaseMessage(BaseNode):
    """
    the foundational class for all message types, providing common attributes and
    operations.

    attributes:
        _role (Optional[str]): The role of the message, indicating its purpose or origin.
        _sender (Optional[str]): Identifier for the entity that sent the message.
        recipient (Optional[str]): Identifier for the intended recipient of the message.
        timestamp (Optional[datetime]): The timestamp when the message was sent.

    Properties:
        role (str): Accessor and mutator for the message's role.
        sender (str): Accessor and mutator for the message's sender.
        content_str (str): Serialize the message's content to a string.
        dict (Dict[str, Any]): Convert the message's attributes to a dictionary.
        to_pd_series (pd.Series): Convert the message's attributes to a pandas Series.
    """

    _role: str = None
    _sender: str = None
    recipient: str = None
    timestamp: str = None

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, role):
        self._role = role

    @property
    def content_str(self):
        if isinstance(self.content, Dict):
            return json.dumps(self.content)
        elif isinstance(self.content, str):
            return self.content
        else:
            try:
                return str(self.content)
            except ValueError:
                print(f"Content is not serializable for Node: {self._id}")
                return 'null'

    @property
    def dict(self, **kwargs):
        return {
            'node_id': self.id_,
            'metadata': self.metadata or 'null',
            'timestamp': self.timestamp,
            'labels': self.label or 'null',
            'role': self.role,
            'sender': self._sender,
            'recipient': self.recipient,
            'content': self.content_str,
            'related_nodes': self.related_nodes or 'null'
        }

    @property
    def to_pd_series(self):
        return pd.Series(self.dict)

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, sender):
        self._sender = sender

    @property
    def msg_sender(self) -> str:
        """
        Retrieves the sender identifier of the message.

        Returns:
            The identifier of the message sender.
        """
        return self.roled_msg[MessageField.SENDER.value]

    @property
    def msg_recipient(self) -> str:
        """
        Retrieves the recipient identifier of the message.

        Returns:
            The identifier of the message recipient.
        """
        return self.roled_msg[MessageField.RECIPIENT.value]

    @property
    def msg_timestamp(self) -> Any:
        """
        Retrieves the timestamp of the message.

        Returns:
            The timestamp marking when the message was created or sent.
        """
        return self.roled_msg[MessageField.TIMESTAMP.value]

    @property
    def as_pd_series(self) -> pd.Series:
        """
        Converts the message to a pandas Series object, facilitating data analysis and manipulation.

        Returns:
            A pandas Series object representing the structured message data.
        """
        return pd.Series(self.roled_msg)

    def add_recipient(self, recipient: str) -> None:
        """
        Updates the recipient identifier for the message.

        Args:
            recipient: The new recipient identifier to be assigned to the message.
        """
        self.recipient = recipient

    def _to_roled_message(self):
        """
        Serializes the message attributes into a dictionary, using `MessageField` enum values as keys.

        Returns:
            A dictionary representation of the message, suitable for serialization or further processing.
        """
        return {
            MessageField.ROLE.value: self._role.value,
            MessageField.CONTENT.value: (
                json.dumps(self.content) if isinstance(self.content, dict)
                else self.content
            )
        }

    def __str__(self):
        content_preview = (
            (str(self.content)[:75] + '...') if self.content and len(self.content) > 75
            else str(self.content)
        )
        return (
            f"Message({MessageField.ROLE.value}={self._role.value or 'none'}, \
                {MessageField.SENDER.value}={self._sender or 'none'}, \
                {MessageField.CONTENT.value}='{content_preview or 'none'}, \
                {MessageField.RECIPIENT.value}={self.recipient or 'none'}, \
                {MessageField.TIMESTAMP.value}={self.timestamp or 'none'})"
        )
