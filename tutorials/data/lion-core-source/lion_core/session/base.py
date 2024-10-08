from typing import ClassVar

from lionabc import AbstractSpace, BaseiModel
from pydantic import Field, model_validator

from lion_core.communication.system import System
from lion_core.generic.node import Node
from lion_core.generic.pile import Pile
from lion_core.session.msg_handlers.system_msg import validate_system
from lion_core.sys_utils import SysUtil


class BaseSession(Node, AbstractSpace):
    system: System | None = Field(None)
    user: str | None = Field(None)
    imodel: BaseiModel | None = Field(None)
    name: str | None = Field(None)
    pile_type: ClassVar[type] = Pile

    @model_validator(mode="before")
    def validate_system(cls, data: dict):
        system = data.pop("system", None)
        sender = data.pop("system_sender", None)
        system_datetime = data.pop("system_datetime", None)

        system = validate_system(
            system=system,
            sender=sender,
            system_datetime=system_datetime,
        )
        data["system"] = system
        return data

    @model_validator(mode="after")
    def check_system_recipient(self):
        if not SysUtil.is_id(self.system.recipient):
            self.system.recipient = self.ln_id
        return self


__all__ = ["BaseSession"]
# File: lion_core/session/base.py
