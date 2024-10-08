from collections.abc import Callable
from typing import Any

from lionabc.exceptions import LionTypeError, LionValueError
from lionfuncs import ucall

from lion_core.action.action_executor import ActionExecutor
from lion_core.action.action_processor import ActionProcessor
from lion_core.form.base import BaseForm
from lion_core.form.form import Form
from lion_core.generic.progression import Progression
from lion_core.rule.base import Rule
from lion_core.rule.rulebook import RuleBook


class RuleProcessor(ActionProcessor):

    event_type: type[Rule] = Rule

    def __init__(
        self,
        capacity: int,
        refresh_time: float,
        rulebook: RuleBook = None,
        strict_rules: bool = True,
        structure_func: Callable = None,
    ):
        super().__init__(capacity, refresh_time)
        self.rulebook = rulebook or RuleBook()
        self.strict_rules = strict_rules
        self.structure_func = structure_func

    def init_rule(
        self,
        rule_order: list = None,
        rule_progress: str = None,  # an existing progress in rulebook
    ):
        if not rule_order:
            rule_order = self.rulebook.default_rule_order

        rule_progress = self.rulebook.rule_flow._find_prog(rule_progress)
        for i in rule_order:
            self.rulebook.init_rule(i, progress=rule_progress)

    async def process_field(
        self,
        field: str,
        value: Any,
        /,
        *,
        field_annotation=None,
        form: BaseForm = None,
        rule_progress=None,
        check_func: Callable = None,
        **kwargs,
    ):
        if field_annotation is None:
            if isinstance(form, BaseForm) and field in form.all_fields:
                field_annotation = form.field_getattr(field, "annotation")

        for i in self.rulebook.rule_flow[rule_progress]:
            rule: Rule = self.rulebook.active_rules[i]
            if await rule.apply(
                field,
                value,
                annotation=field_annotation,
                check_func=check_func,
                **kwargs,
            ):
                try:
                    return await rule.validate(value)
                except Exception as e:
                    raise LionValueError(
                        f"Failed to validate field: {field}"
                    ) from e

        if self.strict_rules:
            error_message = (
                f"Failed to validate {field} because no rule applied."
                " To return the original value directly when no rule "
                "applies, set strict=False."
            )
            raise LionValueError(error_message)

        return value

    async def process(
        self,
        form: Form,
        response: dict | str,
        rule_progress: Progression | str = None,
        structure_str: bool = True,
        structure_func: Callable | None = None,
        **kwargs,  # additional kwargs for fallback_structure
    ):
        return await self.process_form(
            form,
            response,
            rule_progress=rule_progress,
            structure_str=structure_str,
            structure_func=structure_func,
            **kwargs,
        )

    async def process_form(
        self,
        form: Form,
        model_response: dict | str,
        rule_progress=None,
        structure_str: bool = True,
        structure_func: Callable | None = None,
        **kwargs,  # additional kwargs for fallback_structure
    ):
        if isinstance(model_response, str):
            if len(form.request_fields) == 1:
                model_response = {form.request_fields[0]: model_response}
            else:
                if structure_str:
                    structure_func = structure_func or self.structure_func

                    if structure_func is None:
                        raise ValueError(
                            "Response is a string, you asked to structure "
                            "the string but no structure function is provided"
                        )
                    try:
                        model_response = await ucall(
                            structure_func, model_response, **kwargs
                        )
                    except Exception as e:
                        raise ValueError(
                            "Failed to structure the response string"
                            "Response is a string, but form has multiple"
                            " fields to be filled"
                        ) from e

            if not isinstance(model_response, dict):
                raise LionTypeError(
                    expected_type=dict,
                    received_type=type(model_response),
                )

        dict_ = {}
        for k, v in model_response.items():
            if k in form.request_fields:
                kwargs = form.validation_kwargs.get(k, {})
                _annotation = form.field_getattr(k, "annotation")

                kwargs["annotation"] = _annotation
                if (keys := form.field_getattr(k, "keys", None)) is not None:
                    kwargs["keys"] = keys

                v = await self.process_field(
                    k, v, rule_progress=rule_progress, **kwargs
                )

            dict_[k] = v

        form.fill_request_fields(**dict_)
        return form


class RuleExecutor(ActionExecutor):
    pass
