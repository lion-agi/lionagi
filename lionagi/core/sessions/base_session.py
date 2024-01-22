from typing import Any, Union, List, Dict
from dotenv import load_dotenv
from abc import ABC

from lionagi.schema import Tool

from ..messages.messages import System
from ..instruction_set.instruction_set import InstructionSet
from ..branch.branch import Branch

load_dotenv()


class BaseSession(ABC):
    
    def __init__(self, system: Union[str, Dict], default_branch:str = 'main') -> None:
        self.branches = {default_branch: Branch(System(system))}
        self.current_branch_name = default_branch
        self.current_branch = self.branches[self.current_branch_name]

    def _new_branch(self, branch_name: str, from_: str) -> None:
        """Creates a new branch based on an existing one.

        Args:
            name: The name of the new branch.
            from_: The name of the branch to clone from.

        Raises:
            ValueError: If the new branch name already exists or the source branch does not exist.
        """
        if branch_name in self.branches.keys():
            raise ValueError(f'Invalid new branch name {branch_name}. Already existed.')
        if from_ not in self.branches.keys():
            raise ValueError(f'Invalid source branch name {from_}. Not exist.')

        self.branches[branch_name] = self.branches[from_].clone()

    def switch_branch(self, name: str) -> None:
        """Switches the current active branch to the specified branch.

        Args:
            name: The name of the branch to switch to.

        Raises:
            ValueError: If the specified branch does not exist.
        """
        if name not in self.branches.keys():
            raise ValueError(f'Invalid source branch name {name}. Not exist.')
        self.current_branch_name = name
        self.current_branch = self.branches[name]

    def merge_branch(
        self, from_: str, to_: str, update: bool = True, if_delete: bool = False
    ) -> None:
        """Merges one branch into another.

        Args:
            from_: The name of the branch to merge from.
            to_: The name of the branch to merge into.
            update: Whether to update the target branch with the source branch's data.
            if_delete: Whether to delete the source branch after merging.

        Raises:
            ValueError: If either the source or target branch name does not exist.
        """
        if from_ not in self.branches.keys():
            raise ValueError(f'Invalid source branch name {from_}. Not exist.')
        if to_ not in self.branches.keys():
            raise ValueError(f'Invalid target branch name {from_}. Not exist.')

        self.branches[to_].merge(self.branches[from_], update)
        if if_delete:
            if from_ == self.current_branch_name:
                self.current_branch_name = to_
                self.current_branch = self.branches[to_]
            self.branches.pop(from_)

    def delete_branch(self, name: str, verbose=True) -> bool:
        """Deletes the specified branch.

        Args:
            name: The name of the branch to delete.

        Returns:
            bool: True if the branch is deleted, False otherwise.

        Raises:
            ValueError: If the specified branch is currently active.
        """
        if name == self.current_branch_name:
            raise ValueError(f'{name} is the current active branch, please switch to another branch before delete it.')
        if name not in self.branches.keys():
            return False
        else:
            self.branches.pop(name)
            if verbose:
                print(f'Branch {name} is deleted.')
            return True
       
    #### Branch Methods: effective to current active branch 
    def change_system_message(self, system: System) -> None:
        """Changes the system message of the current active branch.

        Args:
            system: The new system message.
        """
        self.current_branch.change_system_message(system)

    def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
        """Adds an instruction set to the current active branch.

        Args:
            name: The name of the instruction set.
            instruction_set: The instruction set to add.
        """
        self.current_branch.add_instruction_set(name, instruction_set)

    def remove_instruction_set(self, name: str) -> bool:
        """Removes an instruction set from the current active branch.

        Args:
            name: The name of the instruction set to remove.

        Returns:
            bool: True if the instruction set is removed, False otherwise.
        """
        return self.current_branch.remove_instruction_set(name)

    def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
        """Registers one or more tools to the current active branch.

        Args:
            tools: The tool or list of tools to register.
        """
        self.current_branch.register_tools(tools)

    def delete_tool(self, name: str) -> bool:
        """Deletes a tool from the current active branch.

        Args:
            name: The name of the tool to delete.

        Returns:
            bool: True if the tool is deleted, False otherwise.
        """
        return self.current_branch.delete_tool(name)

    def report(self) -> Dict[str, Any]:
        """Generates a report of the current active branch.

        Returns:
            Dict[str, Any]: The report of the current active branch.
        """
        return self.current_branch.report()
