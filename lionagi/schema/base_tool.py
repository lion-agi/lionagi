from typing import Any
from pydantic import field_serializer
from .base_node import BaseNode

class Tool(BaseNode):
    # name: str = None
    func: Any
    content: Any = None
    parser: Any = None
    schema_: dict

    @field_serializer('func')
    def serialize_func(self, func):
        return func.__name__
