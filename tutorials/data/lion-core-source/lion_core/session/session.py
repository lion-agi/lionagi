from typing import Any

from lionabc import BaseiModel
from lionabc.exceptions import ItemNotFoundError, LionValueError
from lionfuncs import LN_UNDEFINED
from pydantic import Field, PrivateAttr

from lion_core.action.tool_manager import ToolManager
from lion_core.communication.mail_manager import MailManager
from lion_core.communication.message import RoledMessage
from lion_core.generic.exchange import Exchange
from lion_core.generic.flow import Flow
from lion_core.generic.pile import Pile, pile
from lion_core.generic.progression import Progression, progression
from lion_core.generic.utils import to_list_type
from lion_core.session.base import BaseSession
from lion_core.session.branch import Branch
from lion_core.sys_utils import SysUtil


class Session(BaseSession):
    """
    Manages multiple conversation branches and mail transfer in a session.

    Attributes:
        branches (Pile | None): Collection of conversation branches.
        default_branch (Branch | None): The default conversation branch.
        mail_transfer (Exchange | None): Mail transfer system.
        mail_manager (MailManager | None): Manages mail operations.
        conversations (Flow | None): Manages conversation flow.
    """

    branches: Pile | None = Field(None)
    default_branch: Branch | None = Field(None, exclude=True)
    mail_transfer: Exchange | None = Field(None)
    mail_manager: MailManager | None = Field(None, exclude=True)
    conversations: Flow | None = Field(None)
    _branch_type: type[Branch] = PrivateAttr(Branch)

    async def new_branch(
        self,
        system: Any = None,
        system_sender: str | None = None,
        system_datetime: Any = None,
        user: str | None = None,
        name: str | None = None,
        imodel: BaseiModel | None = None,
        messages: Pile | None = None,
        progress: Progression | None = None,
        tool_manager: ToolManager | None = None,
        tools: Any = None,
        **kwargs,  # additional branch parameters
    ) -> Branch:
        if system in [None, LN_UNDEFINED]:
            system = self.system.clone()
            system.sender = self.ln_id
            system_sender = self.ln_id

        branch = self._branch_type(
            system=system,
            system_sender=system_sender,
            system_datetime=system_datetime,
            name=name,
            user=user,
            imodel=imodel or self.imodel,
            messages=messages,
            progress=progress,
            tool_manager=tool_manager,
            tools=tools,
            **kwargs,
        )

        self.conversations.register(branch.progress, name=name)
        self.branches.include(branch)
        self.mail_manager.add_sources(branch)
        if self.default_branch is None:
            self.default_branch = branch
        return branch

    def remove_branch(
        self,
        branch: Branch | str,
        delete: bool = False,
    ):
        branch = SysUtil.get_id(branch)

        if branch not in self.branches:
            _s = (
                str(branch)
                if len(str(branch)) < 10
                else str(branch)[:10] + "..."
            )
            raise ItemNotFoundError(f"Branch {_s}.. does not exist.")
        branch: Branch = self.branches[branch]

        self.conversations.exclude(prog=branch.progress)
        self.branches.exclude(branch)
        self.mail_manager.delete_source(branch.ln_id)

        if self.default_branch.ln_id == branch.ln_id:
            if self.branches.is_empty():
                self.default_branch = None
            else:
                self.default_branch = self.branches[0]

        if delete:
            del branch

    def split_branch(self, branch: Branch | str) -> Branch:
        """
        Split a branch, creating a new branch with the same messages and tools.

        Args:
            branch: The branch to split or its identifier.

        Returns:
            The newly created branch.
        """
        branch: Branch = self.branches[branch]
        system = branch.system.clone() if branch.system else None
        if system:
            system.sender = branch.ln_id
        progress = progression()
        messages = pile({}, RoledMessage, strict_type=False)

        for id_ in branch.progress:
            clone_message: RoledMessage = branch.messages[id_].clone()
            progress.append(clone_message.ln_id)
            messages.append(clone_message)

        tools = (
            list(branch.tool_manager.registry.values())
            if branch.tool_manager.registry
            else None
        )
        branch_clone = self._branch_type(
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

    def change_default_branch(self, branch: Branch | str):
        """
        Change the default branch of the session.

        Args:
            branch: The branch to set as default or its identifier.
        """
        branch = self.branches[branch]
        if branch and len(branch) == 1:
            self.default_branch = branch
        raise LionValueError("Session can only have one default branch.")

    def collect(self, from_: Branch | str | Pile[Branch] | None = None):
        """
        Collect mail from specified branches.

        Args:
            from_: The branches to collect mail from. If None, collect
                from all.

        Raises:
            ValueError: If mail collection fails.
        """
        if from_ is None:
            self.mail_manager.collect_all()
        else:
            try:
                sources = to_list_type(from_)
                for source in sources:
                    self.mail_manager.collect(SysUtil.get_id(source))
            except Exception as e:
                raise ValueError(f"Failed to collect mail. Error: {e}")

    def send(self, to_: Branch | str | Pile[Branch] | None = None):
        """
        Send mail to specified branches.

        Args:
            to_: The branches to send mail to. If None, send to all.

        Raises:
            ValueError: If mail sending fails.
        """
        if to_ is None:
            self.mail_manager.send_all()
        else:
            try:
                sources = to_list_type(to_)
                for source in sources:
                    self.mail_manager.send(SysUtil.get_id(source))
            except Exception as e:
                raise ValueError(f"Failed to send mail. Error: {e}")

    def collect_send_all(self, receive_all: bool = False):
        """
        Collect and send mail for all branches, optionally receiving all mail.

        Args:
            receive_all: If True, receive all mail for all branches.
        """
        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches:
                branch.receive_all()


__all__ = ["Session"]
# File: lion_core/session/session.py
