====================================
Adapter
====================================
This module provides a **pluggable adaptation** framework for converting 
LionAGI objects to or from various formats—such as JSON strings, 
CSV/Excel files, or Pandas DataFrames—without scattering I/O logic 
throughout your code. Each adapter implements a protocol that knows 
how to handle one or more file/data types.

The system centers on:

- **Adapter**: A protocol specifying two main methods 
  (``from_obj`` and ``to_obj``) for inbound/outbound transformations.
- **AdapterRegistry**: A class that registers adapters under a key 
  (e.g., ``".json"``, ``"pd_dataframe"``, etc.) and uses them to adapt 
  objects.
- **Concrete Adapters**: Various classes like 
  :class:`JsonAdapter`, :class:`JsonFileAdapter`, 
  :class:`PandasDataFrameAdapter`, etc., each handling a specific 
  data format.


-------------------
1. Adapter Protocol
-------------------
.. module:: lionagi.protocols.adapter
   :synopsis: The adapter protocol and core registry classes.

.. class:: Adapter
   :noindex:
   :protocol:

   A runtime-checkable protocol specifying two main methods:

   - :meth:`from_obj(cls, subj_cls: type[T], obj: Any, **kwargs) -> dict | list[dict]`  
     Convert an external format (e.g., JSON string or CSV file) 
     **into** a dictionary or list of dictionaries describing the subject.

   - :meth:`to_obj(cls, subj: T, **kwargs) -> Any`  
     Convert an internal LionAGI object **out** to a specified format 
     (e.g., a JSON string, a CSV file, etc.).

   **Class Attributes**:

   .. attribute:: obj_key
      :type: str

      A string that identifies the adapter in the registry. 
      For example, ``".json"``, ``"pd_dataframe"``, or ``".xlsx"``.


------------------
2. AdapterRegistry
------------------
.. class:: AdapterRegistry

   A central registry that holds multiple :class:`Adapter` objects, 
   each keyed by its :attr:`Adapter.obj_key`.  
   
   - :meth:`register(adapter)`: Register a new adapter class or instance.
   - :meth:`get(obj_key) -> Adapter`: Retrieve the adapter matching 
     a key (like ``".json"``).
   - :meth:`adapt_from(subj_cls, obj, obj_key, **kwargs) -> dict|list[dict]`:  
     Use the registry's matching adapter to convert external data 
     **into** a dictionary or list of dictionaries.
   - :meth:`adapt_to(subj, obj_key, **kwargs) -> Any`:  
     Use the matching adapter to convert a subject **out** to 
     the external format.

   **Example**::

      reg = AdapterRegistry()
      reg.register(MyJsonAdapter)  # custom adapter with obj_key="myjson"

      # inbound
      data_dict = reg.adapt_from(MyObject, '{"foo": "bar"}', "myjson")
      # outbound
      json_str = reg.adapt_to(my_obj_instance, "myjson")


------------------
3. Built-in Adapters
------------------
The module defines several **concrete** adapters for common formats.

JsonAdapter
~~~~~~~~~~~
.. class:: JsonAdapter

   :attr:`obj_key` = ``"json"``

   **Purpose**:  
   Convert a JSON string to/from a LionAGI object's dictionary representation.

   - :meth:`from_obj(subj_cls, obj: str, /) -> dict`:  
     Expects a JSON string ``obj``. Returns a dictionary after parsing.
   - :meth:`to_obj(subj: T) -> str`:  
     Calls ``subj.to_dict()`` internally and dumps to a JSON string.


JsonFileAdapter
~~~~~~~~~~~~~~~
.. class:: JsonFileAdapter

   :attr:`obj_key` = ``".json"``

   Similar to :class:`JsonAdapter`, but works **directly with a file** path 
   rather than a string in memory.

   - :meth:`from_obj(subj_cls, obj: str | Path, /) -> dict`:  
     Reads a ``.json`` file from the given path.
   - :meth:`to_obj(subj: T, /, fp: str | Path) -> None`:  
     Writes the subject's dictionary to a file (``fp``) in JSON form.


