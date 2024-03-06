---
tags:
  - API
  - BaseObj
  - LlamaIndex
created: 2024-02-26
completed: true
---


# DataNode API Reference

This document provides the API reference for the `DataNode` class, which extends `BaseNode` to include functionalities for integration with llama index and `langchain` formats. It aims to support serialization to and deserialization from these specific formats, facilitating interoperability with these systems.

## DataNode Class

> Child class of [[Base Component#^9e015a|BaseNode]]

The `DataNode` class represents a data node with additional methods for converting between DataNode instances and formats used by `llama index` and `langchain`, enabling seamless integration with these platforms.

### Serialization Methods

#### `to_llama_index(node_type=None, **kwargs) -> Any`

Converts the `DataNode` into a format recognized by the `llamaindex` [[TextNode]]  system.

**Parameters:**
- `node_type`: Optionally specifies the type of node for serialization.
- `**kwargs`: Additional keyword arguments for customization.

**Returns:** The llama index format representation of the `DataNode`.

#### `to_langchain(**kwargs) -> Any`

Serializes the `DataNode` into a document format utilized by `langchain` [[Documents]], making it compatible for use within `langchain` applications.

**Parameters:**
- `**kwargs`: Additional keyword arguments for customization.

**Returns:** The `langchain` document representation of the `DataNode`.

### Deserialization Methods

#### `from_llama_index(llama_node: Any, **kwargs) -> "DataNode"`

Creates a `DataNode` instance from a `llama index` node object, facilitating the conversion of data from llama index systems into the application's structure.

**Parameters:**
- `llama_node`: The `llama index` node object to convert.
- `**kwargs`: Additional keyword arguments for customization.

**Returns:** An instance of `DataNode`.

#### `from_langchain(lc_doc: Any) -> "DataNode"`

Generates a `DataNode` instance from a langchain document, enabling the integration of langchain_ data into the application.

**Parameters:**
- `lc_doc`: The langchain_ document to convert.

**Returns:** An instance of `DataNode`.
