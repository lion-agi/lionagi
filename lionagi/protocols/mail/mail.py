from ..messages.base import IDType, Sendable
from .package import Package, PackageCategory


class Mail(Sendable):

    def __init__(
        self,
        sender: IDType,
        recipient: IDType,
        package: Package,
    ):
        super().__init__()
        self.sender = IDType.validate(sender)
        self.recipient = IDType.validate(recipient)
        self.package = package

    @property
    def category(self) -> PackageCategory:
        return self.package.category
