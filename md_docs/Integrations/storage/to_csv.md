
### Functions: `_output_csv`, `to_csv`

**Description**:
These functions handle the conversion of structure data into CSV files and compress them into a ZIP archive. The data includes detailed node and edge information from a given structure.

### Function: `_output_csv`

**Signature**:
```python
def _output_csv(
    node_list, node_dict, edge_list, edge_cls_list, zipname="structure_storage"
)
```

**Parameters**:
- `node_list` (list): A list of dictionaries where each dictionary contains attributes of a single node.
- `node_dict` (dict): A dictionary of lists where each key represents a node type and the value is a list of node attributes for nodes of that type.
- `edge_list` (list): A list of dictionaries where each dictionary contains attributes of a single edge.
- `edge_cls_list` (list): A list of dictionaries where each dictionary contains attributes of edge conditions.
- `zipname` (str): The base name for the output ZIP file that will store the CSV files.

**Returns**:
- `None`: This function does not return a value but outputs a ZIP file containing the CSVs.

**Description**:
Writes provided node and edge data into multiple CSV files and compresses them into a ZIP archive. This helper function takes lists and dictionaries of nodes and edges, converts them to pandas DataFrames, and then writes each DataFrame to a CSV file stored inside a ZIP archive. This includes a separate CSV for each type of node and edge, as well as edge conditions if they exist.

**Usage Example**:
```python
node_list = [...]  # list of node dictionaries
node_dict = {...}  # dictionary of node type lists
edge_list = [...]  # list of edge dictionaries
edge_cls_list = [...]  # list of edge condition dictionaries

_output_csv(node_list, node_dict, edge_list, edge_cls_list, zipname="my_structure")
```

### Function: `to_csv`

**Signature**:
```python
def to_csv(structure, filename="structure_storage")
```

**Parameters**:
- `structure`: An object representing the structure to be serialized. This structure should have methods to return lists of nodes and edges.
- `filename` (str): The base name of the output ZIP file that will store the CSV files.

**Returns**:
- `None`: This function does not return a value but outputs a ZIP file containing CSVs.

**Description**:
Converts a structure into a series of CSV files and stores them in a compressed ZIP archive. This function processes a given structure to extract detailed node and edge information, including conditions if applicable. These details are then saved into separate CSV files for nodes, edges, and any edge conditions, which are subsequently bundled into a ZIP file.

**Usage Example**:
```python
structure = ...  # some structure object
to_csv(structure, filename="my_structure")
```

