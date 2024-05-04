from pydantic import Field, field_validator
from typing import Any
from ..abc import Component, Ordering, get_lion_id, LionIDable, Condition


class Edge(Component, Ordering):

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

    condition: Condition | None = Field(
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

    @field_validator("head", "tail", mode="before")
    def _validate_head_tail(cls, value):
        return get_lion_id(value)

    async def check_condition(self, obj: dict[str, Any]) -> bool:
        if not self.condition:
            raise ValueError("The condition for the edge is not set.")
        if await self.condition.applies(obj):
            return True
        return False

    def __len__(self):
        return 1

    def __contains__(self, item: LionIDable) -> bool:
        return get_lion_id(item) in (self.head, self.tail)

    def __str__(self) -> str:
        """
        Returns a simple string representation of the Edge.
        """
        return f"Edge (id_={self.ln_id}, from={self.head}, to={self.tail}, label={self.label})"
