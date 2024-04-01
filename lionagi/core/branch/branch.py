# """
# This module contains the Branch class, which represents a branch in a conversation tree.
# """

# from collections import deque
# from typing import Any, TypeVar, Callable

# from lionagi.libs.sys_util import PATH_TYPE
# from lionagi.libs import StatusTracker, BaseService, convert, dataframe

# from ..schema import TOOL_TYPE, Tool, DataLogger
# from ..tool import ToolManager, func_to_tool

# from lionagi.core.branch.base.base_branch import BaseBranch
# from lionagi.core.messages.system import System
# from lionagi.core.mail.schema import BaseMail

# from lionagi.core.branch.base.util import MessageUtil

# from .util import MessageUtil
# from .base_branch import BaseBranch
# from .branch_flow_mixin import BranchFlowMixin

# from dotenv import load_dotenv

# load_dotenv()

# T = TypeVar("T", bound=Tool)


# class Branch(BaseBranch, BranchFlowMixin):
#     """
#     Represents a conversational branch, encapsulating messaging, tools, and service integration.

#     A Branch is a key component in managing conversational flows, tools, and external services
#     within a conversational AI framework. It extends the BaseBranch with additional functionalities
#     such as tool management, service interactions, and the ability to send and receive packaged data
#     (mails) between branches or external services.

#     Attributes:
#         branch_name (str | None): Optional name for the branch.
#         system (dict | list | System | None): System configuration or predefined system messages.
#         messages (dataframe.ln_DataFrame | None): Dataframe containing the messages within the branch.
#         service (BaseService | None): The service associated with this branch for external API calls.
#         sender (str | None): Default identifier for the sender of messages from this branch.
#         llmconfig (dict[str, str | int | dict] | None): Configuration details for language model interactions.
#         tools (list[Callable | Tool] | None): List of tools or callable functions registered to the branch.
#         datalogger (DataLogger | None): Logger for tracking branch operations and data flows.
#         persist_path (PATH_TYPE | None): Filesystem path for persisting branch data, if necessary.
#         tool_manager (ToolManager | None): Manages the registration and invocation of tools within the branch.
#         status_tracker (StatusTracker): Tracks the status of various operations within the branch.
#         pending_ins (dict): A dictionary holding pending incoming mails, categorized by sender.
#         pending_outs (deque): A queue of pending outgoing mails to be processed or sent.

#     The Branch class facilitates the creation of complex conversational flows, tool integrations,
#     and interactions with external services, providing a robust framework for developing advanced
#     conversational AI applications.

#     Example:
#         >>> branch = Branch(name="CustomerSupport", service=my_service, llmconfig=my_llm_config)
#         >>> branch.register_tools([my_tool])
#         >>> branch.send(recipient="other_branch", category="tools", package=my_tool)
#     """

#     def __init__(
#         self,
#         name: str | None = None,
#         system: dict | list | System | None = None,
#         messages: dataframe.ln_DataFrame | None = None,
#         service: BaseService | None = None,
#         sender: str | None = None,
#         llmconfig: dict[str, str | int | dict] | None = None,
#         tools: list[Callable | Tool] | None = None,
#         datalogger: None | DataLogger = None,
#         persist_path: PATH_TYPE | None = None,  # instruction_sets=None,
#         tool_manager: ToolManager | None = None,
#         **kwargs,
#     ):
#         """
#         Initializes a new Branch instance with various configurations.

#         Args:
#             name (str | None): Optional name for the branch.
#             system (dict | list | System | None): System configuration or messages.
#             messages (dataframe.ln_DataFrame | None): Initial messages for the branch.
#             service (BaseService | None): The service associated with this branch.
#             sender (str | None): Default sender for messages from this branch.
#             llmconfig (dict[str, str | int | dict] | None): LLM configuration.
#             tools (list[Callable | Tool] | None): List of tools or functions to be registered.
#             datalogger (DataLogger | None): Optional data logger for branch operations.
#             persist_path (PATH_TYPE | None): File system path for data persistence.
#             tool_manager (ToolManager | None): Tool manager for handling tools.
#             **kwargs: Additional keyword arguments.
#         """

