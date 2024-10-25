from lion_core.rule.base import Rule
from lionfuncs import string_similarity
from typing_extensions import override


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
        return string_similarity(
            word=value,
            correct_words_list=self.keys,
            return_most_similar=True,
        )
