from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from lionagi.libs.string_similarity import SIMILARITY_TYPE
from lionagi.libs.string_similarity.algorithms import SIMILARITY_ALGO_MAP


class ValidateKeysParams(BaseModel):
    """Parameters for validate_keys function.

    Attributes:
        similarity_algo: String similarity algorithm to use or custom function
        similarity_threshold: Minimum similarity score for fuzzy matching
        fuzzy_match: If True, use fuzzy matching for key correction
        handle_unmatched: How to handle unmatched keys
        fill_value: Default value for filling unmatched keys
        fill_mapping: Dictionary mapping unmatched keys to default values
        strict: If True, raise ValueError if any expected key is missing
    """

    similarity_algo: SIMILARITY_TYPE | Callable[[str, str], float] = Field(
        default="jaro_winkler",
        description="String similarity algorithm to use or custom function",
    )
    similarity_threshold: float = Field(
        default=0.85,
        description="Minimum similarity score for fuzzy matching",
        ge=0.0,
        le=1.0,
    )
    fuzzy_match: bool = Field(
        default=True,
        description="If True, use fuzzy matching for key correction",
    )
    handle_unmatched: Literal["ignore", "raise", "remove", "fill", "force"] = (
        Field(
            default="ignore",
            description="How to handle unmatched keys",
        )
    )
    fill_value: Any = Field(
        default=None,
        description="Default value for filling unmatched keys",
    )
    fill_mapping: dict[str, Any] | None = Field(
        default=None,
        description="Dictionary mapping unmatched keys to default values",
    )
    strict: bool = Field(
        default=False,
        description="If True, raise ValueError if any expected key is missing",
    )

    @field_validator("similarity_algo")
    def validate_similarity_algo(
        cls, v: SIMILARITY_TYPE | Callable[[str, str], float]
    ) -> SIMILARITY_TYPE | Callable[[str, str], float]:
        if isinstance(v, str) and v not in SIMILARITY_ALGO_MAP:
            raise ValueError(f"Unknown similarity algorithm: {v}")
        return v
