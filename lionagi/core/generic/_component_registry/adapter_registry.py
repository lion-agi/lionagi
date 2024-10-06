from lion_core.protocols.adapter import AdapterRegistry

from lionagi.integrations.bridge.langchain_.adapter import LangChainDocumentAdapter
from lionagi.integrations.bridge.llamaindex_.adapter import LlamaIndexNodeAdapter

from .data_adapter import JsonDataAdapter, PandasSeriesDataAdapter, XMLDataAdapter
from .data_source_adapter import JsonFileAdapter, XMLFileAdapter


class ComponentAdapterRegistry(AdapterRegistry): ...


ComponentAdapterRegistry.register(JsonDataAdapter)
ComponentAdapterRegistry.register(XMLDataAdapter)
ComponentAdapterRegistry.register(PandasSeriesDataAdapter)
ComponentAdapterRegistry.register(JsonFileAdapter)
ComponentAdapterRegistry.register(XMLFileAdapter)
ComponentAdapterRegistry.register(LangChainDocumentAdapter)
ComponentAdapterRegistry.register(LlamaIndexNodeAdapter)


__all__ = ["ComponentAdapterRegistry"]
