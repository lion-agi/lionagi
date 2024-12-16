from typing import Any, Final, Literal, TypedDict, TypeVar, Union


class UndefinedType:
    def __init__(self) -> None:
        self.undefined = True

    def __bool__(self) -> Literal[False]:
        return False

    def __deepcopy__(self, memo):
        # Ensure UNDEFINED is universal
        return self

    def __repr__(self) -> Literal["UNDEFINED"]:
        return "UNDEFINED"

    __slots__ = ["undefined"]


UNDEFINED = UndefinedType()

# Type definitions
NUM_TYPE_LITERAL = Literal["int", "float", "complex"]
NUM_TYPES = Union[type[int], type[float], type[complex], NUM_TYPE_LITERAL]
NumericType = TypeVar("NumericType", int, float, complex)

# Type mapping
TYPE_MAP = {"int": int, "float": float, "complex": complex}

# Regex patterns for different numeric formats
PATTERNS = {
    "scientific": r"[-+]?(?:\d*\.)?\d+[eE][-+]?\d+",
    "complex_sci": r"[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?[-+](?:\d*\.)?\d+(?:[eE][-+]?\d+)?[jJ]",
    "complex": r"[-+]?(?:\d*\.)?\d+[-+](?:\d*\.)?\d+[jJ]",
    "pure_imaginary": r"[-+]?(?:\d*\.)?\d*[jJ]",
    "percentage": r"[-+]?(?:\d*\.)?\d+%",
    "fraction": r"[-+]?\d+/\d+",
    "decimal": r"[-+]?(?:\d*\.)?\d+",
    "special": r"[-+]?(?:inf|infinity|nan)",
}


md_json_char_map = {"'": '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}

py_json_msp = {
    "str": "string",
    "int": "number",
    "float": "number",
    "list": "array",
    "tuple": "array",
    "bool": "boolean",
    "dict": "object",
}


# Define constants for valid boolean string representations
TRUE_VALUES: Final[frozenset[str]] = frozenset(
    [
        "true",
        "1",
        "yes",
        "y",
        "on",
        "correct",
        "t",
        "enabled",
        "enable",
        "active",
        "activated",
    ]
)

FALSE_VALUES: Final[frozenset[str]] = frozenset(
    [
        "false",
        "0",
        "no",
        "n",
        "off",
        "incorrect",
        "f",
        "disabled",
        "disable",
        "inactive",
        "deactivated",
        "none",
        "null",
        "n/a",
        "na",
    ]
)


class KeysDict(TypedDict, total=False):
    """TypedDict for keys dictionary."""

    key: Any  # Represents any key-type pair
