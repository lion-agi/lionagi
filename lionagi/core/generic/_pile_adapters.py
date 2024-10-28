from lion_core.protocols.adapters import (
    AdapterRegistry,
    CSVFileAdapter,
    ExcelFileAdapter,
    JsonAdapter,
    JsonFileAdapter,
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
