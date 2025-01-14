====================================================
``libs.nested`` Subpackage
====================================================

The ``lionagi.libs.nested`` subpackage offers a range of functions and utilities
for manipulating deeply nested Python data structures (dictionaries, lists, 
and mixed compositions). It supports:

- Flattening nested dictionaries/lists into a single-level representation
- Filtering nested structures by custom predicates
- Navigating or modifying deeply nested items (get/set/insert/pop)
- Merging multiple nested structures



-----------------------------
1) ``flatten.py``: Flattening
-----------------------------
.. module:: lionagi.libs.nested.flatten

This module provides a ``flatten`` function to convert nested structures into 
a flat dictionary, with keys representing the path (optionally joined by 
a separator).

.. function:: flatten(nested_structure, /, parent_key=(), sep="|", coerce_keys=True, dynamic=True, coerce_sequence=None, max_depth=None) -> dict[str, Any] | dict[tuple, Any]

   Recursively traverse a nested structure (dictionaries or lists) and produce 
   a single-level dictionary. The path to each leaf value is recorded as either 
   a string (by joining keys with ``sep``) or a tuple of keys/indices if 
   ``coerce_keys=False``.

   **Parameters**:
   
   - **nested_structure**: The data to flatten (dict, list, or any nested mixture).
   - **parent_key**: Internal usage; the base path (tuple) in recursion.
   - **sep** (str): The separator used to join keys when coerce_keys=True.
   - **coerce_keys** (bool): If True, the resulting dict keys are strings 
     joined by ``sep``. If False, they remain tuples.
   - **dynamic** (bool): Whether to treat sequences (lists) dynamically. 
     If True, flattens them similarly to dicts. 
   - **coerce_sequence** ({"dict","list",None}): Force any sequence to become 
     either a dict or remain a list in the flattened result.
   - **max_depth** (int|None): Limit the flattening recursion depth.

   **Returns**:
      A dictionary whose keys are the "paths" to each leaf, and values 
      the original leaf data.

   **Example**::

      >>> nested = {"a": 1, "b": {"c": 2, "d": [3,4]}}
      >>> flatten(nested)
      {'a': 1, 'b|c': 2, 'b|d|0': 3, 'b|d|1': 4}


-----------------------------
2) ``filter.py``: nfilter
-----------------------------
.. module:: lionagi.libs.nested.filter

Tools to filter nested structures by a predicate.

.. function:: nfilter(nested_structure, /, condition: Callable[[Any], bool]) -> dict | list

   Traverse a nested dict or list and remove items (or sub-branches) for which 
   ``condition(x)`` is False, preserving only those that pass. If a node is 
   itself a dict/list, it's kept if it passes or has children that pass.

   **Parameters**:

   - **nested_structure**: The dict/list to filter.
   - **condition** (Callable): A function returning True to keep the item, 
     False to remove.

   **Returns**:
      The filtered nested structure of the same type (dict or list).

   **Example**::
      
      >>> data = {"a": 1, "b": {"c": 2, "d": 3}, "e": [4,5,6]}
      >>> nfilter(data, lambda x: isinstance(x, int) and x > 2)
      {'b': {'d': 3}, 'e': [4, 5, 6]}


----------------------------
3) ``nget.py``: Nested Getter
----------------------------
.. module:: lionagi.libs.nested.nget

Retrieves a value from a nested structure by following a list of indices or keys.

.. function:: nget(nested_structure, /, indices: list[int|str], default=UNDEFINED) -> Any

   Follow the chain of keys/indices in a nested dict/list structure to retrieve 
   a final value. If at any point a key or index is invalid, return ``default`` 
   (or raise an error if no default is specified).

   **Parameters**:
   - **nested_structure**: The data to access.
   - **indices** (list): The chain of keys/indices to follow. 
   - **default**: Value to return if not found; if omitted and not found, 
     raises an error.

   **Returns**:
      The value at the nested location, or ``default``.

   **Example**::
      
      >>> data = {"a": {"b": [10, 20]}}
      >>> nget(data, ["a","b",1])
      20
      >>> nget(data, ["a","x"], default=None)
      None


-------------------------------
4) ``ninsert.py``: Nested Insert
-------------------------------
.. module:: lionagi.libs.nested.ninsert

Inserts a new value at a path within a nested structure, expanding the 
lists/dicts as necessary.

.. function:: ninsert(nested_structure, /, indices: list[str|int], value: Any) -> None

   Like a nested "insert" - if the path's container doesn't exist, 
   it creates empty dicts or lists automatically.

   **Parameters**:
   - **nested_structure**: The dict or list to modify.
   - **indices** (list): The chain of keys/indices specifying the insertion path.
   - **value**: The new value to insert.

   **Example**::
      
      >>> data = {}
      >>> ninsert(data, ["a", 0], 99)
      >>> data
      {'a': [99]}


-----------------------------
5) ``nmerge.py``: Merging
-----------------------------
.. module:: lionagi.libs.nested.nmerge

