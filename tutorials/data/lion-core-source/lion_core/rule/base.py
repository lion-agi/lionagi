import inspect
from abc import abstractmethod
from collections.abc import Callable
from typing import Any

from lionabc import Action, Condition
from lionabc.exceptions import LionOperationError
from lionfuncs import to_dict, to_list, ucall
from pydantic import Field, PrivateAttr
from typing_extensions import override

from lion_core.form.base import BaseForm
from lion_core.generic.element import Element
from lion_core.generic.note import Note, note

RULE_SYS_FIELDS = [
    "base_config",
    "fix",
    "apply_types",
    "exclude_types",
    "apply_fields",
    "exclude_fields",
    "validation_kwargs",
    "accept_info_key",
]


class Rule(Element, Condition, Action):
    base_config: dict | None = {}
    info: Note | None = Field(default_factory=note)
    status: str = Field(default="active")
    _is_init: bool = PrivateAttr(False)

    def __init__(
        self,
        *,
        info: Note = None,
        accept_info_key=[],
        **kwargs,
    ):
        super().__init__()
        self.info = prepare_info(
            info=info,
            base_config=self.base_config,
            accept_info_key=accept_info_key
            or self.base_config.get("accept_info_key", []),
            **kwargs,
        )

    @property
    def fix(self):
        return self.info.get(["fix"], False)

    @fix.setter
    def fix(self, value: bool):
        if not isinstance(value, bool):
            raise LionOperationError("fix must be a boolean")
        self.info["fix"] = value

    @property
    def apply_types(self):
        return self.info.get(["apply_types"], [])

    @apply_types.setter
    def apply_types(self, value: list[str]):
        apply_types = validate_types(value)
        self.info["apply_types"] = apply_types

    @property
    def exclude_types(self):
        return self.info.get(["exclude_types"], [])

    @exclude_types.setter
    def exclude_types(self, value: list[str]):
        exclude_types = validate_types(value)
        self.info["exclude_types"] = exclude_types

    @property
    def apply_fields(self):
        return self.info.get(["apply_fields"], [])

    @apply_fields.setter
    def apply_fields(self, value: list[str]):
        value = to_list(value, dropna=True, flatten=True)
        for i in value:
            if not isinstance(i, str):
                raise LionOperationError("apply_fields must be a list of str")

        self.info["apply_fields"] = value

    @property
    def exclude_fields(self):
        return self.info.get(["exclude_fields"], [])

    @exclude_fields.setter
    def exclude_fields(self, value: list[str]):
        value = to_list(value, dropna=True, flatten=True)
        for i in value:
            if not isinstance(i, str):
                raise LionOperationError(
                    "exclude_fields must be a list of str"
                )

        self.info["exclude_fields"] = value

    @property
    def validation_kwargs(self) -> dict:
        """a dict for fix_value method"""
        return self.info.get(["validation_kwargs"], {})

    @validation_kwargs.setter
    def validation_kwargs(self, value: dict):
        value = to_dict(value)
        self.info["validation_kwargs"] = value

    # must only return True or False
    @override
    async def apply(
        self,
        field: str,
        value: Any,
        /,
        annotation: Any = None,
        check_func: Callable | Any = None,
        **kwargs,
    ) -> bool:
        """
        Apply the rule to a specific field.

        Args:
            field: The field to apply the rule to.
            value: The value of the field.
            form: The form containing the field.
            apply_fields: Fields to apply the rule to
                (overrides instance setting).
            exclude_fields: Fields to exclude from the rule
                (overrides instance setting).
            annotation: Field annotation for type-based rule application.
            check_func: Custom function for condition checking
            **kwargs: Additional arguments for the check function or
                self.rule_condition

        Returns:
            bool: True if the rule should be applied, False otherwise.

        Raises:
            LionOperationError: If an invalid check function is provided.
        """

        if field in self.exclude_fields:
            return False

        if field in self.apply_fields:
            return True

        if self.rule_condition != Rule.rule_condition:
            check_func = check_func or self.rule_condition
            if not isinstance(check_func, Callable):
                raise LionOperationError("Invalid check function provided")
            try:
                a = await ucall(check_func, field, value, **kwargs)
                if isinstance(a, bool):
                    return a
            except Exception:
                return False

        # if not in custom fields, nor using custom validation condition
        # we will resort to use field annotation
        if not annotation:
            return False

        if isinstance(annotation, dict) and field in annotation:
            annotation = annotation[field]
        annotation = (
            [annotation] if isinstance(annotation, str) else annotation
        )

        if annotation and len(annotation) > 0:
            for i in annotation:
                if i in self.apply_types and i not in self.exclude_types:
                    return True
            return False

        return False

    # must only return True or False
    async def rule_condition(
        self,
        field: str,
        value: Any,
        /,
        form: BaseForm,
        **kwargs,
    ) -> bool:
        """
        Default rule condition method.

        This method can be optionally overridden in subclasses to implement
        specific condition checking logic.

        Returns:
            bool: Always returns False in the base implementation.
        """
        return False

    @abstractmethod
    async def check_value(self, value: Any, /):
        """raise error if check failed"""
        ...

    async def fix_value(self, value: Any, /) -> Any:
        return value

    async def validate(self, value: Any, /) -> Any:
        try:
            await self.check_value(value)
            return value

        except Exception as e1:
            if self.fix:
                try:
                    return await self.fix_value(value)
                except Exception as e2:
                    raise LionOperationError(
                        f"Failed to validate field: {e2}",
                    ) from e1
        return value

    @override
    async def invoke(
        self,
        field: str,
        value: Any,
        /,
        form: BaseForm,
        check_func: Callable | Any = None,
        **kwargs,  # additional kwargs for check func or self.rule_condition
    ) -> Any:
        if not await self.apply(
            field,
            value,
            form=form,
            check_func=check_func,
            **kwargs,
        ):
            return value
        return await self.validate(value)


def prepare_info(
    info: dict | None,
    base_config: dict,
    accept_info_key: list,
    **kwargs,
):
    d_ = {}
    if info is not None:
        if isinstance(info, dict):
            d_ = info
        if isinstance(info, Note):
            d_ = info.to_dict()

    config = {**base_config, **kwargs}
    d_ = {**d_, **config}
    _d = {}

    for k, v in d_.items():
        if k not in RULE_SYS_FIELDS + accept_info_key:
            _d["validation_kwargs"] = _d.get("validation_kwargs", {})
            _d["validation_kwargs"].update({k: v})
        else:
            _d[k] = v

    return note(**_d)


def validate_types(value):
    apply_types = []
    value = to_list(value, dropna=True, flatten=True)

    for i in value:
        if isinstance(i, str):
            apply_types.append(i)
        elif inspect.isclass(i):
            apply_types.append(i.__name__)

    if len(apply_types) != len(value):
        raise LionOperationError("apply_types must be a list of str or type")

    return apply_types


# File: lion_core/rule/base.py
