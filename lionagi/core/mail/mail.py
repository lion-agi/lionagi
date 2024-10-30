from lionagi.core.collections.abc import Element, Field, Sendable

from .package import Package, PackageCategory


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
