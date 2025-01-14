.. _lionagi-adapters:

=========================================
Adapter System
=========================================
.. module:: lionagi.protocols.adapters
   :synopsis: Provides a unified interface for converting data to/from external formats.

Overview
--------
This system introduces the concept of an **Adapter** that knows how to
translate an internal object (like a Pydantic-based Element or a 
``Collective``) to an external representation (JSON, CSV, Excel, Pandas
DataFrame, etc.), and vice versa. Adapters are registered in a global
:class:`AdapterRegistry` under a specific **key** (like ``".csv"`` or
``"pd_dataframe"``), allowing other code to call ``adapt_from`` or
``adapt_to`` generically.

Contents
--------
.. contents::
   :local:
   :depth: 2


Adapter and Registry
--------------------

The core components of the adapter system are the :class:`Adapter` protocol
and the :class:`AdapterRegistry` class that manages adapter instances.

Protocol Documentation
^^^^^^^^^^^^^^^^^^^

.. class:: Adapter
   :module: lionagi.protocols.adapters.adapter

   **Protocol**: A formal interface describing a two-way converter that transforms
    objects between external representations and internal formats.

    Attributes
    ----------
    obj_key : str
        A unique key or extension that identifies what format this
        adapter supports (e.g. ".csv", "json", "pd_dataframe")

    Methods
    -------
    from_obj(subj_cls, obj, /, *, many, **kwargs)
        Converts a raw external object into a dictionary or list of dictionaries.
    to_obj(subj, /, *, many, **kwargs)
        Converts an internal object into the target format.

Method Documentation
^^^^^^^^^^^^^^^^^^

.. method:: Adapter.from_obj(subj_cls, obj, /, *, many, **kwargs)

    Converts a raw external object (file contents, JSON string, etc.)
    into a dictionary or list of dictionaries.

    Parameters
    ----------
    subj_cls : type[T]
        The target class type to convert into
    obj : Any
        The raw object to convert from
    many : bool
        Whether to expect/return multiple items
    **kwargs
        Additional conversion options

    Returns
    -------
    dict | list[dict]
        The converted data in dictionary form

.. method:: Adapter.to_obj(subj, /, *, many, **kwargs)

    Converts an internal object (e.g., a Pydantic-based model)
    into the target format (file, JSON, DataFrame, etc.).

    Parameters
    ----------
    subj : T
        The object to convert
    many : bool
        Whether to expect/handle multiple items
    **kwargs
        Additional conversion options

    Returns
    -------
    Any
        The converted object in the target format

Registry Documentation
^^^^^^^^^^^^^^^^^^^

.. class:: AdapterRegistry
   :module: lionagi.protocols.adapters.adapter

   A container that maps string/file extensions or object keys to
    specific adapter implementations.

    Class Methods
    ------------
    list_adapters()
        List all registered adapter keys
    register(adapter)
        Register a new adapter class
    get(obj_key)
        Get the adapter instance for a key
    adapt_from(subj_cls, obj, obj_key, **kwargs)
        Convert from external format using the appropriate adapter
    adapt_to(subj, obj_key, **kwargs)
        Convert to external format using the appropriate adapter

Method Documentation
^^^^^^^^^^^^^^^^^^

.. classmethod:: AdapterRegistry.list_adapters()

    List all registered adapter keys.

    Returns
    -------
    list[tuple[str | type, ...]]
        List of registered adapter keys

.. classmethod:: AdapterRegistry.register(adapter)

    Register a new adapter class.

    Parameters
    ----------
    adapter : type[Adapter]
        The adapter class to register

    Raises
    ------
    AttributeError
        If adapter is missing required methods

.. classmethod:: AdapterRegistry.get(obj_key)

    Get the adapter instance for a key.

    Parameters
    ----------
    obj_key : type | str
        The key or type to look up

    Returns
    -------
    Adapter
        The registered adapter instance

.. classmethod:: AdapterRegistry.adapt_from(subj_cls, obj, obj_key, **kwargs)

    Convert from external format using the appropriate adapter.

    Parameters
    ----------
    subj_cls : type[T]
        The target class type
    obj : Any
        The object to convert
    obj_key : type | str
        The adapter key to use
    **kwargs
        Additional conversion options

    Returns
    -------
    dict | list[dict]
        The converted data

