from ..generic.abc import Rule
from ._default_rules import DEFAULT_RULES


rules_ = {
    "choice": DEFAULT_RULES.CHOICE.value,
    "actionrequest": DEFAULT_RULES.ACTION_REQUEST.value,
    "bool": DEFAULT_RULES.BOOL.value,
    "number": DEFAULT_RULES.NUMBER.value,
    "dict": DEFAULT_RULES.DICT.value,
    "str": DEFAULT_RULES.STR.value,
}

order_ = [
    "choice",
    "actionrequest",
    "bool",
    "number",
    "dict",
    "str",
]


class BaseValidator:

    rules: dict[str, Rule] = rules_
    order: list[str] = order_

    async def validate(self, value, *args, strict=False, **kwargs):

        for i in self.order:
            if i in self.rules:
                try:
                    if await self.rules[i].applies(value, *args, **kwargs):
                        if (
                            a := await self.rules[i].invoke(value, *args, **kwargs)
                        ) is not None:
                            return a
                except Exception as e:
                    raise ValueError(f"failed to validate field") from e
        if strict:
            raise ValueError(f"failed to validate field")
        return value
