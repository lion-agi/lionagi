from collections.abc import Mapping, Generator
from collections import deque

from .abc._component import Component
from .abc._concepts import Record, Ordering
from .abc._exceptions import LionValueError

def _to_list_type(value):
    if isinstance(value, (Mapping, Record)):
        return list(value.values())
    if isinstance(value, Ordering):
        return list(value.order)
    if isinstance(value, Component):
        return [Component]
    if isinstance(value, (tuple, list, set, Generator, deque)):
        return list(value)
    return [value]

def _single_idable(value, _raise=False):
    if not isinstance(value, (str, Component)):
        if not _raise:
            return False
        
            
    return True