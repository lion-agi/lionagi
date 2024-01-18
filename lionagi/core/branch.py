from copy import deepcopy
from typing import Any, Dict, Union
from datetime import datetime
from pandas import DataFrame

from ..tools.tool_manager import ToolManager
from .messages import Message
from .conversation import Conversation


class Branch(Conversation):
    """
    Branch of a conversation with message tracking and tool management.

    This class extends the Conversation class, managing a branch of conversation
    with the ability to track messages, maintain instruction sets, and manage tools
    using a ToolManager.

    Args:
        init_message: The initial message or messages of the conversation branch.
        instruction_sets: A set of instructions to be used in the conversation.
            Defaults to None, which creates an empty dict.
        tool_manager: A ToolManager instance to manage tools. Defaults to None,
            which creates a new ToolManager instance.

    Raises:
        ValueError: If the input `init_message` is not a DataFrame or Message instance.

    Attributes:
        instruction_sets: Instruction sets associated with the conversation branch.
        tool_manager: Tool manager for the branch.
        messages: DataFrame containing the conversation messages.
        system_message: The system message of the conversation branch.

    Examples:
        # Creating a Branch with an initial message
        initial_message = Message(role="user", content="Hi there!")
        branch = Branch(init_message=initial_message)

        # Creating a Branch with initial messages as DataFrame
        messages_df = DataFrame({
            "role": ["user", "system"],
            "content": ["Hi there!", "Hello!"]
        })
        branch = Branch(init_message=messages_df)
    """

    def __init__(self, init_message: Union[Message, DataFrame],
                 instruction_sets: dict = None,
                 tool_manager: ToolManager = None) -> None:
        super().__init__()
        self.instruction_sets = instruction_sets if instruction_sets else {}
        self.tool_manager = tool_manager if tool_manager else ToolManager()

        if isinstance(init_message, DataFrame):
            self.messages = init_message
        elif isinstance(init_message, Message):
            self.add_message(init_message)
        else:
            raise ValueError('Please input a valid init_message: DataFrame or Message')
        self.system_message = self.messages.loc[0, 'content']

    def change_system_message(self, system: Message):
        """
        Change the system message to the provided message.

        Args:
            system: A Message object representing the new system message.
        """
        message_dict = system.to_dict()
        message_dict['timestamp'] = datetime.now()
        self.messages.loc[0] = message_dict
        self.system_message = self.messages.loc[0, 'content']

    def add_instruction_set(self, name, instruction_set):
        """
        Add an instruction set to the conversation branch.

        Args:
            name: The name of the instruction set.
            instruction_set: The instruction set to be added.
        """
        self.instruction_sets[name] = instruction_set

    def remove_instruction_set(self, name):
        """
        Remove an instruction set from the conversation branch by name.

        Args:
            name: The name of the instruction set to be removed.

        Returns:
            The removed instruction set if it exists, else None.
        """
        return self.instruction_sets.pop(name)

    def register_tools(self, tools):
        """
        Register a list of tools to the ToolManager.

        Args:
            tools: A single tool or a list of tools to be registered.
        """
        if not isinstance(tools, list):
            tools = [tools]
        self.tool_manager.register_tools(tools=tools)

    def delete_tool(self, name):
        """
        Delete a tool from the ToolManager by name.

        Args:
            name: The name of the tool to be deleted.

        Returns:
            True if the tool was successfully deleted, False otherwise.
        """
        if name in self.tool_manager.registry:
            self.tool_manager.registry.pop(name)
            return True
        return False

    def clone(self):
        """
        Create a deep copy of the current branch.

        Returns:
            A new Branch instance that is a deep copy of the current branch.
        """
        cloned = Branch(self.messages.copy())
        cloned.instruction_sets = deepcopy(self.instruction_sets)
        cloned.tool_manager = ToolManager()
        cloned.tool_manager.registry = deepcopy(self.tool_manager.registry)
        return cloned

    def merge(self, branch, update=True):
        """
        Merge another Branch into the current one.

        Args:
            branch: The Branch to merge into the current one.
            update: Whether to update the current Branch. If False, only adds
                non-existing items from the other Branch.
        """
        message_copy = branch.messages.copy()
        branch_system = message_copy.loc[0]
        message_copy.drop(0, inplace=True)
        self.messages = self.messages.merge(message_copy, how='outer')
        if update:
            self.instruction_sets.update(branch.instruction_sets)
            self.tool_manager.registry.update(branch.tool_manager.registry)
            self.messages.loc[0] = branch_system
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.tool_manager.registry.items():
                if key not in self.tool_manager.registry:
                    self.tool_manager.registry[key] = value

    def report(self) -> Dict[str, Any]:
        """
        Generate a report about the conversation branch.

        Returns:
            A dictionary containing information about total messages, a summary by role,
            instruction sets, registered tools, and the messages themselves.
        """

        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.message_counts(),
            "instruction_sets": self.instruction_sets,
            "registered_tools": self.tool_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    def to_chatcompletion_message(self):
        """
        Convert the conversation branch to a list of messages for chat completion.

        Returns:
            A list of dictionaries with 'name' or 'role' and 'content' from the conversation messages.
        """
        message = []
        for _, row in self.messages.iterrows():
            out = {"role": row['role'], "content": row['content']}
            message.append(out)
        return message
    