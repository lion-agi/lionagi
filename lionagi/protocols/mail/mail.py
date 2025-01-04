# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import field_validator

from .._concepts import Sendable
from ..generic.element import Element
from ..messages.base import IDType
from .package import Package, PackageCategory


class Mail(Element, Sendable):

    sender: IDType
    recipient: IDType
    package: Package

    @field_validator("sender", "recipient")
    def _validate_sender_recipient(cls, value):
        return IDType.validate(value)

    @property
    def category(self) -> PackageCategory:
        return self.package.category
