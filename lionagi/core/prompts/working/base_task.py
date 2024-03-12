from pydantic import BaseModel, Field
from typing import List, Dict, Type

class TaskInstruction(BaseModel):
    task_name: str
    input_types: List[str] = []
    output_types: List[str] = []

    def validate_context_inputs(self, context: Dict[str, Any]):
        missing_inputs = [input_type for input_type in self.input_types if input_type not in context]
        if missing_inputs:
            raise ValueError(f"Missing inputs in context: {', '.join(missing_inputs)}")
        return True

from typing import Any, Dict

class InstructionWithContext(BaseModel):
    instruction: TaskInstruction
    context: Dict[str, Any]

    def compose(self) -> str:
        # Validate that all required inputs are present in the context
        self.instruction.validate_context_inputs(self.context)

        # Compose the instruction with actual inputs from the context
        composed_instruction = f"Task: {self.instruction.task_name}\n"
        for input_type in self.instruction.input_types:
            composed_instruction += f"{input_type}: {self.context.get(input_type)}\n"
        return composed_instruction

    class Config:
        arbitrary_types_allowed = True

# Define a task instruction (e.g., "Translate Text")
translate_instruction = TaskInstruction(
    task_name="Translate Text",
    input_types=["Source Language", "Target Language", "Text"],
    output_types=["Translated Text"]
)

# Actual input values provided in the context
context_data = {
    "Source Language": "English",
    "Target Language": "French",
    "Text": "Hello, world!"
}

# Combine the instruction with context
instruction_with_context = InstructionWithContext(
    instruction=translate_instruction,
    context=context_data
)

# Compose and validate the full instruction
full_instruction = instruction_with_context.compose()
print(full_instruction)


from pydantic import BaseModel, ValidationError, create_model
from typing import Any, Dict, Type, List

class InstructionTemplate(BaseModel):
    task: str
    input_types: Dict[str, Type[Any]]  # Expected input types
    output_types: Dict[str, Type[Any]]  # Expected output types

    # Dynamically create Pydantic models based on input/output types for validation
    @property
    def input_model(self) -> Type[BaseModel]:
        return create_model('InputModel', **self.input_types)
    
    @property
    def output_model(self) -> Type[BaseModel]:
        return create_model('OutputModel', **self.output_types)

    def validate_input(self, input_data: Dict[str, Any]):
        try:
            # Validates input data against the expected types
            valid_input = self.input_model(**input_data)
            return valid_input.dict()
        except ValidationError as e:
            print("Input validation error:", e.json())
            return None

    def validate_output(self, output_data: Dict[str, Any]):
        try:
            # Validates output data against the expected types
            valid_output = self.output_model(**output_data)
            return valid_output.dict()
        except ValidationError as e:
            print("Output validation error:", e.json())
            return None

# Example of defining an instruction template
instruction_template = InstructionTemplate(
    task="Data Retrieval",
    input_types={"user_id": int, "query": str},
    output_types={"result": List[str]}
)

# Example context provided dynamically
context_input = {
    "user_id": 123,
    "query": "Retrieve user data"
}

# Validate the actual inputs using the instruction template
validated_input = instruction_template.validate_input(context_input)
if validated_input is not None:
    # Proceed with processing using validated input
    print("Validated Input:", validated_input)
else:
    # Handle invalid input scenario
    print("Invalid input according to template.")

from pydantic import BaseModel, Field
from typing import List, Type, Dict, Any

class TaskInput(BaseModel):
    name: str
    type: Type
    required: bool = True

class TaskOutput(BaseModel):
    name: str
    type: Type

class TaskSchema(BaseModel):
    task_name: str
    inputs: List[TaskInput] = []
    outputs: List[TaskOutput] = []


