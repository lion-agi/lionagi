import asyncio
from collections.abc import Callable
from typing import Any, Dict, List, Union

from lionfuncs import lcall

from lionagi.core.collections.abc import FieldError
from lionagi.libs import SysUtil

from ..report.form import Form
from ..report.report import Report
from ..rule._default import DEFAULT_RULES
from ..rule.base import Rule
from ..rule.rulebook import RuleBook

_DEFAULT_RULEORDER = [
    "choice",
    "actionrequest",
    "number",
    "mapping",
    "str",
    "bool",
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
    """
    Validator class to manage the validation of forms using a RuleBook.
    """

    def __init__(
        self,
        *,
        rulebook: RuleBook = None,
        rules: dict[str, Rule] = None,
        order: list[str] = None,
        init_config: dict[str, dict] = None,
        active_rules: dict[str, Rule] = None,
        formatter: Callable = None,
        format_kwargs: dict = {},
    ):
        """
        Initialize the Validator.

        Args:
            rulebook (RuleBook, optional): The RuleBook containing validation rules.
            rules (Dict[str, Rule], optional): Dictionary of validation rules.
            order (List[str], optional): List defining the order of rule application.
            init_config (Dict[str, Dict], optional): Configuration for initializing rules.
            active_rules (Dict[str, Rule], optional): Dictionary of currently active rules.
        """

        self.ln_id: str = SysUtil.create_id()
        self.timestamp: str = SysUtil.get_timestamp(sep=None)[:-6]
        self.rulebook = rulebook or RuleBook(
            rules or _DEFAULT_RULES, order or _DEFAULT_RULEORDER, init_config
        )
        self.active_rules: dict[str, Rule] = (
            active_rules or self._initiate_rules()
        )
        self.validation_log = []
        self.formatter = formatter
        self.format_kwargs = format_kwargs

    def _initiate_rules(self) -> dict[str, Rule]:
        """
        Initialize rules from the rulebook.

        Returns:
            dict: A dictionary of active rules.
        """

        def _init_rule(rule_name: str) -> Rule:

            if not issubclass(self.rulebook[rule_name], Rule):
                raise FieldError(
                    f"Invalid rule class for {rule_name}, must be a subclass of Rule"
                )

            _config = self.rulebook.rule_config[rule_name] or {}
            if not isinstance(_config, dict):
                raise FieldError(
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
            if getattr(_rules[idx], "_is_init", None)
        }

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
        """
        Validate a specific field in a form.

        Args:
            field (str): The field to validate.
            value (Any): The value of the field.
            form (Form): The form containing the field.
            *args: Additional arguments.
            annotation (list[str], optional): Annotations for the field.
            strict (bool): Whether to enforce strict validation.
            use_annotation (bool): Whether to use annotations for validation.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The validated value.

        Raises:
            LionFieldError: If validation fails.
        """
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
                self.log_validation_error(field, value, str(e))
                raise FieldError(f"Failed to validate {field}") from e

        if strict:
            error_message = (
                f"Failed to validate {field} because no rule applied. To return the "
                f"original value directly when no rule applies, set strict=False."
            )
            self.log_validation_error(field, value, error_message)
            raise FieldError(error_message)

    async def validate_report(
        self, report: Report, forms: list[Form], strict: bool = True
    ) -> Report:
        """
        Validate a report based on active rules.

        Args:
            report (Report): The report to validate.
            forms (list[Form]): A list of forms to include in the report.
            strict (bool): Whether to enforce strict validation.

        Returns:
            Report: The validated report.
        """
        report.fill(forms, strict=strict)
        return report

    async def validate_response(
        self,
        form: Form,
        response: dict | str,
        strict: bool = True,
        use_annotation: bool = True,
    ) -> Form:
        """
        Validate a response for a given form.

        Args:
            form (Form): The form to validate against.
            response (dict | str): The response to validate.
            strict (bool): Whether to enforce strict validation.
            use_annotation (bool): Whether to use annotations for validation.

        Returns:
            Form: The validated form.

        Raises:
            ValueError: If the response format is invalid.
        """
        if isinstance(response, str):
            if len(form.requested_fields) == 1:
                response = {form.requested_fields[0]: response}
            else:
                if self.formatter:
                    if asyncio.iscoroutinefunction(self.formatter):
                        response = await self.formatter(
                            response, **self.format_kwargs
                        )
                        print("formatter used")
                    else:
                        response = self.formatter(
                            response, **self.format_kwargs
                        )
                        print("formatter used")

        if not isinstance(response, dict):
            raise ValueError(
                f"The form response format is invalid for filling."
            )

        dict_ = {}
        for k, v in response.items():
            if k in form.requested_fields:
                kwargs = form.validation_kwargs.get(k, {})
                _annotation = form._field_annotations[k]
                if (
                    keys := form._get_field_attr(k, "choices", None)
                ) is not None:
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

                elif (
                    _keys := form._get_field_attr(k, "keys", None)
                ) is not None:

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

    def add_rule(self, rule_name: str, rule: Rule, config: dict = None):
        """
        Add a new rule to the validator.

        Args:
            rule_name (str): The name of the rule.
            rule (Rule): The rule object.
            config (dict, optional): Configuration for the rule.
        """
        if rule_name in self.active_rules:
            raise ValueError(f"Rule '{rule_name}' already exists.")
        self.active_rules[rule_name] = rule
        self.rulebook.rules[rule_name] = rule
        self.rulebook.ruleorder.append(rule_name)
        self.rulebook.rule_config[rule_name] = config or {}

    def remove_rule(self, rule_name: str):
        """
        Remove an existing rule from the validator.

        Args:
            rule_name (str): The name of the rule to remove.
        """
        if rule_name not in self.active_rules:
            raise ValueError(f"Rule '{rule_name}' does not exist.")
        del self.active_rules[rule_name]
        del self.rulebook.rules[rule_name]
        self.rulebook.ruleorder.remove(rule_name)
        del self.rulebook.rule_config[rule_name]

    def list_active_rules(self) -> list:
        """
        List all active rules.

        Returns:
            list: A list of active rule names.
        """
        return list(self.active_rules.keys())

    def enable_rule(self, rule_name: str, enable: bool = True):
        """
        Enable a specific rule.

        Args:
            rule_name (str): The name of the rule.
            enable (bool): Whether to enable or disable the rule.
        """
        if rule_name not in self.active_rules:
            raise ValueError(f"Rule '{rule_name}' does not exist.")
        self.active_rules[rule_name].enabled = enable

    def disable_rule(self, rule_name: str):
        """
        Disable a specific rule.

        Args:
            rule_name (str): The name of the rule to disable.
        """
        self.enable_rule(rule_name, enable=False)

    def log_validation_attempt(self, form: Form, result: dict):
        """
        Log a validation attempt.

        Args:
            form (Form): The form being validated.
            result (dict): The result of the validation.
        """
        log_entry = {
            "form_id": form.ln_id,
            "timestamp": SysUtil.get_timestamp(),
            "result": result,
        }
        self.validation_log.append(log_entry)

    def log_validation_error(self, field: str, value: Any, error: str):
        """
        Log a validation error.

        Args:
            field (str): The field that failed validation.
            value (Any): The value of the field.
            error (str): The error message.
        """
        log_entry = {
            "field": field,
            "value": value,
            "error": error,
            "timestamp": SysUtil.get_timestamp(),
        }
        self.validation_log.append(log_entry)

    def get_validation_summary(self) -> dict[str, Any]:
        """
        Get a summary of validation results.

        Returns:
            dict: A summary of validation attempts, errors, and successful attempts.
        """
        summary = {
            "total_attempts": len(self.validation_log),
            "errors": [log for log in self.validation_log if "error" in log],
            "successful_attempts": [
                log for log in self.validation_log if "result" in log
            ],
        }
        return summary
