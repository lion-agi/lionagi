from typing import Callable, Any
from .base_schema import BaseNode

class Tool(BaseNode):
    name: str = None
    func: Callable = None
    content: Any = None
    parser: Callable = None
    schema: Any = None