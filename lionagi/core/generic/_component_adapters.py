from lion_core.protocols.adapters import (
    AdapterRegistry,
    JsonAdapter,
    JsonFileAdapter,
    PandasSeriesAdapter,
)

from lionagi.integrations.langchain_.adapter import LangChainDocumentAdapter
from lionagi.integrations.llamaindex_.adapter import LlamaIndexNodeAdapter

ADAPTERS = [
    JsonAdapter,
    JsonFileAdapter,
    PandasSeriesAdapter,
    LlamaIndexNodeAdapter,
    LangChainDocumentAdapter,
]


class ComponentAdapterRegistry(AdapterRegistry):
    _adapters = {k.obj_key: k() for k in ADAPTERS}


__all__ = ["ComponentAdapterRegistry"]
