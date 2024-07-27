from __future__ import annotations


import pandas as pd

from lion_core.session.branch import Branch as CoreBranch

from lionagi.os.primitives import Node
from lionagi.app.Pandas.convert import to_df


class Branch(Node, CoreBranch):

    def __init__(self, *args, **kwargs): ...

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


__all__ = ["Branch"]


# File path: lionagi/os/space/branch.py
