
### Functions: `output_node_list`, `output_edge_list`, `ParseNode`

**Description**:
These functions and class methods provide utilities for processing structure objects, extracting and formatting nodes and edges, and converting code strings into callable functions or classes. The `ParseNode` class includes static methods for parsing various node types from dictionaries.

### Function: `output_node_list`

**Signature**:
```python
def output_node_list(structure)
```

**Parameters**:
- `structure`: The structure object containing nodes and potentially other nested structures.

**Returns**:
- `tuple`: A tuple containing a summary list of all nodes and a dictionary categorizing nodes by type.

**Description**:
Processes a structure object to extract and format all associated nodes into a summary list and detailed output dictionary. This function traverses a structure, extracting key properties of nodes and organizing them by type into a dictionary for easy access and manipulation.

**Usage Example**:
```python
summary_list, output = output_node_list(structure)
```

### Function: `output_edge_list`

**Signature**:
```python
def output_edge_list(structure)
```

**Parameters**:
- `structure`: The structure object containing edges.

**Returns**:
- `tuple`: A tuple containing a list of all edges with their details and a list of unique condition classes.

**Description**:
Extracts and formats all edges from a given structure into a list and maps any associated condition classes. This function collects edge data from a structure, including identifiers, timestamps, labels, and conditions, and compiles any unique condition classes associated with these edges.

**Usage Example**:
```python
edge_list, edge_cls_list = output_edge_list(structure)
```

### Class: `ParseNode`

**Description**:
Provides static methods for converting code strings to functional definitions, classes, and for parsing various types of structured nodes based on dictionary definitions. This utility class facilitates the dynamic execution of code and the instantiation of objects from serialized data.

### Methods:

#### `convert_to_def`

**Signature**:
```python
@staticmethod
def convert_to_def(function_code)
```

**Parameters**:
- `function_code` (str): The string code of the function to convert.

**Returns**:
- `function`: The converted function as a callable.

**Raises**:
- `ValueError`: If the function code is invalid or the function name cannot be detected.

**Description**:
Converts a string containing a function definition into a callable function object.

**Usage Example**:
```python
function_code = """
def example_function():
    return 'Hello, world!'
"""
func = ParseNode.convert_to_def(function_code)
print(func())  # Output: Hello, world!
```

#### `convert_to_class`

**Signature**:
```python
@staticmethod
def convert_to_class(cls_code)
```

**Parameters**:
- `cls_code` (str): The string code of the class to convert.

**Returns**:
- `class`: The converted class.

**Raises**:
- `ValueError`: If the class code is invalid or the class name cannot be detected.

**Description**:
Converts a string containing a class definition into a class object.

**Usage Example**:
```python
class_code = """
class ExampleClass:
    def greet(self):
        return 'Hello, world!'
"""
cls = ParseNode.convert_to_class(class_code)
instance = cls()
print(instance.greet())  # Output: Hello, world!
```

#### `parse_system`

**Signature**:
```python
@staticmethod
def parse_system(info_dict)
```

**Parameters**:
- `info_dict` (dict): A dictionary containing properties of a system node.

**Returns**:
- `System`: An instantiated System node filled with properties from `info_dict`.

**Description**:
Parses dictionary information into a System node object.

**Usage Example**:
```python
info_dict = {"ln_id": "1", "content": '{"system_info": "info"}'}
system_node = ParseNode.parse_system(info_dict)
```

#### `parse_instruction`

**Signature**:
```python
@staticmethod
def parse_instruction(info_dict)
```

**Parameters**:
- `info_dict` (dict): A dictionary containing properties of an instruction node.

**Returns**:
- `Instruction`: An instantiated Instruction node filled with properties from `info_dict`.

**Description**:
Parses dictionary information into an Instruction node object.

**Usage Example**:
```python
info_dict = {"ln_id": "1", "content": '{"instruction": "instruction"}'}
instruction_node = ParseNode.parse_instruction(info_dict)
```

#### `parse_directiveSelection`

**Signature**:
```python
@staticmethod
def parse_directiveSelection(info_dict)
```

**Parameters**:
- `info_dict` (dict): A dictionary containing properties of an action selection node.

**Returns**:
- `DirectiveSelection`: An instantiated DirectiveSelection node filled with properties from `info_dict`.

**Description**:
Parses dictionary information into a DirectiveSelection node object.

**Usage Example**:
```python
info_dict = {"ln_id": "1", "directive": "directive", "directive_kwargs": '{"key": "value"}'}
directive_node = ParseNode.parse_directiveSelection(info_dict)
```

#### `parse_tool`

**Signature**:
```python
@staticmethod
def parse_tool(info_dict)
```

**Parameters**:
- `info_dict` (dict): A dictionary containing properties and function code for a tool node.

**Returns**:
- `Tool`: An instantiated Tool node with the function converted from code.

**Raises**:
- `ValueError`: If unsafe code is detected in the function definition.

**Description**:
Parses dictionary information into a Tool node object, converting associated function code into a callable.

**Usage Example**:
```python
info_dict = {
    "ln_id": "1",
    "timestamp": "2023-01-01",
    "function": "def example_tool(): return 'Tool function'"
}
tool_node = ParseNode.parse_tool(info_dict)
```

#### `parse_condition`

**Signature**:
```python
@staticmethod
def parse_condition(condition, cls_code)
```

**Parameters**:
- `condition` (dict): A dictionary containing the serialized form of the condition's arguments.
- `cls_code` (str): The class code to instantiate the condition class.

**Returns**:
- An instance of the condition class filled with properties from the `condition` dictionary.

**Raises**:
- `ValueError`: If the condition or class code is invalid.

**Description**:
Parses a condition dictionary and corresponding class code into a class instance representing the condition.

**Usage Example**:
```python
condition = {"args": {"arg1": "value1"}}
cls_code = """
class ExampleCondition:
    def __init__(self, arg1):
        self.arg1 = arg1
"""
condition_instance = ParseNode.parse_condition(condition, cls_code)
```
