import pytest

from lionagi.core.mail import Mail
from lionagi.core.mail.package import Package
from datetime import datetime

"""
More to be added
"""


def trim_timestamp_to_day(timestamp_str):
    dt = datetime.fromisoformat(timestamp_str)
    return dt.strftime('%Y-%m-%d')


class MockPackage(Package):
    """A mock package class for testing purposes."""


@pytest.fixture
def mail():
    """Fixture to create a Mail instance with a MockPackage."""
    package = MockPackage()
    mail_instance = Mail(timestamp=datetime.today().strftime('%Y-%m-%d'), package=package)
    return mail_instance


def test_mail_category(mail):
    """Test the category property of Mail."""
    assert mail.category is None





# from lionagi.core.generic.mail import *
#
# import unittest
#
#
# class TestMail(unittest.TestCase):
#     def setUp(self):
#         self.mail = Mail(
#             sender="node1",
#             recipient="node2",
#             category=MailPackageCategory.MESSAGES,
#             package="Hello, World!"
#         )
#
#     def test_mail_initialization(self):
#         """Test initialization of Mail objects."""
#         self.assertIsInstance(self.mail, BaseComponent)
#         self.assertEqual(self.mail.sender, "node1")
#         self.assertEqual(self.mail.recipient, "node2")
#         self.assertEqual(self.mail.category, MailPackageCategory.MESSAGES)
#         self.assertEqual(self.mail.package, "Hello, World!")
#
#     def test_mail_str(self):
#         """Test the string representation of Mail."""
#         expected_str = "Mail from node1 to node2 with category messages and package Hello, World!"
#         self.assertEqual(str(self.mail), expected_str)
#
# class TestMailBox(unittest.TestCase):
#     def setUp(self):
#         self.mailbox = MailBox()
#         self.mail1 = Mail(
#             sender="node1",
#             recipient="node3",
#             category="model",
#             package={"model": "Random Forest"}
#         )
#         self.mail2 = Mail(
#             sender="node2",
#             recipient="node3",
#             category=MailPackageCategory.SERVICE,
#             package={"service": "Prediction"}
#         )
#
#     def test_adding_mails(self):
#         """Test adding mails to MailBox."""
#         self.mailbox.pending_ins["node1"] = self.mail1
#         self.mailbox.pending_outs["node3"] = self.mail2
#
#         self.assertIn("node1", self.mailbox.pending_ins)
#         self.assertIn("node3", self.mailbox.pending_outs)
#         self.assertEqual(self.mailbox.pending_ins["node1"], self.mail1)
#         self.assertEqual(self.mailbox.pending_outs["node3"], self.mail2)
#
#     def test_mailbox_str(self):
#         """Test the string representation of MailBox."""
#         self.mailbox.pending_ins["node1"] = self.mail1
#         self.mailbox.pending_outs["node3"] = self.mail2
#         expected_str = "MailBox with 1 pending incoming mails and 1 pending outgoing mails."
#         self.assertEqual(str(self.mailbox), expected_str)
#
# if __name__ == "__main__":
#     unittest.main()