.. classmethod:: AdapterRegistry.adapt_to(subj, obj_key, **kwargs)

    Convert to external format using the appropriate adapter.

    Parameters
    ----------
    subj : T
        The object to convert
    obj_key : type | str
        The adapter key to use
    **kwargs
        Additional conversion options

    Returns
    -------
    Any
        The converted object


JSON Adapters
-------------

The JSON adapter module provides two adapter implementations for working with
JSON data: one for in-memory strings and another for file operations.

Class Documentation
^^^^^^^^^^^^^^^^^

.. class:: JsonAdapter
   :module: lionagi.protocols.adapters.json_adapter

   **Inherits from**: :class:`~lionagi.protocols.adapters.adapter.Adapter`

   Adapter that converts to/from JSON **strings** in memory.
    Example usage: taking a Python dictionary and making JSON,
    or parsing JSON string to a dict.

    Attributes
    ----------
    obj_key : str
        "json" - identifies this adapter for JSON string operations

    Methods
    -------
    from_obj(subj_cls, obj, /, *, many=False, **kwargs)
        Convert a JSON string into a dict or list of dicts
    to_obj(subj, /, *, many=False, **kwargs)
        Convert an object (or collection) to a JSON string

Method Documentation
^^^^^^^^^^^^^^^^^^

.. classmethod:: JsonAdapter.from_obj(subj_cls, obj, /, *, many=False, **kwargs)

    Convert a JSON string into a dict or list of dicts.

    Parameters
    ----------
    subj_cls : type[T]
        The target class for context (not always used)
    obj : str
        The JSON string
    many : bool, optional
        If True, expects a JSON array (returns list[dict]).
        Otherwise returns a single dict or the first element.
    **kwargs
        Extra arguments for json.loads()

    Returns
    -------
    dict | list[dict]
        The loaded JSON data

.. classmethod:: JsonAdapter.to_obj(subj, /, *, many=False, **kwargs)

    Convert an object (or collection) to a JSON string.

    Parameters
    ----------
    subj : T
        The object to serialize
    many : bool, optional
        If True, convert multiple items to a JSON array
    **kwargs
        Extra arguments for json.dumps()

    Returns
    -------
    str
        The resulting JSON string

File Adapter Documentation
^^^^^^^^^^^^^^^^^^^^^^^

.. class:: JsonFileAdapter
   :module: lionagi.protocols.adapters.json_adapter

   **Inherits from**: :class:`~lionagi.protocols.adapters.adapter.Adapter`

   Adapter that reads/writes JSON data to/from a file on disk.
    The file extension key is ".json".

    Attributes
    ----------
    obj_key : str
        ".json" - identifies this adapter for JSON file operations

    Methods
    -------
    from_obj(subj_cls, obj, /, *, many=False, **kwargs)
        Read a JSON file from disk and return a dict or list of dicts
    to_obj(subj, /, *, fp, many=False, mode="w", **kwargs)
        Write a dict (or list) to a JSON file

Method Documentation
^^^^^^^^^^^^^^^^^^

.. classmethod:: JsonFileAdapter.from_obj(subj_cls, obj, /, *, many=False, **kwargs)

    Read a JSON file from disk and return a dict or list of dicts.

    Parameters
    ----------
    subj_cls : type[T]
        The target class for context
    obj : str | Path
        The JSON file path
    many : bool
        If True, expects a list. Otherwise single dict or first element.
    **kwargs
        Extra arguments for json.load()

    Returns
    -------
    dict | list[dict]
        The loaded data from file

.. classmethod:: JsonFileAdapter.to_obj(subj, /, *, fp, many=False, mode="w", **kwargs)

    Write a dict (or list) to a JSON file.

    Parameters
    ----------
    subj : T
        The object/collection to serialize
    fp : str | Path
        The file path to write
    many : bool
        If True, write as a JSON array of multiple items
    mode : str, default="w"
        File open mode
    **kwargs
        Extra arguments for json.dump()

    Returns
    -------
    None


CSV and Excel Adapters
----------------------

