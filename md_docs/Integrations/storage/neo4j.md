
### Class: `Neo4j`

**Description**:
Manages interactions with a Neo4j graph database, facilitating the creation, retrieval, and management of graph nodes and relationships asynchronously. Provides methods to add various types of nodes and relationships, query the graph based on specific criteria, and enforce database constraints to ensure data integrity.

### Attributes:
- `database` (str): The name of the database to connect to.
- `driver` (neo4j.AsyncGraphDatabase.driver): The Neo4j driver for asynchronous database operations.

### Methods:

#### `__init__`

**Signature**:
```python
def __init__(self, uri, user, password, database)
```

**Parameters**:
- `uri` (str): The URI for the Neo4j database.
- `user` (str): The username for database authentication.
- `password` (str): The password for database authentication.
- `database` (str): The name of the database to use.

**Description**:
Initializes the Neo4j database connection using provided credentials and database information.

**Usage Example**:
```python
neo4j_service = Neo4j(uri="bolt://localhost:7687", user="neo4j", password="password", database="mydatabase")
```

#### `add_structure_node`

**Signature**:
```python
@staticmethod
async def add_structure_node(tx, node, name)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node` (dict): The properties of the node to be added, including 'ln_id' and 'timestamp'.
- `name` (str): The name of the structure, which is set on the node.

**Description**:
Asynchronously adds a structure node to the graph.

**Usage Example**:
```python
await neo4j_service.add_structure_node(tx, node={"ln_id": "1", "timestamp": "2023-01-01"}, name="MyStructure")
```

#### `add_system_node`

**Signature**:
```python
@staticmethod
async def add_system_node(tx, node)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node` (dict): The properties of the system node including 'ln_id', 'timestamp', 'content'.

**Description**:
Asynchronously adds a system node to the graph.

**Usage Example**:
```python
await neo4j_service.add_system_node(tx, node={"ln_id": "1", "timestamp": "2023-01-01", "content": "System content"})
```

#### `add_instruction_node`

**Signature**:
```python
@staticmethod
async def add_instruction_node(tx, node)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node` (dict): The properties of the instruction node including 'ln_id', 'timestamp', 'content'.

**Description**:
Asynchronously adds an instruction node to the graph.

**Usage Example**:
```python
await neo4j_service.add_instruction_node(tx, node={"ln_id": "1", "timestamp": "2023-01-01", "content": "Instruction content"})
```

#### `add_tool_node`

**Signature**:
```python
@staticmethod
async def add_tool_node(tx, node)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node` (dict): The properties of the tool node including 'ln_id', 'timestamp', 'function', 'parser'.

**Description**:
Asynchronously adds a tool node to the graph.

**Usage Example**:
```python
await neo4j_service.add_tool_node(tx, node={"ln_id": "1", "timestamp": "2023-01-01", "function": "tool_function", "parser": "tool_parser"})
```

#### `add_directiveSelection_node`

**Signature**:
```python
@staticmethod
async def add_directiveSelection_node(tx, node)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node` (dict): The properties of the directive selection node including 'ln_id', 'directive', 'directiveKwargs'.

**Description**:
Asynchronously adds a directive selection node to the graph.

**Usage Example**:
```python
await neo4j_service.add_directiveSelection_node(tx, node={"ln_id": "1", "directive": "directive_name", "directiveKwargs": "kwargs"})
```

#### `add_baseAgent_node`

**Signature**:
```python
@staticmethod
async def add_baseAgent_node(tx, node)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node` (dict): The properties of the agent node including 'ln_id', 'timestamp', 'structureId', 'outputParser'.

**Description**:
Asynchronously adds an agent node to the graph.

**Usage Example**:
```python
await neo4j_service.add_baseAgent_node(tx, node={"ln_id": "1", "timestamp": "2023-01-01", "structureId": "structure_1", "outputParser": "parser"})
```

#### `add_forward_edge`

**Signature**:
```python
@staticmethod
async def add_forward_edge(tx, edge)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `edge` (dict): The properties of the edge including 'ln_id', 'timestamp', 'head', 'tail', 'label', 'condition'.

**Description**:
Asynchronously adds a forward relationship between two nodes in the graph.

**Usage Example**:
```python
await neo4j_service.add_forward_edge(tx, edge={"ln_id": "1", "timestamp": "2023-01-01", "head": "head_node", "tail": "tail_node", "label": "label", "condition": "condition"})
```

#### `add_bundle_edge`

**Signature**:
```python
@staticmethod
async def add_bundle_edge(tx, edge)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `edge` (dict): The properties of the edge including 'ln_id', 'timestamp', 'head', 'tail', 'label', 'condition'.

**Description**:
Asynchronously adds a bundle relationship between two nodes in the graph.

