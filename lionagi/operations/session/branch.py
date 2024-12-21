# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pandas as pd

from lionagi.core.action.action_manager import FUNCTOOL, ActionManager
from lionagi.core.communication.types import MESSAGE_FIELDS, MessageManager
from lionagi.core.generic.types import Component, LogManager, Pile, Progression
from lionagi.core.typing import ID
from lionagi.operations.strategies.strategy import Strategy
from lionagi.service import iModel
from lionagi.settings import Settings

from .branch_mixins import BranchActionMixin, BranchOperationMixin


class Branch(Component, BranchActionMixin, BranchOperationMixin):

    user: str | None = None
    name: str | None = None
    msgs: MessageManager = None
    acts: ActionManager = None
    imodel: iModel | None = None
    parse_imodel: iModel | None = None

    strategy_operative: Strategy | None = None

    @classmethod
    def create(
        cls,
        user: str | None = None,
        name: str | None = None,
        msgs: MessageManager = None,
        acts: ActionManager = None,
        imodel: iModel | None = None,
        parse_imodel: iModel | None = None,
        tools: list[FUNCTOOL] | None = None,
        data: dict = None,
        **kwargs,
    ) -> dict:
        user = user or data.pop("user", None)
        name = name or data.pop("name", None)
        message_manager = msgs or data.pop("msgs", None)
        if not message_manager:
            message_manager = MessageManager(
                messages=data.pop("messages", None),
                logger=LogManager(
                    **Settings.Branch.BRANCH.message_log_config.to_dict()
                ),
                system=data.pop("system", None),
            )

        acts = acts or data.pop("acts", None)
        if not acts:
            acts = ActionManager(
                logger=LogManager(
                    **Settings.Branch.BRANCH.action_log_config.to_dict()
                )
            )
        if tools:
            acts.register_tools(tools)

        imodel = imodel or iModel(**Settings.iModel.CHAT.to_dict())
        parse_imodel = parse_imodel or iModel(
            **Settings.iModel.PARSE.to_dict()
        )
        return cls(
            user=user,
            name=name,
            msgs=message_manager,
            acts=acts,
            imodel=imodel,
            parse_imodel=parse_imodel,
            **kwargs,
        )

    async def aclone(self, sender: ID.Ref = None) -> Branch:
        async with self.msgs.messages:
            return self.clone(sender)

    def clone(self, sender: ID.Ref = None) -> Branch:
        """
        Split a branch, creating a new branch with the same messages and tools.

        Args:
            branch: The branch to split or its identifier.

        Returns:
            The newly created branch.
        """
        if sender is not None:
            if not ID.is_id(sender):
                raise ValueError(
                    "Input value for branch.clone sender is not a valid sender"
                )
            sender = ID.get_id(sender)

        system = self.msgs.system.clone() if self.msgs.system else None
        tools = (
            list(self.acts.registry.values()) if self.acts.registry else None
        )
        branch_clone = Branch(
            system=system,
            user=self.user,
            messages=[i.clone() for i in self.msgs.messages],
            tools=tools,
        )
        for message in branch_clone.msgs.messages:
            message.sender = sender or self.ln_id
            message.recipient = branch_clone.ln_id
        return branch_clone

    def dump_log(self, clear: bool = True, persist_path: str | Path = None):
        self.msgs.logger.dump(clear, persist_path)
        self.acts.logger.dump(clear, persist_path)

    def to_df(self, *, progress: Progression = None) -> pd.DataFrame:
        if progress is None:
            progress = self.msgs.progress

        msgs = [
            self.msgs.messages[i] for i in progress if i in self.msgs.messages
        ]
        p = Pile(items=msgs)
        return p.to_df(columns=MESSAGE_FIELDS)