Merge multiple nested dictionaries or lists into a single structure, 
handling collisions and optionally sorting lists.

.. function:: nmerge(nested_structure, /, overwrite=False, dict_sequence=False, sort_list=False, custom_sort=None) -> dict|list

   Given a list of homogeneously typed items (all dicts or all lists), 
   merges them into one dictionary or list. For dicts, can combine or 
   overwrite duplicates. For lists, concatenates (and can optionally sort).

   **Parameters**:
   - **nested_structure** (list[dict|list]): The items to merge.
   - **overwrite** (bool): If True, later dict keys overwrite earlier ones.
   - **dict_sequence** (bool): If True and not overwriting, assign unique 
     keys for collisions.
   - **sort_list** (bool): Sort the merged list if merging lists.
   - **custom_sort** (Callable|None): A custom comparator or sort key.

   **Returns**:
   - The merged dictionary or list.

   **Example**::
      
      >>> dicts = [{"a":1}, {"b":2}, {"a":3}]
      >>> nmerge(dicts)
      {'a': [1, 3], 'b': 2}
      >>> nmerge(dicts, overwrite=True)
      {'a': 3, 'b': 2}

      >>> lists = [[1,2],[3,1]]
      >>> nmerge(lists, sort_list=True)
      [1, 1, 2, 3]


-----------------------------
6) ``npop.py``: Nested Pop
-----------------------------
.. module:: lionagi.libs.nested.npop

Removes and returns a value from a nested structure, by path. 
Analogous to a standard dict.pop() or list.pop(), but nested.

.. function:: npop(input_, /, indices, default=UNDEFINED) -> Any

   Traverse the nested dict/list using *indices* and pop the final item 
   (remove from parent container). If not found, return *default* if given, 
   else raise KeyError/IndexError.

   **Parameters**:
   - **input_** (dict|list): The data structure to pop from.
   - **indices** (str|int|Sequence[str|int]): Path to the item.
   - **default**: If provided, returned when the path doesn't exist.

   **Returns**:
   - The removed item's value.

   **Example**::
      
      >>> data = {"x": [10, 20]}
      >>> npop(data, ["x", 1])
      20
      >>> data
      {'x': [10]}


-----------------------------
7) ``nset.py``: Nested Set
-----------------------------
.. module:: lionagi.libs.nested.nset

Set or overwrite a value in a nested structure at a specified path.

.. function:: nset(nested_structure, /, indices, value) -> None

   Like nget, but modifies the final location to *value*. Creates intermediate 
   dicts/lists if needed.

   **Parameters**:
   - **nested_structure** (dict|list): The data to modify.
   - **indices** (Sequence[str|int]): The path of keys/indices.
   - **value** (Any): The value to store.

   **Example**::
      
      >>> data = {"a": {"b": [10, 20]}}
      >>> nset(data, ["a","b",1], 99)
      >>> data
      {'a': {'b': [10, 99]}}


----------------------------------
8) ``utils.py``: Internal Helpers
----------------------------------
.. module:: lionagi.libs.nested.utils

Contains internal helper routines for index manipulation and structural checks.

- **is_homogeneous**, **is_same_dtype**, **is_structure_homogeneous**: 
  For checking uniform types in containers.
- **deep_update**: Recursively update one dictionary with another.
- **get_target_container**: Get the immediate container for the final index 
  in a nested path.
- **ensure_list_index**: Helper to expand a list until an index is valid.

These are mostly used internally by the other nested modules, but can also 
be used if you need to detect homogeneous structures or create missing slots 
in a list.


-----------
Usage Example
-----------
Below is a short demonstration combining several features:

.. code-block:: python

   from lionagi.libs.nested.flatten import flatten
   from lionagi.libs.nested.nfilter import nfilter
   from lionagi.libs.nested.nget import nget
   from lionagi.libs.nested.nset import nset
   from lionagi.libs.nested.npop import npop

   data = {
       "a": 1,
       "b": {
           "c": 2,
           "d": [10, 20, 30],
       },
   }

   # Flatten:
   flat = flatten(data)
   print(flat)
   # {"a": 1, "b|c": 2, "b|d|0": 10, "b|d|1": 20, "b|d|2": 30}

   # Filter: keep only values > 10
   filtered = nfilter(data, lambda x: isinstance(x, int) and x > 10)
   # => {"b": {"d": [20,30]}}

   # nget: get data["b"]["d"][1] => 20
   val = nget(data, ["b","d",1])
   # val = 20

   # nset: data["b"]["c"] = 99
   nset(data, ["b","c"], 99)

   # npop: remove data["b"]["d"][0] => returns 10
   popped = npop(data, ["b","d",0])
   # data is now {"a": 1, "b": {"c": 99, "d": [20,30]}}

This subpackage makes it simple to deeply manipulate nested dictionaries 
and lists without cumbersome loops or repeated checks.
