from lionagi.libs.ln_convert import to_num
from .base import Rule


class NumberRule(Rule):
    """
    upper_bound: int | float | None = None,
    lower_bound: int | float | None = None,
    num_type: Type[int | float] = float,
    precision: int | None = None,

    when validating number field, we do not support complex numbers
    conversion from model output yet, if you wish to interact with
    complex numbers, create a new rule by inheriting from Rule class
    """

    def __init__(self, apply_type="int, float", **kwargs):
        super().__init__(apply_type, **kwargs)

    async def validate(self, value):
        return isinstance(value, (int, float, complex))

    async def fix_field(self, value):
        if isinstance(value, (int, float, complex)):
            return value

        value = to_num(value, **self.validation_kwargs)
        if isinstance(value, (int, float)):
            return value
        raise ValueError(f"Failed to convert {value} into a numeric value")
