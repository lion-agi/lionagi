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

from enum import Enum
from lionagi.libs.ln_convert import to_str, to_dict
from lionagi.core.collections.abc import Field
from .template.base import BaseUnitForm


class UnitForm(BaseUnitForm):
    """Form for managing unit directives and outputs."""

    actions: dict | None = Field(
        None,
        description=(
            "Actions to take based on the context and instruction."
            " Format: {action_n: {function: ..., arguments: {param1: ..., param2: ...}}}."
            "Leave blank if no actions are needed."
            "must use provided functions and parameters, DO NOT MAKE UP NAMES!!!"
            "Flag `action_required` as True if filled."
            "When providing parameters, you must follow the provided type and format, "
            "if the parameter is a number, you should provide a number like 1, 23, or 1.1 if float is allowed."
        ),
        examples=["{action_1: {function: 'add', arguments: {num1: 1, num2: 2}}}"]
    )

    action_required: bool | None = Field(
        None,
        description="Set to True if actions are required. Provide actions if True.",
        examples=[True, False],
    )

    answer: str | None = Field(
        None,
        description=(
            "Provide the answer to the questions asked. If an accurate answer cannot "
            "be provided at this step, set `extend_required` to True."
            "if actions are required at this step, set `action_required` to True and reply with 'PELASE_ACTION`."
        ),
    )

    extension_required: bool | None = Field(
        None,
        description=(
            "Set to True if more steps are needed to provide an accurate answer. If "
            "True, additional rounds are allowed."
        ),
        examples=[True, False],
    )

    prediction: None | str = Field(
        None,
        description="Provide the likely prediction basing on context and instruction.",
    )

    plan: dict | str | None = Field(
        None,
        description=(
            "Provide a step-by-step plan. Format: {step_n: {plan: ..., reason: ...}}. "
            "Achieve the final answer at the last step. Set `extend_required` to True "
            "if plan requires more steps."
        ),
        examples=["{step_1: {plan: '...', reason: '...'}}"],
    )

    next_steps: dict | str | None = Field(
        None,
        description="Brainstorm ideas on next actions to take. Format: {next_step_n: {plan: ..., reason: ...}} next_step is about anticipating the future actions, but it does not have to be in a sequential format. Set `extend_required` to True if more steps are needed.",
    )


    score: float | None = Field(
        None,
        description=(
            "A numeric score. Higher is better. If not otherwise instructed,"
            " fill this field with your own performance rating. Try hard and be self-critical"
        ),
        examples=[0.2, 5, 2.7],
    )

    reflection: str | None = Field(
        None,
        description="Reason your own reasoning. create specific items on how/where/what you could improve to better achieve the task, or can the problem be solved in a different and better way. If you can think of a better solution, please provide it and flag the necessary fields in `action_required`, `extension_required`, `next_steps`.",
    )

    selection: Enum | str | list | None = Field(
        None, description="a single item from the choices."
    )

    tool_schema: list | dict | None = Field(
        None, 
        description="The list of tools available for using."
    )

    assignment: str = "task -> answer"

    def __init__(
        self,
        instruction=None,
        *,
        context=None,
        reason: bool = True,
        predict: bool = False,
        score=True,
        select=None,
        plan=None,
        brainstorm=None,
        reflect=None,
        tool_schema=None,
        allow_action: bool = False,
        allow_extension: bool = False,
        max_extension: int = None,
        confidence=None,
        score_num_digits=None,
        score_range=None,
        select_choices=None,
        plan_num_step=None,
        predict_num_sentences=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = (
            f"Follow the prompt and provide the necessary output.\n"
            f"- Additional instruction: {to_str(instruction or 'N/A')}\n"
            f"- Additional context: {to_str(context or 'N/A')}\n"
        )

        if reason:
            self.append_to_request("reason")

        if allow_extension:
            self.append_to_request("extension_required")
            self.task += f"- Allow auto-extension for another {max_extension} rounds.\n"
            
        if allow_action:
            self.append_to_request("actions, action_required, reason")
            self.task += "- Reason and prepare actions with GIVEN TOOLS ONLY.\n"
            
        if tool_schema:
            self.append_to_input("tool_schema")
            self.tool_schema = tool_schema

        if brainstorm:
            self.append_to_request("next_steps, extension_required")
            self.task += "- Explore ideas on next actions to take.\n"

        if plan:
            plan_num_step = plan_num_step or 3
            max_extension = max_extension or plan_num_step
            allow_extension = True
            self.append_to_request("plan, extension_required")
            self.task += f"- Generate a {plan_num_step}-step plan based on the context.\n"

        if predict:
            self.append_to_request("prediction")
            self.task += f"- Predict the next {predict_num_sentences or 1} sentence(s).\n"

        if select:
            self.append_to_request("selection")
            self.task += f"- Select 1 item from the provided choices: {select_choices}.\n"

        if confidence:
            self.append_to_request("confidence_score")

        if score:
            self.append_to_request("score")

            score_range = score_range or [0, 10]
            score_num_digits = score_num_digits or 0

            self.validation_kwargs["score"] = {
                "upper_bound": score_range[1],
                "lower_bound": score_range[0],
                "num_type": int if score_num_digits == 0 else float,
                "precision": score_num_digits if score_num_digits != 0 else None,
            }

            self.task += (
                f"- Give a numeric score in [{score_range[0]}, {score_range[1]}] "
                f"and precision of {score_num_digits or 0} decimal places.\n"
            )
            
        if reflect:
            self.append_to_request("reflection")


    def display(self):
        fields = self.work_fields.copy()
        
        if "task" in fields and len(str(fields["task"])) > 2000:
            fields["task"] = fields["task"][:2000] + "..."
        
        if "tool_schema" in fields:
            tools = to_dict(fields["tool_schema"])["tools"]
            fields["tool_used"] = [i["function"]["name"] for i in tools]
            fields.pop("tool_schema")
            
        if "actions" in fields:
            a = ""
            for _, v in fields["actions"].items():
                a += f"\n- **{v["function"]}**({', '.join([f'{k}: {v}' for k, v in v["arguments"].items()])}), "
            fields["actions"] = a[:-2]
            
        if "action_response" in fields:
            a = ""
            for _, v in fields["action_response"].items():
                a += f"\n- **{v["function"]}**({', '.join([f'{k}: {v}' for k, v in v["arguments"].items()])}"
                if len(str(v["output"])) > 30:
                    a += f" \n \t{v["output"]}), "
                else:
                    a += f") = {v["output"]}, "
                    
            fields["action_response"] = a[:-2]    
        
        super().display(fields=fields)