from pydantic import Field

from lionagi.core.collections.abc import Actionable
from lionagi.core.generic.node import Node
from .tool import Tool


class DirectiveSelection(Node, Actionable):
    directive: str = Field(
        "chat", description="The action to be performed", alias="action_type"
    )
    directive_kwargs: dict = Field(
        default_factory=dict,
        description="The arguments for the action",
        alias="action_arguments",
    )

    async def invoke(self):
        pass


class ActionNode(DirectiveSelection):
    tools: list[Tool] | Tool | None = Field(
        default_factory=list,
        description="The tools to be used in the action",
        alias="tool",
    )
    instruction: Node = Field(
        ..., description="The instruction for the action", alias="instruct"
    )

    async def invoke(self, branch, context=None):
        if self.directive == "chat":
            return await branch.chat(
                instruction=self.instruction.instruct,
                tools=self.tools,
                **self.directive_kwargs
            )
        elif self.directive == "direct":
            if self.tools:
                self.directive_kwargs["allow_action"] = True
            return await branch.direct(
                instruction=self.instruction.instruct,
                context=context,
                tools=self.tools,
                **self.directive_kwargs
            )
        else:
            raise ValueError("Invalid directive, valid directives are: \"chat\", \"direct\"")
