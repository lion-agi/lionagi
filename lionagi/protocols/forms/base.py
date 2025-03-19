# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from pydantic import ConfigDict, Field
from pydantic_core import PydanticUndefined

from lionagi.utils import UNDEFINED

from ..generic.element import Element


class BaseForm(Element):
    """
    A minimal base form class to store fields and define output logic.
    Typically, you'll inherit from this for domain-specific forms.
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    # A short "assignment" describing input->output
    assignment: str | None = Field(
        default=None,
        description="A small DSL describing transformation, e.g. 'a,b -> c'.",
    )
    # Which fields are produced as 'final' or 'required' outputs.
    output_fields: list[str] = Field(
        default_factory=list,
        description="Which fields are considered mandatory outputs.",
    )
    # Whether None counts as valid or incomplete
    none_as_valid: bool = Field(
        default=False,
        description="If True, None is accepted as a valid value for completion checks.",
    )
    has_processed: bool = Field(
        default=False,
        description="Marks if the form is considered completed or 'processed'.",
    )

    def is_completed(self) -> bool:
        """Check if all required output fields are set (and not UNDEFINED/None if not allowed)."""
        missing = self.check_completeness()
        return not missing

    def check_completeness(
        self, how: Literal["raise", "return_missing"] = "return_missing"
    ) -> list[str]:
        """
        Return a list of any 'required' output fields that are missing or invalid.
        If how='raise', raise an exception if missing any.
        """
        invalid_vals = [UNDEFINED, PydanticUndefined]
        if not self.none_as_valid:
            invalid_vals.append(None)

        missing = []
        for f in self.output_fields:
            val = getattr(self, f, UNDEFINED)
            if val in invalid_vals:
                missing.append(f)

        if missing and how == "raise":
            raise ValueError(f"Form missing required fields: {missing}")
        return missing

    def get_results(self, valid_only: bool = False) -> dict[str, Any]:
        """
        Return a dict of all `output_fields`, optionally skipping invalid/None if `valid_only`.
        """
        results = {}
        invalid_vals = [UNDEFINED, PydanticUndefined]
        if not self.none_as_valid:
            invalid_vals.append(None)

        for f in self.output_fields:
            val = getattr(self, f, UNDEFINED)
            if valid_only and val in invalid_vals:
                continue
            results[f] = val
        return results


# File: lionagi/protocols/forms/base.py
