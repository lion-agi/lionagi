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

from lionagi.libs.ln_convert import strip_lower
from lionagi.libs.ln_func_call import rcall
from lionagi.core.collections.abc import Directive
from lionagi.core.validator.validator import Validator
from lionagi.core.collections import iModel
from .unit_form import UnitForm
from .unit_mixin import DirectiveMixin
from .util import retry_kwargs


class Unit(Directive, DirectiveMixin):

    default_template = UnitForm

    def __init__(
        self, branch, imodel: iModel = None, template=None, rulebook=None
    ) -> None:
        self.branch = branch
        if imodel and isinstance(imodel, iModel):
            branch.imodel = imodel
            self.imodel = imodel
        else:
            self.imodel = branch.imodel
        self.form_template = template or self.default_template
        self.validator = Validator(rulebook=rulebook) if rulebook else Validator()

    async def chat(
        self,
        instruction=None,
        context=None,
        system=None,
        sender=None,
        recipient=None,
        branch=None,
        requested_fields=None,
        form=None,
        tools=False,
        invoke_tool=True,
        return_form=True,
        strict=False,
        rulebook=None,
        imodel=None,
        clear_messages=False,
        use_annotation=True,
        return_branch=False,
        **kwargs,
    ):
        kwargs = {**retry_kwargs, **kwargs}
        return await rcall(
            self._chat,
            instruction=instruction,
            context=context,
            system=system,
            sender=sender,
            recipient=recipient,
            branch=branch,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            invoke_tool=invoke_tool,
            return_form=return_form,
            strict=strict,
            rulebook=rulebook,
            imodel=imodel,
            clear_messages=clear_messages,
            use_annotation=use_annotation,
            return_branch=return_branch,
            **kwargs,
        )

    async def direct(
        self,
        instruction=None,
        *,
        context=None,
        form=None,
        branch=None,
        tools=None,
        return_branch=False,
        reason: bool = False,
        predict: bool = False,
        score=None,
        select=None,
        plan=None,
        allow_action: bool = False,
        allow_extension: bool = False,
        max_extension: int = None,
        confidence=None,
        score_num_digits=None,
        score_range=None,
        select_choices=None,
        plan_num_step=None,
        predict_num_sentences=None,
        directive: str = None,
        **kwargs,
    ):
        kwargs = {**retry_kwargs, **kwargs}

        if not directive:

            return await rcall(
                self._direct,
                instruction=instruction,
                context=context,
                form=form,
                branch=branch,
                tools=tools,
                return_branch=return_branch,
                reason=reason,
                predict=predict,
                score=score,
                select=select,
                plan=plan,
                allow_action=allow_action,
                allow_extension=allow_extension,
                max_extension=max_extension,
                confidence=confidence,
                score_num_digits=score_num_digits,
                score_range=score_range,
                select_choices=select_choices,
                plan_num_step=plan_num_step,
                predict_num_sentences=predict_num_sentences,
                **kwargs,
            )

        return await rcall(
            self._mono_direct,
            directive=directive,
            instruction=instruction,
            context=context,
            branch=branch,
            tools=tools,
            **kwargs,
        )

    async def select(self, *args, **kwargs):
        """
        Asynchronously performs a select operation using the _select method with
        retry logic.

        Args:
            *args: Positional arguments to pass to the _select method.
            **kwargs: Keyword arguments to pass to the _select method, including
                retry configurations.

        Returns:
            Any: The result of the select operation.
        """
        from .template.select import SelectTemplate

        kwargs = {**retry_kwargs, **kwargs}
        kwargs["template"] = kwargs.get("template", SelectTemplate)
        return await rcall(self._select, *args, **kwargs)

    async def predict(self, *args, **kwargs):
        """
        Asynchronously performs a predict operation using the _predict method with
        retry logic.

        Args:
            *args: Positional arguments to pass to the _predict method.
            **kwargs: Keyword arguments to pass to the _predict method, including
                retry configurations.

        Returns:
            Any: The result of the predict operation.
        """
        from .template.predict import PredictTemplate

        kwargs = {**retry_kwargs, **kwargs}
        kwargs["template"] = kwargs.get("template", PredictTemplate)
        return await rcall(self._predict, *args, **kwargs)

    async def score(self, *args, **kwargs):
        from .template.score import ScoreTemplate

        kwargs = {**retry_kwargs, **kwargs}
        kwargs["template"] = kwargs.get("template", ScoreTemplate)
        return await rcall(self._score, *args, **kwargs)

    async def plan(self, *args, **kwargs):
        from .template.plan import PlanTemplate

        kwargs = {**retry_kwargs, **kwargs}
        kwargs["template"] = kwargs.get("template", PlanTemplate)
        return await rcall(self._plan, *args, **kwargs)

    async def _mono_direct(
        self,
        directive: str,  # examples, "chat", "predict", "act"
        instruction=None,  # additional instruction
        context=None,  # context to perform the instruction on
        system=None,  # optionally swap system message
        branch=None,
        tools=None,
        template=None,
        **kwargs,
    ):

        if template:
            kwargs["template"] = template

        kwargs = {**retry_kwargs, **kwargs}
        branch = branch or self.branch

        if system:
            branch.add_message(system=system)

        if hasattr(self, strip_lower(directive)):
            directive = getattr(self, strip_lower(directive))

            return await directive(
                context=context,
                instruction=instruction,
                tools=tools,
                **kwargs,
            )

        raise ValueError(f"invalid directive: {directive}")
