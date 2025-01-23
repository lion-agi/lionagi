.. _lionagi-tools:

================================================
Tools System
================================================
.. module:: lionagi.tools
   :synopsis: Provides a collection of tools for file operations, code execution, and document management.

Overview
--------
The **tools** system in LionAGI provides a collection of specialized tools that inherit from 
:class:`LionTool`. Each tool is designed to handle specific operations like file reading/writing, 
code execution in sandboxes, or document management. The system includes:

- :class:`ReaderTool`: For reading and chunking documents
- :class:`WriterTool`: For writing and saving files with restrictions
- :class:`CoderTool`: For sandbox code execution and file operations

Contents
--------
.. contents::
   :local:
   :depth: 2


Base Tool
---------
.. class:: LionTool
   :module: lionagi.tools.base

   **Abstract Base Class**: The foundation for all tools in LionAGI.

   Attributes
   ----------
   is_lion_system_tool : bool
       Flag indicating this is a system tool (True by default).
   system_tool_name : str
       The name used to identify this tool in the system.

   Methods
   -------
   .. method:: to_tool() -> Tool
      :abstractmethod:

      Must be implemented by subclasses to return a :class:`Tool` instance
      that wraps this tool's functionality.


ReaderTool
----------
.. class:: ReaderTool
   :module: lionagi.tools.reader

   **Inherits from**: :class:`LionTool`

   A tool for reading, searching, and chunking documents. Supports operations like:
   
   - Opening files/URLs and converting to text
   - Reading partial slices of documents
   - Searching for substrings
   - Splitting documents into chunks
   - Managing multiple documents in memory

   The tool uses a document converter to handle various file formats and stores documents
   in memory for efficient access.

   Actions
   -------
   - **open**: Convert a file/URL to text and store for partial reads
   - **read**: Return a partial slice of an opened document
   - **search**: Find substrings in the document text
   - **list_docs**: Show currently opened documents
   - **close**: Remove a document from memory
   - **chunk_doc**: Split text into memory chunks
   - **list_chunks**: View chunk metadata
   - **read_chunk**: Get a specific chunk
   - **read_chunks**: Get multiple chunks

   Example
   -------
   .. code-block:: python

       from lionagi.tools import ReaderTool

       reader = ReaderTool()
       # Open a document
       response = reader.handle_request({
           "action": "open",
           "path_or_url": "example.txt"
       })
       doc_id = response.doc_info.doc_id

       # Read a portion
       chunk = reader.handle_request({
           "action": "read",
           "doc_id": doc_id,
           "start_offset": 0,
           "end_offset": 100
       })


WriterTool
----------
.. class:: WriterTool
   :module: lionagi.tools.writer

   **Inherits from**: :class:`LionTool`

   A tool for writing and saving files, with built-in safety restrictions on
   where files can be written. Supports:
   
   - Creating/opening documents for writing
   - Writing or appending text (with offset control)
   - Saving files to disk (in allowed directories only)
   - Managing multiple documents in memory

   The tool enforces a root directory restriction for all disk writes to prevent
   unauthorized file access.

   Actions
   -------
   - **open**: Create or open a document for writing
   - **write**: Write/append text with optional offsets
   - **list_docs**: Show documents in memory
   - **close**: Remove a document
   - **save_file**: Save text to disk (restricted)
   - **save_chunks**: Save chunk objects to disk

   Example
   -------
   .. code-block:: python

       from lionagi.tools import WriterTool

       writer = WriterTool(allowed_root="./data")
       # Create a new document
       response = writer.handle_request({
           "action": "open",
           "path": "newfile.txt"
       })
       doc_id = response.doc_info.doc_id

       # Write some content
       writer.handle_request({
           "action": "write",
           "doc_id": doc_id,
           "content": "Hello, world!"
       })


CoderTool
---------
.. class:: CoderTool
   :module: lionagi.tools.coder

   **Inherits from**: :class:`LionTool`

   A tool that combines sandbox code execution (via E2B) with local file operations.
   Provides:
   
   - E2B sandbox management for safe code execution
   - Package installation in sandboxes
   - File upload/download to/from sandboxes
   - Local file string replacement
   - Fuzzy file finding in Git repositories
   - Shell command execution

   The tool requires an E2B API key for sandbox operations.

   Actions
   -------
   **Sandbox Operations**:
      - **start_sandbox**: Create new E2B sandbox
      - **stop_sandbox**: Stop existing sandbox
      - **list_sandboxes**: Show active sandboxes
      - **run_code**: Execute code in sandbox
      - **install_pkg**: Install packages (pip/npm/apt)
      - **upload_file**: Send file to sandbox
      - **download_file**: Get file from sandbox

   **Local Operations**:
      - **file_str_replace**: Replace strings in files
      - **fuzzy_find**: Search files with fuzzy matching
      - **shell_command**: Run local shell commands

   Example
   -------
   .. code-block:: python

       from lionagi.tools import CoderTool

       coder = CoderTool(e2b_api_key="your-key")
       # Start a sandbox
       response = coder.handle_request({
           "action": "start_sandbox"
       })
       sandbox_id = response.sandbox_id

       # Run some Python code
       coder.handle_request({
           "action": "run_code",
           "sandbox_id": sandbox_id,
           "code": "print('Hello from sandbox!')",
           "language": "python"
       })


File Locations
-------------
- **base.py**: The :class:`LionTool` abstract base class
- **reader.py**: The :class:`ReaderTool` implementation
- **writer.py**: The :class:`WriterTool` implementation
- **coder.py**: The :class:`CoderTool` implementation
- **types.py**: Tool exports and type definitions

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
