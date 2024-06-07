from collections.abc import Mapping, Generator
from collections import deque
import random
from .abc import LionTypeError, Record, Ordering, Component, get_lion_id, Element

DEFAULT_EXPERT_MODEL_LIST = ["gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"]

def to_list_type(value):
    """
    Convert the provided value to a list.

    This function ensures that the input value is converted to a list,
    regardless of its original type. It handles various types including
    Component, Mapping, Record, tuple, list, set, Generator, and deque.

    Args:
        value: The value to convert to a list.

    Returns:
        list: The converted list.

    Raises:
        TypeError: If the value cannot be converted to a list.
    """
    if isinstance(value, Component) and not isinstance(value, (Record, Ordering)):
        return [value]
    if isinstance(value, (Mapping, Record)):
        return list(value.values())
    # if isinstance(value, Ordering):
    #     return list(value.order)
    if isinstance(value, (tuple, list, set, Generator, deque)):
        return list(value)
    return [value]


def _validate_order(value) -> list[str]:
    """
    Validate and convert the order field to a list of strings.

    This function ensures that the input value is a valid order and converts it to a list of strings.
    It handles various input types including string, Ordering, and Element.

    Args:
        value: The value to validate and convert.

    Returns:
        list[str]: The validated and converted order list.

    Raises:
        LionTypeError: If the value contains invalid types.
    """
    if value is None:
        return []
    if isinstance(value, str) and len(value) == 32:
        return [value]
    elif isinstance(value, Ordering):
        return value.order

    elif isinstance(value, Element):
        return [value.ln_id]

    try:
        return [i for item in to_list_type(value) if (i := get_lion_id(item))]
    except Exception as e:
        raise LionTypeError("Progression must only contain lion ids.") from e

def get_random_config(
    model_list=DEFAULT_EXPERT_MODEL_LIST,
    temperature_range = (0.7, 1.2),
    top_p_range = (0.8, 1.0),
    frequency_penalty_range = (0.0, 0.5),
    presence_penalty_range = (0.0, 0.5),
    max_tokens = 100,  
):
    return {
        "model": random.choice(model_list),
        "temperature": random.uniform(*temperature_range),
        "top_p": random.uniform(*top_p_range),
        "frequency_penalty": random.uniform(*frequency_penalty_range),
        "presence_penalty": random.uniform(*presence_penalty_range),
        "max_tokens": max_tokens,
    }