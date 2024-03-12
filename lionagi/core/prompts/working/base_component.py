from abc import ABC, abstractmethod
from typing import Any, Dict

class Component(ABC):

    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """
        Render the component into a structured format that can be easily integrated into messages.

        :return: A dictionary representing the rendered component.
        """
        pass

class TextComponent(Component):
    def __init__(self, text: str):
        self.text = text

    def render(self) -> Dict[str, Any]:
        return {"type": "text", "content": self.text}

class ActionComponent(Component):
    def __init__(self, action: str, data: Dict[str, Any]):
        self.action = action
        self.data = data

    def render(self) -> Dict[str, Any]:
        return {"type": "action", "action": self.action, "data": self.data}


from pydantic import BaseModel, ValidationError, validator
from typing import Any, Optional, List, Dict, Type

class FieldComponent(BaseModel):
    name: str
    value: Optional[Any] = None
    required: bool = True

    @validator('value')
    def check_required(cls, v, values, **kwargs):
        if values['required'] and v is None:
            raise ValueError('This field is required.')
        return v
