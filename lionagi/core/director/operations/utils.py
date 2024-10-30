from enum import Enum
from inspect import isclass


def is_enum(choices):
    return isclass(choices) and issubclass(choices, Enum)
