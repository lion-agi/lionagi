from __future__ import annotations

from typing import Any, Union
from pydantic import Field, field_validator

from lion_core.communication import System, MailManager
from lion_core.action import ToolManager

from lion_core.session.session import Session as CoreSession


from lionagi.os.sys_util import SysUtil
from lionagi.os.primitives import (
    pile,
    progression,
    Pile,
    Progression,
    Exchange,
    Node,
    Flow,
    flow,
)
from lionagi.os.operator.imodel.imodel import iModel
from lionagi.os.space.branch import Branch


FindableBranch = list[Branch | str] | Pile | Branch | str | None


class Session(CoreSession):

    def __init__(
        self,
        system: System | dict | str | list = None,
        *,
        system_sender: Any = None,
        system_datetime: bool | str | None = None,
        default_branch: Branch | str | None = None,
        default_branch_name: str | None = None,
        branches: Pile[Branch] | None = None,
        mail_transfer: Exchange | None = None,
        branch_user: str | None = None,
        session_user: str | None = None,
        session_name: str | None = None,
        tools: Any = None,
        tool_manager: ToolManager | None = None,
        imodel: iModel | None = None,
    ):
        super().__init__(
            system=system,
            system_sender=system_sender,
            system_datetime=system_datetime,
            default_branch=default_branch,
            default_branch_name=default_branch_name,
            branches=branches,
            mail_transfer=mail_transfer,
            branch_user=branch_user,
            session_user=session_user,
            session_name=session_name,
            tools=tools,
            tool_manager=tool_manager,
            imodel=imodel,
        )

        self.branches = pile(list(self.branches))

    async def assess(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def chat(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def direct(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def learn(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def memorize(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def plan(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def query(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def rank(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def regurgitate(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def respond(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def route(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def score(self, *args, branch: FindableBranch = None, **kwargs): ...

    async def strategize(self, *args, **kwargs): ...


__all__ = ["Session"]
