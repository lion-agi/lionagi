from lionagi.libs.ln_convert import to_str
from .base import Rule


class StringRule(Rule):

    def __init__(self, apply_type="str", **kwargs):
        super().__init__(apply_type=apply_type, **kwargs)

    async def validate(self, value):
        return isinstance(value, str)

    async def perform_fix(self, value):
        try:
            return to_str(value, **self.validation_kwargs)
        except Exception as e:
            raise ValueError(f"Failed to convert {value} into a string value") from e
