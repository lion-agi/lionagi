
# LionAGI Edges Tutorial

## Introduction

This tutorial introduces the `Edge` class in the LionAGI framework, which is used to define and manage connections between `Component` nodes. Edges are essential for creating relationships and dependencies between different components in a system. This guide will cover the creation, manipulation, and usage of edges within the LionAGI framework.

## Table of Contents

1. [Creating Components and Edges](#creating-components-and-edges)
2. [Edge Attributes](#edge-attributes)

## Creating Components and Edges

To start working with edges, you first need to create `Component` instances that will act as the nodes in the graph. Then, you can create an `Edge` instance that connects these nodes.

### Example Usage

The following code demonstrates how to create two `Component` instances and an `Edge` instance connecting them.

```python
from lionagi.core.generic.abc import Component
from lionagi.core.generic import Edge

# Create two Component instances
node1 = Component()
node2 = Component()

# Create an Edge instance connecting node1 and node2
edge1 = Edge(head=node1, tail=node2)
```

## Edge Attributes

The `Edge` class includes several attributes that define the relationship between the connected nodes. These attributes include a unique identifier, creation timestamp, metadata, content, head, tail, condition, label, and bundle status.

### Example Usage

You can convert the edge to a dictionary to inspect its attributes.

```python
edge1.to_dict()
# Output:
# {'ln_id': '2252ef4f7b0509a5faee4d28c52b37e0',
#  'created': '2024-05-14T02:06:40.300575',
#  'metadata': {},
#  'content': None,
#  'head': 'ae581fde1783a854ed0f35875d2bb0d5',
#  'tail': 'd7e531e8b8b7cb67d38842ef0330ef23',
#  'condition': None,
#  'label': None,
#  'bundle': False}
```

### Printing Edge Attributes

You can print the attributes of the edge directly.

```python
edge1
# Output:
# ln_id         2252ef4f7b0509a5faee4d28c52b37e0
# created             2024-05-14T02:06:40.300575
# metadata                                    {}
# content                                   None
# head          ae581fde1783a854ed0f35875d2bb0d5
# tail          d7e531e8b8b7cb67d38842ef0330ef23
# condition                                 None
# label                                     None
# bundle                                   False
# class_name                                Edge
# dtype: object
```

This concludes the basic introduction to the `Edge` class in the LionAGI framework. By understanding these fundamental operations, you can effectively create and manage connections between components within your LionAGI-based systems.
