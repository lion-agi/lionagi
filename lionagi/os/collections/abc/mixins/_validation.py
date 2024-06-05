import contextlib
from typing import Any


class ComponentValidationMixin:

    @staticmethod
    def _validate_embedding(value: Any) -> list:
        if not value:
            return []
        if isinstance(value, str):
            if len(value) < 10:
                return []

            string_elements = value.strip("[]").split(",")
            # Convert each string element to a float
            with contextlib.suppress(ValueError):
                return [float(element) for element in string_elements]
        raise ValueError("Invalid embedding format.")