The pandas adapters module provides implementations for reading and writing
CSV and Excel files using pandas DataFrame operations.

CSV Adapter Documentation
^^^^^^^^^^^^^^^^^^^^^

.. class:: CSVFileAdapter
   :module: lionagi.protocols.adapters.pandas_.csv_adapter

   **Inherits from**: :class:`~lionagi.protocols.adapters.adapter.Adapter`

   Reads/writes CSV files to a list of dicts or vice versa,
    using `pandas`.

    Attributes
    ----------
    obj_key : str
        ".csv" - identifies this adapter for CSV file operations

    Methods
    -------
    from_obj(subj_cls, obj, /, *, many=False, **kwargs)
        Read a CSV file into a list of dictionaries
    to_obj(subj, /, *, fp, many=False, **kwargs)
        Write an object's data to a CSV file

Method Documentation
^^^^^^^^^^^^^^^^^^

.. classmethod:: CSVFileAdapter.from_obj(subj_cls, obj, /, *, many=False, **kwargs)

    Read a CSV file into a list of dictionaries.

    Parameters
    ----------
    subj_cls : type[T]
        The target class for context (not used)
    obj : str | Path
        The CSV file path
    many : bool, optional
        If True, returns list[dict]; if False, returns only
        the first dict
    **kwargs
        Additional options for `pd.read_csv`

    Returns
    -------
    list[dict]
        The parsed CSV data as a list of row dictionaries

.. classmethod:: CSVFileAdapter.to_obj(subj, /, *, fp, many=False, **kwargs)

    Write an object's data to a CSV file.

    Parameters
    ----------
    subj : T
        The item(s) to convert. If `many=True`, can be a Collective
    fp : str | Path
        File path to write the CSV
    many : bool
        If True, we assume a collection of items, else a single item
    **kwargs
        Extra params for `DataFrame.to_csv`

    Returns
    -------
    None

Excel Adapter Documentation
^^^^^^^^^^^^^^^^^^^^^^^

.. class:: ExcelFileAdapter
   :module: lionagi.protocols.adapters.pandas_.excel_adapter

   **Inherits from**: :class:`~lionagi.protocols.adapters.adapter.Adapter`

   Reads/writes Excel (XLSX) files, using `pandas`.

    Attributes
    ----------
    obj_key : str
        ".xlsx" - identifies this adapter for Excel file operations

    Methods
    -------
    from_obj(subj_cls, obj, /, *, many=False, **kwargs)
        Read an Excel file into a list of dictionaries
    to_obj(subj, /, *, fp, many=False, **kwargs)
        Write data to an Excel file

Method Documentation
^^^^^^^^^^^^^^^^^^

.. classmethod:: ExcelFileAdapter.from_obj(subj_cls, obj, /, *, many=False, **kwargs)

    Read an Excel file into a list of dictionaries.

    Parameters
    ----------
    subj_cls : type[T]
        Target class for context
    obj : str | Path
        The Excel file path
    many : bool, optional
        If True, returns list[dict]. If False, returns single dict or first element
    **kwargs
        Additional options for `pd.read_excel`

    Returns
    -------
    list[dict]
        The parsed Excel data as a list of row dictionaries

.. classmethod:: ExcelFileAdapter.to_obj(subj, /, *, fp, many=False, **kwargs)

    Write data to an Excel file.

    Parameters
    ----------
    subj : T
        The object(s) to convert to Excel rows
    fp : str | Path
        Path to save the XLSX file
    many : bool
        If True, writes multiple items (e.g., a Collective)
    **kwargs
        Extra parameters for `DataFrame.to_excel`

    Returns
    -------
    None


Pandas DataFrame and Series Adapters
------------------------------------

The pandas adapters module provides implementations for converting between
pandas data structures (DataFrame/Series) and Python dictionaries.

