
### Functions: `text_reader`, `load`, `_plain_reader`, `_langchain_reader`, `_llama_index_reader`, `_self_defined_reader`

**Description**:
These functions provide utilities for reading and loading data using various reader types. They support different reading strategies and integration with external libraries like Langchain and LlamaIndex.

### Function: `text_reader`

**Signature**:
```python
def text_reader(args, kwargs)
```

**Parameters**:
- `args`: Positional arguments for the `dir_to_nodes` function.
- `kwargs`: Keyword arguments for the `dir_to_nodes` function.

**Returns**:
- `list`: A list of Node instances.

**Description**:
Reads text files from a directory and converts them to Node instances.

**Usage Example**:
```python
args = ['path/to/text/files']
kwargs = {'file_extension': 'txt'}
nodes = text_reader(args, kwargs)
```

### Function: `load`

**Signature**:
```python
def load(
    reader: str | Callable = "text_reader",
    input_dir=None,
    input_files=None,
    recursive: bool = False,
    required_exts: list[str] = None,
    reader_type=ReaderType.PLAIN,
    reader_args=None,
    reader_kwargs=None,
    load_args=None,
    load_kwargs=None,
    to_lion: bool | Callable = True,
)
```

**Parameters**:
- `reader` (str | Callable): The reader function or its name. Defaults to "text_reader".
- `input_dir` (str, optional): The directory to read files from. Defaults to None.
- `input_files` (list[str], optional): Specific files to read. Defaults to None.
- `recursive` (bool, optional): Whether to read files recursively. Defaults to False.
- `required_exts` (list[str], optional): List of required file extensions. Defaults to None.
- `reader_type` (ReaderType, optional): The type of reader to use. Defaults to ReaderType.PLAIN.
- `reader_args` (list, optional): Positional arguments for the reader function. Defaults to None.
- `reader_kwargs` (dict, optional): Keyword arguments for the reader function. Defaults to None.
- `load_args` (list, optional): Positional arguments for loading. Defaults to None.
- `load_kwargs` (dict, optional): Keyword arguments for loading. Defaults to None.
- `to_lion` (bool | Callable, optional): Whether to convert the data to Node instances or a custom parser. Defaults to True.

**Returns**:
- `pile`: A pile of Node instances.

**Raises**:
- `ValueError`: If the `reader_type` is not supported.

**Description**:
Loads data using the specified reader and converts it to Node instances.

**Usage Example**:
```python
nodes = load(input_dir='path/to/text/files', required_exts=['txt'])
```

### Function: `_plain_reader`

**Signature**:
```python
def _plain_reader(reader, reader_args, reader_kwargs)
```

**Parameters**:
- `reader` (str | Callable): The reader function or its name.
- `reader_args` (list): Positional arguments for the reader function.
- `reader_kwargs` (dict): Keyword arguments for the reader function.

**Returns**:
- `pile`: A pile of Node instances.

**Raises**:
- `ValueError`: If the reader is not supported.

**Description**:
Reads data using a plain reader.

**Usage Example**:
```python
nodes = _plain_reader('text_reader', ['path/to/files'], {'ext': 'txt'})
```

### Function: `_langchain_reader`

**Signature**:
```python
def _langchain_reader(reader, reader_args, reader_kwargs, to_lion: bool | Callable)
```

**Parameters**:
- `reader` (str | Callable): The reader function or its name.
- `reader_args` (list): Positional arguments for the reader function.
- `reader_kwargs` (dict): Keyword arguments for the reader function.
- `to_lion` (bool | Callable): Whether to convert the data to Node instances or a custom parser.

**Returns**:
- `pile`: A pile of Node instances or custom parsed nodes.

**Description**:
Reads data using a Langchain reader.

**Usage Example**:
```python
nodes = _langchain_reader('langchain_reader', ['arg1'], {'key': 'value'}, True)
```

### Function: `_llama_index_reader`

**Signature**:
```python
def _llama_index_reader(
    reader,
    reader_args,
    reader_kwargs,
    load_args,
    load_kwargs,
    to_lion: bool | Callable,
)
```

**Parameters**:
- `reader` (str | Callable): The reader function or its name.
- `reader_args` (list): Positional arguments for the reader function.
- `reader_kwargs` (dict): Keyword arguments for the reader function.
- `load_args` (list): Positional arguments for loading.
- `load_kwargs` (dict): Keyword arguments for loading.
- `to_lion` (bool | Callable): Whether to convert the data to Node instances or a custom parser.

**Returns**:
- `pile`: A pile of Node instances or custom parsed nodes.

**Description**:
Reads data using a LlamaIndex reader.

**Usage Example**:
```python
nodes = _llama_index_reader('llama_reader', ['arg1'], {'key': 'value'}, [], {}, True)
```

### Function: `_self_defined_reader`

**Signature**:
```python
def _self_defined_reader(
    reader,
    reader_args,
    reader_kwargs,
    load_args,
    load_kwargs,
    to_lion: bool | Callable,
)
```

**Parameters**:
- `reader` (str | Callable): The reader function or its name.
- `reader_args` (list): Positional arguments for the reader function.
- `reader_kwargs` (dict): Keyword arguments for the reader function.
- `load_args` (list): Positional arguments for loading.
- `load_kwargs` (dict): Keyword arguments for loading.
- `to_lion` (bool | Callable): Whether to convert the data to Node instances or a custom parser.

**Returns**:
- `pile`: A pile of Node instances or custom parsed nodes.

**Raises**:
- `ValueError`: If the self-defined reader is not valid.

**Description**:
Reads data using a self-defined reader function with the provided arguments and keyword arguments.

**Usage Example**:
```python
nodes = _self_defined_reader(custom_reader, ['arg1'], {'key': 'value'}, [], {}, custom_parser)
```

### Detailed Examples

#### Example for `text_reader`

```python
args = ['path/to/text/files']
kwargs = {'file_extension': 'txt'}
nodes = text_reader(args, kwargs)
print(nodes)
```

#### Example for `load`

```python
nodes = load(input_dir='path/to/text/files', required_exts=['txt'])
print(nodes)
```

#### Example for `_plain_reader`

```python
nodes = _plain_reader('text_reader', ['path/to/files'], {'ext': 'txt'})
print(nodes)
```

#### Example for `_langchain_reader`

```python
nodes = _langchain_reader('langchain_reader', ['arg1'], {'key': 'value'}, True)
print(nodes)
```

#### Example for `_llama_index_reader`

```python
nodes = _llama_index_reader('llama_reader', ['arg1'], {'key': 'value'}, [], {}, True)
print(nodes)
```

#### Example for `_self_defined_reader`

```python
nodes = _self_defined_reader(custom_reader, ['arg1'], {'key': 'value'], [], {}, custom_parser)
print(nodes)
```
