import lionagi.libs.ln_nested as nested
from lionagi.core.messages.base.base_message import BaseMessage


class Instruction(BaseMessage):
    """
    Represents an instruction message, a specialized subclass of Message.

    This class is specifically used for creating messages that are instructions from the user,
    including any associated context. It sets the message role to 'user'.
    """

    def __init__(
        self,
        instruction: dict | list | str,
        context=None,
        sender: str | None = None,
        output_fields=None,
        response_format=None,
    ):
        super().__init__(
            role="user", sender=sender or "user", content={"instruction": instruction}
        )

        self._add_context(context)
        self._add_response_format(output_fields, response_format)

    @property
    def instruct(self):
        """
        Gets the 'instruction' field of the message.

        Returns:
            The 'instruction' part of the message.
        """
        return nested.nget(self.content, ["instruction"], "null")

    @instruct.setter
    def instruct(self, value):
        self.content.update({"instruction": value})


    @property
    def context(self):
        """
        Gets the 'context' field of the message.

        Returns:
            The 'context' part of the message.
        """
        return nested.nget(self.content, ["context"], "null")


    @context.setter
    def context(self, value):
        self.content.update({"context": value})

    @property
    def response_format(self):
        """
        Gets the 'response_format' field of the message.

        Returns:
            The 'response_format' part of the message.
        """
        return nested.nget(self.content, ["response_format"], "null")

    @response_format.setter
    def response_format(self, value):
        self.content.update({"response_format": value})


    def __str__(self):
        return f"Instruction: {self.instruction}"


    def _add_context(self, context=None):
        if context:
            self.content.update({"context": context})

    def _add_response_format(self, output_fields=None, response_format=None):
        if output_fields is not None:
            _format = f"""
            Follow the following response format.
            ```json
            {output_fields}
            ```         
            """
            self.content.update({"response_format": _format})
        elif response_format is not None:
            self.content.update({"response_format": response_format})
