from lion_core.abc import BaseExecutor, BaseProcessor


class BaseValidator(BaseExecutor, BaseProcessor):
    def __init__(
        self,
        *,
        rulebook: RuleBook = None,
        rules: Dict[str, Rule] = None,
        order: List[str] = None,
        init_config: Dict[str, Dict] = None,
        active_rules: Dict[str, Rule] = None,
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
        self.active_rules: Dict[str, Rule] = active_rules or self._initiate_rules()
        self.validation_log = []

    def _initiate_rules(self) -> Dict[str, Rule]:
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
