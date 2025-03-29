from enum import Enum

from pydantic import Field

from lionagi.models import HashableModel

__all__ = (
    "ParameterKind",
    "Parameter",
    "Decorator",
    "Import",
    "Attribute",
    "Function",
    "Method",
    "Class",
    "Module",
)


class ParameterKind(str, Enum):
    """
    Distinguishes how a function/method parameter is used.
    Primarily inspired by Python's param categories, but can be ignored by simpler languages.
    Pay attention to the languege's own conventions for parameter handling.
    """

    POSITIONAL_ONLY = "positional_only"  # E.g. Python's '/'-based params
    POSITIONAL_OR_KEYWORD = "positional_or_keyword"  # Default for many
    VAR_POSITIONAL = "var_positional"  # *args-like
    KEYWORD_ONLY = "keyword_only"  # Python's '*' marker
    VAR_KEYWORD = "var_keyword"  # **kwargs-like


class Parameter(HashableModel):
    """
    Represents one parameter in a function or method signature.
    """

    name: str = Field(
        ...,
        description="Exact identifier for the parameter (e.g., 'user_id', 'self', 'arg').",
    )
    type: str | None = Field(
        default=None,
        description=(
            "Type annotation as a string (e.g., 'str', 'int', 'SomeClass'). None if untyped or not declared."
        ),
    )
    default_value_repr: str | None = Field(
        default=None,
        description=(
            "String representation of default value if present (e.g., 'None', '10', '\"hi\"'). "
            "None if parameter is required with no default."
        ),
    )
    kind: ParameterKind = Field(
        default=ParameterKind.POSITIONAL_OR_KEYWORD,
        description=(
            "Parameter's calling convention category. 'positional_or_keyword' is typical if unspecified."
        ),
    )


class Decorator(HashableModel):
    """
    A decorator or annotation attached to a function, class, or method.
    Common in Python (@deco), Java (@Override), .NET ([Attribute]), etc.
    """

    name: str = Field(
        ...,
        description="Decorator/annotation name (e.g., '@staticmethod', '[ApiController]', '@Override').",
    )
    arguments_repr: list[str] | None = Field(
        default=None,
        description=(
            "If this decorator/annotation is called with arguments, provide them as a list of string expressions "
            "(e.g., `['\"/home\"', 'methods=[\"GET\"]']`). None if no arguments."
        ),
    )


class Import(HashableModel):
    """
    Represents an import/using/include statement. Merges Python's 'import X' and 'from Y import Z' logic.
    Other languages can interpret accordingly.
    """

    module: str | None = Field(
        default=None,
        description=(
            "The module/package/namespace from which symbols are imported (e.g., 'os.path', 'java.util'). "
            "None for a direct import statement like 'import X' if no sub-path is specified."
        ),
    )
    name: str = Field(
        ...,
        description=(
            "The symbol or module being imported (e.g., 'os', 'List', 'time', '*')."
        ),
    )
    alias: str | None = Field(
        default=None,
        description="Alias name if used ('import X as Y'), else None.",
    )
    level: int = Field(
        default=0,
        description=(
            "For Pythonic relative imports. Number of leading dots. 0 if absolute or not applicable."
        ),
    )


class Attribute(HashableModel):
    """
    A variable/constant/field at class or module level. Possibly static/final, with an initial value.
    """

    name: str = Field(
        ...,
        description="Identifier for this attribute/field (e.g., 'MAX_CONNECTIONS', 'version').",
    )
    type: str | None = Field(
        default=None,
        description="String type annotation if declared. None if untyped.",
    )
    initial_value_repr: str | None = Field(
        default=None,
        description="String representation of any initial value (e.g., '100', 'true', 'None'). None if uninitialized.",
    )
    is_static: bool = Field(
        default=False,
        description="True if this is a static (class-level) attribute. Otherwise instance-level or module-level.",
    )
    is_final: bool = Field(
        default=False,
        description="True if this attribute/field is read-only/const/final after initialization.",
    )
    visibility: str | None = Field(
        default=None,
        description="Optional access modifier (e.g., 'public', 'private', 'protected'). None if default or not applicable.",
    )


class Function(HashableModel):
    """
    Represents a standalone function or procedure.
    For methods (attached to classes), see 'Method' below.
    """

    name: str = Field(
        ..., description="Function name identifier (e.g., 'process_data')."
    )
    parameters: list[Parameter] = Field(
        default_factory=list,
        description="Ordered list of Parameter objects for this function.",
    )
    return_type: str | None = Field(
        default=None,
        description="Return type string if declared. None if not declared or no explicit type.",
    )
    is_async: bool = Field(
        default=False,
        description="True if an 'async' function in languages that support it. Else False.",
    )
    docstring: str | None = Field(
        default=None,
        description="Documentation string or comment describing this function.",
    )
    decorators: list[Decorator] = Field(
        default_factory=list,
        description="List of decorators/annotations on this function (e.g., @staticmethod).",
    )


class Method(Function):
    """
    A function bound to a class, including potential method-specific flags (static, abstract, etc.).
    Inherits fields from 'Function.'
    """

    is_static: bool = Field(
        default=False,
        description="True if method is static (no instance or 'self' needed).",
    )
    is_classmethod: bool = Field(
        default=False,
        description="True if method is recognized as a class method (receives class as first arg).",
    )
    is_abstract: bool = Field(
        default=False,
        description="True if the method is abstract (no concrete implementation).",
    )
    visibility: str | None = Field(
        default=None,
        description="Access level like 'public', 'private', etc., if relevant to the language.",
    )


class Class(HashableModel):
    """
    Represents a class, interface, or other composite type, with optional docstring, attributes, methods, etc.
    """

    name: str = Field(
        ...,
        description="Class/struct/interface name (e.g., 'UserRepository', 'MyDataClass').",
    )
    base_types: list[str] = Field(
        default_factory=list,
        description="List of parent classes or interfaces by name. Empty if none.",
    )
    is_abstract: bool = Field(
        default=False,
        description="True if this is an abstract class (cannot be instantiated directly).",
    )
    is_interface: bool = Field(
        default=False,
        description="True if this represents an interface definition rather than a concrete class.",
    )
    docstring: str | None = Field(
        default=None,
        description="Documentation for the class/interface, if any.",
    )
    decorators: list[Decorator] = Field(
        default_factory=list,
        description="Class-level decorators/annotations (e.g., @dataclass).",
    )
    attributes: list[Attribute] = Field(
        default_factory=list,
        description="Fields or properties declared at class level.",
    )
    methods: list[Method] = Field(
        default_factory=list,
        description="List of Method objects representing this class's methods.",
    )
