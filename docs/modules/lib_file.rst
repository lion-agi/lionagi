=====================================
``libs.file`` Subpackage
=====================================

This subpackage provides convenient file and directory manipulation utilities,
including functions for:

- Splitting text or token streams into chunks
- Reading/writing files
- Listing or filtering directory contents
- Copying files
- Processing entire directories concurrently for chunked ingestion



-------------------------------------
1) ``chunk.py``: Splitting into Chunks
-------------------------------------
.. module:: lionagi.libs.file.chunk

Contains utilities for splitting text or token lists into smaller sections, 
with optional overlap. It also supports bundling metadata with each chunk, 
and can optionally tokenize text using a custom tokenizer.

.. function:: chunk_by_chars(text: str, chunk_size=2048, overlap=0, threshold=256) -> list[str]

   Split a *string* into multiple chunks of roughly ``chunk_size`` characters.
   If the text is short enough for only one chunk, it returns the entire text.
   Overlap is optional, expressed as a fraction of ``chunk_size``. If the last 
   chunk is under the ``threshold``, it merges with the previous chunk.

   **Parameters**:
   - **text** (str): The entire text to chunk.
   - **chunk_size** (int): Target length of each chunk in characters.
   - **overlap** (float): Fraction of chunk size to overlap the edges.
   - **threshold** (int): Minimum size for the last chunk (avoid tiny 
     leftover chunk).

   **Returns**:
   - list of str: The splitted chunks.

   **Example**::
      
      >>> text = "This is a sample text for chunking."
      >>> chunks = chunk_by_chars(text, 10, 0.2)
      >>> chunks
      ['This is a ', 'a sample t', ... ]


.. function:: chunk_by_tokens(tokens: list[str], chunk_size=1024, overlap=0, threshold=128, return_tokens=False) -> list[str|list[str]]

   Split a list of tokens into multiple chunks of length ~``chunk_size`` 
   tokens. Overlap is optional, again as a fraction of chunk size. 
   If the final chunk is under ``threshold``, it merges with the previous chunk.

   **Parameters**:
   - **tokens** (list[str]): The token list to chunk.
   - **chunk_size** (int): Max tokens per chunk.
   - **overlap** (float): Fraction of chunk size to overlap.
   - **threshold** (int): Minimum token count for the last chunk.
   - **return_tokens** (bool): If True, returns lists of tokens. Otherwise,
     returns joined strings.

   **Returns**:
   - list of either str or list[str]

   **Example**::
      
      >>> tokens = ["This","is","a","sample","text"]
      >>> chunk_by_tokens(tokens, 3, 0.2)
      ['This is a', 'a sample text']


.. function:: chunk_content(content: str, chunk_by="chars", tokenizer=str.split, chunk_size=1024, overlap=0, threshold=256, metadata=None, return_tokens=False, **kwargs) -> list[dict[str, Any]]

   High-level function to chunk a big string, either by characters or by tokens
   (using a given tokenizer), and attach optional metadata. Returns a list of 
   dictionaries, one per chunk, each containing:

   - `"chunk_content"`: The chunk string or token list
   - `"chunk_id"`, `"total_chunks"`
   - `"chunk_size"`: The length of the chunk
   - Additional fields from *metadata*

   **Parameters**:
   - **content** (str): The content to chunk.
   - **chunk_by** ({"chars","tokens"}): Splitting method.
   - **tokenizer** (Callable): A function that splits the text into tokens 
     (only used if chunk_by="tokens").
   - **chunk_size** (int): The nominal chunk length in chars or tokens.
   - **overlap** (float): Fraction of chunk size for overlap.
   - **threshold** (int): Minimum size for the final chunk.
   - **metadata** (dict | None): Additional data to attach to each chunk.
   - **return_tokens** (bool): If True and chunk_by="tokens", 
     store token lists instead of joined strings.

   **Returns**:
   - list of dict: Each dict describes a chunk + metadata.


----------------------------------
2) ``ops.py``: File-level Utilities
----------------------------------
.. module:: lionagi.libs.file.ops

General file reading, copying, listing:

.. function:: copy_file(src, dest) -> None

   Copy a single file from *src* to *dest*, preserving metadata. Raises 
   errors if the file doesn't exist or permissions are invalid.

.. function:: get_file_size(path) -> int

   Returns the size (in bytes) of a single file or total size of all files
   under a directory path. Raises exceptions if path is invalid or there's 
   no permission.

.. function:: list_files(dir_path, extension=None) -> list[Path]

   Recursively list all files in *dir_path*. If *extension* is given, 
   only include those with the matching suffix.

