# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from functools import partial
from typing import Self

import pandas as pd
from pydantic import Field, JsonValue, model_validator

from lionagi.operatives.types import ActionManager, Tool
from lionagi.protocols.mail.exchange import Exchange
from lionagi.protocols.mail.manager import MailManager
from lionagi.protocols.messages.base import MessageFlag
from lionagi.protocols.types import (
    ID,
    MESSAGE_FIELDS,
    Communicatable,
    Node,
    Pile,
    Progression,
    Relational,
    RoledMessage,
    SenderRecipient,
    System,
    pile,
)

from .._errors import ItemNotFoundError
from ..service.imodel import iModel
from ..utils import lcall
from .branch import Branch

msg_pile = partial(pile, item_type={RoledMessage}, strict_type=False)


class Session(Node, Communicatable, Relational):
    """
    Manages multiple conversation branches and mail transfer in a session.

    Attributes:
        branches (Pile | None): Collection of conversation branches.
        default_branch (Branch | None): The default conversation branch.
        mail_transfer (Exchange | None): Mail transfer system.
        mail_manager (MailManager | None): Manages mail operations.
    """

    branches: Pile[Branch] = Field(default_factory=pile)
    default_branch: Branch = Field(default_factory=Branch, exclude=True)
    mail_transfer: Exchange = Field(default_factory=Exchange)
    mail_manager: MailManager = Field(
        default_factory=MailManager, exclude=True
    )

    @model_validator(mode="after")
    def _add_mail_sources(self) -> Self:
        if self.default_branch not in self.branches:
            self.branches.include(self.default_branch)
        if self.branches:
            self.mail_manager.add_sources(self.branches)
        return self

    def new_branch(
        self,
        system: System | JsonValue = None,
        system_sender: SenderRecipient = None,
        system_datetime: bool | str = None,
        user: SenderRecipient = None,
        name: str | None = None,
        imodel: iModel | None = None,
        messages: Pile[RoledMessage] = None,
        progress: Progression = None,
        tool_manager: ActionManager = None,
        tools: Tool | Callable | list = None,
        **kwargs,  # additional branch parameters
    ) -> Branch:

        kwargs["system"] = system
        kwargs["system_sender"] = system_sender
        kwargs["system_datetime"] = system_datetime
        kwargs["user"] = user
        kwargs["name"] = name
        kwargs["imodel"] = imodel
        kwargs["messages"] = messages
        kwargs["progress"] = progress
        kwargs["tool_manager"] = tool_manager
        kwargs["tools"] = tools
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        branch = Branch(**kwargs)

        self.branches.include(branch)
        self.mail_manager.add_sources(branch)
        if self.default_branch is None:
            self.default_branch = branch
        return branch

    def remove_branch(
        self,
        branch: ID.Ref,
        delete: bool = False,
    ):
        branch = ID.get_id(branch)

        if branch not in self.branches:
            _s = (
                str(branch)
                if len(str(branch)) < 10
                else str(branch)[:10] + "..."
            )
            raise ItemNotFoundError(f"Branch {_s}.. does not exist.")
        branch: Branch = self.branches[branch]

        self.branches.exclude(branch)
        self.mail_manager.delete_source(branch.id)

        if self.default_branch.id == branch.id:
            if not self.branches:
                self.default_branch = None
            else:
                self.default_branch = self.branches[0]

        if delete:
            del branch

    async def asplit(self, branch: ID.Ref) -> Branch:
        """
        Split a branch, creating a new branch with the same messages and tools.

        Args:
            branch: The branch to split or its identifier.

        Returns:
            The newly created branch.
        """
        async with self.branches:
            return self.split(branch)

    def split(self, branch: ID.Ref) -> Branch:
        """
        Split a branch, creating a new branch with the same messages and tools.

        Args:
            branch: The branch to split or its identifier.

        Returns:
            The newly created branch.
        """
        branch: Branch = self.branches[branch]
        branch_clone = branch.clone(sender=self.id)
        self.branches.append(branch_clone)
        return branch_clone

    def change_default_branch(self, branch: ID.Ref):
        """
        Change the default branch of the session.

        Args:
            branch: The branch to set as default or its identifier.
        """
        branch = self.branches[branch]
        if not isinstance(branch, Branch):
            raise ValueError("Input value for branch is not a valid branch.")
        self.default_branch = branch

    def to_df(
        self,
        branches: ID.RefSeq = None,
        exclude_clone: bool = False,
        exlcude_load: bool = False,
    ) -> pd.DataFrame:
        out = self.concat_messages(
            branches=branches,
            exclude_clone=exclude_clone,
            exclude_load=exlcude_load,
        )
        return out.to_df(columns=MESSAGE_FIELDS)

    def concat_messages(
        self,
        branches: ID.RefSeq = None,
        exclude_clone: bool = False,
        exclude_load: bool = False,
    ) -> Pile[RoledMessage]:
        if not branches:
            branches = self.branches

        if any(i not in self.branches for i in branches):
            raise ValueError("Branch does not exist.")

        exclude_flag = []
        if exclude_clone:
            exclude_flag.append(MessageFlag.MESSAGE_CLONE)
        if exclude_load:
            exclude_flag.append(MessageFlag.MESSAGE_LOAD)

        messages = lcall(
            branches,
            lambda x: [
                i for i in self.branches[x].messages if i not in exclude_flag
            ],
            sanitize_input=True,
            flatten=True,
            unique_input=True,
            unique_output=True,
        )
        return msg_pile(messages)

    def to_df(
        self,
        branches: ID.RefSeq = None,
        exclude_clone: bool = False,
        exclude_load: bool = False,
    ) -> pd.DataFrame:
        out = self.concat_messages(
            branches=branches,
            exclude_clone=exclude_clone,
            exclude_load=exclude_load,
        )
        return out.to_df(columns=MESSAGE_FIELDS)

    def send(self, to_: ID.RefSeq = None):
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
                lcall(
                    to_,
                    lambda x: self.mail_manager.send(ID.get_id(x)),
                    sanitize_input=True,
                    unique_input=True,
                    use_input_values=True,
                )
            except Exception as e:
                raise ValueError(f"Failed to send mail. Error: {e}")

    async def acollect_send_all(self, receive_all: bool = False):
        """
        Collect and send mail for all branches, optionally receiving all mail.

        Args:
            receive_all: If True, receive all mail for all branches.
        """
        async with self.mail_manager.sources:
            self.collect_send_all(receive_all)

    def collect_send_all(self, receive_all: bool = False):
        """
        Collect and send mail for all branches, optionally receiving all mail.

        Args:
            receive_all: If True, receive all mail for all branches.
        """
        self.collect()
        self.send()
        if receive_all:
            lcall(self.branches, lambda x: x.receive_all())

    def collect(self, from_: ID.RefSeq = None):
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
                lcall(
                    from_,
                    lambda x: self.mail_manager.collect(ID.get_id(x)),
                    sanitize_input=True,
                    unique_input=True,
                    use_input_values=True,
                )
            except Exception as e:
                raise ValueError(f"Failed to collect mail. Error: {e}")


__all__ = ["Session"]
# File: autoos/session/session.py
