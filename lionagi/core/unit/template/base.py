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
    """
    A base form class for units that includes fields for confidence scoring and reasoning.

    Attributes:
        template_name (str): The name of the template.
        confidence_score (float): A numeric confidence score between 0 and 1 with precision to 2 decimal places.
        reason (str | None): A field for providing concise reasoning for the process.
    """

    template_name: str = "UnitDirective"

    confidence_score: float = Field(
        None,
        description=(
            "Provide a numeric confidence score on how likely you successfully achieved the task  between 0 and 1, with precision in 2 decimal places. 1 being very confident in a good job, 0 is not confident at all."
        ),
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        },
    )

    reason: str | None = Field(
        None,
        description=(
            "Explain yourself, provide concise reasoning for the process. Must start with: Let's think step by step, "
        ),
    )
