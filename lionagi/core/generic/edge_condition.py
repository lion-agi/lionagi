from typing import Any
from pydantic import Field
from lionagi.core.collections.abc import Condition


class EdgeCondition(Condition):
    source: Any = Field(
        title="Source",
        description="The source for condition check",
    )

    def __init__(self, source):
        super().__init__()
        self.source = source
