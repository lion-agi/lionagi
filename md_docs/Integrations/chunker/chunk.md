
### Functions: `datanodes_convert`, `text_chunker`, `chunk`, `_self_defined_chunker`, `_llama_index_chunker`, `_langchain_chunker`, `_plain_chunker`

**Description**:
These functions provide utilities for converting, chunking, and processing documents using various chunker types and conversion functions. They support different chunking strategies and integration with external libraries like Langchain and LlamaIndex.

### Function: `datanodes_convert`

**Signature**:
```python
def datanodes_convert(documents, chunker_type)
```

**Parameters**:
- `documents` (list): List of documents to be converted.
- `chunker_type` (ChunkerType): The type of chunker to convert the documents to.

**Returns**:
- `list`: The converted documents.

**Description**:
Converts documents to the specified chunker type. Depending on the chunker type, each document is converted using the appropriate method.

**Usage Example**:
```python
documents = [Node(...), Node(...)]
converted_docs = datanodes_convert(documents, ChunkerType.LLAMAINDEX)
```

### Function: `text_chunker`

**Signature**:
```python
def text_chunker(documents, args, kwargs)
```

**Parameters**:
- `documents` (list): List of documents to be chunked.
- `args` (tuple): Positional arguments for the chunking function.
- `kwargs` (dict): Keyword arguments for the chunking function.

**Returns**:
- `pile`: A pile of chunked Node instances.

**Description**:
Chunks text documents into smaller pieces using the specified arguments and keyword arguments for the chunking function.

**Usage Example**:
```python
documents = [Node(...), Node(...)]
chunked_docs = text_chunker(documents, args, kwargs)
```

### Function: `chunk`

**Signature**:
```python
def chunk(
    docs,
    field: str = "content",
    chunk_size: int = 1500,
    overlap: float = 0.1,
    threshold: int = 200,
    chunker="text_chunker",
    chunker_type=ChunkerType.PLAIN,
    chunker_args=None,
    chunker_kwargs=None,
    chunking_kwargs=None,
    documents_convert_func=None,
    to_lion: bool | Callable = True,
)
```

**Parameters**:
- `docs` (list): List of documents to be chunked.
- `field` (str, optional): The field to chunk. Defaults to "content".
- `chunk_size` (int, optional): The size of each chunk. Defaults to 1500.
- `overlap` (float, optional): The overlap between chunks. Defaults to 0.1.
- `threshold` (int, optional): The threshold for chunking. Defaults to 200.
- `chunker` (str, optional): The chunker function or its name. Defaults to "text_chunker".
- `chunker_type` (ChunkerType, optional): The type of chunker to use. Defaults to ChunkerType.PLAIN.
- `chunker_args` (list, optional): Positional arguments for the chunker function. Defaults to None.
- `chunker_kwargs` (dict, optional): Keyword arguments for the chunker function. Defaults to None.
- `chunking_kwargs` (dict, optional): Additional keyword arguments for chunking. Defaults to None.
- `documents_convert_func` (Callable, optional): Function to convert documents. Defaults to None.
- `to_lion` (bool | Callable, optional): Whether to convert the data to Node instances or a custom parser. Defaults to True.

**Returns**:
- `pile`: A pile of chunked Node instances.

**Raises**:
- `ValueError`: If the chunker_type is not supported.

**Description**:
Chunks documents using the specified chunker and chunker type, applying the given parameters and conversion functions.

**Usage Example**:
```python
chunked_docs = chunk(docs, field='text', chunk_size=1000, overlap=0.2)
```

### Function: `_self_defined_chunker`

**Signature**:
```python
def _self_defined_chunker(
    documents,
    chunker,
    chunker_args,
    chunker_kwargs,
    chunking_kwargs,
    to_lion: bool | Callable,
)
```

**Parameters**:
- `documents` (list): List of documents to be chunked.
- `chunker` (str | Callable): The chunker function or its name.
- `chunker_args` (list): Positional arguments for the chunker function.
- `chunker_kwargs` (dict): Keyword arguments for the chunker function.
- `chunking_kwargs` (dict): Additional keyword arguments for chunking.
- `to_lion` (bool | Callable): Whether to convert the data to Node instances or a custom parser.

**Returns**:
- `pile`: A pile of chunked Node instances or custom parsed nodes.

**Raises**:
- `ValueError`: If the self-defined chunker is not valid.

**Description**:
Chunks documents using a self-defined chunker function with the provided arguments and keyword arguments.

