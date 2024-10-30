
## Class: `Node`

**Description**:
`Node` is the base class for all nodes in the abstract syntax tree (AST). It serves as the parent class for specific types of nodes representing different constructs in the AST.

### Class: `IfNode`

**Description**:
`IfNode` represents an `IF` statement in the AST. It contains the condition to evaluate, the block of statements to execute if the condition is true, and an optional block of statements to execute if the condition is false.

**Attributes**:
- `condition (str)`: The condition to evaluate.
- `true_block (list)`: The block of statements to execute if the condition is true.
- `false_block (list, optional)`: The block of statements to execute if the condition is false.

**Usage Examples**:
```python
if_node = IfNode(condition="x > 10", true_block=["print('x is greater than 10')"], false_block=["print('x is not greater than 10')"])
print(if_node.condition)  # Output: x > 10
```

### Class: `ForNode`

**Description**:
`ForNode` represents a `FOR` loop in the AST. It contains the iterator variable, the collection to iterate over, and the block of statements to execute for each item in the collection.

**Attributes**:
- `iterator (str)`: The iterator variable.
- `collection (str)`: The collection to iterate over.
- `block (list)`: The block of statements to execute for each item in the collection.

**Usage Examples**:
```python
for_node = ForNode(iterator="i", collection="range(10)", block=["print(i)"])
print(for_node.iterator)  # Output: i
```

### Class: `TryNode`

**Description**:
`TryNode` represents a `TRY-EXCEPT` block in the AST. It contains the block of statements to execute in the `TRY` part and the block of statements to execute in the `EXCEPT` part.

**Attributes**:
- `try_block (list)`: The block of statements to execute in the `TRY` part.
- `except_block (list)`: The block of statements to execute in the `EXCEPT` part.

**Usage Examples**:
```python
try_node = TryNode(try_block=["x = 1 / y"], except_block=["print('Division by zero')"])
print(try_node.try_block)  # Output: ['x = 1 / y']
```

### Class: `ActionNode`

**Description**:
`ActionNode` represents an action in the AST. It contains the action to be performed.

**Attributes**:
- `action (str)`: The action to be performed.

**Usage Examples**:
```python
action_node = ActionNode(action="print('Hello, world!')")
print(action_node.action)  # Output: print('Hello, world!')
```

### Summary

The `Node` class and its derived classes (`IfNode`, `ForNode`, `TryNode`, `ActionNode`) provide a structure for representing different constructs in an abstract syntax tree (AST). Each derived class has specific attributes that define the respective construct's details, such as conditions, blocks of statements, iterators, collections, and actions. These classes can be used to build and manipulate the AST for various programming constructs.
