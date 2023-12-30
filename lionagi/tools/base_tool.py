from typing import Any, Callable
from ..schema.base_node import BaseNode


class BaseTool(BaseNode):
    name: str = None
    func: Callable = None
    content: Any = None
    parser: Callable = None
    
    def initialize(self):
        ...

    def execute(self):
        ...

    def shutdown(self):
        ...

    def __enter__(self):
        self.initialize()
        return self