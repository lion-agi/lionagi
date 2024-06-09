from pydantic import Field, field_validator
from ..abc import Element, Field, Sendable, get_lion_id, LionTypeError
from .package import PackageCategory, Package


class BaseMail(Element, Sendable):

    sender: str = Field(
        "N/A",
        title="Sender",
        description=("The id of the sender node, or 'system', 'user', or 'assistant'."),
    )

    recipient: str = Field(
        "N/A",
        title="Recipient",
        description=(
            "The id of the recipient node, or 'system', 'user', or 'assistant'."
        ),
    )

    @field_validator("sender", "recipient", mode="before")
    def _validate_sender_recipient(cls, value):
        """Validate the sender and recipient fields.

        Args:
            value (Any): The value to validate.

        Returns:
            str: The validated value.

        Raises:
            LionTypeError: If the value is invalid.
        """
        if value is None:
            return "N/A"

        if value in ["system", "user", "N/A", "assistant"]:
            return value

        a = get_lion_id(value)
        if not isinstance(a, str) or len(a) != 32:
            raise LionTypeError(
                "Invalid sender or recipient value. "
                "Expected a valid node id or one of "
                "'system' or 'user'."
            )
        return a


class Mail(BaseMail):
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
