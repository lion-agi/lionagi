import warnings

from lion_core.generic.flow import Flow
from lion_core.generic.progression import Progression
from pydantic import Field
from typing_extensions import deprecated

from lionagi.core.collections.pile import Pile

# update progressions field to use lionagi Pile class
progressions: Pile[Progression] = Field(
    default_factory=lambda: Pile({}, item_type={Progression})
)


@property
@deprecated("`sequences` parameter has been renamed to `progressions`")
def sequences(self: Flow):
    warnings.warn(
        message=(
            "`sequences` parameter has been renamed to `progressions`. "
            "`sequences` is reserved as a property for backward compatibility,"
            " it will be removed in v1.0.0."
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    return self.progressions


Flow.progressions = progressions
Flow.sequences = sequences


def flow(progressions=None, default_name=None, /):
    """Create a new Flow object."""
    return Flow(progressions=progressions, default_name=default_name)


__all__ = ["Flow", "flow"]
