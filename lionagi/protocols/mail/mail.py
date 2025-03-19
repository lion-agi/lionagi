# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import field_validator

from .._concepts import Sendable
from ..generic.element import Element
from ..messages.base import IDType
from .package import Package, PackageCategory


class Mail(Element, Sendable):
    """
    A single mail message that can be sent between communicatable entities.
    It includes a sender, recipient, and a package that describes the
    mail's content.

    Attributes
    ----------
    sender : IDType
        The ID representing the mail sender.
    recipient : IDType
        The ID representing the mail recipient.
    package : Package
        The package (category + payload) contained in this mail.
    """

    sender: IDType
    recipient: IDType
    package: Package

    @field_validator("sender", "recipient")
    def _validate_sender_recipient(cls, value):
        """
        Validate that the sender and recipient fields are correct IDTypes.
        """
        return IDType.validate(value)

    @property
    def category(self) -> PackageCategory:
        """
        Shortcut for retrieving the category from the underlying package.

        Returns
        -------
        PackageCategory
        """
        return self.package.category


# File: lionagi/protocols/mail/mail.py
