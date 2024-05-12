from lionagi.libs.ln_parse import StringMatch
from .util import validate_keys
from .base import Rule


class ChoiceRule(Rule):

    def __init__(self, apply_type="enum", keys=None, **kwargs):
        super().__init__(apply_type, **kwargs)
        self.keys = self._validate_keys(keys)

    def _validate_keys(self, value):
        """
        examples: {"a": 1, "b": 2}, ["a", "b"], "a, b", {"a", "b"}, "Enum class"
        """
        if not value:
            if (
                not "keys" in self.validation_kwargs
                and not "choices" in self.validation_kwargs
            ):
                raise ValueError(f"keys not provided")

            value = self.validation_kwargs.get(
                "keys", self.validation_kwargs.get("choices", None)
            )

        try:
            value = validate_keys(value)

        except Exception as e:
            raise ValueError(f"failed to get keys") from e

        return value

    async def validate(self, value, *args, **kwargs):
        """
        return value or raise error
        """
        if not value in self.keys:
            raise ValueError(f"{value} is not in chocies {self.keys}")
        return value

    async def perform_fix(self, value):
        return StringMatch.choose_most_similar(value, self.keys)
