from abc import abstractmethod
from typing import Any, Dict, List

from pandas import Series

from lionagi.core.collections.abc import (
    Actionable,
    Component,
    Condition,
    FieldError,
)
from lionagi.libs import SysUtil

_rule_classes = {}


class Rule(Component, Condition, Actionable):
    """
    Combines a condition and an action that can be applied based on it.

    Attributes:
        apply_type (str): The type of data to which the rule applies.
        fix (bool): Indicates whether the rule includes a fix action.
        fields (list[str]): List of fields to which the rule applies.
        validation_kwargs (dict): Keyword arguments for validation.
        applied_log (list): Log of applied rules.
        invoked_log (list): Log of invoked rules.
        _is_init (bool): Indicates whether the rule is initialized.
    """

    exclude_type: list[str] = []
    apply_type: list[str] | str = None
    fix: bool = True
    fields: list[str] = []
    validation_kwargs: dict = {}
    applied_log: list = []
    invoked_log: list = []
    _is_init: bool = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in _rule_classes:
            _rule_classes[cls.__name__] = cls

    def add_log(
        self, field: str, form: Any, apply: bool = True, **kwargs
    ) -> None:
        """
        Adds an entry to the applied or invoked log.

        Args:
            field (str): The field being validated.
            form (Any): The form being validated.
            apply (bool): Indicates whether the log is for an applied rule.
            **kwargs: Additional configuration parameters.
        """
        a = {
            "type": "rule",
            "class": self.class_name,
            "ln_id": self.ln_id,
            "timestamp": SysUtil.get_timestamp(sep=None)[:-6],
            "field": field,
            "form": form.ln_id,
            "config": kwargs,
        }
        if apply:
            self.applied_log.append(a)
        else:
            self.invoked_log.append(a)

    async def applies(
        self,
        field: str,
        value: Any,
        form: Any,
        *args,
        annotation: list[str] = None,
        use_annotation: bool = True,
        **kwargs,
    ) -> bool:
        """
        Determines whether the rule applies to a given field and value.

        Args:
            field (str): The field being validated.
            value (Any): The value of the field.
            form (Any): The form being validated.
            *args: Additional arguments.
            annotation (list[str], optional): Annotations for the field.
            use_annotation (bool): Indicates whether to use annotations.
            **kwargs: Additional keyword arguments.

        Returns:
            bool: True if the rule applies, otherwise False.
        """
        if self.fields:
            if field in self.fields:
                self.add_log(field, form, **kwargs)
                return True

        if use_annotation:
            annotation = annotation or form._get_field_annotation(field)
            annotation = (
                [annotation] if isinstance(annotation, str) else annotation
            )

            for i in annotation:
                if i in self.apply_type and i not in self.exclude_type:
                    self.add_log(field, form, **kwargs)
                    return True
            return False

        a = await self.rule_condition(field, value, *args, **kwargs)

        if a:
            self.add_log(field, form, **kwargs)
            return True
        return False

    async def invoke(self, field: str, value: Any, form: Any) -> Any:
        """
        Invokes the rule's validation logic on a field and value.

        Args:
            field (str): The field being validated.
            value (Any): The value of the field.
            form (Any): The form being validated.

        Returns:
            Any: The validated or fixed value.

        Raises:
            ValueError: If validation or fixing fails.
        """
        try:
            a = await self.validate(value, **self.validation_kwargs)
            self.add_log(field, form, apply=False, **self.validation_kwargs)
            return a

        except Exception as e1:
            if self.fix:
                try:
                    a = await self.perform_fix(value, **self.validation_kwargs)
                    self.add_log(
                        field, form, apply=False, **self.validation_kwargs
                    )
                    return a
                except Exception as e2:
                    raise FieldError(f"failed to fix field") from e2
            raise FieldError(f"failed to validate field") from e1

    async def rule_condition(self, field, value, *args, **kwargs) -> bool:
        """
        Additional condition, if choosing not to use annotation as a qualifier.

        Args:
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            bool: False by default, should be overridden by subclasses.
        """
        return False

    async def perform_fix(self, value: Any, *args, **kwargs) -> Any:
        """
        Attempts to fix a value if validation fails.

        Args:
            value (Any): The value to fix.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The fixed value.

        Raises:
            ValueError: If the fix fails.
        """
        return value

    @abstractmethod
    async def validate(self, value: Any) -> Any:
        """
        Abstract method to validate a value.

        Args:
            value (Any): The value to validate.

        Returns:
            Any: The validated value.

        Raises:
            ValueError: If validation fails.
        """
        pass

    def _to_dict(self) -> dict[str, Any]:
        """
        Converts the rule's attributes to a dictionary.

        Returns:
            dict: A dictionary representation of the rule.
        """
        return {
            "ln_id": self.ln_id[:8] + "...",
            "rule": self.__class__.__name__,
            "apply_type": self.apply_type,
            "fix": self.fix,
            "fields": self.fields,
            "validation_kwargs": self.validation_kwargs,
            "num_applied": len(self.applied_log),
            "num_invoked": len(self.invoked_log),
        }

    def __str__(self) -> str:
        """
        Returns a string representation of the rule using a pandas Series.

        Returns:
            str: A string representation of the rule.
        """
        series = Series(self._to_dict())
        return series.__str__()

    def __repr__(self) -> str:
        """
        Returns a string representation of the rule using a pandas Series.

        Returns:
            str: A string representation of the rule.
        """
        series = Series(self._to_dict())
        return series.__repr__()
