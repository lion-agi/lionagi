from typing import Any
from lionagi.libs import validation_funcs
from abc import abstractmethod

from ..abc import Condition, Actionable


class Rule(Condition, Actionable):

    def __init__(self, **kwargs):
        self.validation_kwargs = kwargs
        self.fix = kwargs.get("fix", False)

    @abstractmethod
    async def invoke(self, /, *args: Any, **kwargs: Any) -> Any:
        """Invoke the action with the given arguments."""

    @abstractmethod
    async def perform(self, /, *args: Any, **kwargs: Any) -> Any:
        """Perform the work with the given arguments."""
