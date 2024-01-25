# """
# propose 4 new pratical methods to the cluster class, stay within scope, the methods should enhance the core capabilities of the class.  
# ---------
# ## system: 
# you are a world-class software engineer with deep expertise in ML and LLM, 
# you are tasked with creating a new class called cluster, which is comprised of branches, but they are for a single purpose, such they can be defined with specific workflows. you are provided with the source codes for branch class, please improve the cluster class to be more efficient and effective.

# ## task:
# thoroughly improve the cluster class
# 1. correct any mistakes
# 2. black style linting
# 3. concise google format docstring with sample usages
# 4. sample usages should have >>> in front 
# 5. type hints
# """

# '''existing branch class
# import json
# from copy import deepcopy
# from typing import Any, Dict, Union, List, Optional
# from datetime import datetime
# import pandas as pd

# from ...utils.call_util import lcall
# from ...schema.base_tool import Tool
# from ...tools.tool_manager import ToolManager
# from ..messages.messages import Message, Instruction, System
# from .conversation import Conversation


# class Branch(Conversation):
#     """
#     Branch of a conversation with message tracking and tool management.

#     This class extends the Conversation class, managing a branch of conversation
#     with the ability to track messages, maintain instruction sets, and manage tools
#     using a ToolManager.

#     Args:
#         init_message: The initial message or messages of the conversation branch.
#         instruction_sets: A set of instructions to be used in the conversation.
#             Defaults to None, which creates an empty dict.
#         tool_manager: A ToolManager instance to manage tools. Defaults to None,
#             which creates a new ToolManager instance.

#     Raises:
#         ValueError: If the input `init_message` is not a DataFrame or Message instance.

#     Attributes:
#         instruction_sets: Instruction sets associated with the conversation branch.
#         tool_manager: Tool manager for the branch.
#         messages: DataFrame containing the conversation messages.
#         system_message: The system message of the conversation branch.

#     Examples:
#         # Creating a Branch with an initial message
#         initial_message = Message(role="user", content="Hi there!")
#         branch = Branch(init_message=initial_message)

#         # Creating a Branch with initial messages as DataFrame
#         messages_df = DataFrame({
#             "role": ["user", "system"],
#             "content": ["Hi there!", "Hello!"]
#         })
#         branch = Branch(init_message=messages_df)
#     """

#     def __init__(self, init_message: Union[Message, pd.DataFrame],
#                  instruction_sets: dict = None,
#                  tool_manager: ToolManager = None) -> None:
#         super().__init__()
#         self.instruction_sets = instruction_sets if instruction_sets else {}
#         self.tool_manager = tool_manager if tool_manager else ToolManager()

#         if isinstance(init_message, pd.DataFrame):
#             self.messages = init_message
#         elif isinstance(init_message, Message):
#             self.add_message(init_message)
#         else:
#             raise ValueError('Please input a valid init_message: DataFrame or Message')
#         self.system_message = self.messages.loc[0, 'content']

#     def change_system_message(self, system: Message):
#         """
#         Change the system message to the provided message.

#         Args:
#             system: A Message object representing the new system message.
#         """
#         message_dict = system.to_dict()
#         message_dict['timestamp'] = datetime.now()
#         self.messages.loc[0] = message_dict
#         self.system_message = self.messages.loc[0, 'content']

#     def add_instruction_set(self, name, instruction_set):
#         """
#         Add an instruction set to the conversation branch.

#         Args:
#             name: The name of the instruction set.
#             instruction_set: The instruction set to be added.
#         """
#         self.instruction_sets[name] = instruction_set

#     def remove_instruction_set(self, name):
#         """
#         Remove an instruction set from the conversation branch by name.

#         Args:
#             name: The name of the instruction set to be removed.

#         Returns:
#             The removed instruction set if it exists, else None.
#         """
#         return self.instruction_sets.pop(name)

#     def register_tools(self, tools):
#         """
#         Register a list of tools to the ToolManager.

#         Args:
#             tools: A single tool or a list of tools to be registered.
#         """
#         if not isinstance(tools, list):
#             tools = [tools]
#         self.tool_manager.register_tools(tools=tools)

#     def delete_tool(self, name):
#         """
#         Delete a tool from the ToolManager by name.

#         Args:
#             name: The name of the tool to be deleted.

#         Returns:
#             True if the tool was successfully deleted, False otherwise.
#         """
#         if name in self.tool_manager.registry:
#             self.tool_manager.registry.pop(name)
#             return True
#         return False

#     def clone(self):
#         """
#         Create a deep copy of the current branch.

#         Returns:
#             A new Branch instance that is a deep copy of the current branch.
#         """
#         cloned = Branch(self.messages.copy())
#         cloned.instruction_sets = deepcopy(self.instruction_sets)
#         cloned.tool_manager = ToolManager()
#         cloned.tool_manager.registry = deepcopy(self.tool_manager.registry)
#         return cloned

