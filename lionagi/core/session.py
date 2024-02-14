import pandas as pd

from typing import Any, List, Union, Dict, Optional, Callable, Tuple
from dotenv import load_dotenv

from lionagi.utils.sys_util import to_df
from lionagi.schema import Tool
from lionagi._services.oai import OpenAIService
from .messages.messages import System, Instruction
from .branch import Conversation
from .branch import Branch
from .branch_manager import BranchManager

load_dotenv()


class Session:

    def __init__(
        self,
        system: Optional[Union[str, System]] = None,
        sender: Optional[str] = None,
        llmconfig: Optional[Dict[str, Any]] = None,
        service: OpenAIService = None,
        branches: Optional[Dict[str, Branch]] = None,
        default_branch: Optional[Branch] = None,
        default_branch_name: str = 'main',
        tools = None, 
        instruction_sets=None, tool_manager=None,
        messages=None
    ):
        self.branches = branches if isinstance(branches, dict) else {}
        self.service = service or OpenAIService()
        
        self._setup_default_branch(
            system, sender, default_branch, default_branch_name, messages, 
            instruction_sets, tool_manager, service, llmconfig, tools
        )
        self.tool_manager
        
        self._verify_default_branch()
        self.branch_manager = BranchManager(self.branches)
  

# --- default branch methods ---- #
    @property
    def last_row(self) -> pd.Series:
        """
        Retrieve the last row from the conversation messages as a pandas Series.

        Returns:
            pd.Series: The last message in the conversation.
        """
        return self.default_branch.last_message
    
    @property
    def first_system(self) -> pd.Series:
        """
        Retrieve the first system message from the conversation.

        Returns:
            pd.Series: The first message in the conversation where the role is 'system'.
        """
        return self.default_branch.first_system
        
    @property
    def last_response(self) -> pd.Series:
        """
        Retrieve the last response message from the conversation.

        Returns:
            pd.Series: The last message in the conversation where the role is 'assistant'.
        """
        return self.default_branch.last_response

    @property
    def last_response_content(self) -> Dict:
        """
        Retrieve the last response message content from the conversation.

        Returns:
            pd.Series: The last message in the conversation where the role is 'assistant'.
        """
        return self.default_branch.last_response_content

    @property
    def last_instruction(self) -> pd.Series:
        """
        Retrieve the last instruction message from the conversation.

        Returns:
            pd.Series: The last message in the conversation where the role is 'user'.
        """
        return self.default_branch.last_instruction

    @property
    def last_action_request(self):
        """
        Retrieve the last action request message from the conversation.

        Returns:
            pd.Series: The last message in the conversation with sender 'action_request'.
        """
        return self.default_branch.last_action_request
    
    @property
    def last_action_response(self):
        """
        Retrieve the last action response message from the conversation.

        Returns:
            pd.Series: The last message in the conversation with sender 'action_response'.
        """
        return self.default_branch.last_action_response

    @property
    def len_messages(self):
        """
        Get the total number of messages in the conversation.

        Returns:
            int: The total number of messages.
        """
        return self.default_branch.len_messages
    
    @property
    def len_instructions(self):
        """
        Get the total number of instruction messages (messages with role 'user') in the conversation.

        Returns:
            int: The total number of instruction messages.
        """
        return self.default_branch.len_instructions
    
    @property
    def len_responses(self):
        """
        Get the total number of response messages (messages with role 'assistant') in the conversation.

        Returns:
            int: The total number of response messages.
        """

        return self.default_branch.len_responses



# ------ branch method -------#

  
  
  
  
  
        
#     def new_branch(
#         self, 
#         branch_name: Optional[str] = None,
#         system=None,
#         sender=None,
#         messages: Optional[pd.DataFrame] = None,
#         instruction_sets = None,
#         tool_manager = None,
#         service = None,
#         llmconfig = None,
#         tools=None,
#     ) -> None:        
#         if branch_name in self.branches.keys():
#             raise ValueError(f'Invalid new branch name {branch_name}. Branch already existed.')
#         new_ = Branch(
#             name=branch_name,
#             messages=messages,
#             messages=messages, 
#             instruction_sets=instruction_sets, 
#             tool_manager=tool_manager, 
#             service=service, 
#             llmconfig=llmconfig, 
#             tools=tools
#         )
#         if system:
#             new_.add_message(system=system, sender=sender)

