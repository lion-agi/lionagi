
# LionAGI Progression Tutorial

## Introduction

This tutorial introduces the `progression` class in the LionAGI framework, which is used to define and manage sequences of nodes. The `progression` class allows for the creation, manipulation, and combination of node sequences, providing a flexible way to handle ordered collections of nodes.

## Table of Contents

1. [Creating a Progression](#creating-a-progression)
2. [Extending a Progression](#extending-a-progression)
3. [Indexing and Slicing](#indexing-and-slicing)
4. [Containment Check](#containment-check)
5. [Adding and Removing Elements](#adding-and-removing-elements)
6. [Iteration](#iteration)
7. [Combination and Comparison](#combination-and-comparison)
8. [Conclusion](#conclusion)

## Creating a Progression

The first step is to create instances of the `progression` class. A progression is an ordered collection of `Node` objects.

### Example Usage

The following code demonstrates how to create a `progression` instance with multiple `Node` objects.

```python
from lionagi.core.generic import progression, Node

# Create a generator for Node objects
nodes = (Node() for _ in range(5))

# Create a progression with the nodes
p = progression(nodes)

# Check the order of nodes in the progression
p.order
# Output: ['6ba9f6930f3cbc962539c1a5bc72232a', '21be8b61b3493dedcba498427ae7070e', '288670e1de7c0a1bf863e7faa71999e6', '6493dbd31ee331cd7459fedbd2ef4f57', 'e7e8b7f37734f867c6f059813ec2c84e']
```

## Extending a Progression

You can add single or multiple nodes to an existing progression.

### Example Usage

The following code demonstrates how to extend a progression with additional nodes.

```python
# Add a single node to the progression
cc = Node()
p.extend(cc)

# Add multiple nodes at once
cc, dd, ee = Node(), Node(), Node()
p.extend([cc, dd, ee])
```

## Indexing and Slicing

Progressions support indexing and slicing to access specific elements or sub-sequences.

### Example Usage

The following code demonstrates how to index and slice a progression.

```python
# Access a specific element in the progression
p[0]
# Output: '99bc24161ae23c8424d28bcdc6e11bfb'

# Slice the progression to get a sub-sequence of nodes
p[1:5]
# Output: ['21be8b61b3493dedcba498427ae7070e', '288670e1de7c0a1bf863e7faa71999e6', '6493dbd31ee331cd7459fedbd2ef4f57', 'e7e8b7f37734f867c6f059813ec2c84e']
```

## Containment Check

You can check if a node or a sequence of nodes exists in the progression.

### Example Usage

The following code demonstrates how to perform containment checks.

```python
# Check if a node exists in the progression
cc in p
# Output: True

# Check if a list of nodes exists in the progression
[cc, dd] in p
# Output: True
```

## Adding and Removing Elements

You can append or remove nodes from the progression using addition and subtraction operations.

### Example Usage

The following code demonstrates how to add and remove elements from a progression.

```python
# Append a node to the progression
p += dd
len(p)
# Output: 10

# Remove a node from the progression
p -= cc
len(p)
# Output: 9

cc in p
# Output: False

# Use the exclude method to remove a node
p.exclude(cc)
cc in p
# Output: False
```

## Iteration

You can iterate through the nodes in a progression.

### Example Usage

The following code demonstrates how to iterate through a progression.

```python
for node in p:
    print(node)
# Output:
# 99bc24161ae23c8424d28bcdc6e11bfb
# 21be8b61b3493dedcba498427ae7070e
# 288670e1de7c0a1bf863e7faa71999e6
# 6493dbd31ee331cd7459fedbd2ef4f57
# e7e8b7f37734f867c6f059813ec2c84e
# 5b629cda276e94c97f081ecde9a9c108
# 28834285955e63ebeab616ad5c692bcb
# b0bf6fbe09d76bd7c1e08578001071e9
# 7a1caa75dcf3987c9b7a5ca6cd8d40ce
```

## Combination and Comparison

Progressions can be combined and compared with other progressions.

### Example Usage

The following code demonstrates how to combine and compare progressions.

```python
# Combine two progression objects
p2 = progression()
for _ in range(5):
    p2 += Node()

combined = p + p2
len(combined)
# Output: 14

# Check if the combination is commutative
p + p2 == p2 + p
# Output: False

# Check if adding a progression to itself is consistent
p + p == p + p
# Output: True
```

## Conclusion

In this tutorial, we covered the basics of working with the `progression` class from the LionAGI framework, including creation, extending with nodes, indexing, slicing, containment checks, adding and removing elements, iteration, and combination. By understanding these fundamental operations, you can effectively utilize the `progression` class in your Python projects.

---
