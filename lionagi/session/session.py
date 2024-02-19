from collections import deque
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from lionagi.util.sys_util import create_path
from lionagi.util import to_list, to_df
from lionagi.schema import Tool
from working.base_service import BaseService
from lionagi.session.branch.branch import Branch
from lionagi.mail.base.mail_manager import MailManager
from lionagi.session.messages.messages import Instruction, System


class Session:
    def __init__(
            self, default_branch=None, default_branch_name=None, system=None,
            sender=None, llmconfig=None, service=None, branches=None, tools=None,
            instruction_sets=None, action_manager=None, messages=None, datalogger=None,
            persist_path=None, **kwargs):

        self.branches = branches or {}
        self.default_branch = default_branch or Branch(
            sender=sender,
            branch_name=default_branch_name or 'main', system=system, llmconfig=llmconfig,
            service=service, tools=tools, instruction_sets=instruction_sets,
            persist_path=persist_path, messages=messages, **kwargs)

        self.datalogger = datalogger or DataLogger(persist_path=persist_path)
        self.mail_manager = MailManager(self.branches)

    @property
    def all_messages(self):
        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.messages))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_responses(self):
        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.responses))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_assistant_responses(self):
        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.assistant_responses))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_action_responses(self):
        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.action_response))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_action_requests(self):
        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.action_request))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def info(self) -> Dict[str, int]:
        dict_ = {}
        for k, v in self.branches.items():
            dict_[k] = v.info

        return dict_

    @property
    def sender_info(self) -> Dict[str, int]:
        dict_ = {}
        for k, v in self.branches.items():
            dict_[k] = v.sender_info

        return dict_

    @property
    def default_branch_name(self):
        return self.default_branch.branch_name

    def concat_logs(self):
        for _, v in self.branches:
            self.datalogger.extend(v.datalogger.logs)

    def log_to_csv(
            self, filename: str = 'log.csv', file_exist_ok: bool = False,
            timestamp: bool = True, time_prefix: bool = False, verbose: bool = True,
            clear: bool = True, **kwargs):

        self.concat_logs()
        self.datalogger.to_csv(
            filepath=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    def log_to_json(
            self, filename: str = 'log.json', file_exist_ok: bool = False,
            timestamp: bool = True, time_prefix: bool = False, verbose: bool = True,
            clear: bool = True, **kwargs):

        self.concat_logs()
        self.datalogger.to_json(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    @classmethod
    def from_csv(
            cls, filepath, default_branch_name=None, system=None, sender=None,
            llmconfig=None, service=None, tools=None, instruction_sets=None,
            action_manager=None, persist_path=None, read_kwargs=None,
            **kwargs) -> 'Session':

        default_branch = Branch.from_csv(
            sender=sender,
            filepath=filepath, branch_name=default_branch_name or 'main',
            system=system, llmconfig=llmconfig, service=service, tools=tools,
            instruction_sets=instruction_sets, persist_path=persist_path,
            action_manager=action_manager, read_kwargs=read_kwargs)

        self = cls(
            default_branch=default_branch, datalogger=datalogger,
            persist_path=persist_path, **kwargs
        )

        return self

    @classmethod
    def from_json(
            cls, filepath, default_branch_name=None, system=None, sender=None,
            llmconfig=None, service=None, tools=None, instruction_sets=None,
            action_manager=None, persist_path=None, read_kwargs=None,
            **kwargs) -> 'Session':

        default_branch = Branch.from_json(
            sender=sender,
            filepath=filepath, branch_name=default_branch_name or 'main',
            system=system, llmconfig=llmconfig, service=service, tools=tools,
            instruction_sets=instruction_sets, persist_path=persist_path,
            action_manager=action_manager, read_kwargs=read_kwargs)

        self = cls(
            default_branch=default_branch, datalogger=datalogger,
            persist_path=persist_path, **kwargs
        )

        return self

    def to_csv(
            self, filepath=None, branch='all', file_exist_ok=False, timestamp=True,
            time_prefix=False, verbose=True, clear=True, **kwargs):
        if branch == 'all':
            self.default_branch.messages = self.all_messages
            self.default_branch.to_csv(
                filepath=filepath, file_exist_ok=file_exist_ok, timestamp=timestamp,
                time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
            )
        else:
            branch = self.get_branch(branch)
            branch.to_csv(
                filepath=filepath, file_exist_ok=file_exist_ok, timestamp=timestamp,
                time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
            )

    def to_json(
            self, filepath=None, branch='all', file_exist_ok=False, timestamp=True,
            time_prefix=False, verbose=True, clear=True, **kwargs):
        if branch == 'all':
            for _, v in self.branches:
                v.to_json(
                    filepath=filepath, file_exist_ok=file_exist_ok, timestamp=timestamp,
                    time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
                )
        else:
            branch = self.get_branch(branch)
            branch.to_json(
                filepath=filepath, file_exist_ok=file_exist_ok, timestamp=timestamp,
                time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
            )

    def register_tools(self, tools):
        self.default_branch.register_tools(tools)

    def new_branch(
            self, branch_name: Optional[str] = None, system=None, sender=None,
            messages: Optional[pd.DataFrame] = None, instruction_sets=None,
            action_manager=None, service=None, llmconfig=None, tools=None,
            datalogger=None, persist_path=None, **kwargs) -> None:

        if branch_name in self.branches.keys():
            raise ValueError(
                f'Invalid new branch name {branch_name}. Branch already existed.')

        new_branch = Branch(
            branch_name=branch_name,
            system=system,
            messages=messages,
            sender=sender,
            service=service or self.service,
            llmconfig=llmconfig or self.llmconfig,
            tools=tools,
            action_manager=action_manager,
            instruction_sets=instruction_sets,
            datalogger=datalogger,
            persist_path=persist_path,
            **kwargs
        )

        self.branches[branch_name] = new_branch
        self.mail_manager.sources[branch_name] = new_branch
        self.mail_manager.mails[branch_name] = {}

    def get_branch(
            self,
            branch: Optional[Union[Branch, str]] = None,
            get_name: bool = False
    ) -> Union[Branch, Tuple[Branch, str]]:
        if isinstance(branch, str):
            if branch not in self.branches.keys():
                raise ValueError(f'Invalid branch name {branch}. Not exist.')
            else:
                if get_name:
                    return self.branches[branch], branch
                return self.branches[branch]

        elif isinstance(branch, Branch) and branch in self.branches.values():
            if get_name:
                return (
                    branch,
                    [key for key, value in self.branches.items() if value == branch][0]
                )
            return branch

        elif branch is None:
            if get_name:
                return self.default_branch, self.default_branch_name
            return self.default_branch

        else:
            raise ValueError(f'Invalid branch input_ {branch}.')

    def change_default_branch(self, branch: Union[str, Branch]) -> None:

        branch_ = self.get_branch(branch)
        self.default_branch = branch_

    def delete_branch(self, branch: Union[Branch, str], verbose: bool = True) -> bool:

        _, branch_name = self.get_branch(branch, get_name=True)

        if branch_name == self.default_branch_name:
            raise ValueError(
                f'{branch_name} is the current default branch, please switch to another branch before delete it.'
            )
        else:
            self.branches.pop(branch_name)
            # self.mail_manager.sources.pop(branch_name)
            self.mail_manager.mails.pop(branch_name)
            if verbose:
                print(f'Branch {branch_name} is deleted.')
            return True

    def merge_branch(
            self,
            from_branch: Union[str, Branch],
            to_branch: Union[str, Branch],
            update: bool = True,
            del_: bool = False
    ) -> None:
        from_branch = self.get_branch(branch=from_branch)
        to_branch = self.get_branch(branch=to_branch)
        to_branch.merge_branch(from_branch, update=update)

        if del_:
            if from_branch == self.default_branch:
                self.default_branch = to_branch
            self.delete_branch(from_branch, verbose=False)

    def collect(self, from_: Union[str, Branch, List[str], List[Branch]] = None):
        if from_ is None:
            for branch in self.branches.keys():
                self.mail_manager.collect(branch)
        else:
            if not isinstance(from_, list):
                from_ = [from_]
            for branch in from_:
                if isinstance(branch, Branch):
                    branch = branch.name
                if isinstance(branch, str):
                    self.mail_manager.collect(branch)

    def send(self, recipient: Union[str, Branch, List[str], List[Branch]] = None):
        if recipient is None:
            for branch in self.branches.keys():
                self.mail_manager.send(branch)
        else:
            if not isinstance(recipient, list):
                recipient = [recipient]
            for branch in recipient:
                if isinstance(branch, Branch):
                    branch = branch.name
                if isinstance(branch, str):
                    self.mail_manager.send(branch)

    def collect_send_all(self, receive_all=False):
        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches.values():
                branch.receive_all()

    def setup_default_branch(self, **kwargs):
        self._setup_default_branch(**kwargs)
        self._verify_default_branch()

    def _verify_default_branch(self):
        if self.branches:
            if self.default_branch_name not in self.branches.keys():
                raise ValueError('default branch name is not in imported branches')
            if self.default_branch is not self.branches[self.default_branch_name]:
                raise ValueError(
                    f'default branch does not match Branch object under {self.default_branch_name}')

        if not self.branches:
            self.branches[self.default_branch_name] = self.default_branch

    def _setup_default_branch(
            self, system, sender, default_branch, default_branch_name, messages,
            instruction_sets, tool_manager, service, llmconfig, tools, dir, logger
    ):

        branch = default_branch or Branch(
            name=default_branch_name, service=service, llmconfig=llmconfig, tools=tools,
            action_manager=tool_manager, instruction_sets=instruction_sets,
            messages=messages, dir=dir, logger=logger
        )

        self.default_branch = branch
        self.default_branch_name = default_branch_name or 'main'
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

    # ----- chatflow ----#
    async def call_chatcompletion(self, branch=None, sender=None, with_sender=False,
                                  tokenizer_kwargs=None, **kwargs):
        branch = self.get_branch(branch)
        await branch.call_chatcompletion(
            sender=sender, with_sender=with_sender,
            tokenizer_kwargs=tokenizer_kwargs or {}, **kwargs
        )

    async def chat(
            self,
            instruction: Union[Instruction, str],
            branch=None,
            context: Optional[Any] = None,
            sender: Optional[str] = None,
            system: Optional[Union[System, str, Dict[str, Any]]] = None,
            tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
            out: bool = True,
            invoke: bool = True,
            **kwargs) -> Any:
        branch = self.get_branch(branch)
        return await branch.chat(
            instruction=instruction, context=context,
            sender=sender, system=system, tools=tools,
            out=out, invoke=invoke, **kwargs
        )

    async def ReAct(
            self,
            instruction: Union[Instruction, str],
            branch=None,
            context=None,
            sender=None,
            system=None,
            tools=None,
            num_rounds: int = 1,
            **kwargs):
        branch = self.get_branch(branch)

        return await branch.ReAct(
            instruction=instruction, context=context,
            sender=sender, system=system, tools=tools,
            num_rounds=num_rounds, **kwargs
        )

    async def auto_followup(
            self,
            instruction: Union[Instruction, str],
            branch=None,
            context=None,
            sender=None,
            system=None,
            tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
            max_followup: int = 3,
            out=True,
            **kwargs):
        branch = self.get_branch(branch)
        return await branch.auto_followup(
            instruction=instruction, context=context,
            sender=sender, system=system, tools=tools,
            max_followup=max_followup, out=out, **kwargs
        )