#         self.branches[branch_name] = new_
#         self.branch_manager.sources[branch_name] = new_
#         self.branch_manager.requests[branch_name] = {}

#     def get_branch(
#         self, 
#         branch: Optional[Union[Branch, str]] = None, 
#         get_name: bool = False
#     ) -> Union[Branch, Tuple[Branch, str]]:
#         if isinstance(branch, str):
#             if branch not in self.branches.keys():
#                 raise ValueError(f'Invalid branch name {branch}. Not exist.')
#             else:
#                 if get_name: 
#                     return self.branches[branch], branch
#                 return self.branches[branch]
        
#         elif isinstance(branch, Branch) and branch in self.branches.values():
#             if get_name:
#                 return branch, [key for key, value in self.branches.items() if value == branch][0]
#             return branch

#         elif branch is None:
#             if get_name:
#                 return self.default_branch, self.default_branch_name
#             return self.default_branch
        
#         else:
#             raise ValueError(f'Invalid branch input {branch}.')

#     def change_default_branch(self, branch: Union[str, Branch]) -> None:
#         branch_, name_ = self.get_branch(branch, get_name=True)
#         self.default_branch = branch_
#         self.default_branch_name = name_

#     def delete_branch(self, branch: Union[Branch, str], verbose: bool = True) -> bool:
#         _, branch_name = self.get_branch(branch, get_name=True)

#         if branch_name == self.default_branch_name:
#             raise ValueError(
#                 f'{branch_name} is the current default branch, please switch to another branch before delete it.'
#             )
#         else:
#             self.branches.pop(branch_name)
#             # self.branch_manager.sources.pop(branch_name)
#             self.branch_manager.requests.pop(branch_name)
#             if verbose:
#                 print(f'Branch {branch_name} is deleted.')
#             return True

#     def merge_branch(
#         self, 
#         from_: Union[str, Branch], 
#         to_: Union[str, Branch], 
#         update: bool = True, 
#         del_: bool = False
#     ) -> None:
#         from_ = self.get_branch(branch=from_)
#         to_, to_name = self.get_branch(branch=to_, get_name=True)
#         to_.merge_branch(from_, update=update)
        
#         if del_:
#             if from_ == self.default_branch:
#                 self.default_branch_name = to_name
#                 self.default_branch = to_
#             self.delete_branch(from_, verbose=False)

# # --- branch chat method --- #
#     async def chat(
#         self, 
#         instruction: Union[Instruction, str],
#         to_: Optional[Union[Branch, str]] = None, 
#         system: Optional[Union[System, str, Dict]] = None,
#         context: Optional[Any] = None,
#         out: bool = True,
#         sender: Optional[str] = None,
#         invoke: bool = True,
#         tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
#         fallback: Optional[Callable] = None,
#         fallback_kwargs: Dict = {},
#         **kwargs
#     ) -> None:
#         branch_ = self.get_branch(to_)
#         if fallback:
#             try:
#                 return await branch_.chat(
#                     instruction=instruction, system=system, context=context,
#                     out=out, sender=sender, invoke=invoke, tools=tools, **kwargs
#                 )
#             except:
#                 return fallback(**fallback_kwargs)

#         return await branch_.chat(
#             instruction=instruction, system=system, context=context,
#             out=out, sender=sender, invoke=invoke, tools=tools, **kwargs)

