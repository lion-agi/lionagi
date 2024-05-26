
### Functions: `_output_excel`, `to_excel`

**Description**:
These functions handle the conversion of structure data into an Excel workbook. The data includes detailed node and edge information from a given structure, with each type of node and edge written to separate sheets in the Excel file.

### Function: `_output_excel`

**Signature**:
```python
def _output_excel(
    node_list,
    node_dict,
    edge_list,
    edge_cls_list,
    structure_name,
    dir="structure_storage",
)
```

**Parameters**:
- `node_list` (list): A list of dictionaries where each dictionary contains attributes of a single node.
- `node_dict` (dict): A dictionary of lists where each key represents a node type and the value is a list of node attributes for nodes of that type.
- `edge_list` (list): A list of dictionaries where each dictionary contains attributes of a single edge.
- `edge_cls_list` (list): A list of dictionaries where each dictionary contains attributes of edge conditions.
- `structure_name` (str): The base name for the output Excel file. The '.xlsx' extension will be added automatically if not included.
- `dir` (str): The directory where the Excel file will be saved. Defaults to "structure_storage".

**Returns**:
- `None`: This function does not return a value but writes data directly to an Excel workbook.

**Raises**:
- `ImportError`: If the required 'openpyxl' library is not installed, which is necessary for pandas to write Excel files.

**Description**:
Writes provided node and edge data into multiple sheets of a single Excel workbook. This helper function takes lists and dictionaries of nodes and edges, converts them into pandas DataFrames, and then writes each DataFrame to a distinct sheet in an Excel workbook. This includes a separate sheet for each type of node and edge, as well as edge conditions if they exist.

**Usage Example**:
```python
node_list = [...]  # list of node dictionaries
node_dict = {...}  # dictionary of node type lists
edge_list = [...]  # list of edge dictionaries
edge_cls_list = [...]  # list of edge condition dictionaries

_output_excel(node_list, node_dict, edge_list, edge_cls_list, structure_name="my_structure")
```

### Function: `to_excel`

**Signature**:
```python
def to_excel(structure, structure_name, dir="structure_storage")
```

**Parameters**:
- `structure`: An object representing the structure to be serialized. This should have methods to return lists of nodes and edges suitable for output.
- `structure_name` (str): The base name of the output Excel file. The '.xlsx' extension will be added automatically if not included.
- `dir` (str): The directory where the Excel file will be saved. Defaults to "structure_storage".

**Returns**:
- `None`: This function does not return a value but outputs an Excel workbook with multiple sheets.

**Description**:
Converts a structure into a series of Excel sheets within a single workbook. This function processes the specified structure to extract detailed node and edge information, including conditions if applicable. These details are then saved into separate sheets within an Excel workbook for nodes, edges, and any edge conditions.

**Usage Example**:
```python
structure = ...  # some structure object
to_excel(structure, structure_name="my_structure")
```

### Detailed Examples

#### Example for `_output_excel`

```python
import pandas as pd

node_list = [
    {"ln_id": "1", "timestamp": "2023-05-23T10:00:00", "type": "System"},
    {"ln_id": "2", "timestamp": "2023-05-23T10:05:00", "type": "Instruction"}
]
node_dict = {
    "System": [{"ln_id": "1", "timestamp": "2023-05-23T10:00:00", "content": "System content"}],
    "Instruction": [{"ln_id": "2", "timestamp": "2023-05-23T10:05:00", "content": "Instruction content"}]
}
edge_list = [
    {"ln_id": "e1", "timestamp": "2023-05-23T10:10:00", "head": "1", "tail": "2", "label": "connects"}
]
edge_cls_list = [
    {"class_name": "Condition1", "class": "class Condition1: pass"}
]

_output_excel(node_list, node_dict, edge_list, edge_cls_list, structure_name="my_structure")
```

#### Example for `to_excel`

```python
class MockStructure:
    def get_nodes(self):
        return [
            {"ln_id": "1", "timestamp": "2023-05-23T10:00:00", "type": "System"},
            {"ln_id": "2", "timestamp": "2023-05-23T10:05:00", "type": "Instruction"}
        ]
    
    def get_edges(self):
        return [
            {"ln_id": "e1", "timestamp": "2023-05-23T10:10:00", "head": "1", "tail": "2", "label": "connects"}
        ]

structure = MockStructure()
to_excel(structure, structure_name="my_structure")
```
