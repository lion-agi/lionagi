from lionagi.libs.ln_convert import to_str
from .base import Rule


class StringRule(Rule):

    fields: list[str] = ["reason", "prediction", "answer"]

    def __init__(self, apply_type="str", **kwargs):
        super().__init__(apply_type=apply_type, **kwargs)

    async def validate(self, value):
        if isinstance(value, str) or value == "":
            return value
        raise ValueError(f"Invalid string field type.")

    async def perform_fix(self, value):
        try:
            return to_str(value, **self.validation_kwargs)
        except Exception as e:
            raise ValueError(f"Failed to convert {value} into a string value") from e
