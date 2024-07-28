from __future__ import annotations

from typing import Any

import pandas as pd

from lion_core.action.tool_manager import ToolManager
from lion_core.communication import RoledMessage
from lion_core.session.branch import Branch as CoreBranch

from lionagi.os.primitives import Pile, Progression, Exchange, pile, progression
from lionagi.os.operator.imodel.imodel import iModel
from lionagi.os.space.branch_converter import BranchConverterRegistry

from lionagi.app.Pandas.convert import to_df


class Branch(CoreBranch):

    def __init__(
        self,
        system: Any = None,
        system_sender: str | None = None,
        system_datetime: Any = None,
        name: str | None = None,
        user: str | None = None,
        imodel: iModel | None = None,
        messages: Pile | None = None,
        tool_manager: ToolManager | None = None,
        mailbox: Exchange | None = None,
        progress: Progression | None = None,
        tools: Any = None,
    ):
        super().__init__(
            system=system,
            system_sender=system_sender,
            system_datetime=system_datetime,
            name=name,
            user=user,
            imodel=imodel or iModel(),
            messages=messages,
            tool_manager=tool_manager,
            mailbox=mailbox or Exchange(),
            progress=progress,
            tools=tools,
        )

        # switch core pile/progression class to use lionagi primitives
        self.messages = pile(list(self.messages), RoledMessage, strict=False)
        self.progress = progression(list(self.progress))
            
    def to_df(self) -> pd.DataFrame:
        fields = [
            "ln_id",
            "message_type",
            "timestamp",
            "role",
            "content",
            "metadata",
            "sender",
            "recipient",
        ]
        dicts_ = []
        for i in self.order:
            _d = {j: getattr(self.messages[i], j, None) for j in fields}
            _d["message_type"] = self.messages[i].class_name()
            dicts_.append(_d)

        return to_df(dicts_)

    async def assess(self, *args, **kwargs): ...

    async def chat(self, *args, **kwargs): ...

    async def direct(self, *args, **kwargs): ...

    async def learn(self, *args, **kwargs): ...

    async def memorize(self, *args, **kwargs): ...

    async def plan(self, *args, **kwargs): ...

    async def query(self, *args, **kwargs): ...

    async def rank(self, *args, **kwargs): ...

    async def regurgitate(self, *args, **kwargs): ...

    async def respond(self, *args, **kwargs): ...

    async def route(self, *args, **kwargs): ...

    async def score(self, *args, **kwargs): ...

    async def strategize(self, *args, **kwargs): ...

    __slots__ = [
        "ln_id",
        "timestamp",
        "from_dict",
        "to_dict",
        "class_name",
        "metadata",
        "content",
        "extra_fields",
        "all_fields",
        "add_field",
        "update_field",
        "system",
        "user",
        "imodel",
        "name",
        "messages",
        "tool_manager",
        "mailbox",
        "progress",
        "set_system",
        "add_message",
        "clear_messages",
        "send",
        "receive",
        "receive_all",
        "convert_from",
        "convert_to",
        "last_response",
        "assistant_responses",
        "update_last_instruction_meta",
        "has_tools",
        "register_tools",
        "delete_tools",
        "to_chat_messages",
        "to_df",
        "assess",
        "chat",
        "direct",
        "learn",
        "memorize",
        "plan",
        "query",
        "rank",
        "regurgitate",
        "respond",
        "route",
        "score",
        "strategize",
    ]


Branch._converter_registry = BranchConverterRegistry

__all__ = ["Branch"]


# File path: lionagi/os/space/branch.py
