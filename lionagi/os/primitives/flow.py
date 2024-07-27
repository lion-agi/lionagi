from functools import partial

from pydantic import Field

from lion_core.generic import Note, Flow as CoreFlow


from lionagi.os.primitives.progression import Progression, progression
from lionagi.os.primitives.pile import Pile, pile


fpile = partial(pile, item_type=Progression)


class Flow(CoreFlow):

    progress: Pile = Field(
        default_factory=pile, description="A collection of progressions"
    )

    registry: Note = Field(
        default_factory=Note, description="information on progressions in the flow"
    )

    default_name: str = Field(
        "main", description="default name for the default progression"
    )

    def __init__(
        self,
        progress: Pile,
        default_name: str = "main",
    ): ...

    pass


def flow(*args, **kwargs):
    return Flow(*args, **kwargs)


__all__ = ["Flow", "flow"]
