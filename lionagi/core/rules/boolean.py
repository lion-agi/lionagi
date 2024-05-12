from lionagi.libs.ln_convert import to_str, strip_lower
from .base import Rule


class BooleanRule(Rule):

    def __init__(self, apply_type="bool", **kwargs):
        super().__init__(apply_type, **kwargs)

    async def validate(self, value):
        if isinstance(value, bool):
            return value
        raise ValueError(f"Invalid boolean field type.")

    async def perform_fix(self, value):
        value = strip_lower(to_str(value))
        if value in ["true", "1", "correct", "yes"]:
            return True

        elif value in ["false", "0", "incorrect", "no", "none", "n/a"]:
            return False

        raise ValueError(f"Failed to convert {value} into a boolean value")
