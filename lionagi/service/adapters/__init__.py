# adapters/__init__.py

from .csv_adapter import CSVFileAdapter
from .db_adapters import MongoAdapter, SQLAdapter
from .excel_adapter import ExcelFileAdapter
from .json_adapter import JsonAdapter, JsonFileAdapter
from .pandas_adapter import PandasDataFrameAdapter
from .registry import AdapterRegistry

default_registry = AdapterRegistry()

# existing registrations...
default_registry.register(".json", JsonFileAdapter)
default_registry.register("json", JsonAdapter)
default_registry.register(".csv", CSVFileAdapter)
default_registry.register(".xlsx", ExcelFileAdapter)
default_registry.register("pd_dataframe", PandasDataFrameAdapter)

# new DB adapter registrations
default_registry.register("sql_db", SQLAdapter)
default_registry.register("mongo_db", MongoAdapter)

__all__ = [
    "default_registry",
    "JsonAdapter",
    "JsonFileAdapter",
    "CSVFileAdapter",
    "ExcelFileAdapter",
    "PandasDataFrameAdapter",
    "SQLAdapter",
    "MongoAdapter",
]