**Usage Example**:
```python
await neo4j_service.add_bundle_edge(tx, edge={"ln_id": "1", "timestamp": "2023-01-01", "head": "head_node", "tail": "tail_node", "label": "label", "condition": "condition"})
```

#### `add_head_edge`

**Signature**:
```python
@staticmethod
async def add_head_edge(tx, structure)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `structure`: The structure node from which head relationships are established.

**Description**:
Asynchronously adds head relationships from a structure node to its head nodes.

**Usage Example**:
```python
await neo4j_service.add_head_edge(tx, structure={"ln_id": "1", "heads": ["head_1", "head_2"]})
```

#### `add_single_condition_cls`

**Signature**:
```python
@staticmethod
async def add_single_condition_cls(tx, condCls)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `condCls` (dict): The properties of the condition class node including 'className' and 'code'.

**Description**:
Asynchronously adds a condition class node to the graph.

**Usage Example**:
```python
await neo4j_service.add_single_condition_cls(tx, condCls={"class_name": "ConditionClass", "class": "class_code"})
```

#### `add_node`

**Signature**:
```python
async def add_node(self, tx, node_dict, structure_name)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node_dict` (dict): A dictionary where keys are node type strings and values are lists of node properties dictionaries.
- `structure_name` (str): The name of the structure to which these nodes belong.

**Description**:
Asynchronously adds various types of nodes to the Neo4j graph based on the provided dictionary of node lists.

**Usage Example**:
```python
await neo4j_service.add_node(tx, node_dict={"GraphExecutor": [node_1, node_2]}, structure_name="MyStructure")
```

#### `add_edge`

**Signature**:
```python
async def add_edge(self, tx, edge_list)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `edge_list` (list[dict]): A list of dictionaries where each dictionary contains properties of an edge.

**Description**:
Asynchronously adds edges to the Neo4j graph based on a list of edge properties.

**Usage Example**:
```python
await neo4j_service.add_edge(tx, edge_list=[edge_1, edge_2])
```

#### `add_condition_cls`

**Signature**:
```python
async def add_condition_cls(self, tx, edge_cls_list)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `edge_cls_list` (list[dict]): A list of dictionaries where each dictionary represents the properties of a condition class.

**Description**:
Asynchronously adds condition class nodes to the Neo4j graph.

**Usage Example**:
```python
await neo4j_service.add_condition_cls(tx, edge_cls_list=[cls_1, cls_2])
```

#### `check_id_constraint`

**Signature**:
```python
@staticmethod
async def check_id_constraint(tx)
```

**Parameters**:
- `tx`: The Neo4j transaction.

**Description**:
Asynchronously applies a unique constraint on the

 'ln_id' attribute for all nodes of type 'LionNode' in the graph.

**Usage Example**:
```python
await neo4j_service.check_id_constraint(tx)
```

#### `check_structure_name_constraint`

**Signature**:
```python
@staticmethod
async def check_structure_name_constraint(tx)
```

**Parameters**:
- `tx`: The Neo4j transaction.

**Description**:
Asynchronously applies a unique constraint on the 'name' attribute for all nodes of type 'Structure' in the graph.

**Usage Example**:
```python
await neo4j_service.check_structure_name_constraint(tx)
```

#### `store`

**Signature**:
```python
async def store(self, structure, structure_name)
```

**Parameters**:
- `structure`: The structure object containing the nodes and edges to be stored.
- `structure_name` (str): The name of the structure, used to uniquely identify it in the graph.

**Description**:
Asynchronously stores a structure and its components in the Neo4j graph.

**Usage Example**:
```python
await neo4j_service.store(structure, structure_name="MyStructure")
```

#### `match_node`

**Signature**:
```python
@staticmethod
async def match_node(tx, node_id)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node_id` (str): The unique identifier of the node to retrieve.

**Returns**:
- `dict`: A dictionary containing the properties of the node if found, otherwise `None`.

**Description**:
Asynchronously retrieves a node from the graph based on its identifier.

**Usage Example**:
```python
node = await neo4j_service.match_node(tx, node_id="1")
```

#### `match_structure_id`

