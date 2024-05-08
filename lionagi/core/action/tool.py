from typing import Callable
from pydantic import field_serializer, Field
from lionagi.libs.ln_func_call import call_handler
from lionagi.core.generic.abc import Actionable
from lionagi.core.generic import Node
from .function_calling import FunctionCalling


class Tool(Node, Actionable):

    function: Callable = Field(
        ...,
        description="The callable function or capability of the tool.",
    )

    schema_: dict | None = Field(
        None,
        description="schema in openai format",
    )

    pre_processor: Callable | None = None
    pre_processor_kwargs: dict | None = None

    post_processor: Callable | None = None
    post_processor_kwargs: dict | None = None

    parser: Callable | None = None  # parse result to json serializable format

    @field_serializer("func")
    def serialize_func(self, func):
        return func.__name__

    @property
    def name(self):
        return self.schema_["function"]["name"]

    @field_serializer("func")
    def serialize_func(self, func):
        return func.__name__

    def create_function_calling(self, kwargs):
        return FunctionCalling.create(tuple(self.function, kwargs))

    async def invoke(self, kwargs={}, func_calling=None):
        if self.pre_processor:
            pre_process_kwargs = self.pre_processor_kwargs or {}
            kwargs = await call_handler(
                self.pre_processor(kwargs, **pre_process_kwargs)
            )
            if not isinstance(kwargs, dict):
                raise ValueError("Pre-processor must return a dictionary.")

        func_call_ = func_calling or self.create_function_calling(kwargs)
        result = await func_call_.invoke()

        if self.post_processor:
            post_process_kwargs = self.post_processor_kwargs or {}
            result = await call_handler(
                self.post_processor(result, **post_process_kwargs)
            )

        return result if not self.parser else self.parser(result)


TOOL_TYPE = bool | Tool | str | list[Tool | str | dict] | dict
