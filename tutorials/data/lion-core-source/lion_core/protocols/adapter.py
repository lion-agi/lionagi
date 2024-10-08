import logging
from typing import Any, Protocol, runtime_checkable

from typing_extensions import get_protocol_members


@runtime_checkable
class Adapter(Protocol):

    obj_key: str
    verbose: bool = False
    config: dict = {}

    @classmethod
    def from_obj(
        cls, subj_cls, obj: Any, /, **kwargs
    ) -> dict | list[dict]: ...

    @classmethod
    def to_obj(cls, subj, /, **kwargs) -> Any: ...


adapter_members = get_protocol_members(Adapter)  # duck typing


class AdapterRegistry:

    _adapters: dict[str, Adapter] = {}

    @classmethod
    def list_adapters(cls):
        return list(cls._adapters.keys())

    @classmethod
    def register(cls, adapter: type[Adapter]):
        for member in adapter_members:
            if not hasattr(adapter, member):
                _str = getattr(adapter, "obj_key", None) or repr(adapter)
                _str = _str[:50] if len(_str) > 50 else _str
                raise AttributeError(
                    f"Adapter {_str} missing required methods."
                )

        if adapter.obj_key in cls._adapters:
            raise ValueError(f"Adapter {adapter.obj_key} already registered.")

        if isinstance(adapter, type):
            cls._adapters[adapter.obj_key] = adapter()
        else:
            cls._adapters[adapter.obj_key] = adapter

    @classmethod
    def get(cls, obj_key: str):
        if obj_key not in cls._adapters:
            raise AttributeError(f"Adapter {obj_key} not found.")
        return cls._adapters[obj_key]

    @classmethod
    def adapt_from(
        cls, subj_cls, obj: Any, obj_key: str, **kwargs
    ) -> dict | list[dict]:
        try:
            return cls.get(obj_key).from_obj(subj_cls, obj, **kwargs)
        except Exception as e:
            logging.error(f"Error adapting data from {obj_key}.")
            raise e

    @classmethod
    def adapt_to(cls, subj, obj_key: str, **kwargs):
        try:
            return cls.get(obj_key).to_obj(subj, **kwargs)
        except Exception as e:
            logging.error(f"Error adapting data to {obj_key}.")
            raise e


__all__ = ["AdapterRegistry", "Adapter"]
