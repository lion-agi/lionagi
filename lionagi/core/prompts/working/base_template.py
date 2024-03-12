import json
from abc import ABC, abstractmethod
from .base_component import Component

class Template(ABC):

    @abstractmethod
    def add_component(self, component: Component):
        """
        Add a component to the template.

        :param component: The component to be added.
        """
        pass

    @abstractmethod
    def render(self) -> str:
        """
        Render the template with all its components into a string format suitable for messages.

        :return: The rendered template as a string.
        """
        pass

class BasicMessageTemplate(Template):
    def __init__(self):
        self.components = []

    def add_component(self, component: Component):
        self.components.append(component)

    def render(self) -> str:
        rendered_components = [component.render() for component in self.components]
        # Convert the rendered components into a string format
        # This can be JSON, XML, or any format suitable for your messaging system
        return json.dumps(rendered_components)


class InstructionTemplate(BaseModel):
    fields: Dict[str, FieldComponent] = {}
    inputs: List[str] = []
    outputs: List[str] = []

    def add_field(self, field: FieldComponent):
        if field.name in self.fields:
            raise ValueError(f"Field {field.name} already exists.")
        self.fields[field.name] = field

    def remove_field(self, field_name: str):
        if field_name in self.fields:
            del self.fields[field_name]
        else:
            raise ValueError(f"Field {field_name} does not exist.")

    def validate_fields(self):
        try:
            # Validate using Pydantic's model validation
            self.validate(self.fields)
        except ValidationError as e:
            print(e.json())

    def compose_prompt(self) -> str:
        prompt = ""
        # Compose the prompt based on inputs and expected outputs
        for input_name in self.inputs:
            input_field = self.fields.get(input_name)
            if input_field and input_field.value is not None:
                prompt += f"{input_field.name}: {input_field.value}\n"
        # Handle outputs similarly
        return prompt

    class Config:
        arbitrary_types_allowed = True


# Example usage
instruction_template = InstructionTemplate()

# Adding fields
instruction_template.add_field(FieldComponent(name="UserID", value="1234", required=True))
instruction_template.add_field(FieldComponent(name="Action", value="RetrieveData", required=True))

# Defining inputs and outputs
instruction_template.inputs = ["UserID", "Action"]
instruction_template.outputs = ["Result"]

# Compose the prompt for LLM
prompt = instruction_template.compose_prompt()

# Validate fields before processing
instruction_template.validate_fields()

# This prompt can now be used with an LLM or further processed
print(prompt)
