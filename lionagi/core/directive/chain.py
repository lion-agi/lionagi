from typing import Type
from .base import BaseDirective
from ._mapping import *


class Chain(Chat):

    async def chain(
        self,
        context=None,
        instruction=None,
        confidence_score=None,
        reason=False,  # for directive
        branch=None,
        rulebook=None,
        imodel=None,
        num_step=None,
        return_branch=False,
        plan_params={},
        plan_kwargs={},
        directive: Type[BaseDirective] | str = None,
        directive_obj=None,
        directive_params={},
        directive_kwargs={},
        **kwargs,
    ):
        branch = branch or self.branch
        plan_params["rulebook"] = rulebook or plan_params.get("rulebook", None)

        direct_plan = Plan(branch=branch, **plan_params)

        plan_kwargs["imodel"] = imodel or plan_kwargs.get("imodel", None)
        plan_kwargs["reason"] = reason or plan_kwargs.get("reason", None)
        plan_kwargs["confidence_score"] = confidence_score or plan_kwargs.get(
            "confidence_score", None
        )
        plan_kwargs["num_step"] = num_step or plan_kwargs.get("num_step", 3)
        plan_kwargs["timing"] = False

        out_form, branch = await direct_plan.plan(
            context=context,
            branch=branch,
            instruction=instruction,
            return_branch=True,
            **plan_kwargs,
        )

        plan = out_form.plan
        # directives = out_form.directives
        plan = [plan] if isinstance(plan, dict) else plan

        directive_params["rulebook"] = rulebook or directive_params.get(
            "rulebook", None
        )

        if not directive_obj:
            if isinstance(directive, str):
                directive = DIRECTIVE_MAPPING.get(directive, Predict)
            if isinstance(directive, type):
                directive = directive or Predict
            if not issubclass(directive, BaseDirective):
                raise ValueError(
                    f"directive must be a subclass of BaseDirective, got {type(directive)}"
                )

        directive_obj = directive_obj or directive(branch=branch, **directive_params)

        directive_kwargs = {**directive_kwargs, **kwargs}
        directive_kwargs["reason"] = reason or directive_kwargs.get("reason", None)
        directive_kwargs["confidence_score"] = confidence_score or directive_kwargs.get(
            "confidence_score", None
        )

        chain_forms = []
        for idx in range(len(plan)):
            _form = await directive_obj.direct(
                instruction=plan[f"step_{idx+1}"], **directive_kwargs
            )
            chain_forms.append(_form)

        out_form.add_field("chain_forms", list, None, chain_forms)

        reasons = {}
        confidence_scores = []
        for idx, item in enumerate(chain_forms):
            reasons[f"step_{idx+1}"] = getattr(item, "reason", "N/A")
            confidence_scores.append(getattr(item, "confidence_score", 0))

        if reasons:
            setattr(out_form, "chain_reasons", reasons)

        if sum(confidence_scores) > 0:
            setattr(
                out_form,
                "chain_confidence_score",
                sum(confidence_scores) / len(chain_forms),
            )

        if return_branch:
            return out_form, branch

        return out_form
