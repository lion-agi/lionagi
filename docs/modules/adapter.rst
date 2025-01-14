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
.. automodule:: lionagi.protocols.adapters.adapter
   :members:
   :undoc-members:
   :show-inheritance:

   :class:`Adapter` is a Python protocol specifying two methods:
   ``from_obj()`` and ``to_obj()``. The :class:`AdapterRegistry` is a
   container that associates each adapter with a key or extension.


JSON Adapters
-------------
.. automodule:: lionagi.protocols.adapters.json_adapter
   :members:
   :undoc-members:
   :show-inheritance:

   - **JsonAdapter**: For reading/writing **in-memory** JSON strings.  
   - **JsonFileAdapter**: For reading/writing JSON files from disk.


CSV and Excel Adapters
----------------------
.. automodule:: lionagi.protocols.adapters.pandas_.csv_adapter
   :members:
   :undoc-members:
   :show-inheritance:

   Provides **CSVFileAdapter** using pandas.

.. automodule:: lionagi.protocols.adapters.pandas_.excel_adapter
   :members:
   :undoc-members:
   :show-inheritance:

   Provides **ExcelFileAdapter** for `.xlsx` files with pandas.


Pandas DataFrame and Series Adapters
------------------------------------
.. automodule:: lionagi.protocols.adapters.pandas_.pd_dataframe_adapter
   :members:
   :undoc-members:
   :show-inheritance:

   **PandasDataFrameAdapter** handles converting a list of elements
   to a single ``pd.DataFrame``, or a DataFrame back into a list of
   dictionaries.

.. automodule:: lionagi.protocols.adapters.pandas_.pd_series_adapter
   :members:
   :undoc-members:
   :show-inheritance:

   **PandasSeriesAdapter** transforms a single item to/from a
   single-row ``pd.Series``.


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
