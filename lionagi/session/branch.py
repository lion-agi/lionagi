# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pandas as pd
from pydantic import model_validator

from lionagi.service.imodel import iModel

from ..action.types import ActionManager
from ..fields.instruct import Instruct, OperationInstruct
from ..protocols.base import ID, MESSAGE_FIELDS
from ..protocols.component import Component
from ..protocols.log import LogManager
from ..protocols.messages import MessageManager
from ..protocols.pile import Pile
from ..protocols.progression import Progression
from ..settings import Settings
from .branch_mixin import BranchActionMixin, BranchOperationMixin


class Branch(Component, BranchActionMixin, BranchOperationMixin):

    user: str | None = None
    name: str | None = None
    msgs: MessageManager = None
    acts: ActionManager = None
    imodel: iModel | None = None
    parse_imodel: iModel | None = None

    @model_validator(mode="before")
    def _validate_data(cls, data: dict) -> dict:

        user = data.pop("user", None)
        name = data.pop("name", None)
        message_manager = data.pop("msgs", None)
        if not message_manager:
            message_manager = MessageManager(
                messages=data.pop("messages", None),
                logger=data.pop("logger", None),
                system=data.pop("system", None),
            )
        if not message_manager.logger:
            message_manager.logger = LogManager(
                **Settings.Branch.BRANCH.message_log_config.to_dict(True)
            )

        acts = data.pop("acts", None)
        if not acts:
            acts = ActionManager()
            acts.logger = LogManager(
                **Settings.Branch.BRANCH.action_log_config.to_dict(True)
            )
        if "tools" in data:
            acts.register_tools(data.pop("tools"))

        imodel = data.pop(
            "imodel",
            iModel(**Settings.iModel.CHAT),
        )

        out = {
            "user": user,
            "name": name,
            "msgs": message_manager,
            "acts": acts,
            "imodel": imodel,
            **data,
        }
        return out

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

    async def aclone(self, sender: ID.Ref = None) -> "Branch":
        async with self.msgs.messages:
            return self.clone(sender)

    def clone(self, sender: ID.Ref = None) -> "Branch":
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
            message.sender = sender or self.id
            message.recipient = branch_clone.id
        return branch_clone

    async def instruct(self, instruct: Instruct, /, **kwargs):
        config = {**instruct.to_dict(), **kwargs}
        if any(i in config for i in OperationInstruct.reserved_kwargs):
            return await self.operate(**config)
        return await self.communicate(**config)
