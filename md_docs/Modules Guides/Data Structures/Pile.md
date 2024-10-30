
# LionAGI Pile Tutorial

## Introduction

The `pile` object in the LionAGI framework is a versatile container used throughout the system to manage collections of nodes. This tutorial will guide you through the creation, manipulation, and various operations you can perform on a `pile`.

## Table of Contents

1. [Creating a Pile of Nodes](#creating-a-pile-of-nodes)
2. [Operations on Piles](#operations-on-piles)
   - [Addition](#addition)
   - [Subtraction](#subtraction)
   - [Containment](#containment)
   - [Inclusion](#inclusion)
   - [Exclusion](#exclusion)
   - [Getting and Setting Items](#getting-and-setting-items)
   - [Other Operations](#other-operations)

## Creating a Pile of Nodes

We start by importing the LionAGI package and creating nodes to add to a `pile`.

### Example Usage

The following code demonstrates how to create nodes and add them to a `pile`.

```python
import lionagi as li

# Create nodes with content
nodes1 = [li.Node(content=i) for i in ["A", "B", "C"]]
nodes2 = [li.Node(content=i) for i in ["D", "E", "F"]]

# Create piles with the nodes
p1 = li.pile(nodes1)
p2 = li.pile(nodes2)
```

## Operations on Piles

### Addition

You can combine two piles using the addition operator.

```python
(p1 + p2).to_df()
# Output:
#                               ln_id                     created metadata  \
# 0  fe113f7535d5fc7a13c2a39cf4988a85  2024-05-14T02:08:19.627716       {}
# 1  8ba59c0be228e9d6f95777ba4ce8fe0e  2024-05-14T02:08:19.627765       {}
# 2  0f11633a9f33e7866c6bd8c7c9d574ec  2024-05-14T02:08:19.627794       {}
# 3  465808ddaedb3584f7142e90795b5792  2024-05-14T02:08:19.627859       {}
# 4  1719cfdb3758af5e1d459ec2c6068f7a  2024-05-14T02:08:19.627884       {}
# 5  5db3bd0ce6cacbad02131cc06b51c8f6  2024-05-14T02:08:19.627907       {}
#
#   content                                          relations
# 0       A  {'in': {'ln_id': '9614a5b636f38b686b16a55e9a68...
# 1       B  {'in': {'ln_id': '168347c994109b7506c2a586e24a...
# 2       C  {'in': {'ln_id': 'dc68605d002dedf62e9918d4edbe...
# 3       D  {'in': {'ln_id': '858859716aad49bc9689281f49eb...
# 4       E  {'in': {'ln_id': '41bafe78e6bea8a923bf63558e20...
# 5       F  {'in': {'ln_id': '8cb744ddd688adbca33cc90ce3d7...
```

### Subtraction

Subtraction removes items of one pile from another.

```python
try:
    (p1 - p2).to_df()
except Exception as e:
    print(e)
# Output: Item not found. Item: '                              ln_id                     created metadata  \...
```

### Containment

You can check if one pile is contained within another.

```python
p1 in p2
# Output: False
```

### Inclusion

Inclusion adds the elements of one pile to another.

```python
print(p1.include(p2))
# Output: True

p1.to_df()
# Output:
#                               ln_id                     created metadata  \
# 0  fe113f7535d5fc7a13c2a39cf4988a85  2024-05-14T02:08:19.627716       {}
# 1  8ba59c0be228e9d6f95777ba4ce8fe0e  2024-05-14T02:08:19.627765       {}
# 2  0f11633a9f33e7866c6bd8c7c9d574ec  2024-05-14T02:08:19.627794       {}
# 3  1719cfdb3758af5e1d459ec2c6068f7a  2024-05-14T02:08:19.627884       {}
# 4  5db3bd0ce6cacbad02131cc06b51c8f6  2024-05-14T02:08:19.627907       {}
# 5  1fa0a179f4746aacc5885a9608d6ff0d  2024-05-14T02:08:19.711415       {}
#
#           content                                          relations
# 0  have a good day  {'in': {'ln_id': '54b6fbef6f8df99b0c4cc986c334...
# 1  have a good day  {'in': {'ln_id': '420b25b5b1cc011dec9b2b3b9328...
# 2                C  {'in': {'ln_id': 'dc68605d002dedf62e9918d4edbe...
# 3                E  {'in': {'ln_id': '41bafe78e6bea8a923bf63558e20...
# 4                F  {'in': {'ln_id': '8cb744ddd688adbca33cc90ce3d7...
# 5      hello world  {'in': {'ln_id': '60fc4e543b9f2d390000f02157b2...
```

### Exclusion

Exclusion removes the elements of one pile from another.

```python
print(p1.exclude(p2))
# Output: True

p1.to_df()
# Output:
#                               ln_id                     created metadata  \
# 0  fe113f7535d5fc7a13c2a39cf4988a85  2024-05-14T02:08:19.627716       {}
# 1  8ba59c0be228e9d6f95777ba4ce8fe0e  2024-05-14T02:08:19.627765       {}
# 2  0f11633a9f33e7866c6bd8c7c9d574ec  2024-05-14T02:08:19.627794       {}
# 3  1719cfdb3758af5e1d459ec2c6068f7a  2024-05-14T02:08:19.627884       {}
# 4  5db3bd0ce6cacbad02131cc06b51c8f6  2024-05-14T02:08:19.627907       {}
# 5  1fa0a179f4746aacc5885a9608d6ff0d  2024-05-14T02:08:19.711415       {}
#
#           content                                          relations
# 0  have a good day  {'in': {'ln_id': '54b6fbef6f8df99b0c4cc986c334...
# 1  have a good day  {'in': {'ln_id': '420b25b5b1cc011dec9b2b3b9328...
# 2                C  {'in': {'ln_id': 'dc68605d002dedf62e9918d4edbe...
# 3                E  {'in': {'ln_id': '41bafe78e6bea8a923bf63558e20...
# 4                F  {'in': {'ln_id': '8cb744ddd688adbca33cc90ce3d7...
# 5      hello world  {'in': {'ln_id': '60fc4e543b9f2d390000f02157b2...
```

### Getting and Setting Items

You can access and modify individual items in a `pile`.

#### Get Item

```python
aa = p2[0]
aa
# Output:
# ln_id        465808ddaedb3584f7142e90795b5792
# created            2024-05-14T02:08:19.627859
# metadata                                   {}
# content                                     D
# relations                              [0,

 0]
# dtype: object
```

#### Set Item

```python
p1[0] = li.Node(content="have a good day")
p1.to_df()
# Output:
#                               ln_id                     created metadata  \
# 0  099cf0b20fc92ad173e3d25ddb8f886c  2024-05-14T02:08:19.699664       {}
# 1  59e43c92f08df845e20d080bbc6866c2  2024-05-14T02:08:19.687793       {}
# 2  8ba59c0be228e9d6f95777ba4ce8fe0e  2024-05-14T02:08:19.627765       {}
# 3  0f11633a9f33e7866c6bd8c7c9d574ec  2024-05-14T02:08:19.627794       {}
# 4  1719cfdb3758af5e1d459ec2c6068f7a  2024-05-14T02:08:19.627884       {}
# 5  5db3bd0ce6cacbad02131cc06b51c8f6  2024-05-14T02:08:19.627907       {}
#
#           content                                          relations
# 0  have a good day  {'in': {'ln_id': '54b6fbef6f8df99b0c4cc986c334...
# 1  have a good day  {'in': {'ln_id': '420b25b5b1cc011dec9b2b3b9328...
# 2                B  {'in': {'ln_id': '168347c994109b7506c2a586e24a...
# 3                C  {'in': {'ln_id': 'dc68605d002dedf62e9918d4edbe...
# 4                E  {'in': {'ln_id': '41bafe78e6bea8a923bf63558e20...
# 5                F  {'in': {'ln_id': '8cb744ddd688adbca33cc90ce3d7...
```

### Other Operations

#### Inserting Nodes

You can insert nodes at specific positions in a pile.

```python
p1.insert(0, li.Node(content="have a good day"))
p1.to_df()
# Output:
#                               ln_id                     created metadata  \
# 0  099cf0b20fc92ad173e3d25ddb8f886c  2024-05-14T02:08:19.699664       {}
# 1  59e43c92f08df845e20d080bbc6866c2  2024-05-14T02:08:19.687793       {}
# 2  8ba59c0be228e9d6f95777ba4ce8fe0e  2024-05-14T02:08:19.627765       {}
# 3  0f11633a9f33e7866c6bd8c7c9d574ec  2024-05-14T02:08:19.627794       {}
# 4  1719cfdb3758af5e1d459ec2c6068f7a  2024-05-14T02:08:19.627884       {}
# 5  5db3bd0ce6cacbad02131cc06b51c8f6  2024-05-14T02:08:19.627907       {}
#
#           content                                          relations
# 0  have a good day  {'in': {'ln_id': '54b6fbef6f8df99b0c4cc986c334...
# 1  have a good day  {'in': {'ln_id': '420b25b5b1cc011dec9b2b3b9328...
# 2                B  {'in': {'ln_id': '168347c994109b7506c2a586e24a...
# 3                C  {'in': {'ln_id': 'dc68605d002dedf62e9918d4edbe...
# 4                E  {'in': {'ln_id': '41bafe78e6bea8a923bf63558e20...
# 5                F  {'in': {'ln_id': '8cb744ddd688adbca33cc90ce3d7...
```

#### Appending Nodes

You can append nodes to a pile.

```python
node = li.Node(content="hello world")
p1 += node
p1.to_df()
# Output:
#                               ln_id                     created metadata  \
# 0  099cf0b20fc92ad173e3d25ddb8f886c  2024-05-14T02:08:19.699664       {}
# 1  59e43c92f08df845e20d080bbc6866c2  2024-05-14T02:08:19.687793       {}
# 2  8ba59c0be228e9d6f95777ba4ce8fe0e  2024-05-14T02:08:19.627765       {}
# 3  0f11633a9f33e7866c6bd8c7c9d574ec  2024-05-14T02:08:19.627794       {}
# 4  1719cfdb3758af5e1d459ec2c6068f7a  2024-05-14T02:08:19.627884       {}
# 5  5db3bd0ce6cacbad02131cc06b51c8f6  2024-05-14T02:08:19.627907       {}
# 6  1fa0a179f4746aacc5885a9608d6ff0d  2024-05-14T02:08:19.711415       {}
#
#           content                                          relations
# 0  have a good day  {'in': {'ln_id': '54b6fbef6f8df99b0c4cc986c334...
# 1  have a good day  {'in': {'ln_id': '420b25b5b1cc011dec9b2b3b9328...
# 2                B  {'in': {'ln_id': '168347c994109b7506c2a586e24a...
# 3                C  {'in': {'ln_id': 'dc68605d002dedf62e9918d4edbe...
# 4                E  {'in': {'ln_id': '41bafe78e6bea8a923bf63558e20...
# 5                F  {'in': {'ln_id': '8cb744ddd688adbca33cc90ce3d7...
# 6      hello world  {'in': {'ln_id': '60fc4e543b9f2d390000f02157b2...
```

#### Removing Nodes

You can remove a node from a pile using the subtraction operator.

```python
p1 -= nodes1[1]  # the original sequence second element was B
p1.to_df()
# Output:
#                               ln_id                     created metadata  \
# 0  099cf0b20fc92ad173e3d25ddb8f886c  2024-05-14T02:08:19.699664       {}
# 1  59e43c92f08df845e20d080bbc6866c2  2024-05-14T02:08:19.687793       {}
# 2  0f11633a9f33e7866c6bd8c7c9d574ec  2024-05-14T02:08:19.627794       {}
# 3  1719cfdb3758af5e1d459ec2c6068f7a  2024-05-14T02:08:19.627884       {}
# 4  5db3bd0ce6cacbad02131cc06b51c8f6  2024-05-14T02:08:19.627907       {}
# 5  1fa0a179f4746aacc5885a9608d6ff0d  2024-05-14T02:08:19.711415       {}
#
#           content                                          relations
# 0  have a good day  {'in': {'ln_id': '54b6fbef6f8df99b0c4cc986c334...
# 1  have a good day  {'in': {'ln_id': '420b25b5b1cc011

dec9b2b3b9328...
# 2                C  {'in': {'ln_id': 'dc68605d002dedf62e9918d4edbe...
# 3                E  {'in': {'ln_id': '41bafe78e6bea8a923bf63558e20...
# 4                F  {'in': {'ln_id': '8cb744ddd688adbca33cc90ce3d7...
# 5      hello world  {'in': {'ln_id': '60fc4e543b9f2d390000f02157b2...
```

### Combining Empty Piles

You can combine two empty piles.

```python
a = li.pile()
b = li.pile()

list(a + b)
# Output: []
```

### Length of a List

```python
len([True, True])
# Output: 2
```

This completes the basic operations on the `pile` object in the LionAGI framework. You should now be able to create piles, perform various operations, and manipulate the data within them effectively.
