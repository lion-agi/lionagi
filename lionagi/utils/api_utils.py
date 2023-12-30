import json
import uuid
from typing import Any, Dict, Optional, Union, TypeVar, Type

from pydantic import BaseModel, Field, validator




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







