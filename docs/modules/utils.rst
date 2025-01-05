===================================================
General Purpose Helpers
===================================================

The ``lionagi.utils`` module provides an extensive set of general-purpose utilities 
that facilitate everything from copying and flattening data structures, handling 
(asynchronous) bulk operations, concurrency/throttling, fuzzy JSON/XML parsing, 
and more. It also contains core definitions like :data:`UNDEFINED` and 
:class:`HashableModel`.


-----------------------------------
Key Types & Constant: ``UNDEFINED``
-----------------------------------

.. module:: lionagi.utils

.. data:: UNDEFINED

   A global sentinel object used to represent an undefined or sentinel value 
   that is distinct from Python's built-ins like ``None``. Often used in 
   Pydantic contexts or to indicate the absence of a field.

.. class:: UndefinedType

   A helper class representing the :data:`UNDEFINED` sentinel. Once created,
   it is globally reused by LionAGI's internal processing to consistently 
   represent “no value.”


-------------------------
Hashable Model & Helpers
-------------------------

.. class:: HashableModel
   :extends: pydantic.BaseModel

   A Pydantic model that is also hashable by converting its data into 
   a hashable format (like JSON strings). This is useful when you need 
   to store model instances as dictionary keys or in sets.

   **Methods**:

   .. method:: to_dict(**kwargs) -> dict
      Converts model fields to a dictionary, excluding any that are set 
      to :data:`UNDEFINED`.

   .. method:: from_dict(data: dict, **kwargs) -> Self
      Class method to create an instance from a dictionary, using Pydantic
      validation.

   .. method:: __hash__() -> int
      Produces a stable hash from the underlying dictionary data.

.. function:: hash_dict(data) -> int

   Internal utility to recursively handle dictionary, list, or Pydantic 
   objects by converting them into JSON-like strings for hashing.


---------------------
General Utility Types
---------------------

.. class:: Params
   :extends: pydantic.BaseModel

   A generic base class for creating param objects that can also be 
   callable. Subclasses often provide typed arguments for higher-order 
   functions (like :func:`to_list`, :func:`lcall`, etc.).

.. class:: DataClass
   :abstract:

   An abstract base class used for simpler data-carrying structures 
   that are not strictly Pydantic.


------------------------
Time & Path Management
------------------------

.. function:: time(*, tz=..., type_="timestamp", ...) -> float | str | datetime

   Get the current time in various formats (timestamp, datetime, ISO8601, or custom).

   :param tz: Timezone for the time (default: from :class:`~lionagi.settings.Settings.Config.TIMEZONE`).
   :param type_: One of ``"timestamp"``, ``"datetime"``, ``"iso"``, or ``"custom"``.
   :param sep: If type_="iso", a separator for date/time (default "T").
   :param custom_format: Required if type_="custom". A strftime format string.
   :return: Time in the requested format.

   **Raises**:
      - ValueError if an invalid ``type_`` is used or missing format.


.. function:: create_path(directory, filename, extension=None, timestamp=False, ...) -> Path

   Generate a new file path, optionally ensuring unique or timestamped filenames.

   :param directory: The directory in which to place the file.
   :param filename: Base name of the file (without extension, or includes).
   :param extension: If not in `filename`, a separate extension. 
   :param timestamp: Whether to add a time string to the filename.
   :param random_hash_digits: If >0, a random hex is appended to avoid collisions.
   :return: A :class:`Path` to the final file location.

   **Example**::

       from lionagi.utils import create_path
       path = create_path("./logs", "session", extension="txt", timestamp=True)
       print(path) 
       # -> something like ./logs/session_20231025.txt


.. class:: CreatePathParams
   :extends: Params

   Pydantic-based parameter object to configure :func:`create_path`. 


--------------------------
Copy, Flatten, & List Ops
--------------------------

.. function:: copy(obj, /, *, deep=True, num=1) -> T | list[T]

   Makes one or more copies of an object. Uses ``deepcopy`` by default (``deep=True``).

   :param obj: The object to copy.
   :param deep: Whether to perform a deep copy (default True).
   :param num: Number of copies to produce; returns a single item if num=1, else a list.
   :return: The copied object or list of copies.

.. function:: to_list(input_, /, flatten=False, dropna=False, unique=False, ...)

   Convert an input (which could be a single item, str, mapping, or iterable) 
   into a Python list with optional flattening, deduplication, or removing 
   None/undefined items.

   **Parameters**:
      - **flatten** (bool) - Recursively flatten nested lists.
      - **dropna** (bool) - Exclude None/:data:`UNDEFINED` entries.
      - **unique** (bool) - Remove duplicates (requires flatten=True).
      - **use_values** (bool) - For enums or mappings, extract `.value()`.

   **Examples**::

       >>> to_list(1)
       [1]
       >>> to_list([1, [2, 3], None], flatten=True, dropna=True)
       [1, 2, 3]


.. class:: ToListParams
   :extends: Params

   Config object used to pass to ``to_list`` in a single structured instance.


-----------------------------------------
Higher-Order Calls: lcall, alcall, bcall
-----------------------------------------

.. function:: lcall(input_, func, /, *args, sanitize_input=False, ...)

   Synchronously apply **func** to each item in an input list (with optional flattening, 
   deduplication, removal of None, etc.). Returns a list of results. 

   If you pass e.g. ``sanitize_input=True``, it uses :func:`to_list` on the input.

.. class:: LCallParams
   :extends: CallParams
   A param object for configuring :func:`lcall` usage, including flattening or 
   dedup options.


