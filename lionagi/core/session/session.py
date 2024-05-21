"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from lionagi.core.collections.abc import Component
from lionagi.core.collections import (
    Pile,
    Progression,
    Flow,
    progression,
    pile,
    flow,
    iModel,
)
from lionagi.core.message import System
from lionagi.libs.ln_api import BaseService
from typing import Any, Tuple
from lionagi.core.action.tool import Tool, TOOL_TYPE
from lionagi.core.action.tool_manager import ToolManager

from lionagi.libs import SysUtil
from lionagi.core.session.branch import Branch
from lionagi.core.collections import (
    pile,
    Pile,
    Exchange
)
from lionagi.core.collections.abc import get_lion_id
from lionagi.core.collections.util import to_list_type
from lionagi.core.mail.mail_manager import MailManager
from lionagi.core.message.util import create_message

class Session:

    def __init__(
        self,
        system: str | System | None = None,  # the default system message for the session
        branches: Any | None = None,
        system_sender: str | None = None,
        user: str | None = None,
        imodel=None,
    ):
        self.ln_id = SysUtil.create_id()
        self.timestamp = SysUtil.get_timestamp(sep=None)[:-6]
        system = system or "You are a helpful assistant, let's think step by step"
        self.system = System(system=system, sender=system_sender)
        self.system_sender = system_sender
        self.branches = self._validate_branches(branches)
        self.mail_transfer = Exchange()
        self.mail_manager = MailManager([self.mail_transfer])
        self.imodel = imodel or iModel()
        self.user = user
        self.default_branch = None
        if self.branches.size() == 0:
            self.new_branch(system=self.system.copy())
        else:
            self.default_branch = self.branches[0]

    def _validate_branches(self, value):
        if isinstance(value, Pile):
            for branch in value.values():
                if not isinstance(branch, Branch):
                    raise ValueError("The branches pile contains non-Branch object")
            return value
        else:
            try:
                value = pile(items=value, item_type=Branch)
                return value
            except Exception as e:
                raise ValueError(f"Invalid branches value. Error:{e}")

    # ---- branch manipulation ---- #
    def new_branch(self,
                   system: System | None = None,
                   system_sender: str | None = None,
                   user: str | None = None,
                   messages: Pile = None,
                   progress: Progression = None,
                   tool_manager: ToolManager = None,
                   tools: Any = None,
                   imodel=None,
                   ):
        if system is None:
            system = self.system.copy()
            system.sender = self.ln_id
            system_sender = self.ln_id
        branch = Branch(system=system,
                        system_sender=system_sender,
                        user=user,
                        messages=messages,
                        progress=progress,
                        tool_manager=tool_manager,
                        tools=tools,
                        imodel=imodel or self.imodel)
        self.branches.append(branch)
        self.mail_manager.add_sources(branch)
        if self.default_branch is None:
            self.default_branch = branch
        return branch

    def delete_branch(self, branch):
        branch_id = get_lion_id(branch)
        self.branches.pop(branch_id)
        self.mail_manager.delete_source(branch_id)

        if self.default_branch == branch:
            if self.branches.size() == 0:
                self.default_branch = None
            else:
                self.default_branch = self.branches[0]

    def split_branch(self, branch):
        branch = self.branches[branch]
        system = branch.system.copy() if branch.system else None
        if system:
            system.sender = branch.ln_id
        progress = progression()
        messages = pile()

        for id_ in branch.progress:
            copy_message = branch.messages[id_].copy()
            progress.append(copy_message.ln_id)
            messages.append(copy_message)

        tools = list(branch.tool_manager.registry.values()) if branch.tool_manager.registry else None
        branch_copy = Branch(system=system,
                             system_sender=branch.ln_id,
                             user=branch.user,
                             progress=progress,
                             messages=messages,
                             tools=tools)
        for message in branch_copy.messages:
            message.sender = branch.ln_id
            message.recipient = branch_copy.ln_id
        self.branches.append(branch_copy)
        self.mail_manager.add_sources(branch_copy)
        return branch_copy

    def change_default_branch(self, branch):
        branch = self.branches[branch]
        self.default_branch = branch

    def collect(self,  from_: Branch | str | Pile[Branch] | None = None):
        if from_ is None:
            self.mail_manager.collect_all()
        else:
            try:
                sources = to_list_type(from_)
                for source in sources:
                    self.mail_manager.collect(get_lion_id(source))
            except Exception as e:
                raise ValueError(f"Failed to collect mail. Error: {e}")

    def send(self, to_: Branch | str | Pile[Branch] | None = None):
        if to_ is None:
            self.mail_manager.send_all()
        else:
            try:
                sources = to_list_type(to_)
                for source in sources:
                    self.mail_manager.send(get_lion_id(source))
            except Exception as e:
                raise ValueError(f"Failed to send mail. Error: {e}")

    def collect_send_all(self, receive_all=False):
        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches:
                branch.receive_all()









