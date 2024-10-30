from typing import Any

from lionagi.core.action.tool_manager import ToolManager
from lionagi.core.collections import (
    Exchange,
    Pile,
    Progression,
    iModel,
    pile,
    progression,
)
from lionagi.core.collections.abc import get_lion_id
from lionagi.core.collections.util import to_list_type
from lionagi.core.mail.mail_manager import MailManager
from lionagi.core.message import System
from lionagi.core.session.branch import Branch
from lionagi.libs import SysUtil


class Session:
    """
    A session for managing branches, mail transfer, and interactions with a model.

    Attributes:
        ln_id (str): The unique identifier for the session.
        timestamp (str): The timestamp when the session was created.
        system (System): The default system message for the session.
        system_sender (str): The sender of the system message.
        branches (Pile[Branch]): The pile of branches in the session.
        mail_transfer (Exchange): The exchange for managing mail transfer.
        mail_manager (MailManager): The manager for handling mail.
        imodel (iModel): The model associated with the session.
        user (str): The user associated with the session.
        default_branch (Branch): The default branch of the session.
    """

    def __init__(
        self,
        system=None,  # the default system message for the session
        branches: Any | None = None,
        system_sender: str | None = None,
        user: str | None = None,
        imodel=None,
        tools=None,
    ):
        self.ln_id = SysUtil.create_id()
        self.timestamp = SysUtil.get_timestamp(sep=None)[:-6]
        system = (
            system or "You are a helpful assistant, let's think step by step"
        )
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
        if tools:
            self.default_branch.tool_manager.register_tools(tools)

    def _validate_branches(self, value):
        """
        Validates and converts the branches input to a Pile of Branch objects.

        Args:
            value (Any): The input value to validate and convert.

        Returns:
            Pile[Branch]: A pile of validated branches.

        Raises:
            ValueError: If the input value contains non-Branch objects.
        """
        if isinstance(value, Pile):
            for branch in value:
                if not isinstance(branch, Branch):
                    raise ValueError(
                        "The branches pile contains non-Branch object"
                    )
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
        """
        Creates a new branch and adds it to the session.

        Args:
            system (System, optional): The system message for the branch.
            system_sender (str, optional): The sender of the system message.
            user (str, optional): The user associated with the branch.
            messages (Pile, optional): The pile of messages for the branch.
            progress (Progression, optional): The progression of messages.
            tool_manager (ToolManager, optional): The tool manager for the branch.
            tools (Any, optional): The tools to register with the tool manager.
            imodel (iModel, optional): The model associated with the branch.

        Returns:
            Branch: The created branch.
        """
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
        """
        Deletes a branch from the session.

        Args:
            branch (Branch | str): The branch or its ID to delete.
        """
        branch_id = get_lion_id(branch)
        self.branches.pop(branch_id)
        self.mail_manager.delete_source(branch_id)

        if self.default_branch == branch:
            if self.branches.size() == 0:
                self.default_branch = None
            else:
                self.default_branch = self.branches[0]

    def split_branch(self, branch):
        """
        Splits a branch, creating a new branch with the same messages and tools.

        Args:
            branch (Branch | str): The branch or its ID to split.

        Returns:
            Branch: The newly created branch.
        """
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
        """
        Changes the default branch of the session.

        Args:
            branch (Branch | str): The branch or its ID to set as the default.
        """
        branch = self.branches[branch]
        self.default_branch = branch

    def collect(self, from_: Branch | str | Pile[Branch] | None = None):
        """
        Collects mail from specified branches.

        Args:
            from_ (Branch | str | Pile[Branch], optional): The branches to collect mail from.
                If None, collects mail from all branches.
        """
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
        """
        Sends mail to specified branches.

        Args:
            to_ (Branch | str | Pile[Branch], optional): The branches to send mail to.
                If None, sends mail to all branches.
        """
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
        """
        Collects and sends mail for all branches, optionally receiving all mail.

        Args:
            receive_all (bool, optional): Whether to receive all mail for all branches.
        """
        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches:
                branch.receive_all()

    async def chat(self, *args, branch=None, **kwargs):
        """
        Initiates a chat interaction with a branch.

        Args:
            *args: Positional arguments to pass to the chat method.
            branch (Branch, optional): The branch to chat with. Defaults to the default branch.
            **kwargs: Keyword arguments to pass to the chat method.

        Returns:
            Any: The result of the chat interaction.

        Raises:
            ValueError: If the specified branch is not found in the session branches.
        """
        if branch is None:
            branch = self.default_branch
        if branch not in self.branches:
            raise ValueError("Branch not found in session branches")
        return await self.branches[branch].chat(*args, **kwargs)

    async def direct(self, *args, branch=None, **kwargs):
        """
        Initiates a direct interaction with a branch.

        Args:
            *args: Positional arguments to pass to the direct method.
            branch (Branch, optional): The branch to interact with. Defaults to the default branch.
            **kwargs: Keyword arguments to pass to the direct method.

        Returns:
            Any: The result of the direct interaction.

        Raises:
            ValueError: If the specified branch is not found in the session branches.
        """
        if branch is None:
            branch = self.default_branch
        if branch not in self.branches:
            raise ValueError("Branch not found in session branches")
        return await self.branches[branch].direct(*args, **kwargs)
