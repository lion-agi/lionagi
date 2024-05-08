from pydantic import Field

from lionagi.core.generic.abc import Actionable
from lionagi.core.generic import Node
from .tool import Tool


class ActionSelection(Node, Actionable):
    action_kwargs: dict = Field(
        default_factory=dict,
        description="The arguments for the action",
        alias="action_arguments",
    )
    action: str = Field(
        "chat", description="The action to be performed", alias="action_type"
    )


class ActionNode(Node, Actionable):
    tools: list[Tool] | Tool | None = Field(
        default_factory=list,
        description="The tools to be used in the action",
        alias="tool",
    )
    instruction: Node = Field(
        ..., description="The instruction for the action", alias="instruct"
    )
