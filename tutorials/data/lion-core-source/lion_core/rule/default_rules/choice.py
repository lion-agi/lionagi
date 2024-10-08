from lionfuncs import choose_most_similar
from typing_extensions import override

from lion_core.rule.base import Rule


class ChoiceRule(Rule):
    @property
    def keys(self):
        return self.info.get(["keys"], [])

    @override
    async def check_value(self, value, /) -> str:
        if value not in self.keys:
            raise ValueError(f"{value} is not in chocies {self.keys}")
        return value

    @override
    async def fix_value(self, value) -> str:
        """
        Suggest a fix for a value that is not within the set of predefined
        choices.

        Args:
            value (str): The value to suggest a fix for.

        Returns:
            str: The most similar value from the set of predefined choices.
        """
        return choose_most_similar(
            word=value,
            correct_words_list=self.keys,
            **self.validation_kwargs,
        )
