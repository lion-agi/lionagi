from typing import TypeAliasType
from lion_core.generic.flow import Flow, flow as _flow


flow = TypeAliasType("flow", Flow)
flow.__call__ = _flow


__all__ = ["Flow", "flow"]
