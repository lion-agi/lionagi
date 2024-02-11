import pandas as pd

from typing import Any, List, Union, Dict, Optional, Callable, Tuple
from dotenv import load_dotenv

from lionagi.schema import Tool
from lionagi._services.oai import OpenAIService
from ..messages.messages import System, Instruction
from ..branch.branch import Branch
from ..branch.branch_manager import BranchManager

load_dotenv()


class Session:
    """
    Manages sessions with conversation branches, tool management, and interaction logging.

    This class orchestrates the handling of different conversation branches, enabling distinct conversational contexts to coexist within a single session. It facilitates the integration with external services for processing chat completions, tool management, and the logging of session activities.

    Attributes:
        branches (Dict[str, Branch]): Maps branch names to Branch instances.
        default_branch (Branch): The primary branch for the session.
        default_branch_name (str): Identifier for the default branch.
        llmconfig (Dict[str, Any]): Configurations for language model interactions.
        service (OpenAIService): Interface for external service interactions.
    """
    def __init__(
        self,
        system: Optional[Union[str, System]] = None,
        sender: Optional[str] = None,
        llmconfig: Optional[Dict[str, Any]] = None,
        service: OpenAIService = None,
        branches: Optional[Dict[str, Branch]] = None,
        default_branch: Optional[Branch] = None,
        default_branch_name: str = 'main',
    ):
        """
        Initializes a session with optional settings for branches, service, and language model configurations.

        Args:
            system (Optional[Union[str, System]]): Initial system message or configuration.
            sender (Optional[str]): Identifier for the sender of the system message.
            llmconfig (Optional[Dict[str, Any]]): Language model configuration settings.
            service (OpenAIService): External service for chat completions and other operations.
            branches (Optional[Dict[str, Branch]]): Predefined conversation branches.
            default_branch (Optional[Branch]): Preselected default branch for the session.
            default_branch_name (str): Name for the default branch, defaults to 'main'.
        """

        self.branches = branches if isinstance(branches, dict) else {}
        if service is None:
            service = OpenAIService()

        self._setup_default_branch(
            default_branch, default_branch_name, service, llmconfig, system, sender)
        
        self._verify_default_branch()
        self.branch_manager = BranchManager(self.branches)
        
    def new_branch(
        self, 
        branch_name: str,
        dir: Optional[str] = None,
        messages: Optional[pd.DataFrame] = None,
        tools: Optional[Union[Tool, List[Tool]]] = None,
        system: Optional[Union[str, System]] = None,
        sender: Optional[str] = None,
        service: Optional[OpenAIService] = None,
        llmconfig: Optional[Dict] = None,
    ) -> None:
        """
        Creates a new branch within the session.

        Args:
            branch_name (str): Name for the new branch.
            dir (Optional[str]): Path for storing branch-related logs.
            messages (Optional[pd.DataFrame]): Initial set of messages for the branch.
            tools (Optional[Union[Tool, List[Tool]]]): Tools to register in the new branch.
            system (Optional[Union[str, System]]): System message or configuration for the branch.
            sender (Optional[str]): Identifier for the sender of the initial message.
            service (Optional[OpenAIService]): Service interface specific to the branch.
            llmconfig (Optional[Dict[str, Any]]): Language model configurations for the branch.

        Raises:
            ValueError: If the branch name already exists within the session.
        """
        if branch_name in self.branches.keys():
            raise ValueError(f'Invalid new branch name {branch_name}. Already existed.')
        new_ = Branch(name=branch_name, dir=dir, messages=messages, service=service, llmconfig=llmconfig)
        if system:
            new_.add_message(system=system, sender=sender)
        if tools:
            new_.register_tools(tools=tools)
        self.branches[branch_name] = new_

        self.branch_manager.sources[branch_name] = new_
        self.branch_manager.requests[branch_name] = {}

    def get_branch(
        self, 
        branch: Optional[Union[Branch, str]] = None, 
        get_name: bool = False
    ) -> Union[Branch, Tuple[Branch, str]]:
        """
        Retrieves a branch from the session by name or as a Branch object.

        If no branch is specified, returns the default branch. Optionally, can also return the branch's name.

        Args:
            branch (Optional[Union[Branch, str]]): The branch name or Branch object to retrieve. Defaults to None, which refers to the default branch.
            get_name (bool): If True, also returns the name of the branch alongside the Branch object.

        Returns:
            Union[Branch, Tuple[Branch, str]]: The requested Branch object, or a tuple of the Branch object and its name if `get_name` is True.

        Raises:
            ValueError: If the specified branch does not exist within the session.
        """
        if isinstance(branch, str):
            if branch not in self.branches.keys():
                raise ValueError(f'Invalid branch name {branch}. Not exist.')
            else:
                if get_name: 
                    return self.branches[branch], branch
                return self.branches[branch]
        
        elif isinstance(branch, Branch) and branch in self.branches.values():
            if get_name:
                return branch, [key for key, value in self.branches.items() if value == branch][0]
            return branch

        elif branch is None:
            if get_name:
                return self.default_branch, self.default_branch_name
            return self.default_branch
        
        else:
            raise ValueError(f'Invalid branch input {branch}.')

    def change_default(self, branch: Union[str, Branch]) -> None:
        """
        Changes the default branch of the session.

        Args:
            branch (Union[str, Branch]): The branch name or Branch object to set as the new default branch.
        """
        branch_, name_ = self.get_branch(branch, get_name=True)
        self.default_branch = branch_
        self.default_branch_name = name_

    def delete_branch(self, branch: Union[Branch, str], verbose: bool = True) -> bool:
        """
        Delete a branch from the session.

        Args:
            branch (Union[Branch, str]): The branch object or its name to be deleted.
            verbose (bool, optional): If True, prints a confirmation message.

        Returns:
            bool: True if the branch is successfully deleted, False otherwise.

        Raises:
            ValueError: If trying to delete the current default branch.
        """
        _, branch_name = self.get_branch(branch, get_name=True)

        if branch_name == self.default_branch_name:
            raise ValueError(
                f'{branch_name} is the current default branch, please switch to another branch before delete it.'
            )
        else:
            self.branches.pop(branch_name)
            # self.branch_manager.sources.pop(branch_name)
            self.branch_manager.requests.pop(branch_name)
            if verbose:
                print(f'Branch {branch_name} is deleted.')
            return True

    def merge_branch(
        self, 
        from_: Union[str, Branch], 
        to_: Union[str, Branch], 
        update: bool = True, 
        del_: bool = False
    ) -> None:
        """
        Merge one branch into another within the session.

        Args:
            from_ (Union[str, Branch]): The branch or its name to merge from.
            to_ (Union[str, Branch]): The branch or its name to merge into.
            update (bool, optional): If True, updates the target branch's system message to be same as `from_`.
            del_ (bool, optional): If True, deletes the 'from' branch after merging.

        Raises:
            ValueError: If the branch does not exist in the session.
        """
        from_ = self.get_branch(branch=from_)
        to_, to_name = self.get_branch(branch=to_, get_name=True)
        to_.merge_branch(from_, update=update)
        
        if del_:
            if from_ == self.default_branch:
                self.default_branch_name = to_name
                self.default_branch = to_
            self.delete_branch(from_, verbose=False)

    async def chat(
        self, 
        instruction: Union[Instruction, str],
        to_: Optional[Union[Branch, str]] = None, 
        system: Optional[Union[System, str, Dict]] = None,
        context: Optional[Any] = None,
        out: bool = True,
        sender: Optional[str] = None,
        invoke: bool = True,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        fallback: Optional[Callable] = None,
        fallback_kwargs: Dict = {},
        **kwargs
    ) -> None:
        """
        Initiate a chat with the specified branch using an instruction.

        Args:
            instruction (Union[Instruction, str]): The instruction or message to send.
            to_ (Optional[Union[Branch, str]], optional): The target branch or its name. Default is the main branch.
            system (Optional[Union[System, str, Dict]], optional): System message or data to use.
            context (Optional[Any], optional): Additional context for the chat.
            out (bool, optional): If True, sends the output message.
            sender (Optional[str], optional): The sender's name.
            invoke (bool, optional): If True, invokes tool processing.
            tools (Union[bool, Tool, List[Tool], str, List[str]], optional): Tools to be used or not used.
            fallback (Optional[Callable], optional): Fallback function to call in case of an exception.
            fallback_kwargs (Dict, optional): Keyword arguments for the fallback function.
            **kwargs: Additional keyword arguments.

        Raises:
            Exception: If an exception occurs in the chat process and no fallback is provided.
        """
        branch_ = self.get_branch(to_)
        if fallback:
            try:
                return await branch_.chat(
                    instruction=instruction, system=system, context=context,
                    out=out, sender=sender, invoke=invoke, tools=tools, **kwargs
                )
            except:
                return fallback(**fallback_kwargs)

        return await branch_.chat(
            instruction=instruction, system=system, context=context,
            out=out, sender=sender, invoke=invoke, tools=tools, **kwargs)

    async def ReAct(
        self,
        instruction: Union[Instruction, str],
        context = None,
        sender = None,
        to_ = None,
        system = None,
        tools = None, 
        num_rounds: int = 1,
        fallback: Optional[Callable] = None,
        fallback_kwargs: Optional[Dict] = None,
        out=True,
        **kwargs  
    ):
        """
        Performs a sequence of reasoning and action steps in a specified or default branch.

        Args:
            instruction (Union[Instruction, str]): Instruction to initiate the ReAct process.
            context: Additional context for reasoning and action. Defaults to None.
            sender: Identifier for the sender. Defaults to None.
            to_: Target branch name or object for ReAct. Defaults to the default branch.
            system: System message or configuration. Defaults to None.
            tools: Tools to be used for actions. Defaults to None.
            num_rounds (int): Number of reasoning-action cycles. Defaults to 1.
            fallback (Optional[Callable]): Fallback function in case of an error. Defaults to None.
            fallback_kwargs (Optional[Dict]): Arguments for the fallback function. Defaults to None.
            out (bool): If True, outputs the result of the ReAct process. Defaults to True.
            **kwargs: Arbitrary keyword arguments for additional customization.

        Returns:
            The outcome of the ReAct process, depending on the specified branch and instructions.
        """
        branch = self.get_branch(to_)
        return await branch.ReAct(
            instruction=instruction, context=context, sender=sender, system=system, tools=tools, 
            num_rounds=num_rounds, fallback=fallback, fallback_kwargs=fallback_kwargs, 
            out=out, **kwargs
        )

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        to_: Optional[Union[Branch, str]] = None,
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        fallback: Optional[Callable] = None,
        fallback_kwargs: Dict = {},
        **kwargs
    ) -> None:
        """
        Automatically follow up on a chat conversation within a branch with multiple messages.

        Args:
            instruction (Union[Instruction, str]): The initial instruction or message to send.
            to_ (Optional[Union[Branch, str]], optional): The target branch or its name. Default is the main branch.
            num (int, optional): The number of follow-up messages to send.
            tools (Union[bool, Tool, List[Tool], str, List[str], List[Dict]], optional): Tools to be used or not used.
            fallback (Optional[Callable], optional): Fallback function to call in case of an exception.
            fallback_kwargs (Dict, optional): Keyword arguments for the fallback function.
            **kwargs: Additional keyword arguments.

        Raises:
            Exception: If an exception occurs in the auto-followup process and no fallback is provided.
        """
        
        branch_ = self.get_branch(to_)
        return await branch_.auto_followup(
            instruction=instruction, num=num, tools=tools, fallback=fallback, fallback_kwargs=fallback_kwargs, **kwargs
        )

    def change_first_system_message(self, system: Union[System, str]) -> None:
        """
        Change the system message of the current default branch.

        Args:
            system (Union[System, str]): The new system message or a System object.
        """
        self.default_branch.change_first_system_message(system)

    def collect(self, from_: Union[str, Branch, List[str], List[Branch]] = None):
        """
        Collect requests from specified branches or all branches if none specified.

        Args:
            from_ (Union[str, Branch, List[str], List[Branch]], optional): The source branch(es) from which to collect requests.
                If None, data is collected from all branches. Can be a single branch or a list of branches.
        """
        if from_ is None:
            for branch in self.branches.keys():
                self.branch_manager.collect(branch)
        else:
            if not isinstance(from_, list):
                from_ = [from_]
            for branch in from_:
                if isinstance(branch, Branch):
                    branch = branch.name
                if isinstance(branch, str):
                    self.branch_manager.collect(branch)

    def send(self, to_: Union[str, Branch, List[str], List[Branch]] = None):
        """
        Collect requests from specified branches or all branches if none specified.

        Args:
            to_ (Union[str, Branch, List[str], List[Branch]], optional): The target branch(es) to which to send requests.
                If None, requests are sent to all branches. Can be a single branch or a list of branches.
        """
        if to_ is None:
            for branch in self.branches.keys():
                self.branch_manager.send(branch)
        else:
            if not isinstance(to_, list):
                to_ = [to_]
            for branch in to_:
                if isinstance(branch, Branch):
                    branch = branch.name
                if isinstance(branch, str):
                    self.branch_manager.send(branch)

    def collect_send_all(self, receive_all=False):
        """
        Collect and send requests across all branches, with an option to invoke receive_all on each branch.

        Args:
            receive_all (bool, optional): If True, triggers the receive_all method on each branch after sending requests.
        """
        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches.values():
                branch.receive_all()

    def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
        """
        Registers one or more tools to the current default branch.

        Args:
            tools (Union[Tool, List[Tool]]): The tool or list of tools to register.
        """
        self.default_branch.register_tools(tools)

    def delete_tool(self, name: str) -> bool:
        """
        Deletes a tool from the current default branch.

        Args:
            name (str): The name of the tool to delete.

        Returns:
            bool: True if the tool is deleted, False otherwise.
        """
        return self.default_branch.delete_tool(name)

    @property
    def describe(self) -> Dict[str, Any]:
        """
        Generates a report of the current default branch.

        Returns:
            Dict[str, Any]: The report of the current default branch.
        """
        return self.default_branch.describe

    @property
    def messages(self) -> pd.DataFrame:
        """
        Get the DataFrame containing conversation messages.

        Returns:
            pd.DataFrame: A DataFrame containing conversation messages.
        """
        return self.default_branch.messages


    @property
    def first_system(self) -> pd.Series:
        """
        Get the first system message of the current default branch.

        Returns:
            System: The first system message of the current default branch.
        """
        return self.default_branch.first_system
    
    @property
    def last_response(self) -> pd.Series:
        """
        Get the last response message of the current default branch.

        Returns:
            str: The last response message of the current default branch.
        """
        return self.default_branch.last_response


    @property
    def last_response_content(self) -> Dict:
        """
        Get the last response content of the current default branch.

        Returns:
            Dict: The last response content of the current default branch.
        """
        return self.default_branch.last_response_content


    def _verify_default_branch(self):
        if self.branches:
            if self.default_branch_name not in self.branches.keys():
                raise ValueError('default branch name is not in imported branches')
            if self.default_branch is not self.branches[self.default_branch_name]:
                raise ValueError(f'default branch does not match Branch object under {self.default_branch_name}')
            
        if not self.branches:
            self.branches[self.default_branch_name] = self.default_branch

    def _setup_default_branch(
        self, default_branch, default_branch_name, service, llmconfig, system, sender
    ):
        self.default_branch = default_branch if default_branch else Branch(
            name=default_branch_name, service=service, llmconfig=llmconfig
        )
        self.default_branch_name = default_branch_name
        if system:
            self.default_branch.add_message(system=system, sender=sender)

        self.llmconfig = self.default_branch.llmconfig
    # def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
    #     """
    #     Adds an instruction set to the current active branch.
    #
    #     Args:
    #         name (str): The name of the instruction set.
    #         instruction_set (InstructionSet): The instruction set to add.
    #     """
    #     self.default_branch.add_instruction_set(name, instruction_set)
    #
    # def remove_instruction_set(self, name: str) -> bool:
    #     """
    #     Removes an instruction set from the current active branch.
    #
    #     Args:
    #         name (str): The name of the instruction set to remove.
    #
    #     Returns:
    #         bool: True if the instruction set is removed, False otherwise.
    #     """
    #     return self.default_branch.remove_instruction_set(name)