.. function:: alcall(input_, func, /, ..., sanitize_input=False, max_concurrent=None, ...)

   Asynchronously apply **func** to each item in the input. Supports:
   - optional concurrency limit
   - automatic retries
   - timeouts
   - pre/post flattening or dedup

   Returns a list of results once all tasks are done.

   **Example**::

      from lionagi.utils import alcall

      async def process_item(x):
          return x*x

      results = await alcall([1,2,3], process_item)
      # -> [1,4,9]


.. class:: ALCallParams
   :extends: CallParams

   A param class collecting all advanced arguments for :func:`alcall`. 
   Can be used to create reusable config for batch asynchronous tasks.


.. function:: bcall(input_, func, /, batch_size, ...)

   Asynchronously process input in **batches**. Returns an async generator. 
   Each yield is the result from a single batch processed via :func:`alcall`.

.. class:: BCallParams
   :extends: CallParams

   Param class for configuring :func:`bcall`. 


------------------------
Fuzzy JSON / XML Parsing
------------------------

.. function:: to_json(input_data, /, fuzzy_parse=False) -> dict | list[dict]

   Extract and parse JSON from a string or list of strings, 
   possibly reading `````json ... ``` code blocks. If multiple blocks
   exist, returns a list of them.

   **Examples**::

       text = "some text ```json {\"a\":1} ``` more text ```json {\"b\":2} ```"
       data = to_json(text) 
       # -> [{'a':1}, {'b':2}]


.. function:: fuzzy_parse_json(str_to_parse)

   Attempt to parse JSON via multiple cleanup heuristics (like 
   replacing single quotes, adding missing brackets, etc.).

.. function:: fix_json_string(str_to_parse)
   Adds matching brackets if unbalanced. 
   Raises ValueError if the string is otherwise irreparable.

.. function:: xml_to_dict(xml_string, /, suppress=False, remove_root=True, root_tag='root') -> dict
   Convert an XML string to a nested dictionary structure. Optionally remove 
   the root element from the output.

.. function:: dict_to_xml(data: dict, root_tag='root') -> str
   Convert a dictionary to a simple XML string.

.. function:: to_dict(
   input_, use_model_dump=True, fuzzy_parse=False, str_type="json", ...
) -> dict

   A universal “to dictionary” approach:
   - If `input_` is a str, tries JSON or XML parse (optionally fuzzy).
   - If `input_` is a Pydantic model, calls `model_dump` or other methods.
   - If `input_` is an iterable, tries to convert to a dict of index->value.
   - If `input_` is an Enum class, optionally uses enumerated values.


------------------------------
Fuzzy Checking & Recursion
------------------------------

.. function:: recursive_to_dict(
   input_, max_recursive_depth=5, recursive_custom_types=False, ...
) -> Any

   Walks the structure of `input_` up to `max_recursive_depth` levels, 
   converting each sub-part to a dictionary if it's recognized (like 
   a Pydantic model, string that can parse to JSON, etc.). 
   Raises RecursionError if depth is too large.

.. function:: is_same_dtype(input_, dtype=None, return_dtype=False) -> bool|tuple[bool, type|None]
   Check if all items share the same type (optionally checking 
   against a known `dtype`). 


----------------------------------
Concurrency/Throttling Decorators
----------------------------------

.. function:: throttle(func, period: float)

   Make *func* only callable once every ``period`` seconds. 
   If *func* is async, internally uses a forced-async approach 
   and a simple time-based check.

.. function:: max_concurrent(func, limit: int)

   Limit concurrency of *func* calls to at most `limit` at once 
   using an asyncio.Semaphore. If *func* is synchronous, it is 
   forced to run in an async threadpool.

.. class:: Throttle

   The underlying class used by :func:`throttle`. 
   Provides a time-based gating mechanism for calls.

.. function:: force_async(fn)

   Wrap a synchronous function *fn* in an async wrapper by 
   using a threadpool executor.


------------------------------
Numeric Conversions
------------------------------

.. function:: to_num(
   input_, upper_bound=None, lower_bound=None, num_type='float', precision=None, ...
) -> int|float|complex|list[int|float|complex]

   Convert a string or object to a numeric type, optionally handling 
   scientific notation, fractions, percentages, complex numbers, 
   or repeated matches within the string.

   :param input_: The data to convert (string, int, float, etc.).
   :param upper_bound: If not None, raise error if the parsed number > this.
   :param lower_bound: Raise error if the parsed number < this.
   :param num_type: 'int', 'float', 'complex' (or the type objects).
   :param precision: Round floats to this many decimal places.
   :param num_count: If > 1, tries to find that many numeric occurrences 
                     in the input string.
   :return: The converted numeric value or list of values.

   **Examples**::

       to_num("3.1415", num_type="float", precision=2)
       # -> 3.14

       to_num("55%", num_type="float")
       # -> 0.55


.. function:: breakdown_pydantic_annotation(model: type[BaseModel], max_depth=None)

   Recursively gather type hints from a Pydantic model, returning 
   a dictionary describing its structure. Potentially used for 
   advanced introspection or generating schema-like info.


------------------------------
System Helpers & Others
------------------------------

.. function:: run_package_manager_command(args: Sequence[str]) -> subprocess.CompletedProcess[bytes]

   Tries to run a package manager command (like ``uv`` or fallback to 
   ``pip``). Used internally if you have a script that wants to 
   install/uninstall Python packages in a consistent manner.
