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

import asyncio
from typing import Any, Dict, List, Union, Callable
from lionagi.libs import SysUtil
from lionagi.libs.lionfuncs import lcall
from lion_core.exceptions import LionValueError
from lionagi.core.collections.model import iModel
from ..rule.base import Rule
from lion_core.rule.default_rules._default import DEFAULT_RULE_INFO, DEFAULT_RULEORDER
from ..rule.rulebook import RuleBook
from ..report.form import Form
from ..report.report import Report


class Validator:
    """
    Validator class to manage the validation of forms using a RuleBook.
    """

    def __init__(
        self,
        *,
        rulebook: RuleBook = None,
        rules: Dict[str, Rule] = None,
        order: List[str] = None,
        init_config: Dict[str, Dict] = None,
        active_rules: Dict[str, Rule] = None,
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

        self.ln_id: str = SysUtil.id()
        self.timestamp: str = SysUtil.time()
        self.rulebook = rulebook or RuleBook(
            rules_info=DEFAULT_RULE_INFO, default_rule_order=DEFAULT_RULEORDER
        )
        if not active_rules:
            for k, v in self.rulebook.rules_info.items():
                self.rulebook.init_rule(k)
        self.validation_log = []
        self.formatter = formatter
        self.format_kwargs = format_kwargs

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
            LionLionValueError: If validation fails.
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
                raise LionValueError(f"Failed to validate {field}") from e

        if strict:
            error_message = (
                f"Failed to validate {field} because no rule applied. To return the "
                f"original value directly when no rule applies, set strict=False."
            )
            self.log_validation_error(field, value, error_message)
            raise LionValueError(error_message)

    async def validate_report(
        self, report: Report, forms: List[Form], strict: bool = True
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
        response: Union[dict, str],
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
            if len(form.request_fields) == 1:
                response = {form.request_fields[0]: response}
            else:
                if self.formatter:
                    if asyncio.iscoroutinefunction(self.formatter):
                        response = await self.formatter(response, **self.format_kwargs)
                        print("formatter used")
                    else:
                        response = self.formatter(response, **self.format_kwargs)
                        print("formatter used")

        if not isinstance(response, dict):
            raise ValueError(f"The form response format is invalid for filling.")

        dict_ = {}
        for k, v in response.items():
            if k in form.request_fields:
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
        self.rulebook.default_rule_order.append(rule_name)
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

    def get_validation_summary(self) -> Dict[str, Any]:
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