#         super().__init__(
#             messages=messages,
#             datalogger=datalogger,
#             persist_path=persist_path,
#             name=name,
#             **kwargs,
#         )

#         # add branch name
#         self.name = name
#         self.sender = sender or "system"
#         self.tool_manager = tool_manager or ToolManager()

#         if tools:
#             try:
#                 tools_ = []
#                 _tools = convert.to_list(tools)
#                 for i in _tools:
#                     if isinstance(i, Tool):
#                         tools_.append(i)
#                     else:
#                         tools_.append(func_to_tool(i))

#                 self.register_tools(tools_)
#             except Exception as e:
#                 raise TypeError(f"Error in registering tools: {e}") from e

#         self.service, self.llmconfig = self._add_service(service, llmconfig)
#         self.status_tracker = StatusTracker()

#         # add instruction sets
#         # self.instruction_sets = instruction_sets

#         self.pending_ins = {}
#         self.pending_outs = deque()

#     @property
#     def has_tools(self) -> bool:
#         """
#         Checks if the branch has any tools registered.

#         Returns:
#             bool: True if there are tools registered, False otherwise.
#         """
#         return self.tool_manager.registry != {}

#     # todo: also update other attributes
#     def merge_branch(self, branch: "Branch", update: bool = True) -> None:
#         """
#         Merges another branch into this one, including messages and tools.

#         Args:
#             branch (Branch): The branch to merge into this one.
#             update (bool): If True, updates the tool registry and other attributes. Defaults to True.
#         """

#         Args:
#             branch (Branch): The branch to merge.
#             update (bool): Whether to update the existing attributes or add new ones (default: True).
#         """
#         message_copy = branch.messages.copy()
#         self.messages = self.messages.merge(message_copy, how="outer")
#         self.datalogger.extend(branch.datalogger.log)

#         if update:
#             # self.instruction_sets.update(branch.instruction_sets)
#             self.tool_manager.registry.update(branch.tool_manager.registry)
#         else:
#             for key, value in branch.instruction_sets.items():
#                 if key not in self.instruction_sets:
#                     self.instruction_sets[key] = value

#             for key, value in branch.tool_manager.registry.items():
#                 if key not in self.tool_manager.registry:
#                     self.tool_manager.registry[key] = value

#     # ----- tool manager methods ----- #
#     def register_tools(
#         self, tools: Union[Tool, list[Tool | Callable], Callable]
#     ) -> None:
#         """
#         Registers tools in the branch's tool manager.

#         Args:
#             tools (Union[Tool, list[Tool]]): The tool(s) to register.
#         """
#         if not isinstance(tools, list):
#             tools = [tools]
#         self.tool_manager.register_tools(tools=tools)

#     def delete_tools(
#         self,
#         tools: TOOL_TYPE,
#         verbose: bool = True,
#     ) -> bool:
#         """
#         Deletes tools from the branch's tool manager.

#         Args:
#             tools (Union[T, list[T], str, list[str]]): The tool(s) to delete.
#             verbose (bool): Whether to print success/failure messages (default: True).

#         Returns:
#             bool: True if the tools were successfully deleted, False otherwise.
#         """
#         if not isinstance(tools, list):
#             tools = [tools]
#         if convert.is_same_dtype(tools, str):
#             for act_ in tools:
#                 if act_ in self.tool_manager.registry:
#                     self.tool_manager.registry.pop(act_)
#             if verbose:
#                 print("tools successfully deleted")
#             return True
#         elif convert.is_same_dtype(tools, Tool):
#             for act_ in tools:
#                 if act_.schema_["function"]["name"] in self.tool_manager.registry:
#                     self.tool_manager.registry.pop(act_.schema_["function"]["name"])
#             if verbose:
#                 print("tools successfully deleted")
#             return True
#         if verbose:
#             print("tools deletion failed")
#         return False

#     def send(self, recipient: str, category: str, package: Any) -> None:
#         """
#         Sends a mail to a recipient.

#         Args:
#             recipient (str): The recipient of the mail.
#             category (str): The category of the mail.
#             package (Any): The package to send in the mail.
#         """
#         mail_ = BaseMail(
#             sender=self.sender, recipient=recipient, category=category, package=package
#         )
#         self.pending_outs.append(mail_)

