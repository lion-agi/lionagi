
# LionAGI Nodes Tutorial

## Introduction

This tutorial introduces the `Node` class in the LionAGI framework, which is used to define and manage nodes in a graph structure. Nodes can have relationships with other nodes, forming a network of connected components. This guide will cover the creation, manipulation, and usage of nodes within the LionAGI framework.

## Table of Contents

1. [Creating Nodes](#creating-nodes)
2. [Establishing Relationships](#establishing-relationships)
3. [Node Attributes and Methods](#node-attributes-and-methods)
4. [Manipulating Node Relationships](#manipulating-node-relationships)

## Creating Nodes

The first step is to create instances of the `Node` class. Nodes are the fundamental units in a graph and can be related to each other.

### Example Usage

The following code demonstrates how to create multiple `Node` instances.

```python
from lionagi.core.generic import Node

# Create three Node instances
a, b, c = Node(), Node(), Node()
```

## Establishing Relationships

Nodes can have relationships with other nodes. These relationships can be either incoming or outgoing, indicating the direction of the connection.

### Example Usage

The following code demonstrates how to establish relationships between nodes.

```python
# Establish an outgoing relation from node 'a' to node 'b'
a.relate(b, "out")  # 'a' is the head, 'b' is the tail

# Establish an incoming relation to node 'a' from node 'c'
a.relate(c, "in")  # 'a' is the tail, 'c' is the head
```

## Node Attributes and Methods

Nodes have several attributes and methods to manage their relationships and other properties.

### Predecessors and Successors

You can retrieve the predecessors and successors of a node, which are the nodes connected by incoming and outgoing edges, respectively.

```python
# Get predecessors of node 'a'
a.predecessors
# Output: ['908ffd19146a7831d9b2d1a9892f8bfe']

# Get successors of node 'a'
a.successors
# Output: ['451711ff6d088d1480cedf949787955d']
```

### Printing Node Edges

You can print the edges of a node to inspect its connections.

```python
for i in a.edges:
    print(i)
# Output:
# ln_id         8040e746e68953ef7d38088146452ea1
# created             2024-05-14T02:09:33.304702
# metadata                                    {}
# content                                   None
# head          908ffd19146a7831d9b2d1a9892f8bfe
# tail          d5100be6f786f545931f321c32d167e5
# condition                                 None
# label                                     None
# bundle                                   False
# class_name                                Edge
# dtype: object
# ln_id         77869eedcdaba2a6aa21f5da74000ea2
# created             2024-05-14T02:09:33.304591
# metadata                                    {}
# content                                   None
# head          d5100be6f786f545931f321c32d167e5
# tail          451711ff6d088d1480cedf949787955d
# condition                                 None
# label                                     None
# bundle                                   False
# class_name                                Edge
# dtype: object
```

### Related Nodes

You can retrieve the nodes related to a specific node.

```python
a.related_nodes
# Output: ['451711ff6d088d1480cedf949787955d', '908ffd19146a7831d9b2d1a9892f8bfe']
```

### Node Relations

The `node_relations` attribute provides a detailed view of the relationships of a node.

```python
a.node_relations
# Output:
# {'out': {'451711ff6d088d1480cedf949787955d': [ln_id         77869eedcdaba2a6aa21f5da74000ea2
#    created             2024-05-14T02:09:33.304591
#    metadata                                    {}
#    content                                   None
#    head          d5100be6f786f545931f321c32d167e5
#    tail          451711ff6d088d1480cedf949787955d
#    condition                                 None
#    label                                     None
#    bundle                                   False
#    class_name                                Edge
#    dtype: object]},
#  'in': {'908ffd19146a7831d9b2d1a9892f8bfe': [ln_id         8040e746e68953ef7d38088146452ea1
#    created             2024-05-14T02:09:33.304702
#    metadata                                    {}
#    content                                   None
#    head          908ffd19146a7831d9b2d1a9892f8bfe
#    tail          d5100be6f786f545931f321c32d167e5
#    condition                                 None
#    label                                     None
#    bundle                                   False
#    class_name                                Edge
#    dtype: object]}}
```

### Counting Edges

You can count the number of edges connected to a node.

```python
len(a.edges)
# Output: 2
```

### Edges as DataFrame

The edges of a node can be represented as a pandas DataFrame for better visualization and analysis.

```python
a.edges.to_df()
# Output:
#                               ln_id                     created metadata  \
# 0  8040e746e68953ef7d38088146452ea1  2024-05-14T02:09:33.304702       {}   
# 1  77869eedcdaba2a6aa21f5da74000ea2  2024-05-14T02:09:33.304591       {}   
# 
#   content                              head                              tail  \
# 0    None  908ffd19146a7831d9b2d1a9892f8bfe  d5100be6f786f545931f321c32d167e5   
# 1    None  d5100be6f786f545931f321c32d167e5  451711ff6d088d1480cedf949787955d   
# 
#   condition label  bundle  
# 0      None  None   False  
# 1      None  None   False  
```

### Relations as DataFrame

You can also convert specific relations to a pandas DataFrame.

```python
a.relations["in"].to_df()
# Output:
#                               ln_id                     created metadata  \
# 0  8040e746e68953ef7d38088146452ea1  2024-05-14T02:09:33.304702       {}   
# 
#   content                              head                              tail  \
# 0    None  908ffd19146a7831d9b2d1a9892f8bfe  d5100be6f786f545931f321c32d167e5   
# 
#   condition label  bundle  
# 0      None  None   False  
```

## Manipulating Node Relationships

Nodes can be dynamically related and unrelated to other nodes.

### Unrelating Nodes

You can remove a relationship between nodes using the `unrelate` method.

```python
a.unrelate(b)
# Output: True

a.related_nodes
# Output: ['908ffd19146a7831d9b2d1a9892f8bfe']
```

### Node Summary

Printing a node provides a summary of its current state and relations.

```python
print(a)
# Output:
# ln_id        d5100be6f786f545931f321c32d167e5
# created            2024-05-14T02:09:33.301428
# metadata                                   {}
# content                                  None
# relations                              [1, 0]
# dtype: object
```

This concludes the tutorial on LionAGI nodes. By understanding these fundamental operations, you can effectively create and manage nodes and their relationships within your LionAGI-based systems.
