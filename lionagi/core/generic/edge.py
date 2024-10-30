from typing import Any

from pydantic import Field, field_validator

from lionagi.core.collections.abc import (
    Component,
    Condition,
    LionIDable,
    get_lion_id,
)
from lionagi.core.generic.edge_condition import EdgeCondition


class Edge(Component):
    """Represents a directed edge between two nodes in a graph."""

    head: str = Field(
        ...,
        title="Head",
        description="The identifier of the head node of the edge.",
    )

    tail: str = Field(
        ...,
        title="Out",
        description="The identifier of the tail node of the edge.",
    )

    condition: Condition | EdgeCondition | None = Field(
        default=None,
        description="Optional condition that must be met for the edge "
        "to be considered active.",
    )

    label: str | None = Field(
        default=None,
        description="An optional label for the edge.",
    )

    bundle: bool = Field(
        default=False,
        description="A flag indicating if the edge is bundled.",
    )

    async def check_condition(self, obj: Any) -> bool:
        """Check if the edge condition is met for the given object."""
        if not self.condition:
            raise ValueError("The condition for the edge is not set.")
        check = await self.condition.applies(obj)
        return check

    @field_validator("head", "tail", mode="before")
    def _validate_head_tail(cls, value):
        """Validate the head and tail fields."""
        return get_lion_id(value)

    def string_condition(self):
        """
        Retrieves the condition class source code as a string.

        This method is useful for serialization and debugging, allowing
        the condition logic to be inspected or stored in a human-readable
        format. It employs advanced introspection techniques to locate and
        extract the exact class definition, handling edge cases like
        dynamically defined classes or classes defined interactively.

        Returns:
            str | None: The condition class source code if available.
                If the condition is None or the source code cannot be
                located, this method returns None.

        Raises:
            TypeError: If the condition class source code cannot be found
                due to the class being defined in a non-standard manner or
                in the interactive interpreter (__main__ context).
        """
        if self.condition is None:
            return

        import inspect
        import sys

        def new_getfile(object, _old_getfile=inspect.getfile):
            if not inspect.isclass(object):
                return _old_getfile(object)

            # Lookup by parent module (as in current inspect)
            if hasattr(object, "__module__"):
                object_ = sys.modules.get(object.__module__)
                if hasattr(object_, "__file__"):
                    return object_.__file__

            # If parent module is __main__, lookup by methods (NEW)
            for name, member in inspect.getmembers(object):
                if (
                    inspect.isfunction(member)
                    and object.__qualname__ + "." + member.__name__
                    == member.__qualname__
                ):
                    return inspect.getfile(member)
            else:
                raise TypeError(f"Source for {object!r} not found")

        inspect.getfile = new_getfile

        import inspect

        from IPython.core.magics.code import extract_symbols

        obj = self.condition.__class__
        cell_code = "".join(inspect.linecache.getlines(new_getfile(obj)))
        class_code = extract_symbols(cell_code, obj.__name__)[0][0]
        return class_code

    def __len__(self):
        """Return the length of the edge (always 1)."""
        return 1

    def __contains__(self, item: LionIDable) -> bool:
        """Check if the given item is the head or tail of the edge."""
        return get_lion_id(item) in (self.head, self.tail)