**Usage Example**:
```python
chunked_docs = _self_defined_chunker(docs, custom_chunker, ['arg1'], {'key': 'value'}, {}, custom_parser)
```

### Function: `_llama_index_chunker`

**Signature**:
```python
def _llama_index_chunker(
    documents,
    documents_convert_func,
    chunker,
    chunker_args,
    chunker_kwargs,
    to_lion: bool | Callable,
)
```

**Parameters**:
- `documents` (list): List of documents to be chunked.
- `documents_convert_func` (Callable): Function to convert documents.
- `chunker` (str | Callable): The chunker function or its name.
- `chunker_args` (list): Positional arguments for the chunker function.
- `chunker_kwargs` (dict): Keyword arguments for the chunker function.
- `to_lion` (bool | Callable): Whether to convert the data to Node instances or a custom parser.

**Returns**:
- `pile`: A pile of chunked Node instances or custom parsed nodes.

**Description**:
Chunks documents using a LlamaIndex chunker function, converting the documents if necessary and applying the provided arguments.

**Usage Example**:
```python
chunked_docs = _llama_index_chunker(docs, convert_func, llama_chunker, ['arg1'], {'key': 'value'}, True)
```

### Function: `_langchain_chunker`

**Signature**:
```python
def _langchain_chunker(
    documents,
    documents_convert_func,
    chunker,
    chunker_args,
    chunker_kwargs,
    to_lion: bool | Callable,
)
```

**Parameters**:
- `documents` (list): List of documents to be chunked.
- `documents_convert_func` (Callable): Function to convert documents.
- `chunker` (str | Callable): The chunker function or its name.
- `chunker_args` (list): Positional arguments for the chunker function.
- `chunker_kwargs` (dict): Keyword arguments for the chunker function.
- `to_lion` (bool | Callable): Whether to convert the data to Node instances or a custom parser.

**Returns**:
- `pile`: A pile of chunked Node instances or custom parsed nodes.

**Description**:
Chunks documents using a Langchain chunker function, converting the documents if necessary and applying the provided arguments.

**Usage Example**:
```python
chunked_docs = _langchain_chunker(docs, convert_func, langchain_chunker, ['arg1'], {'key': 'value'}, True)
```

### Function: `_plain_chunker`

**Signature**:
```python
def _plain_chunker(documents, chunker, chunker_args, chunker_kwargs)
```

**Parameters**:
- `documents` (list): List of documents to be chunked.
- `chunker` (str | Callable): The chunker function or its name.
- `chunker_args` (list): Positional arguments for the chunker function.
- `chunker_kwargs` (dict): Keyword arguments for the chunker function.

**Returns**:
- `pile`: A pile of chunked Node instances.

**Raises**:
- `ValueError`: If the chunker is not supported.

**Description**:
Chunks documents using a plain chunker function with the provided arguments and keyword arguments.

**Usage Example**:
```python
chunked_docs = _plain_chunker(docs, 'text_chunker', ['arg1'], {'key': 'value'})
```

### Detailed Examples

#### Example for `datanodes_convert`

```python
documents = [Node(content="This is a document"), Node(content="Another document")]
converted_docs = datanodes_convert(documents, ChunkerType.LLAMAINDEX)
print(converted_docs)
```

#### Example for `text_chunker`

```python
documents = [Node(content="This is a document"), Node(content="Another document")]
chunked_docs = text_chunker(documents, [], {"chunk_size": 100})
print(chunked_docs)
```

#### Example for `chunk`

```python
docs = [Node(content="This is a document"), Node(content="Another document")]
chunked_docs = chunk(docs, field='content', chunk_size=1000, overlap=0.2)
print(chunked_docs)
```

#### Example for `_self_defined_chunker`

```python
def custom_chunker(*args, **kwargs):
    # Custom chunker implementation
    pass

chunked_docs = _self_defined_chunk

er(docs, custom_chunker, ['arg1'], {'key': 'value'}, {}, custom_parser)
print(chunked_docs)
```

#### Example for `_llama_index_chunker`

```python
chunked_docs = _llama_index_chunker(docs, convert_func, llama_chunker, ['arg1'], {'key': 'value'}, True)
print(chunked_docs)
```

#### Example for `_langchain_chunker`

```python
chunked_docs = _langchain_chunker(docs, convert_func, langchain_chunker, ['arg1'], {'key': 'value'}, True)
print(chunked_docs)
```

#### Example for `_plain_chunker`

```python
chunked_docs = _plain_chunker(docs, 'text_chunker', ['arg1'], {'key': 'value'})
print(chunked_docs)
```
