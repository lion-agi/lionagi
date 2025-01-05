========================================
``libs.schema`` Subpackage
========================================

This subpackage contains helpers and utilities for rendering, extracting, 
and generating schema data in JSON or Markdown form, as well as introspecting 
function docstrings. The main functionalities include:

- Generating human-readable JSON or Markdown output 
- Extracting code blocks from Markdown text
- Parsing function docstrings (both Google-style and reST-style)
- Generating schema definitions from function signatures
- Extracting JSON Schema from nested data



-----------------------
1) ``as_readable.py``
-----------------------
.. module:: lionagi.libs.schema.as_readable

Functions in this module focus on converting Python objects into 
human-readable JSON or Markdown code blocks.

.. function:: as_readable_json(input_: Any, /, **kwargs) -> str

   Convert arbitrary input data to a human-readable JSON string with optional 
   recursion, fuzzy parsing, Pydantic-model dumping, etc. By default, uses 
   ``to_dict`` internally for robust transformations, then calls 
   ``json.dumps`` with indentation.

   **Parameters**:
   - **input_** (Any): The object to be converted.
   - **kwargs**:
     - Additional arguments (e.g., for controlling recursion depth or 
       ascii-encoding) 
     - Passed on to :func:`lionagi.utils.to_dict` or to 
       ``json.dumps``.

   **Raises**:
   - ValueError: If the conversion to JSON fails.

   **Returns**:
   - str: The object serialized as a nicely formatted JSON string.

.. function:: as_readable(input_: Any, /, *, md: bool = False, **kwargs) -> str

   Build on :func:`as_readable_json` by optionally wrapping the JSON 
   output in triple-backtick Markdown fences. If any error occurs, falls 
   back to a direct string cast.

   **Parameters**:
   - **md** (bool): If True, wraps output with `````json ... ```.
   - **kwargs**: Passed on to :func:`as_readable_json`.

   **Returns**:
   - str: A plain or Markdown-formatted representation.


----------------------------
2) ``code_block.py``
----------------------------
.. module:: lionagi.libs.schema.code_block

Utilities to find and extract code blocks from Markdown text.

.. function:: extract_code_block(str_to_parse: str, return_as_list: bool = False, languages: list[str] | None = None, categorize: bool = False) -> str | list[str] | dict[str, list[str]]

   Searches for code blocks in Markdown or text data marked by triple 
   backticks (```) or tildes (~~~). Optionally filters by a list of language 
   names (like 'python', 'json') and can either return them concatenated, 
   as a list, or grouped by language in a dictionary.

   **Parameters**:
   - **str_to_parse** (str): The Markdown or text content to scan.
   - **return_as_list** (bool): If True, returns a list of code blocks. 
     Otherwise, returns them joined by a double newline.
   - **languages** (list[str] | None): Extract code only for these language 
     identifiers. If None, extract all.
   - **categorize** (bool): If True, returns a dict: ``lang -> [blocks...]``.

   **Returns**:
   - str or list[str] or dict[str, list[str]]: Code blocks found, in the 
     chosen format.


--------------------------------
3) ``extract_docstring.py``
--------------------------------
.. module:: lionagi.libs.schema.extract_docstring

Provides ways to parse Python docstrings in Google- or reST-style formats, 
extracting short descriptions and parameter definitions.

.. function:: extract_docstring(func: Callable, style: Literal["google", "rest"] = "google") -> tuple[str | None, dict[str, str]]

   Unified interface that calls either a Google-style or reST-style docstring 
   parser. Returns a tuple: ``(function_description, {param_name: param_desc, ...})``.

   **Parameters**:
   - **func** (Callable): The target function to parse.
   - **style** ({"google", "rest"}): Which docstring style to expect.

   **Returns**:
   - (str | None, dict[str, str]): A short description (often the first line), 
     plus a dictionary mapping each parameter to its doc line.

   **Example**::

       def myfunc(x: int):
           \"\"\"Example function.

           Args:
               x (int): The x argument.
           \"\"\"
           pass

       short_desc, param_map = extract_docstring(myfunc, style="google")

   **Raises**:
   - ValueError: If an unsupported style is requested.


-------------------------------
4) ``function_to_schema.py``
-------------------------------
.. module:: lionagi.libs.schema.function_to_schema

Converts Python function signatures and docstrings into a JSON schema or 
OpenAI “function call” style specification.

.. function:: function_to_schema(f_, style="google", *, func_description=None, parametert_description=None) -> dict

   Analyze the function name, docstring, signature, and parameter types 
   (from hints) to produce a schema-like definition. By default, it uses 
   Google-style docstrings for extracting parameter descriptions.

   **Parameters**:
   - **f_** (Callable): The function object.
   - **style** (str): "google" or "rest" docstring style.
   - **func_description** (str | None): Override docstring-based function summary.
   - **parametert_description** (dict | None): Override docstring-based param desc.

   **Returns**:
   - dict: A dictionary resembling an “OpenAI function” schema, e.g.::

       {
         "type": "function",
         "function": {
           "name": "func_name",
           "description": "some doc summary",
           "parameters": {
             "type": "object",
             "properties": { ... },
             "required": ["param1", ...]
           }
         }
       }


-----------------------------------
5) ``json_schema_extractor.py``
-----------------------------------
.. module:: lionagi.libs.schema.json_schema_extractor

Extract or generate JSON schemas from nested Python data, also providing 
CFG-grammar or regex approaches for additional downstream usage.

.. function:: extract_json_schema(data: Any, sep='|', coerce_keys=True, dynamic=True, coerce_sequence=None, max_depth=None) -> dict[str, Any]

   Flatten the input (via :func:`lionagi.protocols.nested.flatten`), then 
   derive a JSON schema. For each flattened key => value, generate a property 
   with type guess. The resulting dictionary is a minimal JSON schema.

   **Returns**:
   - dict: With "type": "object" and "properties" describing structure.

.. function:: json_schema_to_cfg(schema: dict[str, Any], start_symbol='S') -> list[tuple[str, list[str]]]

   Convert the schema into a simplified context-free grammar, 
   returning a list of productions. Useful for generating or checking 
   textual forms that match the schema.

.. function:: json_schema_to_regex(schema: dict[str, Any]) -> str

   Convert the schema into a single large regex pattern (approximate!). 
   For each type in the schema, we produce a fragment. 
   This is simplistic—use with caution for complex objects.

.. function:: print_cfg(productions: list[tuple[str, list[str]]])

   Print the grammar in a readable form.


---------
Usage Example
---------

Below is a short usage example demonstrating typical usage:

.. code-block:: python

   from lionagi.libs.schema.as_readable import as_readable
   from lionagi.libs.schema.extract_docstring import extract_docstring
   from lionagi.libs.schema.json_schema_extractor import extract_json_schema
   from lionagi.libs.schema.function_to_schema import function_to_schema

   def example_func(param1: int, param2: str) -> bool:
       \"\"\"Example function.

       Args:
           param1 (int): The first parameter.
           param2 (str): The second parameter.
       \"\"\"
       return True

   # 1) Turn some data into a pretty JSON
   data = {"foo": [1,2,3], "bar": {"nested": True}}
   pretty = as_readable(data, md=True)
   print(pretty)

   # 2) Extract docstring from function
   short_desc, param_desc = extract_docstring(example_func, "google")
   print(short_desc, param_desc)

   # 3) Generate JSON schema from data
   schema = extract_json_schema(data)
   print(schema)

   # 4) Build "function" schema
   f_schema = function_to_schema(example_func, style="google")
   print(f_schema)
