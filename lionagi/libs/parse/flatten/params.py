from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class FlattenParams(BaseModel):
    """Parameters for flatten function.

    Attributes:
        parent_key: Base key for the current recursion level
        sep: Separator for joining keys
        coerce_keys: Join keys into strings if True, keep as tuples if False
        dynamic: Handle sequences (except strings) dynamically if True
        coerce_sequence: Force sequences to be treated as dicts or lists
        max_depth: Maximum depth to flatten
    """

    parent_key: tuple[Any, ...] = Field(
        default=(),
        description="Base key for the current recursion level",
    )
    sep: str = Field(
        default="|",
        description="Separator for joining keys",
    )
    coerce_keys: bool = Field(
        default=True,
        description="Join keys into strings if True, keep as tuples if False",
    )
    dynamic: bool = Field(
        default=True,
        description="Handle sequences (except strings) dynamically if True",
    )
    coerce_sequence: Literal["dict", "list"] | None = Field(
        default=None,
        description="Force sequences to be treated as dicts or lists",
    )
    max_depth: int | None = Field(
        default=None,
        description="Maximum depth to flatten",
        ge=0,
    )

    @field_validator("coerce_sequence")
    def validate_coerce_sequence(
        cls, v: Literal["dict", "list"] | None, values: dict[str, Any]
    ) -> Literal["dict", "list"] | None:
        if v == "list" and values.get("coerce_keys", True):
            raise ValueError(
                "coerce_sequence cannot be 'list' when coerce_keys is True"
            )
        return v