#     async def ReAct(
#         self,
#         instruction: Union[Instruction, str],
#         context = None,
#         sender = None,
#         to_ = None,
#         system = None,
#         tools = None, 
#         num_rounds: int = 1,
#         fallback: Optional[Callable] = None,
#         fallback_kwargs: Optional[Dict] = None,
#         out=True,
#         **kwargs  
#     ):
#         branch = self.get_branch(to_)
#         return await branch.ReAct(
#             instruction=instruction, context=context, sender=sender, system=system, tools=tools, 
#             num_rounds=num_rounds, fallback=fallback, fallback_kwargs=fallback_kwargs, 
#             out=out, **kwargs
#         )

#     async def auto_followup(
#         self,
#         instruction: Union[Instruction, str],
#         to_: Optional[Union[Branch, str]] = None,
#         num: int = 3,
#         tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
#         fallback: Optional[Callable] = None,
#         fallback_kwargs: Dict = {},
#         **kwargs
#     ) -> None:
#         branch_ = self.get_branch(to_)
#         return await branch_.auto_followup(
#             instruction=instruction, num=num, tools=tools, fallback=fallback, fallback_kwargs=fallback_kwargs, **kwargs
#         )

# # ---- branch manipulation methods -----#
#     @classmethod
#     def from_csv(
#         cls, 
#         filepath, 
#         system=None, 
#         sender=None, 
#         branch_name=None, 
#         instruction_sets=None, 
#         tool_manager=None, 
#         service=None, 
#         llmconfig=None, 
#         tools=None, 
#         **kwargs
#     ):
#         """
#         kwargs are for pd.read_csv
#         """  
#         messages = to_df(pd.read_csv(filepath, **kwargs))
#         self = cls(
#             messages=messages,
#             system=system, 
#             branch_name=branch_name, 
#             sender=sender, 
#             instruction_sets=instruction_sets,
#             tool_manager=tool_manager,
#             service=service,
#             llmconfig=llmconfig,
#             tools=tools
#         )
#         return self

#     @classmethod
#     def from_json(
#         cls, 
#         filepath, 
#         system=None, 
#         sender=None, 
#         branch_name=None, 
#         instruction_sets=None, 
#         tool_manager=None, 
#         service=None, 
#         llmconfig=None, 
#         tools=None, 
#         **kwargs
#     ):
#         """
#         kwargs are for pd.read_json
#         """
#         messages = pd.read_json(
#             filepath, orient="records", lines=True, **kwargs
#         )
        
#         self = cls(
#             messages=to_df(messages),
#             system=system, 
#             branch_name=branch_name, 
#             sender=sender, 
#             instruction_sets=instruction_sets,
#             tool_manager=tool_manager,
#             service=service,
#             llmconfig=llmconfig,
#             tools=tools
#         )
#         return self




















#     def change_first_system_message(self, system: Union[System, str]) -> None:
#         """
#         Change the system message of the current default branch.

#         Args:
#             system (Union[System, str]): The new system message or a System object.
#         """
#         self.default_branch.change_first_system_message(system)

#     def collect(self, from_: Union[str, Branch, List[str], List[Branch]] = None):
#         """
#         Collect requests from specified branches or all branches if none specified.

#         Args:
#             from_ (Union[str, Branch, List[str], List[Branch]], optional): The source branch(es) from which to collect requests.
#                 If None, data is collected from all branches. Can be a single branch or a list of branches.
#         """
#         if from_ is None:
#             for branch in self.branches.keys():
#                 self.branch_manager.collect(branch)
#         else:
#             if not isinstance(from_, list):
#                 from_ = [from_]
#             for branch in from_:
#                 if isinstance(branch, Branch):
#                     branch = branch.name
#                 if isinstance(branch, str):
#                     self.branch_manager.collect(branch)

#     def send(self, to_: Union[str, Branch, List[str], List[Branch]] = None):
#         """
#         Collect requests from specified branches or all branches if none specified.

#         Args:
#             to_ (Union[str, Branch, List[str], List[Branch]], optional): The target branch(es) to which to send requests.
#                 If None, requests are sent to all branches. Can be a single branch or a list of branches.
#         """
#         if to_ is None:
#             for branch in self.branches.keys():
#                 self.branch_manager.send(branch)
#         else:
#             if not isinstance(to_, list):
#                 to_ = [to_]
#             for branch in to_:
#                 if isinstance(branch, Branch):
#                     branch = branch.name
#                 if isinstance(branch, str):
#                     self.branch_manager.send(branch)