#     def merge(self, branch, update=True):
#         """
#         Merge another Branch into the current one.

#         Args:
#             branch: The Branch to merge into the current one.
#             update: Whether to update the current Branch. If False, only adds
#                 non-existing items from the other Branch.
#         """
#         message_copy = branch.messages.copy()
#         branch_system = message_copy.loc[0]
#         message_copy.drop(0, inplace=True)
#         self.messages = self.messages.merge(message_copy, how='outer')
#         if update:
#             self.instruction_sets.update(branch.instruction_sets)
#             self.tool_manager.registry.update(branch.tool_manager.registry)
#             self.messages.loc[0] = branch_system
#         else:
#             for key, value in branch.instruction_sets.items():
#                 if key not in self.instruction_sets:
#                     self.instruction_sets[key] = value

#             for key, value in branch.tool_manager.registry.items():
#                 if key not in self.tool_manager.registry:
#                     self.tool_manager.registry[key] = value

#     def report(self) -> Dict[str, Any]:
#         """
#         Generate a report about the conversation branch.

#         Returns:
#             A dictionary containing information about total messages, a summary by role,
#             instruction sets, registered tools, and the messages themselves.
#         """

#         return {
#             "total_messages": len(self.messages),
#             "summary_by_role": self.message_counts(),
#             "instruction_sets": self.instruction_sets,
#             "registered_tools": self.tool_manager.registry,
#             "messages": [
#                 msg.to_dict() for _, msg in self.messages.iterrows()
#             ],
#         }

#     def last_n_named_row(self, name_, n=1):
#         last_response = self.messages[self.messages.name == name_].iloc[-n:]
#         return last_response

#     def add_name_to_messages(self, name_, prefix='Sender'):
#         df = self.messages.copy(deep=False)
#         responss_idx = df[df.name == name_]
        
#         df['content'][responss_idx] = df.content[responss_idx].apply(
#             lambda x: x if x.startswith(prefix) else f"{prefix} {name_}: {x}")

#     def merge_messages(self, messages, drop_duplicates=True):
        
#         if isinstance(messages, list):
#             messages = pd.concat(messages, ignore_index=True, copy=True)
        
#         if isinstance(messages, pd.DataFrame):
#             self.messages = self.messages.merge(messages, ignore_index=True)
#             if drop_duplicates:
#                 self.messages.drop_duplicates(inplace=True)
#             self.messages.reset_index(drop=True, inplace=True)

#         else:
#             raise ValueError("Please input a valid DataFrame")

#     def _tool_parser(
#         self, tools: Union[Dict, Tool, List[Tool], str, List[str], List[Dict]], 
#         **kwargs) -> Dict:
#         """Parses tools and returns keyword arguments for tool usage.

#         Args:
#             tools: A single tool, a list of tools, or a tool name.
#             **kwargs: Additional keyword arguments.

#         Returns:
#             Dict: Keyword arguments including tool schemas.

#         Raises:
#             ValueError: If the tool is not registered.
#         """
#         # 1. single schema: dict
#         # 2. tool: Tool
#         # 3. name: str
#         # 4. list: 3 types of lists
#         if not branch:
#             branch = self
        
#         def tool_check(tool):
#             if isinstance(tool, dict):
#                 return tool
#             elif isinstance(tool, Tool):
#                 return tool.schema_
#             elif isinstance(tool, str):
#                 if branch.tool_manager.name_existed(tool):
#                     tool = branch.tool_manager.registry[tool]
#                     return tool.schema_
#                 else:
#                     raise ValueError(f'Function {tool} is not registered.')

#         if isinstance(tools, bool):
#             tool_kwarg = {"tools": branch.tool_manager.to_tool_schema_list()}
#             kwargs = {**tool_kwarg, **kwargs}

#         else:
#             if not isinstance(tools, list):
#                 tools = [tools]
#             tool_kwarg = {"tools": lcall(tools, tool_check)}
#             kwargs = {**tool_kwarg, **kwargs}

#         return kwargs

#     def _to_chatcompletion_message(self):
#         """
#         Convert the conversation branch to a list of messages for chat completion.

#         Returns:
#             A list of dictionaries with 'name' or 'role' and 'content' from the conversation messages.
#         """
#         message = []
#         for _, row in self.messages.iterrows():
#             out = {"role": row['role'], "content": row['content']}
#             message.append(out)
#         return message

#     def _tool_invoked(self):
#         """Checks if the latest message in the current branch has invoked a tool.