DataFrame Adapter Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. class:: PandasDataFrameAdapter
   :module: lionagi.protocols.adapters.pandas_.pd_dataframe_adapter

   **Inherits from**: :class:`~lionagi.protocols.adapters.adapter.Adapter`

   Converts a set of objects to a single `pd.DataFrame`, or
    a DataFrame to a list of dictionaries. Typically used in memory,
    not for saving to file.

    Attributes
    ----------
    obj_key : str
        "pd_dataframe" - identifies this adapter for DataFrame operations
    alias : tuple
        ("pandas_dataframe", "pd.DataFrame", "pd_dataframe")

    Methods
    -------
    from_obj(subj_cls, obj, /, **kwargs)
        Convert an existing DataFrame into a list of dicts
    to_obj(subj, /, **kwargs)
        Convert multiple items into a DataFrame

Method Documentation
^^^^^^^^^^^^^^^^^^

.. classmethod:: PandasDataFrameAdapter.from_obj(subj_cls, obj, /, **kwargs)

    Convert an existing DataFrame into a list of dicts.

    Parameters
    ----------
    subj_cls : type[T]
        The internal class to which we might parse
    obj : pd.DataFrame
        The DataFrame to convert
    **kwargs
        Additional args for DataFrame.to_dict (like `orient`)

    Returns
    -------
    list[dict]
        Each row as a dictionary

.. classmethod:: PandasDataFrameAdapter.to_obj(subj, /, **kwargs)

    Convert multiple items into a DataFrame, adjusting `created_at` to datetime.

    Parameters
    ----------
    subj : list[T]
        The items to convert. Each item must have `to_dict()`
    **kwargs
        Additional arguments for `pd.DataFrame(...)`

    Returns
    -------
    pd.DataFrame
        The resulting DataFrame

Series Adapter Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^

.. class:: PandasSeriesAdapter
   :module: lionagi.protocols.adapters.pandas_.pd_series_adapter

   **Inherits from**: :class:`~lionagi.protocols.adapters.adapter.Adapter`

   Converts a single item to a Pandas Series and vice versa.
    Great for 1-row data or simpler key-value pairs.

    Attributes
    ----------
    obj_key : str
        "pd_series" - identifies this adapter for Series operations
    alias : tuple
        ("pandas_series", "pd.series", "pd_series")

    Methods
    -------
    from_obj(subj_cls, obj, /, **kwargs)
        Convert a Pandas Series into a dictionary
    to_obj(subj, /, **kwargs)
        Convert a single item to a Series

Method Documentation
^^^^^^^^^^^^^^^^^^

.. classmethod:: PandasSeriesAdapter.from_obj(subj_cls, obj, /, **kwargs)

    Convert a Pandas Series into a dictionary.

    Parameters
    ----------
    subj_cls : type[T]
        Possibly the class we might use to rehydrate the item
    obj : pd.Series
        The series to interpret
    **kwargs
        Additional arguments for `Series.to_dict`

    Returns
    -------
    dict
        The data from the Series as a dictionary

.. classmethod:: PandasSeriesAdapter.to_obj(subj, /, **kwargs)

    Convert a single item to a Series.

    Parameters
    ----------
    subj : T
        The item, which must have `to_dict()`
    **kwargs
        Extra args passed to `pd.Series`

    Returns
    -------
    pd.Series
        The resulting Series


Example Usage
-------------
Below is a simple snippet using the registry:

.. code-block:: python

   from lionagi.protocols.adapters.adapter import AdapterRegistry
   from lionagi.protocols.adapters.json_adapter import JsonAdapter

   # Register the adapter
   AdapterRegistry.register(JsonAdapter)

   # Suppose we have some object with `to_dict()`
   my_element = SomeElement()

   # Convert to JSON string
   json_str = AdapterRegistry.adapt_to(my_element, "json")

   # Convert JSON back into a dictionary
   parsed = AdapterRegistry.adapt_from(type(my_element), json_str, "json")

   # Typically, you'd then call `SomeElement.from_dict(parsed)` if needed.


File Locations
--------------
- **adapter.py**: The core protocol (Adapter) and :class:`AdapterRegistry`.  
- **json_adapter.py**: In-memory JSON and JSON-file adapters.  
- **pandas_/csv_adapter.py**: CSV file adapter.  
- **pandas_/excel_adapter.py**: Excel file adapter (.xlsx).  
- **pandas_/pd_dataframe_adapter.py**: DataFrame adapter.  
- **pandas_/pd_series_adapter.py**: Series adapter.

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
