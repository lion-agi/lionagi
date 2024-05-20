"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from lionagi.core.collections.abc import Field
from lionagi.core.report.form import Form


class BaseUnitForm(Form):
    template_name: str = "UnitDirective"

    confidence_score: float = Field(
        None,
        description=(
            "Provide a numeric confidence score between 0 and 1. Format: num:0.2f. 1 "
            "is very confident, 0 is not confident at all."
        ),
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        }
    )

    reason: str | None = Field(
        None,
        description=(
            "Provide a brief reason for the output. Must start with: Let's think step by step, "
            "because ..."
        )
    )

