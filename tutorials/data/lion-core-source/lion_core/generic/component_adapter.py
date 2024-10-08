from lion_core.protocols.adapter import AdapterRegistry
from lion_core.protocols.data_adapter import JsonDataAdapter
from lion_core.protocols.data_source_adapter import JsonFileAdapter


class ComponentAdapterRegistry(AdapterRegistry):
    pass


ComponentAdapterRegistry.register(JsonDataAdapter)
ComponentAdapterRegistry.register(JsonFileAdapter)

__all__ = ["ComponentAdapterRegistry"]
