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
from .base import BaseUnitForm, Field


class PlanTemplate(BaseUnitForm):

    template_name: str = "plan_template"

    plan: dict | str = Field(
        default_factory=dict,
        description="the generated step by step plan, return as a dictionary following {step_n: {plan: ..., reason: ...}} format",
    )

    signature: str = "task -> plan"

    @property
    def answer(self):
        return getattr(self, "plan", None)

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        confidence_score=False,
        reason=False,
        num_step=3,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = f"""
Generate a {num_step}_step plan based on the given context
1. additional instruction, {to_str(instruction or "N/A")}
2. additional context, {to_str(context or "N/A")}
"""
        if reason:
            self.append_to_request("reason")

        if confidence_score:
            self.append_to_request("confidence_score")
