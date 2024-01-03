from typing import Any
from .base_schema import BaseNode

class Tool(BaseNode):
    name: str = None
    func: Any = None
    content: Any = None
    parser: Any = None
    schema_: Any = None