class TaskInstance(BaseModel):
    schema: TaskSchema
    context: Dict[str, Any]

    def __init__(self, schema: TaskSchema, context: Dict[str, Any], **data: Any):
        super().__init__(**data)
        self.schema = schema
        self.context = context
        self.validate_context()

    def validate_context(self):
        for input_spec in self.schema.inputs:
            if input_spec.required and input_spec.name not in self.context:
                raise ValueError(f"Required input '{input_spec.name}' not provided in context.")
            if input_spec.name in self.context and not isinstance(self.context[input_spec.name], input_spec.type):
                raise TypeError(f"Input '{input_spec.name}' is not of type {input_spec.type.__name__}.")

    def process(self):
        # Implement the logic to process the task with validated inputs
        # and produce outputs as defined in the schema.
        pass

# Example of using TaskSchema and TaskInstance
task_schema = TaskSchema(
    task_name="DataRetrieval",
    inputs=[TaskInput(name="UserID", type=str), TaskInput(name="DateRange", type=dict)],
    outputs=[TaskOutput(name="Data", type=list)]
)

context = {
    "UserID": "user123",
    "DateRange": {"start": "2021-01-01", "end": "2021-01-31"}
}

# Create and validate a task instance with the given context
task_instance = TaskInstance(schema=task_schema, context=context)
task_instance.process()  # Process the task with validated context


from typing import Union, Type, List
from dataclasses import dataclass

@dataclass
class Field:
    name: str
    type_: Type

    def __add__(self, other):
        if not isinstance(other, (Field, OutputField, FieldGroup)):
            return NotImplemented
        return FieldGroup([self]) + other

class OutputField(Field):
    pass

class FieldGroup:
    def __init__(self, fields: List[Union[Field, OutputField]] = None):
        self.fields = fields if fields else []

    def __add__(self, other):
        if isinstance(other, (Field, OutputField)):
            self.fields.append(other)
        elif isinstance(other, FieldGroup):
            self.fields.extend(other.fields)
        else:
            return NotImplemented
        return self

    def __rshift__(self, other):
        if not isinstance(other, (OutputField, FieldGroup)):
            return NotImplemented
        return TaskSchema(self, other if isinstance(other, FieldGroup) else FieldGroup([other]))

class TaskSchema:
    def __init__(self, inputs: FieldGroup, outputs: FieldGroup):
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self):
        input_repr = ' + '.join([f"{field.name}: {field.type_.__name__}" for field in self.inputs.fields])
        output_repr = ' + '.join([f"{field.name}: {field.type_.__name__}" for field in self.outputs.fields])
        return f"{input_repr} --> {output_repr}"

UserID = Field("UserID", str)
DateRange = Field("DateRange", Union[dict, None])
Data = Field("Data", Union[list, None])

output_field1 = OutputField("output_field1", str)
output_field2 = OutputField("output_field2", Union[dict, None])

task_schema = UserID + DateRange + Data >> output_field1 + output_field2

print(task_schema)


from pydantic import BaseModel, validator, root_validator, ValidationError
from typing import Dict, Any, Union, List
from pydantic.fields import Field

class TaskField(BaseModel):
    name: str
    type_: str = Field(..., alias="type")
    required: bool = True
    validate_with: Union[None, str] = None

class TaskSignature(BaseModel):
    inputs: List[TaskField]
    outputs: List[str]  # Output fields names; values are always expected to be strings

    @root_validator(pre=True)
    def check_fields(cls, values):
        # Example of converting all input types to string for validation purposes
        for field in values.get("inputs", []):
            field["type"] = "str"
        return values

    @validator('inputs', each_item=True)
    def validate_input_field(cls, v, values, **kwargs):
        # Custom validation logic can go here, for example:
        if v.validate_with:
            # Assume 'validate_with' is a reference to a custom validation function
            validation_func = globals().get(v.validate_with)
            if not validation_func:
                raise ValueError(f"Validation function {v.validate_with} not found.")
            # Further validation logic using 'validation_func' can be applied here
        return v