PandasSeriesAdapter
~~~~~~~~~~~~~~~~~~~
.. class:: PandasSeriesAdapter

   :attr:`obj_key` = ``"pd_series"``  
   Also aliased as ``("pandas_series", "pd.series", "pd_series")``.

   - :meth:`from_obj(subj_cls, obj: pd.Series, /) -> dict`:  
     Convert a Pandas Series to a dictionary.
   - :meth:`to_obj(subj: T, /, **kwargs) -> pd.Series`:  
     Create a Pandas Series from the subject's dictionary.


PandasDataFrameAdapter
~~~~~~~~~~~~~~~~~~~~~~
.. class:: PandasDataFrameAdapter

   :attr:`obj_key` = ``"pd_dataframe"``  
   Also aliased as ``("pandas_dataframe", "pd.DataFrame", "pd_dataframe")``.

   - :meth:`from_obj(subj_cls, obj: pd.DataFrame, /, **kwargs) -> list[dict]`:  
     Convert a DataFrame to a list of dictionaries (one per row).
   - :meth:`to_obj(subj: list[T], /, **kwargs) -> pd.DataFrame`:  
     Convert a **list** of objects (each with ``.to_dict()``) into a DataFrame.


CSVFileAdapter
~~~~~~~~~~~~~~
.. class:: CSVFileAdapter

   :attr:`obj_key` = ``".csv"``  
   Also aliased as ``("csv_file", "csv")``.

   - :meth:`from_obj(subj_cls, obj: str|Path, /, **kwargs) -> list[dict]`:  
     Reads a CSV file into a list of row-dictionaries.
   - :meth:`to_obj(subj: list[T], /, fp: str|Path, **kwargs) -> None`:  
     Writes a list of objects (via ``.to_dict()``) to a CSV file.


ExcelFileAdapter
~~~~~~~~~~~~~~~~
.. class:: ExcelFileAdapter

   :attr:`obj_key` = ``".xlsx"``  
   Also aliased as ``(".xlsx", "excel_file", "excel", "xlsx", "xls", ".xls")``.

   - :meth:`from_obj(subj_cls, obj: str|Path, /, **kwargs) -> list[dict]`:  
     Reads an Excel file into a list of row-dictionaries.
   - :meth:`to_obj(subj: list[T], /, fp: str|Path, **kwargs) -> None`:  
     Writes a list of objects to an Excel file.


-----------------------------------------------
4. Specialized Adapter Registries
-----------------------------------------------
Some subsystems (e.g., “Nodes” vs. “Piles”) might want different default 
adapters. The module provides two examples:

NodeAdapterRegistry
~~~~~~~~~~~~~~~~~~~
.. class:: NodeAdapterRegistry(AdapterRegistry)

   A registry pre-populated with:

   - :class:`JsonAdapter`
   - :class:`JsonFileAdapter`
   - :class:`PandasSeriesAdapter`

PileAdapterRegistry
~~~~~~~~~~~~~~~~~~~
.. class:: PileAdapterRegistry(AdapterRegistry)

   A registry pre-populated with:

   - :class:`JsonAdapter`
   - :class:`JsonFileAdapter`
   - :class:`PandasDataFrameAdapter`
   - :class:`CSVFileAdapter`
   - :class:`ExcelFileAdapter`


------------------
5. Example Usage
------------------
**Registering Adapters**:

.. code-block:: python

   from lionagi.protocols.adapter import AdapterRegistry, JsonAdapter

   class MyCustomAdapter(JsonAdapter):
       obj_key = "my_json"  # special key

       # override to_obj or from_obj if needed

   # Register custom adapter
   AdapterRegistry.register(MyCustomAdapter)

**Adapting From**:

.. code-block:: python

   # Suppose you have an inbound JSON string
   inbound = '{"key": "value"}'
   # Convert it to a dict
   data_dict = AdapterRegistry.adapt_from(MyObject, inbound, "my_json")

**Adapting To**:

.. code-block:: python

   # Suppose you have 'my_obj' with a .to_dict() method
   out_str = AdapterRegistry.adapt_to(my_obj, "my_json")
   print(out_str)  # A JSON string

**File-Based**:

.. code-block:: python

   # Write to a .csv file
   from lionagi.protocols.adapter import PileAdapterRegistry

   PileAdapterRegistry.adapt_to(my_list_of_objs, ".csv", fp="out.csv")

   # Read from a .csv file
   items = PileAdapterRegistry.adapt_from(MyObjClass, "in.csv", ".csv")
