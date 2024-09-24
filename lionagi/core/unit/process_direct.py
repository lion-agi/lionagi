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

from typing import Any, Callable

from lion_core.setting import LN_UNDEFINED
from lion_core.libs import validate_mapping
from lion_core.form.base import BaseForm
from lionagi.core.unit.unit_form import UnitForm
from lionagi.core.unit.process_chat import process_chat
from lionagi.core.unit.process_act import process_action
from lion_core.session.branch import Branch


async def prepare_output(
    form: UnitForm,
    verbose_direct: bool,
) -> BaseForm:
    """
    Prepare the output form based on the action responses.

    Args:
        form: The form to prepare the output for.
        verbose: Whether to print verbose output.

    Returns:
        The prepared form with updated answer.
    """

    if "PLEASE_ACTION" in form.answer:
        if verbose_direct:
            print("Analyzing action responses and generating answer...")

        answer = await process_chat(
            "please provide final answer basing on the above"
            " information, provide answer value as a string only"
            " do not return as json, do not include other information",
        )

        if isinstance(answer, dict):
            a = answer.get("answer", None)
            if a is not None:
                answer = a

        answer = str(answer).strip()
        if answer.startswith("{") and answer.endswith("}"):
            answer = answer[1:-1]
            answer = answer.strip()
        if '"answer":' in answer:
            answer.replace('"answer":', "")
            answer = answer.strip()
        elif "'answer':" in answer:
            answer.replace("'answer':", "")
            answer = answer.strip()

        form.answer = answer

    return form


async def _direct(
    branch: Branch,
    form: UnitForm | None = None,
    *,
    instruction: str | str = None,
    context: Any = None,
    guidance: str = LN_UNDEFINED,
    reason: bool = False,
    confidence: bool = False,
    plan: bool = False,
    reflect: bool = False,
    tool_schema: list = None,
    invoke_tool: bool = None,
    allow_action: bool = False,
    allow_extension: bool = False,
    max_extension: int = None,  # 3
    plan_num_step: int = None,
    chain: bool = False,
    num_chain: int = None,
    strict_form=LN_UNDEFINED,
    task_description=LN_UNDEFINED,
    tools: Any | None = None,
    clear_messages: bool = False,
    verbose_direct: bool = True,
    invoke_action: bool = True,
    action_response_parser: Callable = None,
    action_parser_kwargs: dict = None,
    strict_validation=None,
    structure_str=None,
    fallback_structure=None,
    chain_plan: bool = False,
    _extension_ctr=None,
    **kwargs: Any,  # additional model kwargs
) -> tuple[Branch, BaseForm] | BaseForm:

    if clear_messages:
        branch.clear_messages()

    if tools:
        tool_schema = branch.tool_manager.get_tool_schema(tools)

    if not form:
        form = UnitForm(
            instruction=instruction,
            context=context,
            guidance=guidance,
            reason=reason,
            confidence=confidence,
            plan=plan,
            reflect=reflect,
            tool_schema=tool_schema,
            invoke_tool=invoke_tool,
            allow_action=allow_action,
            allow_extension=allow_extension,
            max_extension=max_extension,
            plan_num_step=plan_num_step,
            chain=chain,
            num_chain=num_chain,
            strict=strict_form,
            task_description=task_description,
        )

    elif form and tool_schema:
        form.append_to_input("tool_schema", tool_schema)

    if verbose_direct:
        print("Chatting with model...")

    form = await process_chat(
        branch=branch,
        form=form,
        strict_validation=strict_validation,
        structure_str=structure_str,
        fallback_structure=fallback_structure,
        invoke_action=False,
        **kwargs,
    )

    if allow_action and form.action_required:
        if actions := form.actions:
            if verbose_direct:
                print("Found action requests in model response. Processing actions...")

            form = await process_action(
                branch=branch,
                form=form,
                actions=actions,
                invoke_action=invoke_action,
                action_response_parser=action_response_parser,
                action_parser_kwargs=action_parser_kwargs,
            )

            if verbose_direct:
                print("Actions processed!")

    extension_forms = []
    if allow_extension and form.extension_required:
        if verbose_direct:
            print("Found extension requests in model response. Processing extension...")

        ext, _extension_ctr = await _extend(
            branch=branch,
            form=form,
            max_extension=max_extension - _extension_ctr,
            allow_action=allow_action,
            invoke_action=invoke_action,
            reason=reason,
            confidence=confidence,
            reflect=reflect,
            tool_schema=tool_schema,
            tools=tools,
            verbose_direct=verbose_direct,
            action_response_parser=action_response_parser,
            action_parser_kwargs=action_parser_kwargs,
            strict_validation=strict_validation,
            structure_str=structure_str,
            fallback_structure=fallback_structure,
            chain_plan=chain_plan,
            _extension_ctr=_extension_ctr,
        )
        extension_forms.extend(ext)

    return form, extension_forms, branch, _extension_ctr


