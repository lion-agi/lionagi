# import pandas as pd
from typing import Any, List, Union, Dict, Optional, Callable, Tuple
from dotenv import load_dotenv

from lionagi.schema import DataLogger, Tool
from lionagi.utils import to_list
from lionagi.configs.oai_configs import oai_schema
from lionagi._services.oai import OpenAIService
from ..messages.messages import System, Instruction
from ..instruction_set.instruction_set import InstructionSet
from ..branch.branch import Branch
from ..core_util import sign_message

            
load_dotenv()
OAIService = OpenAIService()

class Session:
    """
    Represents a session with conversation branches, tool management, and logging.

    This class encapsulates the management of different conversation branches, each with its own
    messages, instruction sets, and tools. It also handles logging and interactions with an external service.

    Attributes:
        branches (Dict[str, Branch]): A dictionary of conversation branches.
        default_branch (Branch): The default branch for the session.
        default_branch_name (str): The name of the default branch.
        llmconfig (Dict[str, Any]): Configuration settings for the language model.
        logger_ (DataLogger): Logger for session data.
        service (OpenAIService): Service used for handling chat completions and other operations.
    """
    def __init__(
        self,
        system: Union[str, System],
        dir: Optional[str] = None,
        llmconfig: Optional[Dict[str, Any]] = None,
        service: OpenAIService = OAIService,
        branches: Optional[Dict[str, Branch]] = None,
        default_branch: Optional[Branch] = None,
        default_branch_name: str = 'main',
    ):
        """
        Initialize a Session object.

        Args:
            system (Union[str, System]): Initial system message or System object for the default branch.
            dir (str, optional): Directory path for storing logs.
            llmconfig (Dict[str, Any], optional): Configuration settings for the language model.
            service (OpenAIService, optional): Service used for handling chat completions and other operations.
            branches (Dict[str, Branch], optional): Pre-existing branches to initialize in the session.
            default_branch (Branch, optional): Default branch for the session.
            default_branch_name (str, optional): Name of the default branch, defaults to 'main'.
        """

        self.branches = branches or {}
        self.default_branch = default_branch or Branch()
        self.default_branch.add_message(system=system)
        self.default_branch_name = default_branch_name
        self.branches.update({self.default_branch_name: self.default_branch})
        self.llmconfig = llmconfig or oai_schema["chat/completions"]["config"]
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        
    def new_branch(
        self, 
        branch_name: str,
        system: Optional[Union[str, System]] = None, 
        tools: Optional[Union[Tool, List[Tool]]] = None, 
        sender: Optional[str] = None,
        service: Optional[OpenAIService] = None,
    ) -> None:
        """
        Create a new branch in the session.

        Args:
            branch_name (str): Name of the new branch.
            system (Union[str, System], optional): Initial system message or System object for the new branch.
            tools (Optional[Union[Tool, List[Tool]]], optional): Tools to register with the new branch.
            sender (Optional[str], optional): Sender of the initial system message.
            service (OpenAIService, optional): Service used for the new branch if different from the session's service.

        Raises:
            ValueError: If the branch name already exists in the session.
        """
        new_ = Branch()
        if branch_name in self.branches.keys():
            raise ValueError(f'Invalid new branch name {branch_name}. Already existed.')
        if system:
            new_.add_message(system, sender=sender)
        if tools:
            new_.register_tools(tools)    
        new_.service = service or self.service
        self.branches[branch_name] = new_

    def get_branch(
        self, 
        branch: Optional[Union[Branch, str]] = None, 
        get_name: bool = False
    ) -> Union[Branch, Tuple[Branch, str]]:
        """
        Retrieve a branch from the session.

        Args:
            branch (Optional[Union[Branch, str]], optional): The branch or its name to retrieve.
                Defaults to the default branch if not specified.
            get_name (bool, optional): If True, returns the name of the branch along with the branch object.

        Returns:
            Union[Branch, Tuple[Branch, str]]: The branch object or a tuple of the branch object and its name.

        Raises:
            ValueError: If the branch does not exist in the session.
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
        Change the default branch of the session.

        Args:
            branch (Union[str, Branch]): The branch or its name to set as the new default.
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
                f'{branch_name} is the current active branch, please switch to another branch before delete it.'
            )
        else:
            self.branches.pop(branch_name)
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
        to_.merge_conversation(from_, update=update)
        
        if del_:
            if from_ == self.default_branch:
                self.default_branch_name = to_name
                self.default_branch = to_
            self.delete_branch(from_, verbose=False)

    # def send(
    #     self, 
    #     messages: pd.DataFrame, 
    #     to_: Optional[Union[Branch, str, List[str]]] = None, 
    #     sign_: bool = False, 
    #     sender: Optional[str] = None,
    # ) -> None:
    #     """
    #     Send messages to one or more branches.

    #     Args:
    #         messages (pd.DataFrame): The DataFrame containing messages to send.
    #         to_ (Optional[Union[Branch, str, List[str]]], optional): The target branch, branch name, or list of branch names.
    #         sign_ (bool, optional): If True, signs the message with the sender's name.
    #         sender (Optional[str], optional): The sender's name.
    #     """
    #     if sign_: 
    #         messages = messages.drop(columns=['sender'], errors='ignore')
    #         messages = sign_message(messages=messages, sender=sender)
        
    #     for _to in to_list(to_):
    #         branch_ = self.get_branch(_to)
    #         _msg = branch_.messages.copy()
    #         _new_df = pd.concat([_msg, messages], ignore_index=True)
    #         _new_df = _new_df.drop_duplicates()
    #         _new_df.reset_index(drop=True, inplace=True)
    #         branch_.messages = _new_df


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
        if fallback:
            try:
                return await branch_.auto_followup(
                    instruction=instruction, num=num, tools=tools,**kwargs
                )
            except:
                return fallback(**fallback_kwargs)
        
        return await branch_.auto_followup(
            instruction=instruction, num=num, tools=tools,**kwargs
        )

    def change_system(self, system: Union[System, str]) -> None:
        """
        Change the system message of the current default branch.

        Args:
            system (Union[System, str]): The new system message or a System object.
        """
        self.default_branch.change_system_message(system)
  
    def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
        """
        Adds an instruction set to the current active branch.

        Args:
            name (str): The name of the instruction set.
            instruction_set (InstructionSet): The instruction set to add.
        """
        self.default_branch.add_instruction_set(name, instruction_set)

    def remove_instruction_set(self, name: str) -> bool:
        """
        Removes an instruction set from the current active branch.

        Args:
            name (str): The name of the instruction set to remove.

        Returns:
            bool: True if the instruction set is removed, False otherwise.
        """
        return self.default_branch.remove_instruction_set(name)

    def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
        """
        Registers one or more tools to the current active branch.

        Args:
            tools (Union[Tool, List[Tool]]): The tool or list of tools to register.
        """
        self.default_branch.register_tools(tools)

    def delete_tool(self, name: str) -> bool:
        """
        Deletes a tool from the current active branch.

        Args:
            name (str): The name of the tool to delete.

        Returns:
            bool: True if the tool is deleted, False otherwise.
        """
        return self.default_branch.delete_tool(name)

    @property
    def describe(self) -> Dict[str, Any]:
        """
        Generates a report of the current active branch.

        Returns:
            Dict[str, Any]: The report of the current active branch.
        """
        return self.default_branch.describe()
