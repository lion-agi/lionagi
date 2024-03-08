from typing import Any

from lionagi.core.schema import BaseNode


class ToolManual(BaseNode):

    instruct: str
    examples: str | dict
    decidables: str | dict | Any
