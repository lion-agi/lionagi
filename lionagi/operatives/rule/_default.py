from enum import Enum

from .action import ActionRequestRule
from .boolean import BooleanRule
from .choice import ChoiceRule
from .mapping import MappingRule
from .number import NumberRule
from .string import StringRule


class DEFAULT_RULES(Enum):
    CHOICE = ChoiceRule
    MAPPING = MappingRule
    NUMBER = NumberRule
    BOOL = BooleanRule
    STR = StringRule
    ACTION = ActionRequestRule
