from functools import singledispatchmethod
from typing import Any, Callable, Tuple, Dict

from lionagi.libs import ParseUtil
from lionagi.libs.ln_func_call import call_handler
from lionagi.core.generic.abc import Actionable, Element
from lionagi.core.message.action_request import ActionRequest


class FunctionCalling(Element, Actionable):
    """Class for dynamically invoking functions based on various input types,
    allowing function and arguments to be specified through multiple formats.
    """

    def __init__(self, function: Callable, arguments: dict = None):
        """
        Initializes a new instance of FunctionCalling.

        Args:
            function (Callable): The function to be called.
            arguments (Dict, optional): A dictionary of arguments to pass to the function.
                                        Defaults to None, which sets it to an empty dictionary.
        """
        self.function = function
        self.arguments = arguments or {}

    @property
    def func_name(self) -> str:
        """
        Returns the name of the function.

        Returns:
            str: The function's name.
        """
        return self.function.__name__

    @classmethod
    @singledispatchmethod
    def create(cls, func_call: Any) -> "FunctionCalling":
        """
        Creates an instance of FunctionCalling based on the type of input.

        Args:
            func_call (Any): The function call description, which can be a tuple, dict,
                             ActionRequest, or JSON string.

        Returns:
            FunctionCalling: An instance of FunctionCalling prepared to invoke the specified function.

        Raises:
            TypeError: If the input type is not supported.
        """
        raise TypeError(f"Unsupported type {type(func_call)}")

    @create.register
    def _(cls, function_calling: Tuple[Callable, Dict]):
        """
        Handles creation from a tuple input.

        Args:
            func_call (Tuple[Callable, Dict]): Tuple containing a function and its arguments.

        Returns:
            FunctionCalling: An initialized FunctionCalling instance.

        Raises:
            ValueError: If the tuple does not contain exactly two elements.
        """
        if len(function_calling) == 2:
            return cls(function=function_calling[0], arguments=function_calling[1])
        else:
            raise ValueError(f"Invalid function call {function_calling}")

    @create.register
    def _(cls, function_calling: Dict[str, Any]):
        """
        Handles creation from a dictionary input.

        Args:
            func_call (Dict[str, Any]): Dictionary specifying the function and arguments.

        Returns:
            FunctionCalling: An initialized FunctionCalling instance.

        Raises:
            ValueError: If the dictionary structure is not as expected.
        """
        if len(function_calling) == 2 and (
            ["function", "arguments"] <= list(function_calling.keys())
        ):
            return cls.create(
                (function_calling["function"], function_calling["arguments"])
            )
        raise ValueError(f"Invalid function call {function_calling}")

    @create.register
    def _(cls, function_calling: ActionRequest):
        """
        Handles creation from an ActionRequest object.

        Args:
            func_call (ActionRequest): An ActionRequest object containing the function and arguments.

        Returns:
            FunctionCalling: An initialized FunctionCalling instance.
        """
        return cls.create((function_calling.function, function_calling.arguments))

    @create.register
    def _(cls, function_calling: str):
        """
        Handles creation from a JSON string input.

        Args:
            func_call (str): JSON string describing the function and arguments.

        Returns:
            FunctionCalling: An initialized FunctionCalling instance.

        Raises:
            ValueError: If parsing fails or the JSON does not represent a valid function call.
        """
        _call = None
        try:
            _call = ParseUtil.fuzzy_parse_json(function_calling)
        except Exception as e:
            raise ValueError(f"Invalid function call {function_calling}") from e

        if isinstance(_call, dict):
            return cls.create(_call)
        raise ValueError(f"Invalid function call {function_calling}")

    async def invoke(self) -> Any:
        """
        Asynchronously invokes the stored function with the provided arguments.

        Returns:
            Any: The result of the function call.
        """
        return await call_handler(self.func, **self.arguments)

    def __str__(self) -> str:
        """
        Returns a string representation of the function call.

        Returns:
            str: String representation of the function call.
        """
        return f"{self.func_name}({self.arguments})"

    def __repr__(self) -> str:
        return self.__str__()