#     def collect_send_all(self, receive_all=False):
#         """
#         Collect and send requests across all branches, with an option to invoke receive_all on each branch.

#         Args:
#             receive_all (bool, optional): If True, triggers the receive_all method on each branch after sending requests.
#         """
#         self.collect()
#         self.send()
#         if receive_all:
#             for branch in self.branches.values():
#                 branch.receive_all()

#     def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
#         """
#         Registers one or more tools to the current default branch.

#         Args:
#             tools (Union[Tool, List[Tool]]): The tool or list of tools to register.
#         """
#         self.default_branch.register_tools(tools)

#     def delete_tool(self, name: str) -> bool:
#         """
#         Deletes a tool from the current default branch.

#         Args:
#             name (str): The name of the tool to delete.

#         Returns:
#             bool: True if the tool is deleted, False otherwise.
#         """
#         return self.default_branch.delete_tool(name)

#     @property
#     def describe(self) -> Dict[str, Any]:
#         """
#         Generates a report of the current default branch.

#         Returns:
#             Dict[str, Any]: The report of the current default branch.
#         """
#         return self.default_branch.describe

#     @property
#     def messages(self) -> pd.DataFrame:
#         """
#         Get the DataFrame containing conversation messages.

#         Returns:
#             pd.DataFrame: A DataFrame containing conversation messages.
#         """
#         return self.default_branch.messages


#     @property
#     def first_system(self) -> pd.Series:
#         """
#         Get the first system message of the current default branch.

#         Returns:
#             System: The first system message of the current default branch.
#         """
#         return self.default_branch.first_system
    
#     @property
#     def last_response(self) -> pd.Series:
#         """
#         Get the last response message of the current default branch.

#         Returns:
#             str: The last response message of the current default branch.
#         """
#         return self.default_branch.last_response


#     @property
#     def last_response_content(self) -> Dict:
#         """
#         Get the last response content of the current default branch.

#         Returns:
#             Dict: The last response content of the current default branch.
#         """
#         return self.default_branch.last_response_content



#     # def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
#     #     """
#     #     Adds an instruction set to the current active branch.
#     #
#     #     Args:
#     #         name (str): The name of the instruction set.
#     #         instruction_set (InstructionSet): The instruction set to add.
#     #     """
#     #     self.default_branch.add_instruction_set(name, instruction_set)
#     #
#     # def remove_instruction_set(self, name: str) -> bool:
#     #     """
#     #     Removes an instruction set from the current active branch.
#     #
#     #     Args:
#     #         name (str): The name of the instruction set to remove.
#     #
#     #     Returns:
#     #         bool: True if the instruction set is removed, False otherwise.
#     #     """
#     #     return self.default_branch.remove_instruction_set(name)


    def _verify_default_branch(self):
        if self.branches:
            if self.default_branch_name not in self.branches.keys():
                raise ValueError('default branch name is not in imported branches')
            if self.default_branch is not self.branches[self.default_branch_name]:
                raise ValueError(f'default branch does not match Branch object under {self.default_branch_name}')
            
        if not self.branches:
            self.branches[self.default_branch_name] = self.default_branch

    def _setup_default_branch(
        self, system, sender, default_branch, default_branch_name, messages, 
        instruction_sets, tool_manager, service, llmconfig, tools
    ):
        
        branch = default_branch or Branch(
            name=default_branch_name, service=service, llmconfig=llmconfig, tools=tools,
            tool_manager=tool_manager, instruction_sets=instruction_sets, messages=messages
        )
        
        self.default_branch = branch
        self.default_branch_name = default_branch_name
        if system:
            self.default_branch.add_message(system=system, sender=sender)

        self.llmconfig = self.default_branch.llmconfig