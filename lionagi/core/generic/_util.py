from collections.abc import Mapping, Generator
from collections import deque

from .abc._component import Component
from .abc._concepts import Record, Ordering


def _to_list_type(value):
    if isinstance(value, Component) and not isinstance(value, (Record, Ordering)):
        return [value]
    if isinstance(value, (Mapping, Record)):
        return list(value.values())
    if isinstance(value, Ordering):
        return list(value.order)
    if isinstance(value, (tuple, list, set, Generator, deque)):
        return list(value)
    return [value]
