from re import T
from typing import TypeAliasType
from lion_core.generic.log import BaseLog


class Log(BaseLog):
    pass


def _log(loginfo, content):
    return Log(loginfo, content)


log = TypeAliasType("log", Log)
log.__call__ = _log

__all__ = ["Log", "log"]
