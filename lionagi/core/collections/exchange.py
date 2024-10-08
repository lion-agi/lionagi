import warnings

from lion_core.generic.exchange import Exchange
from lionabc import Communicatable
from pydantic import Field
from typing_extensions import deprecated

from lionagi.core.collections.pile import Pile

# update pile_ field to use lionagi Pile class
pile_: Pile = Field(
    default_factory=lambda: Pile(item_type={Communicatable}),
    description="The pile of items in the exchange.",
    title="pending items",
)


@property
@deprecated("`pile` parameter has been renamed to `pile_`")
def pile(self: Exchange):
    warnings.warn(
        message=(
            "`pile` parameter has been renamed to `pile_`. "
            "`pile` is reserved as a property for backward compatibility,"
            " it will be removed in v1.0.0."
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    return self.pile_


Exchange.pile_ = pile_
Exchange.pile = pile


__all__ = ["Exchange"]
