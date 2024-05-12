from ..generic.abc import LionFieldError
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


class Validator:

    def __init__(self, rules=None, order=None):
        self.rules = rules or rules_
        self.order = order or order_

    async def validate(self, value, annotation, strict=False, **kwargs):

        # iterate through the rules according to the order
        for i in self.order:
            # we will skip the rule if it is not present in validator
            if i in self.rules:

                try:
                    # here we check whether the rule applies to the value
                    special_kwargs = {}
                    if "choices" in kwargs:
                        special_kwargs["choices"] = kwargs["choices"]
                    elif "keys" in kwargs:
                        special_kwargs["keys"] = kwargs["keys"]

                    if await self.rules[i].applies(value, annotation, **special_kwargs):
                        # if the rule applies, we invoke the rule
                        if (
                            a := await self.rules[i].invoke(value, **kwargs)
                        ) is not None:
                            return a

                except Exception as e:
                    raise LionFieldError(f"failed to validate field") from e

        # this means no rule applied to the value,
        # if strict is True, we raise an error, else we return the original value
        if strict:
            raise LionFieldError(f"failed to validate field")
        return value
