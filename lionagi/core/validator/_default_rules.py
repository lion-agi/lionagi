from ..generic.abc import Rule
from lionagi.libs import validation_funcs


class ChoiceRule(Rule):

    async def applies(self, choices=None):
        return choices is not None

    async def invoke(self, value, choices=None, **kwargs):
        if value in self.check_choices(choices):
            return value
        if self.perform_fix:
            kwargs = {**self.validation_kwargs, **kwargs}
            return await self.perform_fix(value, choices, **kwargs)
        raise ValueError(f"{value} is not in chocies {choices}")

    async def perform_fix(self, value, choices=None, **kwargs):
        v_ = validation_funcs["enum"](value, choices=choices, fix_=True, **kwargs)
        return v_

    def check_choices(self, choices=None):
        if choices and not isinstance(choices, list):
            try:
                choices = [i.value for i in choices]
            except Exception as e:
                raise ValueError(f"failed to get choices") from e
        return choices


class ActionRequestRule(Rule):

    async def applies(self, annotation=None):
        return any("actionrequest" in i for i in annotation)

    async def invoke(self, value):
        try:
            return validation_funcs["action"](value)
        except Exception as e:
            raise ValueError(f"failed to validate field") from e


class BooleanRule(Rule):

    async def applies(self, annotation=None):
        return "bool" in annotation and "str" not in annotation

    async def invoke(self, value):
        try:
            return validation_funcs["bool"](
                value, fix_=self.fix, **self.validation_kwargs
            )
        except Exception as e:
            raise ValueError(f"failed to validate field") from e


class NumberRule(Rule):

    async def applies(self, annotation=None):
        return (
            any([i in annotation for i in ["int", "float", "number"]])
            and "str" not in annotation
        )

    async def invoke(self, value):
        try:
            return validation_funcs["number"](
                value, fix_=self.fix, **self.validation_kwargs
            )
        except Exception as e:
            raise ValueError(f"failed to validate field") from e


class DictRule(Rule):

    async def applies(self, annotation=None):
        return "dict" in annotation

    async def invoke(self, value, annotation=None, keys=None):
        if "str" not in annotation or keys:
            try:
                return validation_funcs["dict"](
                    value, keys=keys, fix_=self.fix, **self.validation_kwargs
                )
            except Exception as e:
                raise ValueError(f"failed to validate field") from e
        raise ValueError(f"failed to validate field") from e


class StringRule(Rule):

    async def applies(self, annotation=None):
        return "str" in annotation

    async def invoke(self, value):
        try:
            return validation_funcs["str"](
                value, fix_=self.fix, **self.validation_kwargs
            )
        except Exception as e:
            raise ValueError(f"failed to validate field") from e


from enum import Enum


class DEFAULT_RULES(Enum):
    CHOICE = ChoiceRule
    ACTION_REQUEST = ActionRequestRule
    BOOL = BooleanRule
    NUMBER = NumberRule
    DICT = DictRule
    STR = StringRule
