class FieldComponent:
    def __init__(self, name: str, type_: Type):
        self.name = name
        self.type = type_


class FieldGroup:
    def __init__(self, fields: List[FieldComponent] = None):
        self.fields = fields if fields else []

    def add_field(self, field: FieldComponent):
        self.fields.append(field)


class TaskSchema:
    def __init__(self, inputs: FieldGroup, outputs: FieldGroup):
        self.inputs = inputs
        self.outputs = outputs


class TaskSignature:
    def __init__(self, fields: Dict[str, Type], signature_str: str):
        self.fields = {name: FieldComponent(name, type_) for name, type_ in fields.items()}
        self.signature = self.parse_signature(signature_str)

    def parse_signature(self, signature_str: str):
        inputs, outputs = signature_str.split(">>")
        input_names = [name.strip() for name in inputs.split("+")]
        output_names = [name.strip() for name in outputs.split("+")]

        input_group = FieldGroup([self.fields[name] for name in input_names])
        output_group = FieldGroup([self.fields[name] for name in output_names])
        
        return TaskSchema(input_group, output_group)



"""


a = Task("translate", "input1+input2>>output")



--> 

input1 = field(input1)
input2 = field(input2)
output = field(output)

@task
class Translate:
    input1: input1
    input2: input2
    output: output

    
a = Task_KindA("translate", "input1+input2 >> output")
b = Task_KindB("translate", "input1+input2 >> output")
c = Task_KindC("translate", "input1+input2 >> output")



"""


def task(cls):
    cls._is_task = True
    return cls

class field:
    def __init__(self, description):
        self.description = description

class TaskKindBase:
    def __init__(self, task_cls, signature_str):
        if not hasattr(task_cls, '_is_task'):
            raise ValueError("Not a task class.")
        self.task_cls = task_cls
        self.signature_str = signature_str
        # Further processing to interpret signature_str
        # and possibly store as structured data for execution

class Task_KindA(TaskKindBase):
    pass  # Implement specific logic for Task_KindA

class Task_KindB(TaskKindBase):
    pass  # Implement specific logic for Task_KindB

class Task_KindC(TaskKindBase):
    pass  # Implement specific logic for Task_KindC

@task
class Translate:
    aa = field("field1")
    bb = field("field2")
    cc = field("field3")

translate_a = Task_KindA(Translate, "aa + bb >> cc")
translate_b = Task_KindB(Translate, "cc >> aa")
translate_c = Task_KindC(Translate, "aa + cc >> bb")


from typing import Dict, Type, Any, List, Union
from dataclasses import dataclass

def task(cls):
    '''Decorator to mark classes as tasks, enriching them with metadata.'''
    cls._is_task = True
    return cls

class field:
    '''Represents a task field with optional validation.'''
    def __init__(self, description: str, type_: Type = str, validator: Any = None):
        self.description = description
        self.type_ = type_
        self.validator = validator

class TaskKindBase:
    '''Base class for implementing different kinds of task behaviors.'''
    def __init__(self, task_cls, signature_str: str):
        if not hasattr(task_cls, '_is_task'):
            raise ValueError("Provided class is not marked as a task.")
        self.task_cls = task_cls
        self.signature_str = signature_str
        # Interpret signature_str to map inputs and outputs.
        self.inputs, self.outputs = self.parse_signature(signature_str)

    def parse_signature(self, signature: str) -> (List[str], List[str]):
        # Parse the signature string to identify inputs and outputs.
        inputs_part, outputs_part = signature.split(">>")
        inputs = [inp.strip() for inp in inputs_part.split("+")]
        outputs = [out.strip() for out in outputs_part.split("+")]
        return inputs, outputs

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        '''Execute the task logic based on the kind's specific behavior.'''
        raise NotImplementedError("Execute method should be implemented by subclasses.")

class Task_KindA(TaskKindBase):
    '''Implements a specific kind of task logic, e.g., sequential processing.'''
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement task-specific logic here.
        pass

class Task_KindB(TaskKindBase):
    '''Implements another kind of task logic, e.g., parallel processing.'''
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement task-specific logic here.
        pass

# Example of defining a task with fields using the @task decorator
@task
class Translate:
    '''Example task for translation, marked with @task and using fields.'''
    aa = field("Input text", str)
    bb = field("Source language", str)
    cc = field("Target language", str)

# Creating task instances with different behaviors
translate_a = Task_KindA(Translate, "aa + bb >> cc")
translate_b = Task_KindB(Translate, "cc >> aa")

# Example usage
# Assuming inputs for translate_a are provided correctly, it could be executed as:
# result = translate_a.execute({"aa": "Hello, world!", "bb": "English"})
# print(result)


from typing import Type
from pydantic import BaseModel, create_model

class field:
    def __init__(self, type_: Type, description: str = None):
        self.type_ = type_
        self.description = description


def task(cls):
    # Collect fields defined in the class
    fields = {name: (attr.type_, ...) for name, attr in cls.__dict__.items() if isinstance(attr, field)}
    
    # Create a Pydantic model dynamically
    model = create_model(cls.__name__, **fields)
    
    # Update the class to inherit from the dynamically created model and retain its original attributes
    # Note: This is a simplification. Depending on your needs, you might want to merge or override methods.
    cls = type(cls.__name__, (model,), dict(cls.__dict__))
    
    return cls


@task
class Translate:
    aa = field(str, "Input text")
    bb = field(str, "Source language")
    cc = field(str, "Target language")


# Instantiate with automatic validation
translate_instance = Translate(aa="Hello, world!", bb="English", cc="Spanish")

# Access fields
print(translate_instance.aa)

# Serialize to JSON
print(translate_instance.json())
