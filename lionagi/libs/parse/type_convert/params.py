from collections.abc import Callable
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, Field, field_validator

from lionagi.libs.constants import NUM_TYPES

T = TypeVar("T")


class ToDictParams(BaseModel):
    """Parameters for to_dict conversion function."""

    str_type: Literal["json", "xml"] | None = Field(
        default="json",
        description="Type of string to parse",
    )
    fuzzy_parse: bool = Field(
        default=False,
        description="Whether to use fuzzy parsing for JSON-like strings",
    )
    suppress: bool = Field(
        default=False,
        description="Whether to suppress errors and return empty dict",
    )
    parser: Callable[[str], Any] | None = Field(
        default=None,
        description="Custom parser function for string inputs",
    )
    recursive: bool = Field(
        default=False,
        description="Enable recursive conversion of nested structures",
    )
    max_recursive_depth: int | None = Field(
        default=None,
        description="Maximum recursion depth (default 5, max 10)",
        ge=0,
        le=10,
    )
    recursive_python_only: bool = Field(
        default=True,
        description="If False, attempts to convert custom types recursively",
    )
    use_model_dump: bool = Field(
        default=True,
        description="Whether to use model_dump for pydantic models",
    )


class ToNumParams(BaseModel):
    """Parameters for to_num conversion function."""

    upper_bound: int | float | None = Field(
        default=None,
        description="Maximum allowed value (inclusive)",
    )
    lower_bound: int | float | None = Field(
        default=None,
        description="Minimum allowed value (inclusive)",
    )
    num_type: NUM_TYPES = Field(
        default=float,
        description="Target numeric type (int, float, complex)",
    )
    precision: int | None = Field(
        default=None,
        description="Number of decimal places for rounding (float only)",
        ge=0,
    )
    num_count: int = Field(
        default=1,
        description="Number of numeric values to extract",
        gt=0,
    )

    @field_validator("upper_bound")
    def validate_bounds(
        cls, v: float | None, values: dict[str, Any]
    ) -> float | None:
        if v is not None and values.get("lower_bound") is not None:
            if v < values["lower_bound"]:
                raise ValueError(
                    "upper_bound must be greater than lower_bound"
                )
        return v


class ToStrParams(BaseModel):
    """Parameters for to_str conversion function."""

    strip_lower: bool = Field(
        default=False,
        description="Whether to strip and convert to lowercase",
    )
    chars: str | None = Field(
        default=None,
        description="Characters to strip from the result",
    )
    str_type: Literal["json", "xml"] | None = Field(
        default=None,
        description="Type of string input if applicable",
    )
    serialize_as: Literal["json", "xml"] | None = Field(
        default=None,
        description="Output serialization format",
    )
    use_model_dump: bool = Field(
        default=False,
        description="Whether to use model_dump for pydantic models",
    )
    str_parser: Callable[[str], Any] | None = Field(
        default=None,
        description="Custom parser function for string inputs",
    )
    parser_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional keyword arguments for the parser",
    )


class ToListParams(BaseModel):
    """Parameters for to_list conversion function."""

    flatten: bool = Field(
        default=False,
        description="Whether to flatten nested structures",
    )
    dropna: bool = Field(
        default=False,
        description="Whether to drop None values",
    )
    unique: bool = Field(
        default=False,
        description="Whether to return only unique values (requires flatten=True)",
    )
    use_values: bool = Field(
        default=False,
        description="Whether to use .values() for dict-like inputs",
    )

    @field_validator("unique")
    def validate_unique(cls, v: bool, values: dict[str, Any]) -> bool:
        if v and not values.get("flatten", False):
            raise ValueError("unique=True requires flatten=True")
        return v
