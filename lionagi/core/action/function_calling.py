from functools import singledispatchmethod
from typing import Any, Callable
from lionagi.libs import ParseUtil
from lionagi.libs.ln_func_call import call_handler
from ..generic.abc import Actionable
from ..message.action_request import ActionRequest


class FunctionCalling(Actionable):

    def __init__(self, function: Callable, arguments: dict = {}) -> None:
        self.function = function
        self.arguments = arguments

    @property
    def func_name(self):
        return self.function.__name__

    @classmethod
    @singledispatchmethod
    def create(cls, func_call: Any) -> "FunctionCalling":
        raise TypeError(f"Unsupported type {type(func_call)}")

    @create.register
    def _(cls, func_call: tuple):
        if len(func_call) == 2:
            return cls(func=func_call[0], kwargs=func_call[1])
        else:
            raise ValueError(f"Invalid function call {func_call}")

    @create.register
    def _(cls, func_call: dict):
        if len(func_call) == 2 and (
            ["function", "arguments"] <= list(func_call.keys())
        ):
            return cls.create((func_call["function"], func_call["arguments"]))
        raise ValueError(f"Invalid function call {func_call}")

    @create.register
    def _(cls, func_call: ActionRequest):
        return cls.create((func_call.function, func_call.arguments))

    @create.register
    def _(cls, func_call: str):
        _call = None
        try:
            _call = ParseUtil.fuzzy_parse_json(func_call)
        except Exception as e:
            raise ValueError(f"Invalid function call {func_call}") from e

        if isinstance(_call, dict):
            return cls.create(_call)
        raise ValueError(f"Invalid function call {func_call}")

    async def invoke(self):
        return await call_handler(self.func, **self.kwargs)

    def __str__(self):
        return f"{self.func_name}({self.kwargs})"
