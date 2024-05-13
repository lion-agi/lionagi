from typing import Any
from lionagi.libs import SysUtil
from lionagi.libs.ln_func_call import lcall
from lionagi.core.generic.abc import LionFieldError

from ..generic.abc import LionFieldError
from ..rules.base import Rule
from ..rules._default import DEFAULT_RULES
from ..rules.rulebook import RuleBook
from ..report.form import Form
from ..report.report import Report


_DEFAULT_RULEORDER = [
    "choice",
    "actionrequest",
    "bool",
    "number",
    "mapping",
    "str",
]

_DEFAULT_RULES = {
    "choice": DEFAULT_RULES.CHOICE.value,
    "actionrequest": DEFAULT_RULES.ACTION.value,
    "bool": DEFAULT_RULES.BOOL.value,
    "number": DEFAULT_RULES.NUMBER.value,
    "mapping": DEFAULT_RULES.MAPPING.value,
    "str": DEFAULT_RULES.STR.value,
}


class Validator:

    def __init__(
        self,
        *,
        rulebook: RuleBook = None,
        rules=None,
        order: list[str] = None,
        init_config: dict[str, dict] = None,
        active_rules: dict[str, Rule] = None,
    ):
        self.ln_id: str = SysUtil.create_id()
        self.timestamp: str = SysUtil.get_timestamp(sep=None)[:-6]
        self.rulebook = rulebook or RuleBook(
            rules or _DEFAULT_RULES, order or _DEFAULT_RULEORDER, init_config
        )
        self.active_rules: dict[str, Rule] = active_rules or self._initiate_rules()

    def _initiate_rules(self):

        def _init_rule(rule_name):
            if not issubclass(self.rulebook[rule_name], Rule):
                raise LionFieldError(
                    f"Invalid rule class for {rule_name}, must be a subclass of Rule"
                )

            _config = self.rulebook.rule_config[rule_name] or {}
            if not isinstance(_config, dict):
                raise LionFieldError(
                    f"Invalid config for {rule_name}, must be a dictionary"
                )

            _rule = self.rulebook.rules[rule_name](**_config.get("config", {}))
            _rule.fields = _config.get("fields", [])
            _rule._is_init = True
            return _rule

        _rules = lcall(self.rulebook.ruleorder, _init_rule)

        return {
            rule_name: _rules[idx]
            for idx, rule_name in enumerate(self.rulebook.ruleorder)
            if getattr(_rules[idx], "_is_init", None) == True
        }

    async def validate_report(
        self, report: Report, forms, strict: bool = False
    ) -> Report:
        report.fill(forms, strict=strict)
        return report

    async def validate_response(
        self,
        form: Form,
        response: dict | str,
        strict: bool = False,
        use_annotation: bool = True,
    ) -> Form:
        if isinstance(response, str):
            if len(form.requested_fields) == 1:
                response = {form.requested_fields[0]: response}
            else:
                raise ValueError(
                    "Response is a string, but form has multiple fields to be filled"
                )

        dict_ = {}
        for k, v in response.items():

            if k in form.requested_fields:
                kwargs = form.validation_kwargs.get(k, {})
                _annotation = form._field_annotations[k]
                if (keys := form._get_field_attr(k, "choices", None)) is not None:
                    v = await self.validate_field(
                        field=k,
                        value=v,
                        form=form,
                        annotation=_annotation,
                        strict=strict,
                        keys=keys,
                        use_annotation=use_annotation,
                        **kwargs,
                    )

                elif (_keys := form._get_field_attr(k, "keys", None)) is not None:
                    
                    v = await self.validate_field(
                        field=k,
                        value=v,
                        form=form,
                        annotation=_annotation,
                        strict=strict,
                        keys=_keys,
                        use_annotation=use_annotation,
                        **kwargs,
                    )

                else:
                    v = await self.validate_field(
                        field=k,
                        value=v,
                        form=form,
                        annotation=_annotation,
                        strict=strict,
                        use_annotation=use_annotation,
                        **kwargs,
                    )

                dict_[k] = v
        form.fill(**dict_)
        return form

    async def validate_field(
        self,
        field: str,
        value: Any,
        form: Form,
        *args,
        annotation=None,
        strict=True,
        use_annotation=True,
        **kwargs,
    ) -> Any:
        for rule in self.active_rules.values():
            try:
                if await rule.applies(
                    field,
                    value,
                    form,
                    *args,
                    annotation=annotation,
                    use_annotation=use_annotation,
                    **kwargs,
                ):
                    return await rule.invoke(field, value, form)
            except Exception as e:
                raise LionFieldError(f"failed to validate {field}") from e

        if strict:
            raise LionFieldError(
                f"failed to validate {field} because no rule applied, if you want to return the original value directly when no rule applies, set strict=False"
            )
