from typing import Any
from pydantic import field_serializer

from lionagi.core.schema.base_node import BaseNode

# To-Do: manual integration with actions

class BaseActionNode(BaseNode):
    func: Any
    schema_: dict
    manual: Any = None
    parser: Any = None


    @field_serializer('func')
    def serialize_func(self, func):
        return func.__name__



