
### Enums: `ReaderType`, `ChunkerType`
### Functions: `dir_to_path`, `dir_to_nodes`, `chunk_text`, `read_text`, `_file_to_chunks`, `file_to_chunks`, `_datanode_parser`

**Description**:
These enums and functions provide utilities for handling file operations, text chunking, and data node conversions. They include functions for reading files from directories, chunking text, and parsing data nodes using custom parsers.

### Enum: `ReaderType`

**Description**:
Defines the types of readers that can be used for loading data.

**Members**:
- `PLAIN`: Plain reader.
- `LANGCHAIN`: Langchain reader.
- `LLAMAINDEX`: LlamaIndex reader.
- `SELFDEFINED`: Self-defined reader.

### Enum: `ChunkerType`

**Description**:
Defines the types of chunkers that can be used for chunking text or documents.

**Members**:
- `PLAIN`: Plain chunker (default).
- `LANGCHAIN`: Langchain chunker.
- `LLAMAINDEX`: LlamaIndex chunker.
- `SELFDEFINED`: Self-defined chunker.

### Function: `dir_to_path`

**Signature**:
```python
def dir_to_path(
    dir: str, ext: str, recursive: bool = False, flatten: bool = True
) -> List[Path]
```

**Parameters**:
- `dir` (str): The directory to search for files.
- `ext` (str): The file extension to filter by.
- `recursive` (bool): Whether to search subdirectories recursively. Defaults to False.
- `flatten` (bool): Whether to flatten the list. Defaults to True.

**Returns**:
- `List[Path]`: A list of Paths to the files.

**Raises**:
- `ValueError`: If the directory or extension is invalid.

**Description**:
Generates a list of file paths from a directory with the given file extension.

**Usage Example**:
```python
paths = dir_to_path("/path/to/directory", ".txt", recursive=True)
```

### Function: `dir_to_nodes`

**Signature**:
```python
def dir_to_nodes(
    dir_: str,
    ext: Union[List[str], str],
    recursive: bool = False,
    flatten: bool = True,
    clean_text: bool = True,
) -> List[Node]
```

**Parameters**:
- `dir_` (str): The directory path from which to read files.
- `ext` (Union[List[str], str]): The file extension(s) to include. Can be a single string or a list/tuple of strings.
- `recursive` (bool, optional): If True, the function searches for files recursively in subdirectories. Defaults to False.
- `flatten` (bool, optional): If True, flattens the directory structure in the returned paths. Defaults to True.
- `clean_text` (bool, optional): If True, cleans the text read from files. Defaults to True.

**Returns**:
- `List[Node]`: A list of Node objects created from the files in the specified directory.

**Description**:
Converts directory contents into Node objects based on specified file extensions.

**Usage Example**:
```python
nodes = dir_to_nodes("/path/to/dir", [".txt", ".md"], recursive=True)
```

### Function: `chunk_text`

**Signature**:
```python
def chunk_text(
    input: str, chunk_size: int, overlap: float, threshold: int
) -> List[Union[str, None]]
```

**Parameters**:
- `input` (str): The input text to chunk.
- `chunk_size` (int): The size of each chunk.
- `overlap` (float): The amount of overlap between chunks.
- `threshold` (int): The minimum size of the final chunk.

**Returns**:
- `List[Union[str, None]]`: A list of text chunks.

**Raises**:
- `ValueError`: If an error occurs during chunking.

**Description**:
Chunks the input text into smaller parts, with optional overlap and threshold for the final chunk.

**Usage Example**:
```python
chunks = chunk_text("This is a long text to be chunked.", chunk_size=10, overlap=0.2, threshold=5)
```

### Function: `read_text`

**Signature**:
```python
def read_text(filepath: str, clean: bool = True) -> Tuple[str, dict]
```

**Parameters**:
- `filepath` (str): The path to the file to read.
- `clean` (bool): Whether to clean the text by replacing certain characters. Defaults to True.

**Returns**:
- `Tuple[str, dict]`: A tuple containing the content and metadata of the file.

**Raises**:
- `FileNotFoundError`: If the file cannot be found.
- `PermissionError`: If there are permissions issues.
- `OSError`: For other OS-related errors.

**Description**:
Reads text from a file and optionally cleans it, returning the content and metadata.

**Usage Example**:
```python
content, metadata = read_text("/path/to/file.txt")
```

### Function: `_file_to_chunks`

**Signature**:
```python
def _file_to_chunks(
    input: Dict[str, Any],
    field: str = "content",
    chunk_size: int = 1500,
    overlap: float = 0.1,
    threshold: int = 200,
) -> List[Dict[str, Any]]
```

**Parameters**:
- `input` (Dict[str, Any]): The input dictionary containing file content and metadata.
- `field` (str, optional): The field in the input dictionary to chunk. Defaults to "content".
- `chunk_size` (int, optional): The size of each chunk. Defaults to 1500.
- `overlap` (float, optional): The overlap between chunks. Defaults to 0.1.
- `threshold` (int, optional): The threshold for chunking. Defaults to 200.

**Returns**:
- `List[Dict[str, Any]]`: A list of dictionaries representing the chunked file content.

**Raises**:
- `ValueError`: If an error occurs during chunking.

**Description**:
Chunks the file content from the input dictionary into smaller parts.

**Usage Example**:
```python
chunks = _file_to_chunks(input_dict, chunk_size=1000, overlap=0.2)
```

### Function: `file_to_chunks`

**Signature**:
```python
def file_to_chunks(
    input,
    chunk_func=_file_to_chunks,
    **kwargs,
)
```

**Parameters**:
- `input` (Any): The input data to be chunked.
- `chunk_func` (Callable, optional): The function to use for chunking. Defaults to `_file_to_chunks`.
- `**kwargs`: Additional keyword arguments for the chunking function.

**Returns**:
- `List[Any]`: A list of chunked data.

**Description**:
Chunks the input data using the specified chunking function.

**Usage Example**:
```python
chunks = file_to_chunks(input_data, chunk_size=1000, overlap=0.2)
```

### Function: `_datanode_parser`

**Signature**:
```python
def _datanode_parser(nodes, parser)
```

**Parameters**:
- `nodes` (Any): The nodes to be parsed.
- `parser` (Callable): The parser function to use.

**Returns**:
- `Any`: The parsed nodes.

**Raises**:
- `ValueError`: If the parser function fails.

**Description**:
Parses data nodes using the specified parser function.

**Usage Example**:
```python
parsed_nodes = _datanode_parser(nodes, custom_parser)
```