#     def receive(
#         self,
#         sender: str,
#         messages: bool = True,
#         tools: bool = True,
#         service: bool = True,
#         llmconfig: bool = True,
#     ) -> None:
#         """
#         Receives mails from a sender and updates the branch accordingly.

#         Args:
#             sender (str): The sender of the mails.
#             messages (bool): Whether to receive message updates (default: True).
#             tools (bool): Whether to receive tool updates (default: True).
#             service (bool): Whether to receive service updates (default: True).
#             llmconfig (bool): Whether to receive language model configuration updates (default: True).

#         Raises:
#             ValueError: If there are no packages from the specified sender.
#                         If the messages format is invalid.
#                         If the tools format is invalid.
#                         If the provider format is invalid.
#                         If the llmconfig format is invalid.
#         """
#         skipped_requests = deque()
#         if sender not in self.pending_ins:
#             raise ValueError(f"No package from {sender}")
#         while self.pending_ins[sender]:
#             mail_ = self.pending_ins[sender].popleft()

#             if mail_.category == "messages" and messages:
#                 if not isinstance(mail_.package, dataframe.ln_DataFrame):
#                     raise ValueError("Invalid messages format")
#                 MessageUtil.validate_messages(mail_.package)
#                 self.messages = self.messages.merge(mail_.package, how="outer")

#             elif mail_.category == "tools" and tools:
#                 if not isinstance(mail_.package, Tool):
#                     raise ValueError("Invalid tools format")
#                 self.tool_manager.register_tools([mail_.package])

#             elif mail_.category == "provider" and service:
#                 from lionagi.libs.ln_api import BaseService

#                 if not isinstance(mail_.package, BaseService):
#                     raise ValueError("Invalid provider format")
#                 self.service = mail_.package

#             elif mail_.category == "llmconfig" and llmconfig:
#                 if not isinstance(mail_.package, dict):
#                     raise ValueError("Invalid llmconfig format")
#                 self.llmconfig.update(mail_.package)

#             else:
#                 skipped_requests.append(mail_)

#         self.pending_ins[sender] = skipped_requests
#         if self.pending_ins[sender] == deque():
#             self.pending_ins.pop(sender)

#     def receive_all(self) -> None:
#         """
#         Receives all pending mails and updates the branch accordingly.
#         """
#         for key in list(self.pending_ins.keys()):
#             self.receive(key)

#     @staticmethod
#     def _add_service(service, llmconfig):
#         """
#         Initializes the service and LLM configuration for the branch.

#         This static method provides a way to set up the service and LLM configuration
#         based on provided parameters or defaults to a suitable service and configuration.

#         Args:
#             service (BaseService | None): The service to be used by the branch.
#             llmconfig (dict | None): The LLM configuration for the branch.

#         Returns:
#             tuple: A tuple containing the initialized service and LLM configuration.

#         Raises:
#             ValueError: If no suitable service is available or specified.

#         Examples:
#             >>> service, llmconfig = Branch._add_service(None, None)
#         """
#         from lionagi.integrations.provider.oai import OpenAIService

#         if service is None:
#             try:
#                 from lionagi.integrations.provider import Services

#                 service = Services.OpenAI()

#             except:
#                 raise ValueError("No available service")
#         if llmconfig is None:
#             if isinstance(service, OpenAIService):
#                 from lionagi.integrations.config import oai_schema

#                 llmconfig = oai_schema["chat/completions"]["config"]
#             else:
#                 llmconfig = {}
#         return service, llmconfig

#     def _is_invoked(self) -> bool:
#         """
#         Checks if the conversation has been invoked with an action response.

#         This method determines whether the latest message in the conversation
#         includes an action response, indicating that a specific action or command
#         has been invoked.

#         Returns:
#                 bool: True if the conversation has been invoked, False otherwise.

#         """
#         content = self.messages.iloc[-1]["content"]
#         try:
#             if convert.to_dict(content)["action_response"].keys() >= {
#                 "function",
#                 "arguments",
#                 "output",
#             }:
#                 return True
#         except Exception:
#             return False
