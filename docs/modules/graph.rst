.. _lionagi_protocols_graph:

=====================================================
Node, Edge, and Graph
=====================================================
.. module:: lionagi.protocols.graph
   :synopsis: Provides relational abstractions for nodes, edges, and graphs.

Overview
--------
This documentation covers the **graph** structures in LionAGI, comprising 
individual :class:`Node` objects, :class:`Edge` objects that link them, and 
the overarching :class:`Graph` class that manages these relationships. Also 
included is an :class:`EdgeCondition` mechanism for conditional traversal.

Contents
--------
.. contents::
   :local:
   :depth: 2


EdgeCondition
-------------
.. class:: EdgeCondition
   :module: lionagi.protocols.graph.edge

   **Inherits from**: :class:`pydantic.BaseModel`, :class:`~lionagi.protocols._concepts.Condition`

   A **condition** that can be attached to an :class:`Edge` to control or 
   constrain its traversability. This class also integrates with Pydantic for 
   data validation and serialization.

   Attributes
   ----------
   source : Any
       The source object or data used for evaluating the condition.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.graph.edge import EdgeCondition

       class CustomCondition(EdgeCondition):
           async def apply(self, *args, **kwargs) -> bool:
               # implement custom logic here
               return True


Edge
----
.. class:: Edge(Element)
   :module: lionagi.protocols.graph.edge

   **Inherits from**: :class:`~lionagi.protocols.generic.element.Element`

   Represents a **directed connection** from a head node to a tail node in a
   LionAGI graph. An optional :attr:`condition` determines if traversal is 
   allowed. Additional metadata (like :attr:`label`) or properties can be 
   stored in :attr:`properties`.

   Attributes
   ----------
   head : IDType
       The ID of the head node. 
   tail : IDType
       The ID of the tail node.
   properties : dict[str, Any]
       A dictionary holding additional properties, such as labels or 
       an :class:`EdgeCondition`.

   Properties
   ----------
   .. attribute:: label
      :type: list[str] | None

      Read or set a list of labels describing this edge.

   .. attribute:: condition
      :type: EdgeCondition | None

      A condition that determines if this edge is traversable. If None, 
      traversal is unrestricted.

   Methods
   -------
   .. method:: check_condition(*args, **kwargs) -> bool
      :async:

      Evaluates the :attr:`condition` (if any). Returns True if 
      no condition is assigned or if the condition passes.

   .. method:: update_property(key: str, value: Any) -> None

      Adds or updates a custom property in :attr:`properties`.

   .. method:: update_condition_source(source: Any) -> None

      Updates the :attr:`.source` field in the assigned :attr:`condition` 
      without replacing the entire condition object.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.graph.edge import Edge, EdgeCondition

       edge_condition = EdgeCondition(source="some_source")
       edge = Edge(head=my_head_node, tail=my_tail_node, condition=edge_condition, label=["friendship"])
       # edge now connects two nodes with a condition and a descriptive label.


Node
----
.. class:: Node(Element, Relational)
   :module: lionagi.protocols.graph.node

   **Inherits from**: :class:`~lionagi.protocols.generic.element.Element`, :class:`~lionagi.protocols._concepts.Relational`

   A **graph node** that can store arbitrary content, an optional numeric 
   embedding, and metadata in :attr:`metadata`. Nodes integrate with the 
   LionAGI adapter system, enabling easy import/export to JSON, pandas 
   Series, etc.

   Attributes
   ----------
   content : Any
       Arbitrary payload or data associated with this node.
   embedding : list[float] | None
       An optional vector representation (e.g., for search or similarity).

   Methods
   -------
   .. classmethod:: adapt_to(obj_key: str, /, many: bool = False, **kwargs) -> Any

      Converts this node to a specified format using a registered adapter.

   .. classmethod:: adapt_from(obj: Any, obj_key: str, /, many: bool = False, **kwargs) -> Node

      Constructs a node from an external representation, possibly returning
      a subclass if ``lion_class`` data is present.

   .. classmethod:: list_adapters() -> list[str]

      Lists all available adapter keys for node conversions.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.graph.node import Node

       class PersonNode(Node):
           pass

       person = PersonNode(content={"name": "Alice"}, embedding=[0.1, 0.2, 0.3])
       print(person.content)   # => {'name': 'Alice'}
       print(person.embedding) # => [0.1, 0.2, 0.3]


Graph
-----
.. class:: Graph(Element, Relational)
   :module: lionagi.protocols.graph.graph

   **Inherits from**: :class:`~lionagi.protocols.generic.element.Element`, :class:`~lionagi.protocols._concepts.Relational`

   Represents an entire **directed graph** of :class:`Node` and :class:`Edge` objects. 
   Internally, it uses two :class:`~lionagi.protocols.generic.pile.Pile` instances 
   (one for nodes, one for edges) and a `node_edge_mapping` for quick lookups.

   Attributes
   ----------
   internal_nodes : Pile[Node]
       Stores all nodes in the graph.
   internal_edges : Pile[Edge]
       Stores all edges in the graph.
   node_edge_mapping : dict
       Maps each node ID to its incoming and outgoing edges for quick access.

   Methods
   -------
   .. method:: add_node(node: Relational) -> None

      Inserts a node into the graph. Raises :exc:`RelationError` if invalid 
      or already present.

   .. method:: add_edge(edge: Edge) -> None

      Inserts an edge into the graph, linking two existing nodes. 
      Raises :exc:`RelationError` if invalid or if referenced nodes 
      are not found.

   .. method:: remove_node(node: ID[Node].Ref) -> None

      Removes a node and all associated edges from the graph.

   .. method:: remove_edge(edge: Edge | str) -> None

      Removes a specific edge by object or ID.

   .. method:: find_node_edge(node: Any, direction: Literal["both", "in", "out"] = "both") -> list[Edge]

      Finds edges connected to the given node in a specified direction.

   .. method:: get_heads() -> Pile[Node]

      Returns all nodes with no incoming edges (i.e., “head” nodes of subgraphs).

   .. method:: get_predecessors(node: Node) -> Pile[Node]

      Retrieves nodes that point to the given node.

   .. method:: get_successors(node: Node) -> Pile[Node]

      Retrieves nodes that are pointed to by the given node.

   .. method:: to_networkx(**kwargs) -> Any

      Converts this graph to a `networkx.DiGraph` object, including node 
      and edge properties.

   .. method:: display(node_label="lion_class", edge_label="label", draw_kwargs={}, **kwargs) -> None

      Visualizes the graph using networkx and matplotlib (if installed).

   .. method:: is_acyclic() -> bool

      Checks whether the graph has any cycles. Returns True if acyclic.

   Dunder Methods
   --------------
   .. method:: __contains__(item: object) -> bool

      Checks if a given node or edge is in the graph.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.graph.node import Node
       from lionagi.protocols.graph.edge import Edge
       from lionagi.protocols.graph.graph import Graph

       g = Graph()
       node_a, node_b = Node(), Node()
       g.add_node(node_a)
       g.add_node(node_b)

       e = Edge(head=node_a, tail=node_b, label=["relation"])
       g.add_edge(e)

       print(g.get_heads())  # node_a is a "head" if no inbound edges
       print(g.is_acyclic()) # likely True unless you create a cycle

File Locations
--------------
- **EdgeCondition** and **Edge**:  
  ``lionagi/protocols/graph/edge.py``  

- **Node**:  
  ``lionagi/protocols/graph/node.py``  

- **Graph**:  
  ``lionagi/protocols/graph/graph.py``  

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
