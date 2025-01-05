===========================
Graph
===========================

This module provides classes and logic for building and manipulating **directed
graphs** within LionAGI. By representing nodes and edges as **Elements** 
(with unique IDs, timestamps, and metadata), the system enables:

- Adding and removing nodes/edges dynamically,
- Tracking relationships between nodes (predecessors, successors),
- Enforcing optional edge conditions for traversal,
- Visualizing graphs via NetworkX (if installed).

Key classes include:

- :class:`Node`: The fundamental vertex, storing arbitrary content, metadata,
  and optional numeric embeddings.
- :class:`Edge`: Directed link from a **head** node to a **tail** node, 
  optionally associated with a :class:`EdgeCondition`.
- :class:`Graph`: An element containing a collection of internal nodes 
  and edges, plus mapping for quick in-/out-edge lookups.

These classes comply with LionAGI’s base **Relational** concept, so they can 
easily integrate with other LionAGI frameworks (e.g., :class:`~lionagi.protocols.generic.pile.Pile`).



--------------------
1. **Node** 
--------------------
.. module:: lionagi.protocols.graph.node
   :synopsis: Base class for nodes in a graph.

.. class:: Node
   :extends: Element, Relational

   Represents a graph node, storing:

   - :attr:`content`: Arbitrary data relevant to this node.
   - :attr:`embedding`: Optional list of floats (e.g., vector embeddings in ML).
   - :attr:`metadata`: (inherited) Additional dictionary fields.

   **Example**::

      from lionagi.protocols.graph.node import Node

      class MyNode(Node):
          pass

      node = MyNode(content="Hello Node", embedding=[0.1, 0.2, 0.3])
      print(node.id)          # => Unique ID
      print(node.content)     # => "Hello Node"
      print(node.embedding)   # => [0.1, 0.2, 0.3]


Adapters
~~~~~~~~
:class:`Node` integrates with LionAGI’s 
:class:`~lionagi.protocols.adapter.AdapterRegistry`, allowing easy 
serialization to JSON, CSV, etc. (via :meth:`adapt_to` and 
:meth:`adapt_from`).


--------------------
2. **Edge** 
--------------------
.. module:: lionagi.protocols.graph.edge
   :synopsis: Represents a directed link between two nodes.

.. class:: Edge
   :extends: Element

   A directed edge from :attr:`head` (node ID) to :attr:`tail` (node ID).
   Optionally includes:

   - :attr:`condition`: An :class:`EdgeCondition` controlling traversal.
   - :attr:`label`: One or more string labels describing this edge.
   - :attr:`properties`: A dictionary for any additional fields (like 
     weights, timestamps, or custom metadata).

   **Initialization**::

      edge = Edge(
         head=nodeA,
         tail=nodeB,
         condition=some_condition,
         label=["requires_login"]
      )

   **Example**::

      from lionagi.protocols.graph.edge import Edge, EdgeCondition

      cond = EdgeCondition(source="some param")
      edge = Edge(
          head="nodeA",
          tail="nodeB",
          condition=cond,
          label=["example"]
      )
      print(edge.label)        # => ["example"]
      print(edge.condition)    # => EdgeCondition(source="some param")


EdgeCondition
~~~~~~~~~~~~~
.. class:: EdgeCondition
   :extends: pydantic.BaseModel, Condition

   Optionally attached to an Edge, controlling whether that edge can 
   be traversed. Must implement an async :meth:`apply(...) -> bool` 
   method from the **Condition** interface, returning ``True``/``False`` 
   to indicate if traversal is permitted.


--------------------
3. **Graph** 
--------------------
.. module:: lionagi.protocols.graph.graph
   :synopsis: A container managing nodes/edges in a coherent graph structure.

.. class:: Graph
   :extends: Element, Relational

   Stores two main Piles:

   - :attr:`internal_nodes`: A :class:`~lionagi.protocols.generic.pile.Pile`
     of :class:`Node` objects.
   - :attr:`internal_edges`: A Pile of :class:`Edge` objects.

   A :attr:`node_edge_mapping` dictionary tracks incoming (“in”) and 
   outgoing (“out”) edges for each node ID, enabling quick lookups. 
   Some important methods:

   **Adding & Removing**:
   - :meth:`add_node(node)`: Add a :class:`Node`.
   - :meth:`add_edge(edge)`: Add an :class:`Edge`.
   - :meth:`remove_node(...)`: Remove a node and all edges referencing it.
   - :meth:`remove_edge(...)`: Remove a specific edge by object or ID.

   **Navigation**:
   - :meth:`get_predecessors(node)`: Return nodes that have an outgoing edge 
     to ``node``.
   - :meth:`get_successors(node)`: Return nodes that have an incoming edge 
     from ``node``.
   - :meth:`find_node_edge(node, direction='both')`: Return edges going 
     “in”, “out”, or “both.”

   **NetworkX Integration**:
   - :meth:`to_networkx(...)`: Build a NetworkX ``DiGraph`` from 
     the graph’s nodes/edges.
   - :meth:`display(...)`: Visualize the graph with matplotlib + NetworkX 
     (if installed).

   **Acyclic Check**:
   - :meth:`is_acyclic()`: Returns ``True`` if the graph has no cycles.

   **Example**::

      from lionagi.protocols.graph.node import Node
      from lionagi.protocols.graph.edge import Edge
      from lionagi.protocols.graph.graph import Graph

      # Create some nodes
      n1 = Node(content="Node1")
      n2 = Node(content="Node2")

      g = Graph()
      g.add_node(n1)
      g.add_node(n2)

      # Link n1 -> n2
      e12 = Edge(head=n1, tail=n2, label=["example-edge"])
      g.add_edge(e12)

      # Check successors
      successors_of_n1 = g.get_successors(n1)
      print([n.id for n in successors_of_n1])  # => [id of n2]


-----------------------
4. Putting It All Together
-----------------------
A typical usage pattern:

1. **Create** a :class:`Graph`.
2. **Add** nodes (each possibly storing content, embeddings, etc.).
3. **Add** edges referencing existing nodes, optionally labeling them 
   or providing an :class:`EdgeCondition`.
4. **Query** the graph for predecessors/successors, or remove nodes/edges 
   as needed.
5. **Visualize** (if you have networkx + matplotlib) with 
   :meth:`Graph.display(...)`.

If you want advanced logic on edges (like checking user permission or
some dynamic condition), implement an :class:`EdgeCondition` that returns 
``True`` or ``False`` in its :meth:`apply(...)``. Then, an AI or 
some controlling code can call :meth:`Edge.check_condition(...)`` 
to see if the path is allowed.

**Example** (short version):

.. code-block:: python

   from lionagi.protocols.graph.graph import Graph
   from lionagi.protocols.graph.node import Node
   from lionagi.protocols.graph.edge import Edge

   # Setup
   graph = Graph(name="MyGraph")

   # Make nodes
   nA = Node(content="A")
   nB = Node(content="B")
   graph.add_node(nA)
   graph.add_node(nB)

   # Make edge
   eAB = Edge(head=nA, tail=nB, label=["A->B"])
   graph.add_edge(eAB)

   # Retrieve successors
   print(graph.get_successors(nA))  
   # => Pile containing node B

   # Visualize if you have networkx + matplotlib
   # graph.display()


-----------
Summary
-----------
The LionAGI **graph** subsystem allows flexible, **ID-based** linking of 
nodes and edges, storing additional data (embedding, conditions, etc.)
as needed. Combined with concurrency (e.g., 
:class:`~lionagi.protocols.generic.processor.Processor`) or other 
LionAGI features, it forms the foundation for knowledge graphs, 
state machines, or agent-based world models.
