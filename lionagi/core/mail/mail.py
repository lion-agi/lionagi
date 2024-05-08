from ..generic.abc import Element, Field, Sendable
from .package import PackageCategory, Package


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