# Example custom validation function
def is_numeric_str(value: str) -> bool:
    try:
        float(value)  # Try converting to a float
        return True
    except ValueError:
        return False

def parse_and_validate_context(task_signature: TaskSignature, context: Dict[str, Any]):
    validated_data = {}

    for input_field in task_signature.inputs:
        input_value = context.get(input_field.name)

        if input_field.required and input_value is None:
            raise ValidationError(f"Input field '{input_field.name}' is required but not provided.")
        
        if input_field.validate_with and not globals()[input_field.validate_with](input_value):
            raise ValidationError(f"Input field '{input_field.name}' failed validation with {input_field.validate_with}.")

        validated_data[input_field.name] = input_value
    
    # Assuming outputs are always valid as they are produced by the system or predefined logic
    return validated_data

# Usage example
task_signature = TaskSignature(
    inputs=[
        TaskField(name="UserID", type_="str", required=True),
        TaskField(name="Amount", type_="str", required=True, validate_with="is_numeric_str")
    ],
    outputs=["Result"]
)

context = {
    "UserID": "user123",
    "Amount": "100.50"
}

try:
    validated_data = parse_and_validate_context(task_signature, context)
    print("Context data validated successfully:", validated_data)
except ValidationError as e:
    print("Validation error:", e)


"""
with ss as task_schema:
    for i in [a: str|none, b: dict|none, c: str|none]:
        ss += i

task_schema.set(a + b >> c)

"""

class TaskSchema:
    def __init__(self):
        self.inputs = []
        self.outputs = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Exit the context manager, handle exceptions if needed
        pass

    def __iadd__(self, other):
        self.inputs.append(other)
        return self

    def set(self, value):
        input_fields, output_field = value
        self.inputs.extend(input_fields)
        self.outputs.append(output_field)

class Field:
    def __init__(self, name: str, type_: Union[Type, None]):
        self.name = name
        self.type = type_

    def __add__(self, other):
        if isinstance(other, Field):
            return [self, other]
        return NotImplemented

    def __rshift__(self, other):
        return ([self], other)

def field(name: str, type_: Union[Type, None]):
    return Field(name, type_)



"""
fields = {
    "a" : TYPE,
    "b" : TYPE, 
    "c" : TYPE, 
    "d" : TYPE
}

task1 = TaskSignature(fields, "a + b >> c")
task2 = TaskSignature(fields, "a + c >> d")


'''
task1 = a + b >> c      # input a and b leads to output c
task2 = a + c >> d      # input a and c leads to output d

task3 = a + *task1 >> e     # a and output of task1 leads to output e

task4 = *task3 + *task2 >> f     # output of task3 and output of task2 leads to output f

task5 = *(a + b >> c) + *(d + e >> f) >> g

compounded_tasks = task1 -> task2 -> task3 -> task4     # task1 then task2 then task3 then task4



'''



task3 = TaskSignature([task1, task2], )

the *task1 here means the result of task1. so here task1 can be 

"""


from typing import Dict, Union, List, Type
from pydantic import BaseModel, ValidationError

class Field(BaseModel):
    name: str
    type_: Type

class TaskSignature:
    def __init__(self, fields: Dict[str, Type], schema_str: str):
        self.fields = [Field(name=name, type_=type_) for name, type_ in fields.items()]
        self.inputs = []
        self.outputs = []
        self.parse_schema_str(schema_str)

    def parse_schema_str(self, schema_str: str):
        input_str, output_str = schema_str.split(">>")
        input_names = [name.strip() for name in input_str.split("+")]
        output_names = [name.strip() for name in output_str.split("+")]

        for field in self.fields:
            if field.name in input_names:
                self.inputs.append(field)
            if field.name in output_names:
                self.outputs.append(field)

    def __repr__(self):
        inputs_repr = " + ".join(f"{field.name}: {field.type_.__name__}" for field in self.inputs)
        outputs_repr = " + ".join(f"{field.name}: {field.type_.__name__}" for field in self.outputs)
        return f"Inputs: {inputs_repr} >> Outputs: {outputs_repr}"

