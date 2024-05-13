from lionagi.libs.ln_parse import StringMatch
from .util import validate_keys
from .base import Rule


class ChoiceRule(Rule):

    def __init__(self, apply_type="enum", **kwargs):
        super().__init__(apply_type=apply_type, **kwargs)
        self.keys = self.validation_kwargs.get("keys", None)

    async def validate(self, value, *args, **kwargs):
        """
        return value or raise error
        """
        if not value in self.keys:
            raise ValueError(f"{value} is not in chocies {self.keys}")
        return value

    async def perform_fix(self, value):
        return StringMatch.choose_most_similar(value, self.keys)
