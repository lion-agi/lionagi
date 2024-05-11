import inspect
from pydantic import Field
from lionagi.libs import convert, ParseUtil
from .message import RoledMessage, MessageRole


class ActionRequest(RoledMessage):

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
        return self.action_response is not None


def _prepare_arguments(arguments):
    if not isinstance(arguments, dict):
        try:
            arguments = ParseUtil.fuzzy_parse_json(convert.to_str(arguments))
        except Exception as e:
            raise ValueError(f"Invalid arguments: {e}") from e
    if isinstance(arguments, dict):
        return arguments
    raise ValueError(f"Invalid arguments: {arguments}")