#
#
#
# class Session:
#
#     def __init__(
#         self,
#         system: dict | list | System | None = None,
#         sender: str | None = None,
#         llmconfig: dict[str, str | int | dict] | None = None,
#         service: BaseService | None = None,
#         branches: dict[str, Branch] | None = None,
#         default_branch: Branch | None = None,
#         default_branch_name: str | None = None,
#         tools: TOOL_TYPE | None = None,
#         # instruction_sets: Optional[List[Instruction]] = None,
#         tool_manager: ToolManager | None = None,
#         messages: dataframe.ln_DataFrame | None = None,
#         datalogger: None | DataLogger = None,
#         persist_path: Path | str | None = None,
#     ):
#         self.branches = branches if isinstance(branches, dict) else {}
#         self.service = service
#         self.setup_default_branch(
#             system=system,
#             sender=sender,
#             default_branch=default_branch,
#             default_branch_name=default_branch_name,
#             messages=messages,
#             # instruction_sets=instruction_sets,
#             tool_manager=tool_manager,
#             service=service,
#             llmconfig=llmconfig,
#             tools=tools,
#             persist_path=persist_path,
#             datalogger=datalogger,
#         )
#         self.mail_manager = MailManager(self.branches)
#         self.datalogger = self.default_branch.datalogger
#         for key, branch in self.branches.items():
#             branch.name = key
#
#     # ---- branch manipulation ---- #
#     def new_branch(
#         self,
#         branch_name: str,
#         system: dict | list | System | None = None,
#         sender: str | None = None,
#         messages: dataframe.ln_DataFrame | None = None,
#         tool_manager=None,
#         service=None,
#         llmconfig=None,
#         tools: TOOL_TYPE = False,
#     ) -> None:
#         """Create a new branch with the specified configurations.
#
#         Args:
#                 branch_name (str | None): Name of the new branch.
#                 system (Optional[Union[System, str]]): System or context identifier for the new branch.
#                 sender (str | None): Default sender identifier for the new branch.
#                 messages (Optional[dataframe.ln_DataFrame]): Initial set of messages for the new branch.
#                 instruction_sets (Optional[Any]): Instruction sets for the new branch.
#                 tool_manager (Optional[Any]): Tool manager for handling tools in the new branch.
#                 service (BaseService]): External service instance for the ne | None branch.
#                 llmconfig (dict[str, Any] | None): Configuration for language learning models in the new branch.
#                 tools (TOOL_TYPE | None): List of tools available for the new branch.
#
#         Raises:
#                 ValueError: If the branch name already exists.
#
#         Examples:
#                 >>> session.new_branch("new_branch_name")
#         """
#         if branch_name in self.branches.keys():
#             raise ValueError(
#                 f"Invalid new branch name {branch_name}. Branch already existed."
#             )
#         if isinstance(tools, Tool):
#             tools = [tools]
#         new_branch = Branch(
#             name=branch_name,
#             messages=messages,
#             tool_manager=tool_manager,
#             service=service,
#             llmconfig=llmconfig,
#             tools=tools,
#         )
#         if system:
#             new_branch.add_message(system=system, sender=sender)
#
#         self.branches[branch_name] = new_branch
#         self.mail_manager.sources[branch_name] = new_branch
#         self.mail_manager.mails[branch_name] = {}
#
#     def get_branch(
#         self, branch: Branch | str | None = None, get_name: bool = False
#     ) -> Branch | Tuple[Branch, str]:
#         """
#         Retrieve a branch by name or instance.
#
#         Args:
#                 branch (Optional[Branch | str]): The branch name or instance to retrieve.
#                 get_name (bool): If True, returns a tuple of the branch instance and its name.
#
#         Returns:
#                 Union[Branch, Tuple[Branch, str]]: The branch instance or a tuple of the branch instance and its name.
#
#         Raises:
#                 ValueError: If the branch name does not exist or the branch input is invalid.
#
#         Examples:
#                 >>> branch_instance = session.get_branch("existing_branch_name")
#                 >>> branch_instance, branch_name = session.get_branch("existing_branch_name", get_name=True)
#         """
#         if isinstance(branch, str):
#             if branch not in self.branches.keys():
#                 raise ValueError(f"Invalid branch name {branch}. Not exist.")
#             return (
#                 (self.branches[branch], branch) if get_name else self.branches[branch]
#             )
#         elif isinstance(branch, Branch) and branch in self.branches.values():
#             return (branch, branch.name) if get_name else branch
#         elif branch is None:
#             if get_name:
#                 return self.default_branch, self.default_branch_name
#             return self.default_branch
#
#         else:
#             raise ValueError(f"Invalid branch input {branch}.")
#
#     def change_default_branch(self, branch: str | Branch) -> None:
#         """Change the default branch of the session.
#
#         Args:
#                 branch (str | Branch): The branch name or instance to set as the new default.
#
#         Examples:
#                 >>> session.change_default_branch("new_default_branch")
#         """
#         branch_, name_ = self.get_branch(branch, get_name=True)
#         self.default_branch = branch_
#         self.default_branch_name = name_
#
#     def delete_branch(self, branch: Branch | str, verbose: bool = True) -> bool:
#         """Delete a branch from the session.
#
#         Args:
#                 branch (Branch | str): The branch name or instance to delete.
#                 verbose (bool): If True, prints a message upon deletion.
#
#         Returns:
#                 bool: True if the branch was successfully deleted.
#
#         Raises:
#                 ValueError: If attempting to delete the current default branch.
#
#         Examples:
#                 >>> session.delete_branch("branch_to_delete")
#         """
#         _, branch_name = self.get_branch(branch, get_name=True)
#
#         if branch_name == self.default_branch_name:
#             raise ValueError(
#                 f"{branch_name} is the current default branch, please switch to another branch before delete it."
#             )
#         self.branches.pop(branch_name)
#         # self.mail_manager.sources.pop(branch_name)
#         self.mail_manager.mails.pop(branch_name)
#         if verbose:
#             print(f"Branch {branch_name} is deleted.")
#         return True
#
#     def merge_branch(
#         self,
#         from_: str | Branch,
#         to_branch: str | Branch,
#         update: bool = True,
#         del_: bool = False,
#     ) -> None:
#         """Merge messages and settings from one branch to another.
#
#         Args:
#                 from_ (str | Branch): The source branch name or instance.
#                 to_branch (str | Branch): The target branch name or instance where the merge will happen.
#                 update (bool): If True, updates the target branch with the source branch's settings.
#                 del_ (bool): If True, deletes the source branch after merging.
#
#         Examples:
#                 >>> session.merge_branch("source_branch", "target_branch", del_=True)
#         """
#         from_ = self.get_branch(branch=from_)
#         to_branch, to_name = self.get_branch(branch=to_branch, get_name=True)
#         to_branch.merge_branch(from_, update=update)
#
#         if del_:
#             if from_ == self.default_branch:
#                 self.default_branch_name = to_name
#                 self.default_branch = to_branch
#             self.delete_branch(from_, verbose=False)
#
#     def take_branch(self, branch):
#         self.branches[branch.branch_name] = branch
#         self.mail_manager.sources[branch.id_] = branch
#         self.mail_manager.mails[branch.id_] = {}
#
#     def collect(self, from_: str | Branch | list[str | Branch] | None = None):
#         """
#         Collects requests from specified branches or from all branches if none are specified.
#
#         This method is intended to aggregate data or requests from one or more branches for processing or analysis.
#
#         Args:
#                 from_ (Optional[Union[str, Branch, List[str | Branch]]]): The branch(es) from which to collect requests.
#                         Can be a single branch name, a single branch instance, a list of branch names, a list of branch instances, or None.
#                         If None, requests are collected from all branches.
#
#         Examples:
#                 >>> session.collect("branch_name")
#                 >>> session.collect([branch_instance_1, "branch_name_2"])
#                 >>> session.collect()  # Collects from all branches
#         """
#         if from_ is None:
#             for branch in self.branches.values():
#                 self.mail_manager.collect(branch.id_)
#         else:
#             if not isinstance(from_, list):
#                 from_ = [from_]
#             for branch in from_:
#                 if isinstance(branch, str):
#                     branch = self.branches[branch]
#                     self.mail_manager.collect(branch.id_)
#                 elif isinstance(branch, Branch):
#                     self.mail_manager.collect(branch.id_)
#
#     def send(self, to_: str | Branch | list[str | Branch] | None = None):
#         """
#         Sends requests or data to specified branches or to all branches if none are specified.
#
#         This method facilitates the distribution of data or requests to one or more branches, potentially for further tool or processing.
#
#         Args:
#                 to_ (Optional[Union[str, Branch, List[str | Branch]]]): The target branch(es) to which to send requests.
#                         Can be a single branch name, a single branch instance, a list of branch names, a list of branch instances, or None.
#                         If None, requests are sent to all branches.
#
#         Examples:
#                 >>> session.send("target_branch")
#                 >>> session.send([branch_instance_1, "target_branch_2"])
#                 >>> session.send()  # Sends to all branches
#         """
#         if to_ is None:
#             for branch in self.branches.values():
#                 self.mail_manager.send(branch.id_)
#         else:
#             if not isinstance(to_, list):
#                 to_ = [to_]
#             for branch in to_:
#                 if isinstance(branch, str):
#                     branch = self.branches[branch]
#                     self.mail_manager.send(branch.id_)
#                 if isinstance(branch, Branch):
#                     self.mail_manager.send(branch.id_)
#
#     def collect_send_all(self, receive_all=False):
#         """
#         Collects and sends requests across all branches, optionally invoking a receive operation on each branch.
#
#         This method is a convenience function for performing a full cycle of collect and send operations across all branches,
#         useful in scenarios where data or requests need to be aggregated and then distributed uniformly.
#
#         Args:
#                 receive_all (bool): If True, triggers a `receive_all` method on each branch after sending requests,
#                         which can be used to process or acknowledge the received data.
#
#         Examples:
#                 >>> session.collect_send_all()
#                 >>> session.collect_send_all(receive_all=True)
#         """
#         self.collect()
#         self.send()
#         if receive_all:
#             for branch in self.branches.values():
#                 branch.receive_all()
#
#     def setup_default_branch(self, **kwargs):
#         self._setup_default_branch(**kwargs)
#         self._verify_default_branch()
#
#     def _verify_default_branch(self):
#         if self.branches:
#             if self.default_branch_name not in self.branches.keys():
#                 raise ValueError("default branch name is not in imported branches")
#             if self.default_branch is not self.branches[self.default_branch_name]:
#                 raise ValueError(
#                     f"default branch does not match Branch object under {self.default_branch_name}"
#                 )
#
#         if not self.branches:
#             self.branches[self.default_branch_name] = self.default_branch
#
#     def _setup_default_branch(
#         self,
#         system,
#         sender,
#         default_branch,
#         default_branch_name,
#         messages,  # instruction_sets,
#         tool_manager,
#         service,
#         llmconfig,
#         tools,
#         persist_path,
#         datalogger,
#     ):
#
#         branch = default_branch or Branch(
#             name=default_branch_name,
#             service=service,
#             llmconfig=llmconfig,
#             tools=tools,
#             tool_manager=tool_manager,
#             # instruction_sets=instruction_sets,
#             messages=messages,
#             persist_path=persist_path,
#             datalogger=datalogger,
#         )
#
#         self.default_branch = branch
#         self.default_branch_name = default_branch_name or "main"
#         if system:
#             self.default_branch.add_message(system=system, sender=sender)
#
#         self.llmconfig = self.default_branch.llmconfig
