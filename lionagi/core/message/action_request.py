import inspect
from pydantic import Field
from lionagi.libs import convert, ParseUtil
from .message import RoledMessage, MessageRole


class ActionRequest(RoledMessage):
    """
    Represents a request for an action with function and arguments.

    Inherits from `RoledMessage` and provides attributes specific to action requests.

    Attributes:
        function (str): The name of the function to be called.
        arguments (dict): The keyword arguments to be passed to the function.
        action_response (str): The ID of the action response that this request corresponds to.
    """

    function: str | None = Field(
        None, description="The name of the function to be called"
    )

    arguments: dict | None = Field(
        None, description="The keyword arguments to be passed to the function"
    )

    action_response: str | None = Field(
        None,
        description="The id of the action response that this request corresponds to",
    )

    def __init__(
        self,
        function=None,
        arguments=None,
        sender=None,  # sender is the assistant who made the request
        recipient=None,  # recipient is the actionable component
    ):
        """
        Initializes the ActionRequest.

        Args:
            function (str or function, optional): The function to be called.
            arguments (dict, optional): The keyword arguments for the function.
            sender (str, optional): The sender of the request.
            recipient (str, optional): The recipient of the request.
        """
        function = function.__name__ if inspect.isfunction(function) else function
        arguments = _prepare_arguments(arguments)

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender,
            recipient=recipient,
            content={"action_request": {"function": function, "arguments": arguments}},
        )
        self.function = function
        self.arguments = arguments

    def is_responded(self):
        """
        Checks if the action request has been responded to.

        Returns:
            bool: True if the action request has a response, otherwise False.
        """
        return self.action_response is not None


def _prepare_arguments(arguments):
    """
    Prepares the arguments for the action request.

    Args:
        arguments (Any): The arguments to be prepared.

    Returns:
        dict: The prepared arguments.

    Raises:
        ValueError: If the arguments are invalid.
    """
    if not isinstance(arguments, dict):
        try:
            arguments = ParseUtil.fuzzy_parse_json(convert.to_str(arguments))
        except Exception as e:
            raise ValueError(f"Invalid arguments: {e}") from e
    if isinstance(arguments, dict):
        return arguments
    raise ValueError(f"Invalid arguments: {arguments}")
