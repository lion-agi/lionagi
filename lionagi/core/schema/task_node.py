from .base_node import BaseComponent, BaseNode
from typing import ClassVar, Dict, Type, Any, Callable
from abc import ABC, abstractmethod
from pydantic import Field


class PromptField(BaseComponent):
    field_name: str | None = Field(default_factory=str, alias="name")
    field_type: Type | None = Field(default_factory=Any, alias="type")
    field_default: Any | None = Field(default_factory=Any, alias="default")
    field_description: str | None = Field(default_factory=str, alias="description")

    @property
    def field_type_str(self):
        return self.field_type.__name__
    
    def __str__(self):
        return f"Field: {self.field_name} ({self.field_type_str}) - {self.field_description}"


class TaskNode(BaseNode, ABC):
    task_name: str = Field(default_factory=str, description="The name of the task.")
    task_description: ClassVar[str] = "A generic task with no specific behavior defined."
    fields: Dict[str, PromptField] = Field(default_factory=dict, description="A dictionary of fields for the task.")

    def __init__(self, **data):
        super().__init__(**data)
        self.fields = {field.field_name: field for field in self.fields}
    
    def __str__(self):
        return f"Task: {self.task_name} - {self.task_description}\nFields:\n" + "\n".join([str(field) for field in self.fields.values()])


class Task(TaskNode, ABC):
    signature: str = Field(default_factory=str, description="Declare the inputs and outputs of the task.")
    flow: Any = Field(default_factory=Any, description="The function to execute the task.")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.inputs, self.outputs = parse_signature(self.signature)

    @abstractmethod
    def execute(self, **kwargs):
        pass



import re


def parse_signature(expr):
    # Split the expression into the input and output parts
    input_part, output_part = expr.split('>>')
    
    # Initialize variables to hold the parsed components
    inputs = []
    outputs = output_part.strip()
    
    # Further split the input part to handle direct and grouped inputs
    input_components = input_part.split('+')
    for comp in input_components:
        comp = comp.strip()
        if comp.startswith('[') and comp.endswith(']'):
            # Handle list inputs
            list_content = comp[1:-1].strip()
            inputs.append(list_content.split(', '))
        else:
            # Add direct inputs after stripping whitespace
            inputs.append(comp)

    # Check for special output notation (n * dd)
    output_match = re.match(r'(n \* )?(.+)', outputs)
    if output_match:
        outputs = output_match.group(2)
        if output_match.group(1):
            # This indicates separate outputs for each list element
            outputs = f"{output_match.group(1)}{outputs}"
    
    return inputs, outputs




# Example usages
expr1 = 'aa + bb + [cc0, cc1, cc2] >> dd'
expr2 = 'aa + bb + [cc0, cc1, cc2] >> n * dd'

parser = SignatureParser()
inputs1, outputs1 = parser.parse_signature(expr1)
inputs2, outputs2 = parser.parse_signature(expr2)

inputs1, outputs1, inputs2, outputs2

    


class TaskFlow:
    
    def __init__(self, task_cls, signature_str: str):
        self.task_cls = task_cls
        self.signature_str = signature_str
        self.inputs, self.outputs = self.parse_signature(signature_str)


'n*(aa+cc) + bb >> n * dd'   # means each aa[i]/cc[i] pair will be processed into a dd
'aa + bb + n*cc >> n*dd'   # means each element of the list will have their own run


    @staticmethod
    def parse_signature(expr):
        # Split the expression into the input and output parts
        input_part, output_part = expr.split('>>')
        
        # Initialize variables to hold the parsed components
        inputs = []
        outputs = output_part.strip()
        
        # Further split the input part to handle direct and grouped inputs
        input_components = input_part.split('+')
        for comp in input_components:
            comp = comp.strip()
            if '|' in comp:  # Check for grouped inputs
                # Split grouped inputs, strip whitespace, and add as a list
                inputs.append([x.strip() for x in comp.split('|')])
            else:
                # Add direct inputs after stripping whitespace
                inputs.append(comp)
        
        return inputs, outputs

    def generate_prompt(self, **kwargs):
        # Generate a prompt based on inputs provided in kwargs and the task signature
        context = "\n".join([f"- {field}: {kwargs[field]}" for field in self.inputs if field in kwargs])
        prompt = f"Task:\n- {self.task_cls.__doc__}\n\nContext:\n{context}\n-----\n"
        return prompt

    def execute(self, **kwargs):
        prompt = self.generate_prompt(**kwargs)
        # Simulate LLM call with prompt
        response = self.simulate_llm_response(prompt)
        return response

    def simulate_llm_response(self, prompt):
        # Placeholder for LLM interaction
        print(f"Prompt to LLM:\n{prompt}")
        # Simulated response
        return {"Output text": "This is a simulated response.", "Confidence Score": "High"}

    def execute(self, **kwargs):
        # Validate inputs against task_cls fields
        # Transform inputs, generate prompt, call an LLM, etc.
        ...

    
    
'aa + bb + [cc0, cc1, cc2] >> dd'
'aa + bb + [cc0, cc1, cc2] >> n * dd'

'inputs = aa, bb, [cc0, cc1, cc2]'    
'outputs = dd'

def parse_expression(expr):
    # Split the expression into the input and output parts
    input_part, output_part = expr.split('>>')
    
    # Initialize variables to hold the parsed components
    inputs = []
    outputs = output_part.strip()
    
    # Further split the input part to handle direct and grouped inputs
    input_components = input_part.split('+')
    for comp in input_components:
        comp = comp.strip()
        if '|' in comp:  # Check for grouped inputs
            # Split grouped inputs, strip whitespace, and add as a list
            inputs.append([x.strip() for x in comp.split('|')])
        else:
            # Add direct inputs after stripping whitespace
            inputs.append(comp)
    
    return inputs, outputs