**Signature**:
```python
@staticmethod
async def match_structure_id(tx, name)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `name` (str): The name of the structure to retrieve the identifier for.

**Returns**:
- `list`: A list containing the identifier(s) of the matching structure(s).

**Description**:
Asynchronously retrieves the identifier of a structure based on its name.

**Usage Example**:
```python
structure_id = await neo4j_service.match_structure_id(tx, name="MyStructure")
```

#### `head`

**Signature**:
```python
@staticmethod
async def head(tx, node_id)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node_id` (str): The identifier of the structure node whose head nodes are to be retrieved.

**Returns**:
- `list`: A list of dictionaries representing the properties and labels of each head node connected to the structure.

**Description**:
Asynchronously retrieves the head nodes associated with a structure node in the graph.

**Usage Example**:
```python
heads = await neo4j_service.head(tx, node_id="1")
```

#### `forward`

**Signature**:
```python
@staticmethod
async def forward(tx, node_id)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node_id` (str): The identifier of the node from which to retrieve forward relationships.

**Returns**:
- `list`: A list of dictionaries representing the properties and labels of each node connected by a forward relationship.

**Description**:
Asynchronously retrieves all forward relationships and their target nodes for a given node.

**Usage Example**:
```python
forwards = await neo4j_service.forward(tx, node_id="1")
```

#### `bundle`

**Signature**:
```python
@staticmethod
async def bundle(tx, node_id)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `node_id` (str): The identifier of the node from which to retrieve bundle relationships.

**Returns**:
- `list`: A list of dictionaries representing the properties and labels of each node connected by a bundle relationship.

**Description**:
Asynchronously retrieves all bundle relationships and their target nodes for a given node.

**Usage Example**:
```python
bundles = await neo4j_service.bundle(tx, node_id="1")
```

#### `match_condition_class`

**Signature**:
```python
@staticmethod
async def match_condition_class(tx, name)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `name` (str): The class name of the condition to retrieve the code for.

**Returns**:
- `str`: The code of the condition class if found, otherwise `None`.

**Description**:
Asynchronously retrieves the code for a condition class based on its class name.

**Usage Example**:
```python
condition_code = await neo4j_service.match_condition_class(tx, name="ConditionClass")
```

#### `locate_structure`

**Signature**:
```python
async def locate_structure(self, tx, structure_name: str = None, structure_id: str = None)
```

**Parameters**:
- `tx`: The Neo4j transaction.
- `structure_name` (str, optional): The name of the structure to locate.
- `structure_id` (str, optional): The unique identifier of the structure to locate.

**Returns**:
- `str`: The identifier of the located structure.

**Description**:
Asynchronously locates a structure by its name or ID in the Neo4j graph.

**Usage Example**:
```python
structure_id = await neo4j_service.locate_structure(tx, structure_name="MyStructure")
```

#### `get_heads`

**Signature**:
```python
async def get_heads(self, structure_name: str = None, structure_id: str = None)
```

**Parameters**:
- `structure_name` (str, optional): The name of the structure whose head nodes are to be retrieved.
- `structure_id` (str, optional): The identifier of the structure whose head nodes are to be retrieved.

**Returns**:
- `tuple`: A tuple containing the structure identifier and a list of dictionaries, each representing a head node connected to the structure.

**Description**:
Asynchronously retrieves the head nodes associated with a given structure in the graph.

**Usage Example**:
```python
structure_id, heads = await neo4j_service.get_heads(structure_name="MyStructure")
```

#### `get_bundle`

**Signature**:
```python
async def get_bundle(self, node_id)
```

**Parameters**:
- `node_id` (str): The identifier of the node from which bundle relationships are to be retrieved.

**Returns**:
- `list`: A list of dictionaries representing each node connected by a bundle relationship from the specified node.

**Description**:
Asynchronously retrieves all nodes connected by a bundle relationship to a given node in the graph.

**Usage Example**:
```python
bundles = await neo4j_service.get_bundle(node_id="1")
```

#### `get_forwards`

**Signature**:
```python
async def get_forwards(self, node_id)
```

**Parameters**:
- `node_id` (str): The identifier of the node from which forward relationships are to be retrieved.

**Returns**:
- `list`: A list of dictionaries representing each node connected by a forward relationship from the specified node.

**Description**:
Asynchronously retrieves all nodes connected by forward relationships to a given node in the graph.

**Usage Example**:
```python
forwards = await neo4j_service.get_forwards(node_id="1")
```

#### `get_condition_cls_code`

**Signature**:
```python
async def get_condition_cls_code(self, class_name)
```

**Parameters**:
- `class_name` (str): The name of the condition class whose code is to be retrieved.

**Returns**:
- `str`: The code of the condition class if found, or `None` if the class does not exist in the graph.

**Description**:
Asynchronously retrieves the code associated with a specified condition class from the Neo4j graph.

**Usage Example**:
```python
condition_code = await neo4j_service.get_condition_cls_code(class_name="ConditionClass")
```

#### `node_exist`

**Signature**:
```python
async def node_exist(self, node_id)
```

**Parameters**:
- `node_id` (str): The unique identifier of the node to check for existence.

**Returns**:
- `bool`: `True` if the node exists in the graph, `False` otherwise.

**Description**:
Asynchronously checks if a node with the specified identifier exists in the Neo4j graph.

**Usage Example**:
```python
exists = await neo4j_service.node_exist(node_id="1")
```
