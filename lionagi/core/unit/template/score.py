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

from lionagi.libs.ln_convert import to_str
from lionagi.core.collections.abc import Field
from lionagi.core.unit import UnitForm



class ScoreTemplate(UnitForm):

    confidence_score: float | None = Field(
        None,
        description="a numeric score between 0 to 1 formatted in num:0.2f, 1 being very confident and 0 being not confident at all",
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        },
    )

    reason: str | None = Field(
        None,
        description="brief reason for the given output, format: This is my best response because ...",
    )

    template_name: str = "score_template"

    score: float | None = Field(
        None,
        description="a score for the given context and task, numeric",
    )

    assignment: str = "task -> score"

    @property
    def answer(self):
        return getattr(self, "score", None)

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        score_range=(0, 10),
        include_endpoints=True,
        num_digit=0,
        confidence_score=False,
        reason=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        return_precision = ""

        if num_digit == 0:
            return_precision = "integer"
        else:
            return_precision = f"num:{to_str(num_digit)}f"

        self.task = f"""
perform scoring task according to the following constraints:
1. additional objective: {to_str(instruction or "N/A")}.
2. score range: {to_str(score_range)}.
3. include_endpoints: {"yes" if include_endpoints else "no"}.
4. precision, (max number of digits allowed after "."): {return_precision}.
5. additional information: {to_str(context or "N/A")}.
"""
        if reason:
            self.append_to_request("reason")

        if confidence_score:
            self.append_to_request("confidence_score")

        self.validation_kwargs["score"] = {
            "upper_bound": score_range[1],
            "lower_bound": score_range[0],
            "num_type": int if num_digit == 0 else float,
            "precision": num_digit if num_digit != 0 else None,
        }
