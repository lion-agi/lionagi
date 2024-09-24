
# LionAGI Graph Tutorial

## Introduction

This tutorial introduces the `Graph` and `Node` classes in the LionAGI framework, which are used to define and manage nodes and their relationships in a graph structure. This guide will cover the creation of nodes, adding nodes to a graph, establishing edges between nodes, and various methods to manipulate and query the graph.

## Table of Contents

1. [Creating Nodes and a Graph](#creating-nodes-and-a-graph)
2. [Checking Graph Properties](#checking-graph-properties)
3. [Adding Nodes and Edges](#adding-nodes-and-edges)
4. [Retrieving Nodes and Edges](#retrieving-nodes-and-edges)
5. [Displaying the Graph](#displaying-the-graph)
6. [Conclusion](#conclusion)

## Creating Nodes and a Graph

The first step is to create instances of the `Node` class and a `Graph` instance. Nodes represent the fundamental units in the graph, while the graph manages the collection of nodes and their relationships.

### Example Usage

The following code demonstrates how to create multiple `Node` instances and a `Graph` instance.

```python
from lionagi.core.generic import Graph, Node

# Create four Node instances
node1 = Node()
node2 = Node()
node3 = Node()
node4 = Node()

# Create a Graph instance
g = Graph()
```

## Checking Graph Properties

Before adding nodes or edges, you can check the initial properties of the graph, such as the number of nodes and internal edges.

### Example Usage

The following code demonstrates how to check the size of the graph and the number of internal edges.

```python
# The total number of nodes in the graph
g.size()
# Output: 0

# The total number of internal edges among the internal nodes
len(g.internal_edges)
# Output: 0
```

## Adding Nodes and Edges

You can add nodes to the graph and establish edges between them to define their relationships. Adding nodes does not create any edges by default.

### Example Usage

The following code demonstrates how to add nodes and edges to the graph.

```python
# Add nodes to the graph
g.add_node([node1, node2, node3, node4])

# The number of internal edges remains zero since no edges are added yet
len(g.internal_edges)
# Output: 0

# Add edges between the nodes
g.add_edge(node1, node2)
g.add_edge(node2, node3)
g.add_edge(node3, node4)

# The total number of internal edges after adding edges
len(g.internal_edges)
# Output: 3
```

## Retrieving Nodes and Edges

You can retrieve specific nodes, edges, and other properties from the graph.

### Example Usage

The following code demonstrates how to retrieve a node, get the edges of a node, and check if the graph is acyclic.

```python
# Retrieve a node by passing in a 
node5 = g.get_node(node2)
node5 == node2
# Output: True

# Get the number of edges for a specific node
len(g.get_node_edges(node1))
# Output: 1

# Get the number of head nodes in the graph
len(g.get_heads())
# Output: 1

# Check if the graph is acyclic
g.is_acyclic()
# Output: True
```

## Displaying the Graph

You can visualize the graph using the `display` method, which will provide a graphical representation of the nodes and their relationships.

### Example Usage

The following code demonstrates how to display the graph.

```python
# Display the graph
g.display()
```

This will generate a visual representation of the graph, showing the nodes and the edges connecting them.

## Conclusion

In this tutorial, we covered the basics of working with the `Graph` and `Node` classes from the LionAGI framework, including creating nodes and a graph, checking graph properties, adding nodes and edges, retrieving nodes and edges, and displaying the graph. By understanding these fundamental operations, you can effectively create and manage graphs within your LionAGI-based systems.
