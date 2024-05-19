from typing import Any
from pydantic import Field
from .message import RoledMessage, MessageRole
from .action_request import ActionRequest


# action response must correlates to a specific action request
class ActionResponse(RoledMessage):
    """
    Represents a response to a specific action request.

    Inherits from `RoledMessage` and provides attributes specific to action responses.

    Attributes:
        action_request (str): The ID of the action request that this response corresponds to.
        function (str): The name of the function called.
        arguments (dict): The keyword arguments provided.
        func_outputs (Any): The output of the function call.
    """

    action_request: str | None = Field(
        None,
        description="The id of the action request that this response corresponds to",
    )

    function: str | None = Field(None, description="The name of the function called")
    arguments: dict | None = Field(None, description="The keyword arguments provided")
    func_outputs: Any | None = Field(
        None, description="The output of the function call"
    )

    def __init__(
        self,
        action_request: ActionRequest,
        sender: str | None = None,  # the sender of action request
        func_outputs=None,
        **kwargs,
    ):
        """
        Initializes the ActionResponse.

        Args:
            action_request (ActionRequest): The action request that this response corresponds to.
            sender (str, optional): The sender of the action request.
            func_outputs (Any, optional): The output of the function call.

        Raises:
            ValueError: If the action request has already been responded to.
        """
        if action_request.is_responded():
            raise ValueError("Action request has already been responded to")

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",  # sender is the actionable component
            recipient=action_request.sender,  # recipient is the assistant who made the request
            content={
                "action_response": {
                    "function": action_request.function,
                    "arguments": action_request.arguments,
                    "func_outputs": func_outputs,
                }
            },
            **kwargs,
        )
        self.update_request(action_request)
        self.func_outputs = func_outputs

    def update_request(self, action_request: ActionRequest):
        """
        Updates the action request details in the action response.

        Args:
            action_request (ActionRequest): The action request to update from.
        """
        self.function = action_request.function
        self.arguments = action_request.arguments
        self.action_request = action_request.ln_id
        action_request.action_response = self.ln_id

    def _to_dict(self):
        """
        Converts the action response to a dictionary.

        Returns:
            dict: A dictionary representation of the action response.
        """
        return {
            "action_request": self.action_request,
            "function": self.function,
            "arguments": self.arguments,
            "func_outputs": self.func_outputs,
        }
