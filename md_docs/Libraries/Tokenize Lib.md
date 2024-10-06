# Tokenize Utility API Reference

This module provides utility functions for tokenizing and chunking text.

## Classes

### `TokenizeUtil`

A utility class for tokenizing text and chunking it into smaller parts.

#### Methods:

#### `tokenize(text, encoding_model=None, encoding_name=None, return_byte=False, disallowed_tokens=None)`

Tokenizes the input text using the specified encoding model or encoding name. Optionally returns byte-encoded tokens and excludes disallowed tokens.

```python
@staticmethod
def tokenize(
    text: str,
    encoding_model: Optional[str] = None,
    encoding_name: Optional[str] = None,
    return_byte: bool = False,
    disallowed_tokens: Optional[List[str]] = None
) -> Union[List[str], List[int]]:
```

**Parameters**:
- `text` (`str`): The input text to tokenize.
- `encoding_model` (`Optional[str]`): The name of the encoding model to use. Default is None.
- `encoding_name` (`Optional[str]`): The name of the encoding scheme to use. Default is None.
- `return_byte` (`bool`): If True, returns byte-encoded tokens. Default is False.
- `disallowed_tokens` (`Optional[List[str]]`): A list of tokens to exclude from the tokenized output. Default is None.

**Returns**:
- `Union[List[str], List[int]]`: A list of tokens (either as strings or byte-encoded integers).

#### `chunk_by_chars(text: str, chunk_size: int, overlap: float, threshold: int) -> List[Union[str, None]]`

Chunks the input text into smaller parts, with optional overlap and threshold for final chunk.

```python
@staticmethod
def chunk_by_chars(
    text: str, chunk_size: int, overlap: float, threshold: int
) -> list[Union[str, None]]:
```

**Parameters**:
- `text` (`str`): The input text to chunk.
- `chunk_size` (`int`): The size of each chunk.
- `overlap` (`float`): The amount of overlap between chunks.
- `threshold` (`int`): The minimum size of the final chunk.

**Returns**:
- `List[Union[str, None]]`: A list of text chunks.

**Raises**:
- `ValueError`: If an error occurs during chunking.

#### `chunk_by_tokens(text: str, chunk_size: int, overlap: float, threshold: int, encoding_model=None, encoding_name=None, return_tokens=False, return_byte=False) -> List[Union[str, None]]`

Chunks the input text into smaller parts based on token size, with optional overlap and threshold for the final chunk.

```python
@staticmethod
def chunk_by_tokens(
    text: str,
    chunk_size: int,
    overlap: float,
    threshold: int,
    encoding_model: Optional[str] = None,
    encoding_name: Optional[str] = None,
    return_tokens: bool = False,
    return_byte: bool = False
) -> List[Union[str, None]]:
```

**Parameters**:
- `text` (`str`): The input text to chunk.
- `chunk_size` (`int`): The size of each chunk in tokens.
- `overlap` (`float`): The amount of overlap between chunks.
- `threshold` (`int`): The minimum size of the final chunk in number of tokens.
- `encoding_model` (`Optional[str]`): The name of the encoding model to use. Default is None.
- `encoding_name` (`Optional[str]`): The name of the encoding scheme to use. Default is None.
- `return_tokens` (`bool`): If True, returns the chunked tokens. Default is False.
- `return_byte` (`bool`): If True, returns byte-encoded tokens. Default is False.

**Returns**:
- `List[Union[str, None]]`: A list of text chunks or token chunks.

## Usage Examples

```python
from lionagi.libs.tokenize_util import TokenizeUtil

# Tokenize text
tokens = TokenizeUtil.tokenize("Hello, world!", encoding_name="cl100k_base")
print(tokens)  # Output: ['Hello', ',', ' ', 'world', '!']

# Chunk text by characters
chunks = TokenizeUtil.chunk_by_chars("Hello, world!", chunk_size=5, overlap=2, threshold=2)
print(chunks)  # Output: ['Hello,', ' world!']

# Chunk text by tokens
token_chunks = TokenizeUtil.chunk_by_tokens("Hello, world!", chunk_size=2, overlap=0.5, threshold=1)
print(token_chunks)  # Output: ['Hello,', ' world!']
```

These examples demonstrate how to use the tokenization and chunking methods provided by the `TokenizeUtil` class in `ln_tokenize`. You can tokenize text into tokens, chunk text into smaller parts based on character size, and chunk text into smaller parts based on token size.
