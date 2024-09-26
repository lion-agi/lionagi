from pydantic import Field

from lionagi.core.collections.abc import Actionable
from lionagi.core.generic.node import Node

from .tool import Tool


class DirectiveSelection(Node, Actionable):
    """
    Represents a directive selection node which can be invoked to perform an action.

    Attributes:
        directive (str): The action to be performed, with a default value of "chat".
        directive_kwargs (dict): The arguments for the action.

    Methods:
        invoke(): An asynchronous method to perform the action defined by the directive.
    """

    directive: str = Field(
        "chat", description="The action to be performed", alias="action_type"
    )
    directive_kwargs: dict = Field(
        default_factory=dict,
        description="The arguments for the action",
        alias="action_arguments",
    )

    async def invoke(self):
        """
        Perform the action defined by the directive.

        This method is intended to be overridden by subclasses to provide specific
        implementation details for the action.
        """
        pass


class ActionNode(DirectiveSelection):
    """
    Represents an action node that can invoke actions within a branch using tools and instructions.

    Attributes:
        tools (list[Tool] | Tool | None): The tools to be used in the action.
        instruction (Node): The instruction for the action.

    Methods:
        invoke(branch, context=None): An asynchronous method to invoke the action
                                      within the given branch.
    """

    tools: list[Tool] | Tool | None = Field(
        default_factory=list,
        description="The tools to be used in the action",
        alias="tool",
    )
    instruction: Node = Field(
        ..., description="The instruction for the action", alias="instruct"
    )

    async def invoke(self, branch, context=None):
        """
        Invoke the action within the given branch.

        Args:
            branch: The branch in which to perform the action.
            context: Optional; Additional context for the action.

        Returns:
            The result of the action, depending on the directive.

        Raises:
            ValueError: If the directive is not "chat" or "direct".
        """
        if self.directive == "chat":
            return await branch.chat(
                instruction=self.instruction.instruct,
                tools=self.tools,
                **self.directive_kwargs,
            )
        elif self.directive == "direct":
            if self.tools:
                self.directive_kwargs["allow_action"] = True
            return await branch.direct(
                instruction=self.instruction.instruct,
                context=context,
                tools=self.tools,
                **self.directive_kwargs,
            )
        else:
            raise ValueError(
                'Invalid directive, valid directives are: "chat", "direct"'
            )