.. function:: read_file(path) -> str

   Read the contents of *path* (UTF-8) and return the text. 
   Raises FileNotFoundError or PermissionError as needed.


---------------------------------------
3) ``dir_process.py``: Directory Handling
---------------------------------------
.. module:: lionagi.libs.file.dir_process

Tools for processing entire directories in a concurrent or chunked manner.

.. function:: dir_to_files(directory, file_types=None, max_workers=None, ignore_errors=False, verbose=False) -> list[Path]

   Recursively discover all files in *directory* (and subdirs). Optionally 
   filter by a list of extensions. Uses a ThreadPoolExecutor to handle 
   concurrency. If *ignore_errors* is True, logs warnings instead of 
   raising on file access issues.

   **Returns**:
   - list[Path]: The discovered file paths.

.. function:: file_to_chunks(file_path, chunk_func, chunk_size=1500, overlap=0.1, threshold=200, encoding="utf-8", custom_metadata=None, output_dir=None, verbose=False, timestamp=True, random_hash_digits=4) -> list[dict[str, Any]]

   Reads the text from *file_path*, then calls *chunk_func* to split it 
   into smaller chunks. Each chunk is returned as a dictionary with 
   metadata including the file name, size, etc. If *output_dir* is given, 
   it also writes each chunk to a separate JSON file.

   **Parameters**:
   - **file_path** (str|Path): The file to process.
   - **chunk_func** (Callable): A function for chunking the text 
     (e.g., :func:`chunk_by_chars`).
   - **chunk_size**, **overlap**, **threshold**: Passed to the chunker.
   - **encoding** (str): File read encoding.
   - **custom_metadata** (dict|None): Additional metadata to attach 
     to chunks.
   - **output_dir** (Path|None): If not None, writes each chunk to JSON 
     in that directory.
   - **timestamp** (bool), **random_hash_digits** (int): For naming 
     chunk files.

   **Returns**:
   - list of dict: The chunk definitions.


-----------------------------------------
4) ``save.py``: Saving Text or Chunk Files
-----------------------------------------
.. module:: lionagi.libs.file.save

Utilities to save string or chunk data to disk, often used after chunking.

.. function:: save_to_file(text, directory, filename, extension=None, timestamp=False, dir_exist_ok=True, file_exist_ok=False, time_prefix=False, timestamp_format=None, random_hash_digits=0, verbose=True) -> Path

   Create a path via :func:`lionagi.utils.create_path` and write *text* to it 
   using UTF-8. Optionally logs the resulting path if *verbose* is True.

   **Parameters**:
   - **text** (str): The text to save.
   - **directory** (str|Path): Directory to place the file.
   - **filename** (str): Base name (without extension, unless specified).
   - **extension** (str|None): If given, appends to filename with a dot.
   - **timestamp** (bool): If True, embed time in the filename.
   - **random_hash_digits** (int): Add a short random suffix.
   - **verbose** (bool): Print/log the file path after saving.

   **Returns**:
   - Path: The final path that was written.

.. function:: save_chunks(chunks, output_dir, verbose, timestamp, random_hash_digits)

   Helper to save chunk dictionaries to JSON files, each with a name like 
   ``chunk_1_<timestamp>.json``. The chunk itself is written as 
   pretty-printed JSON.


---------
Usage Example
---------
Below is a demonstration of how you might combine modules from this subpackage:

.. code-block:: python

   from lionagi.libs.file.chunk import chunk_by_chars, chunk_content
   from lionagi.libs.file.ops import read_file, list_files
   from lionagi.libs.file.dir_process import file_to_chunks

   # 1) List .txt files in a directory
   text_files = list_files("my_dir", extension="txt")

   # 2) Read the first file
   content = read_file(text_files[0])

   # 3) Chunk by characters
   chunks = chunk_by_chars(content, chunk_size=500, overlap=0.1)

   # 4) Alternatively, chunk with metadata
   meta_chunks = chunk_content(
       content, 
       chunk_by="chars", 
       chunk_size=500, 
       overlap=0.1, 
       metadata={"source": "my_dir/myfile.txt"}
   )

   # 5) Optionally store chunked results
   from lionagi.libs.file.save import save_chunks
   save_chunks(meta_chunks, "output_chunk_dir", verbose=True, timestamp=True, random_hash_digits=2)

   # 6) Or process an entire file in one go:
   results = file_to_chunks(
       "my_dir/myfile.txt", 
       chunk_func=chunk_by_chars, 
       chunk_size=500, 
       overlap=0.1,
       output_dir="output_chunk_dir"
   )

All together, the modules in ``lionagi.libs.file`` facilitate consistent, 
straightforward manipulation of file data, particularly in multi-file contexts 
where chunk-based ingestion is needed.
