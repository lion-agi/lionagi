from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional, List
import json

from .base_prompt_field import BasePromptField


class PromptTemplate(BaseModel):
    fields: Dict[str, BasePromptField] = {}
    field_order: Optional[List[str]] = None

    class Config:
        arbitrary_types_allowed = True

    def add_field(self, field: BasePromptField) -> None:
        """Adds a new field to the template."""
        if field.name in self.fields:
            raise ValueError(f"Field with name '{field.name}' already exists.")
        self.fields[field.name] = field

    def remove_field(self, field_name: str) -> None:
        """Removes a field from the template."""
        if field_name not in self.fields:
            raise KeyError(f"Field with name '{field_name}' does not exist.")
        del self.fields[field_name]

    def update_field(self, field_name: str, **kwargs) -> None:
        """Updates properties of a field."""
        if field_name not in self.fields:
            raise KeyError(f"Field with name '{field_name}' does not exist.")
        for key, value in kwargs.items():
            setattr(self.fields[field_name], key, value)

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processes data through the template's fields."""
        processed_data = {}
        for field_name, field in self.fields.items():
            if field_name in data:
                try:
                    processed_data[field_name] = field.process(data[field_name])
                except Exception as e:
                    raise ValidationError(f"Error processing field '{field_name}': {e}")
        return processed_data

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validates data against the template's fields."""
        for field_name, field in self.fields.items():
            if field_name in data:
                # Reuse Pydantic's validation
                try:
                    field.validate_field(data[field_name])
                except ValidationError as e:
                    raise ValidationError(f"Validation error for field '{field_name}': {e}")
        return True

    def render(self, data: Dict[str, Any]) -> str:
        """Renders data using the template."""
        self.validate_data(data)
        processed_data = self.process_data(data)
        rendered_data = ""
        for field_name in self.field_order if self.field_order else self.fields.keys():
            if field_name in processed_data:
                rendered_data += f"{field_name}: {processed_data[field_name]}\n"
        return rendered_data.strip()

    def export_to_json(self) -> str:
        """Exports the template configuration to a JSON string."""
        return json.dumps(self.dict(), default=str)

    @classmethod
    def import_from_json(cls, json_str: str) -> 'PromptTemplate':
        """Creates a template instance from a JSON string."""
        data = json.loads(json_str)
        template = cls()
        for field_data in data.get("fields", {}).values():
            field = BasePromptField(**field_data)
            template.add_field(field)
        template.field_order = data.get("field_order", [])
        return template