fields = {
    "a": str,
    "b": dict, 
    "c": str
}

task_schema = TaskSignature(fields, "a + b >> c")

print(task_schema)


"""
fields = {"a"}




"""







from abc import ABC, abstractmethod
from typing import Dict, Any, Callable

class Field(ABC):
    def __init__(self, name: str, description: str, required: bool = True):
        self.name = name
        self.description = description
        self.required = required

    @abstractmethod
    def format(self, value: Any) -> str:
        pass

class StringField(Field):
    def format(self, value: str) -> str:
        return str(value)

class IntField(Field):
    def format(self, value: int) -> str:
        return str(value)

class FloatField(Field):
    def format(self, value: float) -> str:
        return str(value)

class CustomField(Field):
    def __init__(self, name: str, description: str, formatter: Callable[[Any], str], required: bool = True):
        super().__init__(name, description, required)
        self.formatter = formatter

    def format(self, value: Any) -> str:
        return self.formatter(value)

class Template(ABC):
    def __init__(self, fields: Dict[str, Field]):
        self.fields = fields

    def render(self, data: Dict[str, Any]) -> str:
        result = self.template
        for field_name, field in self.fields.items():
            if field_name in data:
                formatted_value = field.format(data[field_name])
                result = result.replace(f"{{{field_name}}}", formatted_value)
            elif field.required:
                raise ValueError(f"Missing required field: {field_name}")
        return result

    @abstractmethod
    def template(self) -> str:
        pass

class SystemMessageTemplate(Template):
    def __init__(self, content: str, fields: Dict[str, Field]):
        super().__init__(fields)
        self.content = content

    def template(self) -> str:
        return f"System: {self.content}"

class UserMessageTemplate(Template):
    def __init__(self, instruction: str, context: str, fields: Dict[str, Field]):
        super().__init__(fields)
        self.instruction = instruction
        self.context = context

    def template(self) -> str:
        return f"User: {self.instruction}\nContext: {self.context}"

class AssistantResponseTemplate(Template):
    def __init__(self, response: str, action_request: str, action_response: str, fields: Dict[str, Field]):
        super().__init__(fields)
        self.response = response
        self.action_request = action_request
        self.action_response = action_response

    def template(self) -> str:
        return f"Assistant: {self.response}\nAction Request: {self.action_request}\nAction Response: {self.action_response}"

# Example usage
if __name__ == "__main__":
    # Define fields
    name_field = StringField("name", "The name of the person")
    age_field = IntField("age", "The age of the person")
    height_field = FloatField("height", "The height of the person")
    custom_field = CustomField("custom", "Custom field", lambda x: f"Custom value: {x}")

    # Create templates
    system_template = SystemMessageTemplate("This is a system message with name: {name}", {"name": name_field})
    user_template = UserMessageTemplate("Instruction: {instruction}", "Context: {context}", {
        "instruction": StringField("instruction", "The user instruction"),
        "context": StringField("context", "The context for the instruction", required=False)
    })
    assistant_template = AssistantResponseTemplate("Response: {response}", "Action Request: {action_request}", "Action Response: {action_response}", {
        "response": StringField("response", "The assistant's response"),
        "action_request": StringField("action_request", "The action requested by the assistant", required=False),
        "action_response": StringField("action_response", "The response to the requested action", required=False)
    })

    # Render templates
    system_data = {"name": "John"}
    user_data = {"instruction": "Tell me a joke", "context": "We're having a fun conversation"}
    assistant_data = {"response": "Here's a joke for you: Why don't scientists trust atoms? Because they make up everything!"}

    rendered_system = system_template.render(system_data)
    rendered_user = user_template.render(user_data)
    rendered_assistant = assistant_template.render(assistant_data)

    print(rendered_system)
    print(rendered_user)
    print(rendered_assistant)