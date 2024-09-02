from lionagi.core.collections.abc import Element, Field, Sendable
from .package import PackageCategory, Package

from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.action.function_calling.FunctionCalling",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class Mail(Element, Sendable):
    """Represents a mail component with sender and recipient information."""

    package: Package | None = Field(
        None,
        title="Package",
        description="The package to be delivered.",
    )

    @property
    def category(self) -> PackageCategory:
        """Return the category of the package."""
        return self.package.category

    def to_dict(self):
        return {
            "ln_id": self.ln_id,
            "created": self.timestamp,
            "package_category": self.package.category,
            "package_id": self.package.ln_id,
        }
