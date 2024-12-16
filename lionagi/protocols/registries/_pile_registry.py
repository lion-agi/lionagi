from lionagi.protocols.adapters.adapter import AdapterRegistry
from lionagi.protocols.adapters.json_adapter import (
    JsonAdapter,
    JsonFileAdapter,
)
from lionagi.protocols.adapters.pandas_adapter import (
    CSVFileAdapter,
    ExcelFileAdapter,
    PandasDataFrameAdapter,
)

ADAPTERS = [
    JsonAdapter,
    JsonFileAdapter,
    PandasDataFrameAdapter,
    CSVFileAdapter,
    ExcelFileAdapter,
]


class PileAdapterRegistry(AdapterRegistry):

    _adapters = {k.obj_key: k() for k in ADAPTERS}


__all__ = ["PileAdapterRegistry"]
