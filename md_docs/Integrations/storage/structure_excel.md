
### Functions: `excel_reload`, `StructureExcel`

**Description**:
These functions and class provide utilities for loading and managing structures from Excel files. They include functionality for reloading structures, parsing nodes, and establishing relationships based on data from Excel files.

### Function: `excel_reload`

**Signature**:
```python
def excel_reload(structure_name=None, structure_id=None, dir="structure_storage")
```

**Parameters**:
- `structure_name` (str, optional): The name of the structure to reload.
- `structure_id` (str, optional): The unique identifier of the structure to reload.
- `dir` (str): The directory path where the Excel files are stored.

**Returns**:
- `StructureExecutor`: An instance of `StructureExecutor` containing the reloaded structure.

**Raises**:
- `ValueError`: If neither `structure_name` nor `structure_id` is provided, or if multiple or no files are found matching the criteria.

**Description**:
Loads a structure from an Excel file into a `StructureExecutor` instance. This function uses the `StructureExcel` class to handle the reloading process. It identifies the Excel file based on the provided structure name or ID and reloads the structure from it.

**Usage Example**:
```python
structure_executor = excel_reload(structure_name="example_structure")
```

### Class: `StructureExcel`

**Description**:
Manages the reloading of structures from Excel files. This class handles the identification and parsing of structure data from an Excel workbook. It supports loading from specifically named Excel files based on the structure name or ID.

#### Attributes:
- `structure` (GraphExecutor): The loaded structure, ready for execution.
- `default_agent_executable` (BaseExecutor): The default executor for agents within the structure.

#### Methods:

#### `__init__`

**Signature**:
```python
def __init__(self, structure_name=None, structure_id=None, file_path="structure_storage")
```

**Parameters**:
- `structure_name` (str, optional): The name of the structure to reload.
- `structure_id` (str, optional): The unique identifier of the structure to reload.
- `file_path` (str): The base path where the Excel files are stored.

**Raises**:
- `ValueError`: If both `structure_name` and `structure_id` are provided but do not correspond to a valid file, or if multiple or no files are found when one of the identifiers is provided.

**Description**:
Initializes the `StructureExcel` class with specified parameters. This method sets up the paths and reads the Excel file, preparing the internal dataframes used for structure parsing.

**Usage Example**:
```python
structure_excel = StructureExcel(structure_name="example_structure")
```

#### `get_heads`

**Signature**:
```python
def get_heads()
```

**Returns**:
- `list`: A list of identifiers for the head nodes in the structure.

**Description**:
Retrieves the list of head node identifiers from the loaded structure data. This method parses the 'GraphExecutor' sheet in the loaded Excel file to extract the list of head nodes.

**Usage Example**:
```python
head_nodes = structure_excel.get_heads()
```

#### `_reload_info_dict`

**Signature**:
```python
def _reload_info_dict(node_id)
```

**Parameters**:
- `node_id` (str): The identifier of the node to look up.

**Returns**:
- `dict`: A dictionary containing the properties and values for the specified node.

**Description**:
Retrieves detailed information about a specific node from the Excel file based on its identifier. This method looks up a node's information within the loaded Excel sheets and returns a dictionary containing all the relevant details.

**Usage Example**:
```python
info_dict = structure_excel._reload_info_dict("node_1")
```

#### `parse_agent`

**Signature**:
```python
def parse_agent(info_dict)
```

**Parameters**:
- `info_dict` (dict): A dictionary containing details about the agent node, including its class, structure ID, and output parser code.

**Returns**:
- `BaseAgent`: An initialized agent object.

**Description**:
Parses an agent node from the structure using the agent's specific details provided in a dictionary. This method creates an agent instance based on the information from the dictionary, which includes dynamically loading the output parser code.

**Usage Example**:
```python
agent = structure_excel.parse_agent(info_dict)
```

#### `parse_node`

**Signature**:
```python
def parse_node(info_dict)
```

**Parameters**:
- `info_dict` (dict): A dictionary containing node data, including the node type and associated properties.

**Returns**:
- `Node`: An instance of the node corresponding to the type specified in the `info_dict`.

**Description**:
Parses a node from its dictionary representation into a specific node type like `System`, `Instruction`, etc. This method determines the type of node from the info dictionary and uses the appropriate parsing method to create an instance of that node type.

**Usage Example**:
```python
node = structure_excel.parse_node(info_dict)
```

#### `get_next`

**Signature**:
```python
def get_next(node_id)
```

**Parameters**:
- `node_id` (str): The identifier of the node whose successors are to be found.

**Returns**:
- `list[str]`: A list of identifiers for the successor nodes.

**Description**:
Retrieves the list of identifiers for nodes that are directly connected via outgoing edges from the specified node. This method searches the 'Edges' DataFrame for all entries where the specified node is a head and returns a list of the tail node identifiers.

**Usage Example**:
```python
next_nodes = structure_excel.get_next("node_1")
```

#### `relate`

**Signature**:
```python
def relate(parent_node, node)
```

**Parameters**:
- `parent_node` (Node): The parent node in the relationship.
- `node` (Node): The child node in the relationship.

**Description**:
Establishes a relationship between two nodes in the structure based on the Excel data for edges. This method looks up the edge details connecting the two nodes and applies any conditions associated with the edge to the structure being rebuilt.

**Usage Example**:
```python
structure_excel.relate(parent_node, child_node)
```

#### `parse`

**Signature**:
```python
def parse(node_list, parent_node=None)
```

**Parameters**:
- `node_list` (list[str]): A list of node identifiers to be parsed.
- `parent_node` (Node, optional): The parent node to which the nodes in the list are connected.

**Description**:
Recursively parses a list of nodes and establishes their interconnections based on the Excel data. This method processes each node ID in the list, parsing individual nodes and relating them according to their connections defined in the Excel file.

**Usage Example**:
```python
structure_excel.parse(node_list)
```

#### `reload`

**Signature**:
```python
def reload()
```

**Description**:
Reloads the entire structure from the Excel file. This method initializes a new `GraphExecutor` and uses the Excel data to rebuild the entire structure, starting from the head nodes and recursively parsing and connecting all nodes defined within.

**Usage Example**:
```python
structure_excel.reload()
```
