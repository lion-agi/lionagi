import unittest
from lionagi.core.mail.schema import *


class TestMailCategory(unittest.TestCase):
    def test_mail_category_values(self):
        self.assertEqual(MailCategory.MESSAGES, "messages")
        self.assertEqual(MailCategory.TOOL, "tool")
        self.assertEqual(MailCategory.SERVICE, "service")
        self.assertEqual(MailCategory.MODEL, "model")
        self.assertEqual(MailCategory.NODE, "node")
        self.assertEqual(MailCategory.NODE_LIST, "node_list")
        self.assertEqual(MailCategory.NODE_ID, "node_id")
        self.assertEqual(MailCategory.START, "start")
        self.assertEqual(MailCategory.END, "end")
        self.assertEqual(MailCategory.CONDITION, "condition")


class TestBaseMail(unittest.TestCase):
    def test_init_valid_category_str(self):
        mail = BaseMail("sender", "recipient", "start", {"data": "package"})
        self.assertEqual(mail.sender_id, "sender")
        self.assertEqual(mail.recipient_id, "recipient")
        self.assertEqual(mail.category, MailCategory.START)
        self.assertEqual(mail.package, {"data": "package"})

    def test_init_valid_category_enum(self):
        mail = BaseMail("sender", "recipient", MailCategory.END, {"data": "package"})
        self.assertEqual(mail.sender_id, "sender")
        self.assertEqual(mail.recipient_id, "recipient")
        self.assertEqual(mail.category, MailCategory.END)
        self.assertEqual(mail.package, {"data": "package"})

    def test_init_invalid_category_str(self):
        with self.assertRaises(ValueError) as cm:
            BaseMail("sender", "recipient", "invalid", {"data": "package"})
        self.assertIn("Invalid request title. Valid titles are", str(cm.exception))
        self.assertIn("Error: 'invalid' is not a valid MailCategory", str(cm.exception))

    def test_init_invalid_category_type(self):
        with self.assertRaises(ValueError) as cm:
            BaseMail("sender", "recipient", 123, {"data": "package"})
        self.assertIn("Invalid request title. Valid titles are", str(cm.exception))


class TestStartMail(unittest.TestCase):
    def setUp(self):
        self.start_mail = StartMail()

    def test_init(self):
        self.assertIsInstance(self.start_mail.pending_outs, deque)
        self.assertEqual(len(self.start_mail.pending_outs), 0)

    def test_trigger(self):
        context = {"key": "value"}
        structure_id = "structure_id"
        executable_id = "executable_id"

        self.start_mail.trigger(context, structure_id, executable_id)

        self.assertEqual(len(self.start_mail.pending_outs), 1)
        mail = self.start_mail.pending_outs.pop()
        self.assertIsInstance(mail, BaseMail)
        self.assertEqual(mail.sender_id, self.start_mail.id_)
        self.assertEqual(mail.recipient_id, executable_id)
        self.assertEqual(mail.category, "start")
        self.assertEqual(mail.package, {"context": context, "structure_id": structure_id})


class TestMailTransfer(unittest.TestCase):
    def setUp(self):
        self.mail_transfer = MailTransfer()

    def test_init(self):
        self.assertIsInstance(self.mail_transfer.pending_ins, dict)
        self.assertEqual(len(self.mail_transfer.pending_ins), 0)
        self.assertIsInstance(self.mail_transfer.pending_outs, deque)
        self.assertEqual(len(self.mail_transfer.pending_outs), 0)


if __name__ == "__main__":
    unittest.main()
    