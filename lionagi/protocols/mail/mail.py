# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from .._concepts import Sendable
from ..messages.base import IDType
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
