# import collections
# from typing import Any, Dict, List, Optional, Union, TypeVar, Tuple
# import pandas as pd
#
# from lionagi.util import SysUtil, to_list, to_df
# from lionagi.provider import BaseService
# from lionagi.mail import MailManager
# from lionagi.message import System
# from lionagi.branch import Branch
#
# T = TypeVar('T', Branch, str)
#
#
# class BaseSession:
#     def __init__(
#             self,
#             system: Optional[Union[str, System]] = None,
#             sender: Optional[str] = None,
#             service: Optional[BaseService] = None,
#             logger: Optional[Any] = None,
#             directory: Optional[str] = None,
#             branches: Optional[Dict[str, Branch]] = None,
#             default_branch_name: Optional[str] = 'main'
#     ):
#         self.system = system
#         self.sender = sender
#         self.service = service
#         self.logger = logger(directory=directory) if logger else None
#         self.directory = directory
#         self.branches = branches if branches else {}
#         self.default_branch_name = default_branch_name
#         self.default_branch = self.branches.get(default_branch_name, Branch())
#
#         # Initialize mail manager for branch communication
#         self.mail_manager = MailManager(self.branches)
#
#     @property
#     def messages(self):
#         # Implementation to return messages from the default branch
#         return self.default_branch.messages if self.default_branch else pd.DataFrame()
#
#     def get_branch(
#             self,
#             branch: Optional[Branch | str] = None,
#             get_name: bool = False
#     ) -> Union[Branch, Tuple[Branch, str]]:
#
#         if isinstance(branch, str):
#
#             if branch == 'all':
#                 if get_name:
#                     return self.branches, list(self.branches.keys())
#                 return self.branches
#
#             if branch not in self.branches.keys():
#                 raise ValueError(f'Invalid branch name {branch}. Not exist.')
#             else:
#                 if get_name:
#                     return self.branches[branch], branch
#                 return self.branches[branch]
#
#         elif isinstance(branch, Branch) and branch in self.branches.values():
#             if get_name:
#                 return branch, [
#                     key for key, value in self.branches.items() if value == branch
#                 ][0]
#             return branch
#
#         elif branch is None:
#             if get_name:
#                 return self.default_branch, self.default_branch_name
#             return self.default_branch
#
#         else:
#             raise ValueError(f'Invalid branch input_ {branch}.')
#
#     def new_branch(
#             self,
#             branch_name: Optional[str] = None,
#             system=None,
#             sender=None,
#             messages: Optional[pd.DataFrame] = None,
#             instruction_sets=None,
#             action_manager=None,
#             service=None,
#             llmconfig=None,
#             actions=None,
#     ) -> None:
#
#         if branch_name in self.branches.keys():
#             raise ValueError(
#                 f'Invalid new branch name {branch_name}. Branch already existed.')
#         new_branch = Branch(
#             name=branch_name,
#             messages=messages,
#             instruction_sets=instruction_sets,
#             action_manager=action_manager,
#             service=service,
#             llmconfig=llmconfig,
#             actions=actions
#         )
#         if system:
#             new_branch.add_message(system=system, sender=sender)
#
#         self.branches[branch_name] = new_branch
#         self.mail_manager.sources[branch_name] = new_branch
#         self.mail_manager.mails[branch_name] = {}
#
#     def log_to_csv(self, filename: str = 'log.csv', file_exist_ok: bool = False,
#                    timestamp: bool = True,
#                    time_prefix: bool = False, verbose: bool = True, clear: bool = True,
#                    **kwargs):
#         self.logger.to_csv(
#             filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
#             time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
#         )
#
#     def log_to_json(self, filename: str = 'log.json', file_exist_ok: bool = False,
#                     timestamp: bool = True,
#                     time_prefix: bool = False, verbose: bool = True, clear: bool = True,
#                     **kwargs):
#         self.logger.to_json(
#             filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
#             time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
#         )
#
#     def to_csv(self, filename: str = 'messages.csv', file_exist_ok: bool = False,
#                timestamp: bool = True, time_prefix: bool = False,
#                verbose: bool = True, clear: bool = True, branch=None, **kwargs):
#         if branch:
#             branch = self.get_branch(branch)
#
#         if not filename.endswith('.csv'):
#             filename += '.csv'
#
#         filepath = SysUtil.create_path(
#             self.logger.dir, filename, timestamp=timestamp,
#             dir_exist_ok=file_exist_ok, time_prefix=time_prefix
#         )
#
#         try:
#             self.messages.to_csv(filepath, **kwargs)
#             if verbose:
#                 print(f"{len(self.messages)} messages saved to {filepath}")
#             if clear:
#                 self.clear_messages()
#         except Exception as e:
#             raise ValueError(f"Error in saving to csv: {e}")
#
#     def to_json(self, filename: str = 'messages.json', file_exist_ok: bool = False,
#                 timestamp: bool = True, time_prefix: bool = False,
#                 verbose: bool = True, clear: bool = True, **kwargs):
#
#         if not filename.endswith('.json'):
#             filename += '.json'
#
#         filepath = SysUtil.create_path(
#             self.dir, filename, timestamp=timestamp,
#             dir_exist_ok=file_exist_ok, time_prefix=time_prefix
#         )
#
#         try:
#             self.messages.to_json(
#                 filepath, orient="records", lines=True,
#                 date_format="iso", **kwargs
#             )
#             if clear:
#                 self.clear_messages()
#             if verbose:
#                 print(f"{len(self.messages)} messages saved to {filepath}")
#         except Exception as e:
#             raise ValueError(f"Error in saving to json: {e}")
#
#     @classmethod
#     def from_csv(
#             cls,
#             filepath,
#             system: Optional[Union[str, System]] = None,
#             sender: Optional[str] = None,
#             llmconfig: Optional[Dict[str, Any]] = None,
#             service: BaseService = None,
#             branches: Optional[Dict[str, Branch]] = None,
#             default_branch: Optional[Branch] = None,
#             default_branch_name: str = 'main',
#             actions=None,
#             instruction_sets=None, action_manager=None,
#             **kwargs) -> 'Session':
#         df = pd.read_csv(filepath, **kwargs)
#
#         self = cls(
#             system=system,
#             sender=sender,
#             llmconfig=llmconfig,
#             service=service,
#             branches=branches,
#             default_branch=default_branch,
#             default_branch_name=default_branch_name,
#             actions=actions,
#             instruction_sets=instruction_sets,
#             action_manager=action_manager,
#             messages=df, **kwargs
#         )
#
#         return self
#
#     @classmethod
#     def from_json(
#             cls,
#             filepath,
#             system: Optional[Union[str, System]] = None,
#             sender: Optional[str] = None,
#             llmconfig: Optional[Dict[str, Any]] = None,
#             service: BaseService = None,
#             branches: Optional[Dict[str, Branch]] = None,
#             default_branch: Optional[Branch] = None,
#             default_branch_name: str = 'main',
#             actions=None,
#             instruction_sets=None, action_manager=None,
#             **kwargs) -> 'Session':
#         df = pd.read_json(filepath, **kwargs)
#         self = cls(
#             system=system,
#             sender=sender,
#             llmconfig=llmconfig,
#             service=service,
#             branches=branches,
#             default_branch=default_branch,
#             default_branch_name=default_branch_name,
#             actions=actions,
#             instruction_sets=instruction_sets,
#             action_manager=action_manager,
#             messages=df, **kwargs
#         )
#
#         return self
#
#     @property
#     def all_messages(self) -> pd.DataFrame:
#         """
#         return all messages across branches
#         """
#         dfs = collections.deque()
#         for _, v in self.branches:
#             dfs.append(to_df(v.messages))
#         return to_df(to_list(dfs, flatten=True, dropna=True))
#
#     def collect(self, sender: Union[str, Branch, List[str], List[Branch]] = None):
#         if sender is None:
#             for branch in self.branches.keys():
#                 self.branch_manager.collect(branch)
#         else:
#             if not isinstance(sender, list):
#                 sender = [sender]
#             for branch in sender:
#                 if isinstance(branch, Branch):
#                     branch = branch.name
#                 if isinstance(branch, str):
#                     self.branch_manager.collect(branch)
#
#     def send(self, to_: Union[str, Branch, List[str], List[Branch]] = None):
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