#         Returns:
#             bool: True if a tool has been invoked, False otherwise.
#         """
#         content = self.messages.iloc[-1]['content']
#         try:
#             if json.loads(content)['action_response'].keys() >= {
#                 'function', 'arguments', 'output'
#                 }:
#                 return True
#         except:
#             return False

#     def _handle_messages(
#         self,
#         instruction: Union[Instruction, str],
#         system: Optional[str] = None,
#         context: Optional[Any] = None,
#         name: Optional[str] = None,
#     ):
#         if system:
#             self.change_system_message(System(system))
#         if isinstance(instruction, Instruction):
#             self.add_message(instruction)
#         else:
#             instruct = Instruction(instruction, context, name)
#             self.add_message(instruct)

#     def _get_tools_kwargs(self, tools, **kwargs):
#         if self.tool_manager.registry != {}:
#             if tools:
#                 kwargs = self._tool_parser(tools, **kwargs)
#                 return kwargs
# '''



# # ----- to modify ------
# import json
# from typing import Any, Dict, List, Optional, Union, Callable
# import pandas as pd
# from .branch import Branch
# from ..messages.messages import Message
# from ..instruction_set.instruction_set import InstructionSet

# class Cluster:
#     """
#     Manages a collection of Branch instances for a unified workflow.

#     Each Branch within the Cluster can have different messages and tools but follows
#     the same workflow steps. Branches can exchange information with the main branch.

#     Args:
#         main_branch: The name of the main branch in the cluster.
#         branches: An optional dictionary of branches within the cluster, with the main branch included.

#     Raises:
#         ValueError: If the main branch is not included in the provided branches.

#     Attributes:
#         branches: A dictionary of branches within the cluster.
#         main_branch: The name of the main branch in the cluster.

#     Examples:
#         >>> main_branch = "main"
#         >>> branches = {"main": Branch(init_message=Message(role="user", content="Hello"))}
#         >>> cluster = Cluster(main_branch=main_branch, branches=branches)
#         >>> cluster.add_branch("secondary", Branch(init_message=Message(role="user", content="Hi")))
#     """

#     def __init__(self, main_branch: str, branches: Optional[Dict[str, Branch]] = None) -> None:
#         if branches is None:
#             branches = {}
#         if main_branch not in branches:
#             raise ValueError(f"Main branch '{main_branch}' must be included in the branches.")
#         self.branches: Dict[str, Branch] = branches
#         self.main_branch: str = main_branch

#     def add_branch(self, name: str, branch: Branch) -> None:
#         """
#         Add a new branch to the cluster.

#         Args:
#             name: The name of the new branch.
#             branch: The Branch instance to add to the cluster.

#         Raises:
#             ValueError: If a branch with the same name already exists.
#         """
#         if name in self.branches:
#             raise ValueError(f"Branch with name '{name}' already exists in the cluster.")
#         self.branches[name] = branch

#     def remove_branch(self, name: str) -> None:
#         """
#         Remove a branch from the cluster.

#         Args:
#             name: The name of the branch to remove.

#         Raises:
#             ValueError: If the branch with the specified name does not exist.
#         """
#         if name not in self.branches:
#             raise ValueError(f"Branch with name '{name}' does not exist in the cluster.")
#         del self.branches[name]

#     def broadcast_message(self, message: Message) -> None:
#         """
#         Broadcast a message to all branches within the cluster.

#         Args:
#             message: A Message instance to broadcast to all branches.
#         """
#         for branch in self.branches.values():
#             branch.add_message(message)

#     def synchronize_tools(self) -> None:
#         """
#         Synchronize tools across all branches to match the main branch's tools.
#         """
#         main_tools = self.branches[self.main_branch].tool_manager.registry
#         for branch in self.branches.values():
#             if branch is not self.branches[self.main_branch]:
#                 branch.tool_manager.registry = main_tools.copy()

#     def report_to_main(self, name: str) -> None:
#         """
#         Report a branch's state to the main branch.

#         Args:
#             name: The name of the branch to report to the main branch.

#         Raises:
#             ValueError: If the specified branches do not exist.
#         """
#         if name not in self.branches or self.main_branch not in self.branches:
#             raise ValueError("Specified branches do not exist.")
#         main_branch = self.branches[self.main_branch]
#         reporting_branch = self.branches[name]
#         main_branch.merge(reporting_branch.report())

#     def update_from_main(self, name: str) -> None:
#         """
#         Update a branch's state from the main branch.

#         Args:
#             name: The name of the branch to update from the main branch.

#         Raises:
#             ValueError: If the specified branches do not exist.
#         """
#         if name not in self.branches or self.main_branch not in self.branches:
#             raise ValueError("Specified branches do not exist.")
#         main_branch = self.branches[self.main_branch]
#         updating_branch = self.branches[name]
#         updating_branch.merge(main_branch.report())

