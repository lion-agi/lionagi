import pandas as pd
from typing import Any, List, Union, Dict, Optional, Callable
from dotenv import load_dotenv

from lionagi.schema import DataLogger, Tool
from lionagi.utils import as_dict, lcall, get_flattened_keys, alcall, to_list
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
        branches (Dict): A dictionary of conversation branches.
        default_branch (Branch): The default branch for the session.
        default_branch_name (str): The name of the default branch.
        llmconfig (Dict[str, Any]): Configuration settings for the language model.
        logger_ (DataLogger): Logger for session data.
        service: Service used for handling chat completions and other operations.
    """
    def __init__(
        self,
        system: Union[str, System],
        dir: str = None,
        llmconfig: Dict[str, Any] = None,
        service  = OAIService,
        branches = None,
        default_branch=None,
        default_branch_name='main',
    ):
        """
        Initialize a Session object.

        Args:
            system (Union[str, System]): Initial system message or System object for the default branch.
            dir (str, optional): Directory path for storing logs.
            llmconfig (Dict[str, Any], optional): Configuration settings for the language model.
            service (OAIService, optional): Service used for handling chat completions and other operations.
            branches (optional): Pre-existing branches to initialize in the session.
            default_branch (optional): Default branch for the session.
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
        system: Union[str, System]=None, 
        tools=None, 
        sender=None,
        service=None,
    ) -> None:
        """
        Create a new branch in the session.

        Args:
            branch_name (str): Name of the new branch.
            system (Union[str, System], optional): Initial system message or System object for the new branch.
            tools (optional): Tools to register with the new branch.
            sender (optional): Sender of the initial system message.

        Raises:
            ValueError: If the branch name already exists in the session.
        """
        new_ = Branch()
        if branch_name in self.branches.keys():
            raise ValueError(f'Invalid new branch name {branch_name}. Already existed.')
        if system:
            new_.change_system_message(system, sender=sender)
        if tools:
            new_.register_tools(tools)    
        new_.service = service or self.service
        self.branches[branch_name] = new_

    def get_branch(self, branch: Union[Branch, str]=None, get_name=False):
        """
        Retrieve a branch from the session.

        Args:
            branch (Union[Branch, str], optional): The branch or its name to retrieve.
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

    def delete_branch(self, branch: Union[Branch, str], verbose=True) -> bool:
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
            update (bool, optional): If True, updates existing elements; keeps only new ones otherwise.
            if_delete (bool, optional): If True, deletes the 'from' branch after merging.

        Raises:
            ValueError: If the branch does not exist in the session.
        """
        from_ = self.get_branch(branch=from_)
        to_, to_name = self.get_branch(branch=to_)
        to_.merge_conversation(from_, update=update)
        
        if del_:
            if from_ == self.default_branch:
                self.default_branch_name = to_name
                self.default_branch = to_
            self.delete_branch(from_, verbose=False)

    def send(
        self, 
        messages: pd.DataFrame, 
        to_: Union[Branch, str, List]= None, 
        sign_=False, 
        sender=None, 
    ):
        if sign_: 
            messages = sign_message(messages=messages, sender=sender)
        
        for _to in to_list(to_):
            branch_ = self.get_branch(_to)
            _msg = branch_.messages.copy()
            _new_df = pd.concat([_msg, messages], ignore_index=True)
            _new_df.reset_index(drop=True, inplace=True)
            branch_.messages = _new_df


    async def chat(
        self, 
        instruction: Union[Instruction, str],
        to_: Union[Branch, str]=None, 
        system: Union[System, str, Dict] = None,
        context: Optional[Any] = None,
        out: bool = True,
        sender: Optional[str] = None,
        invoke: bool = True,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
      

        fallback = None,
        fallback_kwargs ={},
        **kwargs
    ) -> None:
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
            out=out, sender=sender, invoke=invoke, tools=tools, **kwargs
        )




    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        to_ : Union[Branch, str]=None,
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        fallback: Callable =None,
        fallback_kwargs = {},
        **kwargs,
    ) -> None:
      

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




    def change_system(self, system):
        self.default_branch.change_system_message(system)
  
    def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
        """Adds an instruction set to the current active branch.

        Args:
            name: The name of the instruction set.
            instruction_set: The instruction set to add.
        """
        self.default_branch.add_instruction_set(name, instruction_set)

    def remove_instruction_set(self, name: str) -> bool:
        """Removes an instruction set from the current active branch.

        Args:
            name: The name of the instruction set to remove.

        Returns:
            bool: True if the instruction set is removed, False otherwise.
        """
        return self.default_branch.remove_instruction_set(name)

    def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
        """Registers one or more tools to the current active branch.

        Args:
            tools: The tool or list of tools to register.
        """
        self.default_branch.register_tools(tools)

    def delete_tool(self, name: str) -> bool:
        """Deletes a tool from the current active branch.

        Args:
            name: The name of the tool to delete.

        Returns:
            bool: True if the tool is deleted, False otherwise.
        """
        return self.default_branch.delete_tool(name)

    def describe(self) -> Dict[str, Any]:
        """Generates a report of the current active branch.

        Returns:
            Dict[str, Any]: The report of the current active branch.
        """
        return self.default_branch.describe()
