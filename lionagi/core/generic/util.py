from collections.abc import Mapping, Generator
from collections import deque

from .abc import LionTypeError, Record, Ordering, Component, get_lion_id


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


def _validate_order(value) -> list[str]:
    """Validate and convert the order field."""
    if value is None:
        return []
    if isinstance(value, str) and len(value) == 32:
        return [value]
    elif isinstance(value, Component):
        return [value.ln_id]

    try:
        return [i for item in _to_list_type(value) if (i := get_lion_id(item))]
    except Exception as e:
        raise LionTypeError("Progression must only contain lion ids.") from e