#     def save_to_file(self, filename: str) -> None:
#         """
#         Save the state of the cluster to a file.

#         Args:
#             filename: The filename for saving the cluster state.

#         Raises:
#             IOError: If an error occurs while saving the file.
#         """
#         cluster_state = {
#             "main_branch": self.main_branch,
#             "branches": {name: branch.report() for name, branch in self.branches.items()}
#         }
#         try:
#             with open(f"{filename}.json", "w") as file:
#                 json.dump(cluster_state, file, indent=4)
#         except IOError as e:
#             raise IOError(f"An error occurred while saving to '{filename}.json': {e}")

#     def find_branch_by_message_content(self, content: str) -> List[str]:
#         """
#         Find branches that contain a specific message content.

#         Args:
#             content: The message content to search for within branches.

#         Returns:
#             List[str]: A list of branch names that contain the specified message content.
#         """
#         return [
#             name for name, branch in self.branches.items()
#             if any(content in message.content for message in branch.messages)
#         ]

#     def execute_instruction_set(self, instruction_set: InstructionSet) -> None:
#         """
#         Execute an instruction set across all branches.

#         Args:
#             instruction_set: An InstructionSet instance to execute across all branches.
#         """
#         for branch in self.branches.values():
#             branch.add_instruction_set(instruction_set.name, instruction_set)

#     def consolidate_reports(self) -> Dict[str, Any]:
#         """
#         Consolidate reports from all branches into a single dictionary.

#         Returns:
#             Dict[str, Any]: A dictionary with consolidated reports from all branches.
#         """
#         return {name: branch.report() for name, branch in self.branches.items()}

#     def get_messages(self) -> pd.DataFrame:
#         """
#         Get a concatenated DataFrame of messages from all branches.

#         Returns:
#             pd.DataFrame: A DataFrame containing all messages from all branches.
#         """
#         return pd.concat([branch.messages for branch in self.branches.values()], ignore_index=True)

#     def aggregate_data(self, criterion: Callable[[Message], bool]) -> pd.DataFrame:
#         """
#         Aggregate data across all branches based on a given criterion.

#         Args:
#             criterion: A function that defines the criterion for aggregation.

#         Returns:
#             pd.DataFrame: A DataFrame with aggregated data.

#         Example:
#             >>> criterion = lambda message: message.role == 'user'
#             >>> aggregated_data = cluster.aggregate_data(criterion)
#         """
#         aggregated_data = pd.DataFrame()
#         for branch in self.branches.values():
#             filtered_data = branch.messages[branch.messages.apply(criterion, axis=1)]
#             aggregated_data = pd.concat([aggregated_data, filtered_data], ignore_index=True)
#         return aggregated_data

#     def apply_function_to_branches(self, func: Callable[[Branch], Any]) -> Dict[str, Any]:
#         """
#         Apply a custom function to each branch in the cluster.

#         Args:
#             func: A function to apply to each branch.

#         Returns:
#             Dict[str, Any]: A dictionary with branch names as keys and the function's return values as values.

#         Example:
#             >>> def custom_func(branch):
#             ...     return len(branch.messages)
#             >>> branch_lengths = cluster.apply_function_to_branches(custom_func)
#         """
#         return {name: func(branch) for name, branch in self.branches.items()}

#     def get_branch_statistics(self) -> Dict[str, Dict[str, Any]]:
#         """
#         Get statistical information about each branch in the cluster.

#         Returns:
#             Dict[str, Dict[str, Any]]: A dictionary with branch names as keys and statistical info as values.

#         Example:
#             >>> stats = cluster.get_branch_statistics()
#         """
#         stats = {}
#         for name, branch in self.branches.items():
#             stats[name] = {
#                 "total_messages": len(branch.messages),
#                 "unique_tools": len(branch.tool_manager.registry),
#                 "instruction_sets": len(branch.instruction_sets)
#             }
#         return stats

#     def create_branch_snapshot(self, branch_name: str) -> Dict[str, Any]:
#         """
#         Create a snapshot of a specific branch's current state.

#         Args:
#             branch_name: The name of the branch to snapshot.

#         Returns:
#             Dict[str, Any]: A snapshot of the branch's state.

#         Raises:
#             ValueError: If the branch does not exist.

#         Example:
#             >>> snapshot = cluster.create_branch_snapshot("main")
#         """
#         if branch_name not in self.branches:
#             raise ValueError(f"Branch with name '{branch_name}' does not exist.")
#         branch = self.branches[branch_name]
#         return {
#             "messages": branch.messages.to_dict(),
#             "tools": branch.tool_manager.registry,
#             "instruction_sets": branch.instruction_sets
#         }
    
    
# ### -------------- assistant's complete professional codes ----------------