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

from lionagi.core.collections import (
    Pile,
    Progression,
    progression,
    pile,
    iModel,
)
from lionagi.core.message import System
from typing import Any
from lionagi.core.action.tool_manager import ToolManager

from lionagi.libs import SysUtil
from lionagi.core.session.branch import Branch
from lionagi.core.collections import pile, Pile, Exchange
from lionagi.core.collections.abc import get_lion_id
from lionagi.core.collections.util import to_list_type
from lionagi.core.mail.mail_manager import MailManager


class Session:

    def __init__(
        self,
        system = None,  # the default system message for the session
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
        self.branches: Pile[Branch] = self._validate_branches(branches)
        self.mail_transfer = Exchange()
        self.mail_manager = MailManager([self.mail_transfer])
        self.imodel = imodel or iModel()
        self.user = user
        self.default_branch = None
        if self.branches.size() == 0:
            self.new_branch(system=self.system.clone())
        else:
            self.default_branch = self.branches[0]

    def _validate_branches(self, value):
        if isinstance(value, Pile):
            for branch in value:
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
    def new_branch(
        self,
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
            system = self.system.clone()
            system.sender = self.ln_id
            system_sender = self.ln_id
        branch = Branch(
            system=system,
            system_sender=system_sender,
            user=user,
            messages=messages,
            progress=progress,
            tool_manager=tool_manager,
            tools=tools,
            imodel=imodel or self.imodel,
        )
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
        system = branch.system.clone() if branch.system else None
        if system:
            system.sender = branch.ln_id
        progress = progression()
        messages = pile()

        for id_ in branch.progress:
            clone_message = branch.messages[id_].clone()
            progress.append(clone_message.ln_id)
            messages.append(clone_message)

        tools = (
            list(branch.tool_manager.registry.values())
            if branch.tool_manager.registry
            else None
        )
        branch_clone = Branch(
            system=system,
            system_sender=branch.ln_id,
            user=branch.user,
            progress=progress,
            messages=messages,
            tools=tools,
        )
        for message in branch_clone.messages:
            message.sender = branch.ln_id
            message.recipient = branch_clone.ln_id
        self.branches.append(branch_clone)
        self.mail_manager.add_sources(branch_clone)
        return branch_clone

    def change_default_branch(self, branch):
        branch = self.branches[branch]
        self.default_branch = branch

    def collect(self, from_: Branch | str | Pile[Branch] | None = None):
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

    async def chat(self, *args, branch=None, **kwargs):
        if branch is None:
            branch = self.default_branch
        if branch not in self.branches:
            raise ValueError("Branch not found in session branches")
        return await self.branches[branch].chat(*args, **kwargs)
    
    async def direct(self, *args, branch=None, **kwargs):
        if branch is None:
            branch = self.default_branch
        if branch not in self.branches:
            raise ValueError("Branch not found in session branches")
        return await self.branches[branch].direct(*args, **kwargs)