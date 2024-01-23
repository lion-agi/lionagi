import json
from datetime import datetime
import pandas as pd
from typing import Any, Dict
from lionagi.utils import as_dict
from lionagi.tools.tool_manager import ToolManager
from ..messages.messages import System
from .conversation import Conversation


class Branch(Conversation):
    """
    Represents a conversation branch with messages, instruction sets, and tool management.

    A `Branch` is a type of conversation that can have messages, system instructions, and registered tools
    for interacting with external services or tools.

    Attributes:
        dir (str): The directory path for storing logs.
        messages (pd.DataFrame): A DataFrame containing conversation messages.
        instruction_sets (dict): A dictionary of instruction sets.
        tool_manager (ToolManager): An instance of ToolManager for managing tools.

    """

    def __init__(self, dir = None, messages: pd.DataFrame=None, instruction_sets: Dict =None, tool_manager=None):
        """
        Initialize a Branch object.

        Args:
            dir (str): The directory path for storing logs.
            messages (pd.DataFrame, optional): A DataFrame containing conversation messages.
            instruction_sets (dict, optional): A dictionary of instruction sets.
            tool_manager: An instance of ToolManager for managing tools.

        Returns:
            Branch: A new Branch object.

        """
        super().__init__(dir)
        self.messages = messages if messages is not None else pd.DataFrame(columns=["node_id", "role", "sender", "timestamp" ,"content"])
        self.instruction_sets = instruction_sets if instruction_sets else {}
        self.tool_manager = tool_manager if tool_manager else ToolManager()
    
    @property
    def system_message(self):
        """
        Get the system message of the conversation.

        Returns:
            str: The content of the system message.

        """
        return self.messages.loc[0, 'content']
    
    def change_system_message(self, system: Any, sender: str=None):
        """
        Change the system message of the conversation.

        Args:
            system (str, dict, System): The new system message.
            sender (str, optional): The sender of the system message.

        Raises:
            ValueError: If the input cannot be converted into a system message.

        """
        if isinstance(system, (str, Dict)):
            system = System(system, sender=sender)
        if isinstance(system, System):
            message_dict = system.to_dict()
            if sender:
                message_dict['sender'] = sender
            message_dict['timestamp'] = datetime.now()
            self.messages.loc[0] = message_dict
        else:
            raise ValueError("Input cannot be converted into a system message.")

    def add_instruction_set(self, name, instruction_set):
        """
        Add an instruction set to the conversation.

        Args:
            name (str): The name of the instruction set.
            instruction_set: The instruction set to add.

        """
        self.instruction_sets[name] = instruction_set

    def remove_instruction_set(self, name):
        """
        Remove an instruction set from the conversation.

        Args:
            name (str): The name of the instruction set to remove.

        Returns:
            bool: True if the instruction set was removed, False otherwise.

        """
        return self.instruction_sets.pop(name)

    def register_tools(self, tools):
        """
        Register one or more tools with the conversation's tool manager.

        Args:
            tools (list or Tool): The tools to register.

        """
        if not isinstance(tools, list):
            tools = [tools]
        self.tool_manager.register_tools(tools=tools)

    def delete_tool(self, name):
        """
        Delete a tool from the conversation's tool manager.

        Args:
            name (str): The name of the tool to delete.

        Returns:
            bool: True if the tool was deleted, False otherwise.

        """
        if name in self.tool_manager.registry:
            self.tool_manager.registry.pop(name)
            return True
        return False

    def clone(self):
        """
        Create a clone of the conversation.

        Returns:
            Branch: A new Branch object that is a clone of the current conversation.

        """
        cloned = Branch(
            dir = self._logger.dir,
            messages=self.messages.copy(), 
            instruction_sets=self.instruction_sets.copy(),
            tool_manager=ToolManager()
        )
        cloned.tool_manager.registry = self.tool_manager.registry.copy()

        return cloned

    def merge(self, branch, update=True):
        """
        Merge another branch into the current conversation.

        Args:
            branch (Branch): The branch to merge.
            update (bool): Whether to update existing elements or keep only new ones.

        """
        messages_copy = branch.messages.copy()
        branch_system = messages_copy.loc[0]
        messages_copy.drop(0, inplace=True)
        self.messages = self.messages.merge(messages_copy, how='outer')
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

    def messages_describe(self) -> Dict[str, Any]:
        """
        Describe the conversation and its messages.

        Returns:
            dict: A dictionary containing information about the conversation and its messages.

        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.info(),
            "instruction_sets": self.instruction_sets,
            "registered_tools": self.tool_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    def to_chatcompletion_message(self):
        """
        Convert the conversation into a chat completion message format.

        Returns:
            list: A list of messages in chat completion message format.

        """
        message = []
        for _, row in self.messages.iterrows():
            out = {"role": row['role'], "content": json.dumps(as_dict(row['content']))}
            message.append(out)
        return message

    def _is_invoked(self):
        """
        Check if the conversation has been invoked with an action response.

        Returns:
            bool: True if the conversation has been invoked, False otherwise.

        """
        content = self.messages.iloc[-1]['content']
        try:
            if json.loads(content)['action_response'].keys() >= {'function', 'arguments', 'output'}:
                return True
        except:
            return False