# you can only plan once
async def _extend(
    branch: Branch,
    form: UnitForm,
    max_extension: int,
    allow_action: bool = False,
    invoke_action: bool = True,
    reason: bool = False,
    confidence: bool = False,
    reflect: bool = False,
    tool_schema: list = None,
    tools: Any | None = None,
    verbose_direct: bool = True,
    action_response_parser: Callable = None,
    action_parser_kwargs: dict = None,
    strict_validation=None,
    structure_str=None,
    fallback_structure=None,
    chain_plan=False,
    _extension_ctr=0,
):
    last_form = form
    extension_forms = []

    directive_kwargs = {
        "allow_action": allow_action,
        "invoke_action": invoke_action,
        "reason": reason,
        "confidence": confidence,
        "reflect": reflect,
        "tool_schema": tool_schema,
        "verbose_direct": verbose_direct,
        "action_response_parser": action_response_parser,
        "action_parser_kwargs": action_parser_kwargs,
        "strict_validation": strict_validation,
        "structure_str": structure_str,
        "fallback_structure": fallback_structure,
        "chain_plan": chain_plan,
        "tools": tools,
    }

    if plan_ := last_form.plan:
        keys = [f"step_{i+1}" for i in range(len(plan_))]
        plan_ = validate_mapping(plan_, keys, handle_unmatched="force")

        if verbose_direct:
            print(f"Model proposed a {len(plan_)}-step plan. Processing plan...")

        inner_ctr = 0

        for i in keys:
            directive_kwargs["instruction"] = plan_[i]

            if verbose_direct:
                print(
                    "---------------- Processing plan step "
                    f"No.{inner_ctr+1}/{len(plan_)}----------------"
                )

            last_form, _, _ = await _direct(branch, last_form, **directive_kwargs)

            directive_kwargs["_sub_extension_ctr"] += 1
            _extension_ctr += 1
            max_extension -= 1

            last_form._is_extension = True
            extension_forms.append(last_form)

            if not chain_plan:
                if (
                    _extension_ctr
                    >= max_extension + directive_kwargs["_sub_extension_ctr"]
                ):
                    break
                if not last_form.extension_required:
                    break

        if verbose_direct:
            print("Plan processed!")

    else:
        if verbose_direct:
            print(
                f"---------------- Processing Extension No.{_extension_ctr+1}----------------"
            )

        directive_kwargs["max_extension"] = max_extension - _extension_ctr
        last_form, _ext, _ = await _direct(branch, last_form, **directive_kwargs)
        extension_forms.append(last_form)
        extension_forms.extend(_ext)

        extension_forms = list(set(extension_forms))
        extra_extent = len(extension_forms) - len(_ext)
        _extension_ctr += extra_extent

    return extension_forms, _extension_ctr


async def process_direct(
    branch: Branch,
    form: UnitForm | None,
    *,
    instruction: str | str = None,
    context: Any = None,
    guidance: str = LN_UNDEFINED,
    reason: bool = False,
    confidence: bool = False,
    plan: bool = False,
    reflect: bool = False,
    tool_schema: list = None,
    invoke_tool: bool = None,
    allow_action: bool = False,
    allow_extension: bool = False,
    max_extension: int = None,
    tools: Any | None = None,
    return_branch=False,
    chain_plan=False,
    **kwargs: Any,  # additional _direct kwargs
):

    _extension_ctr = 0
    extension_forms = []

    d_kwargs = {
        "branch": branch,
        "form": form,
        "instruction": instruction,
        "context": context,
        "guidance": guidance,
        "reason": reason,
        "confidence": confidence,
        "plan": plan,
        "reflect": reflect,
        "tool_schema": tool_schema,
        "invoke_tool": invoke_tool,
        "allow_action": allow_action,
        "allow_extension": allow_extension,
        "max_extension": max_extension,
        "tools": tools,
        "chain_plan": chain_plan,
        **kwargs,
    }

    async def direct(ctr):
        d_kwargs["_extension_ctr"] = ctr
        return await _direct(**d_kwargs)

    form, exts, branch, _extension_ctr = await direct(_extension_ctr)
    extension_forms.extend(exts)

    last_form = exts[-1] if exts and isinstance(exts, list) else form

    sub_ctr = 0
    while _extension_ctr <= max_extension and last_form.extension_required:
        last_form, _ext, branch, sub_ctr = await direct(_extension_ctr)
        last_form._is_extension = True
        sub_ctr += 1
        _extension_ctr += sub_ctr
        d_kwargs["max_extension"] = max_extension - _extension_ctr
        extension_forms.append(last_form)
        extension_forms.extend(_ext)

    if extension_forms:
        extension_forms = list(set(extension_forms))
        form.extension_forms = extension_forms

    return form, branch if return_branch else form
