import warnings
from typing import Any

from lion_core.generic.progression import Progression


def extend(self: Progression, item: Any, /) -> None:
    if not isinstance(item, Progression):
        warnings.warn(
            message=(
                "Since v0.3.0, extend method should only"
                " accept <Progression> type, the behavior of extending"
                " with other types is deprecated and will be removed"
                " in v1.0.0, try using <Progression.include()>` method instead."
            ),
            category=DeprecationWarning,
            stacklevel=2,
        )
        item = self._validate_order(item)
        self.order.extend(item)
        return
    self.order.extend(item.order)


Progression.extend = extend


def progression(order=None, name=None) -> Progression:
    return Progression(order=order, name=name)


__all__ = [
    "Progression",
    "progression",
]
