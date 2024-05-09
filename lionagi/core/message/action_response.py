from typing import Any
from pydantic import Field
from .message import RoledMessage, MessageRole
from .action_request import ActionRequest


# action response must correlates to a specific action request
class ActionResponse(RoledMessage):

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
    ):
        if action_request.is_responded():
            raise ValueError("Action request has already been responded to")

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",  # sender is the actionable component
            recipient=action_request.sender,  # recipient is the assistant who made the request
        )
        self.function = action_request.function
        self.arguments = action_request.arguments
        self.func_outputs = func_outputs
        self.action_request = action_request.ln_id
        action_request.action_response = self.ln_id

    def update_request(self, action_request: ActionRequest):
        self.function = action_request.function
        self.arguments = action_request.arguments
        self.action_request = action_request.ln_id
        action_request.action_response = self.ln_id
