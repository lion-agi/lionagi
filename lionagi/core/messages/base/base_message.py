from lionagi.core.schema import DataNode
from lionagi.libs import ln_convert as convert


class BaseMessage(DataNode):
    """
    Represents a message in a chatbot-like system, inheriting from BaseNode.

    Attributes:
        role (str | None): The role of the entity sending the message, e.g., 'user', 'system'.
        sender (str | None): The identifier of the sender of the message.
        content (Any): The actual content of the message.
    """

    role: str | None = None
    sender: str | None = None

    @property
    def msg(self) -> dict:
        """
        Constructs and returns a dictionary representation of the message.

        Returns:
            A dictionary representation of the message with 'role' and 'content' keys.
        """
        return self._to_message()

    @property
    def msg_content(self) -> str | dict:
        """
        Gets the 'content' field of the message.

        Returns:
            The 'content' part of the message.
        """
        return self.msg["content"]

    def _to_message(self):
        """
        Constructs and returns a dictionary representation of the message.

        Returns:
            dict: A dictionary representation of the message with 'role' and 'content' keys.
        """
        out = {"role": self.role, "content": convert.to_str(self.content)}
        return out

    def __str__(self):
        content_preview = (
            (str(self.content)[:75] + "...")
            if self.content and len(self.content) > 75
            else str(self.content)
        )
        return f"Message(role={self.role}, sender={self.sender}, content='{content_preview}')"
