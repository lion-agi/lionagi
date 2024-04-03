import unittest
from unittest.mock import MagicMock, patch
from collections import deque
from lionagi.core.mail.mail_manager import *


class TestMailManager(unittest.TestCase):
    def setUp(self):
        self.source1 = MagicMock(spec=BaseNode, id_="source1")
        self.source1.pending_ins = {}
        self.source2 = MagicMock(spec=BaseNode, id_="source2")
        self.source2.pending_ins = {}
        self.source3 = MagicMock(spec=BaseNode, id_="source3")
        self.sources_dict = {"source1": self.source1, "source2": self.source2}
        self.sources_list = [self.source1, self.source2]
        self.mail_manager = MailManager(self.sources_dict)

    def test_init_with_dict(self):
        self.assertEqual(self.mail_manager.sources, self.sources_dict)
        self.assertEqual(self.mail_manager.mails, {"source1": {}, "source2": {}})
        self.assertFalse(self.mail_manager.execute_stop)

    def test_init_with_list(self):
        mail_manager = MailManager(self.sources_list)
        self.assertEqual(mail_manager.sources, self.sources_dict)
        self.assertEqual(mail_manager.mails, {"source1": {}, "source2": {}})
        self.assertFalse(mail_manager.execute_stop)

    def test_init_with_invalid_sources(self):
        with self.assertRaises(ValueError) as cm:
            MailManager("invalid_sources")
        self.assertEqual(str(cm.exception), "Failed to add source, please input list or dict.")

    def test_add_sources_with_dict(self):
        self.mail_manager.sources = {}
        self.mail_manager.mails = {}
        self.mail_manager.add_sources(self.sources_dict)
        self.assertEqual(self.mail_manager.sources, self.sources_dict)
        self.assertEqual(self.mail_manager.mails, {"source1": {}, "source2": {}})

    def test_add_sources_with_list(self):
        self.mail_manager.sources = {}
        self.mail_manager.mails = {}
        self.mail_manager.add_sources(self.sources_list)
        self.assertEqual(self.mail_manager.sources, self.sources_dict)
        self.assertEqual(self.mail_manager.mails, {"source1": {}, "source2": {}})

    def test_add_sources_with_existing_source(self):
        self.mail_manager.add_sources(self.sources_dict)
        self.assertEqual(self.mail_manager.sources, self.sources_dict)
        self.assertEqual(self.mail_manager.mails, {"source1": {}, "source2": {}})

    def test_add_sources_with_invalid_sources(self):
        with self.assertRaises(ValueError) as cm:
            self.mail_manager.add_sources("invalid_sources")
        self.assertEqual(str(cm.exception), "Failed to add source, please input list or dict.")

    def test_create_mail(self):
        mail = MailManager.create_mail("sender", "recipient", MailCategory.START, {"data": "package"})
        self.assertIsInstance(mail, BaseMail)
        self.assertEqual(mail.sender_id, "sender")
        self.assertEqual(mail.recipient_id, "recipient")
        self.assertEqual(mail.category, MailCategory.START)
        self.assertEqual(mail.package, {"data": "package"})

    def test_delete_source_existing(self):
        self.mail_manager.delete_source("source1")
        self.assertEqual(self.mail_manager.sources, {"source2": self.source2})
        self.assertEqual(self.mail_manager.mails, {"source2": {}})

    def test_delete_source_nonexistent(self):
        with self.assertRaises(ValueError) as cm:
            self.mail_manager.delete_source("nonexistent_source")
        self.assertEqual(str(cm.exception), "Source nonexistent_source does not exist.")

    def test_collect_existing_sender(self):
        mail1 = MagicMock(spec=BaseMail, sender_id="source1", recipient_id="source2")
        mail2 = MagicMock(spec=BaseMail, sender_id="source1", recipient_id="source2")
        self.source1.pending_outs = deque([mail1, mail2])

        self.mail_manager.collect("source1")

        self.assertEqual(len(self.source1.pending_outs), 0)
        self.assertEqual(self.mail_manager.mails["source2"]["source1"], deque([mail1, mail2]))

    def test_collect_nonexistent_sender(self):
        with self.assertRaises(ValueError) as cm:
            self.mail_manager.collect("nonexistent_source")
        self.assertEqual(str(cm.exception), "Sender source nonexistent_source does not exist.")

    def test_collect_nonexistent_recipient(self):
        mail = MagicMock(spec=BaseMail, sender_id="source1", recipient_id="nonexistent_source")
        self.source1.pending_outs = deque([mail])

        with self.assertRaises(ValueError) as cm:
            self.mail_manager.collect("source1")
        self.assertEqual(str(cm.exception), "Recipient source nonexistent_source does not exist")

    def test_send_existing_recipient(self):
        mail1 = MagicMock(spec=BaseMail, sender_id="source1", recipient_id="source2")
        mail2 = MagicMock(spec=BaseMail, sender_id="source1", recipient_id="source2")
        self.mail_manager.mails["source2"]["source1"] = deque([mail1, mail2])

        self.mail_manager.send("source2")

        self.assertEqual(self.source2.pending_ins, {"source1": deque([mail1, mail2])})
        self.assertEqual(self.mail_manager.mails["source2"], {})

    def test_send_nonexistent_recipient(self):
        with self.assertRaises(ValueError) as cm:
            self.mail_manager.send("nonexistent_source")
        self.assertEqual(str(cm.exception), "Recipient source nonexistent_source does not exist.")

    def test_send_empty_mails(self):
        self.mail_manager.send("source1")
        self.assertFalse(self.source1.pending_ins)

    def test_collect_all(self):
        mail1 = MagicMock(spec=BaseMail, sender_id="source1", recipient_id="source2")
        mail2 = MagicMock(spec=BaseMail, sender_id="source2", recipient_id="source1")
        self.source1.pending_outs = deque([mail1])
        self.source2.pending_outs = deque([mail2])

        self.mail_manager.collect_all()

        self.assertEqual(len(self.source1.pending_outs), 0)
        self.assertEqual(len(self.source2.pending_outs), 0)
        self.assertEqual(self.mail_manager.mails["source2"]["source1"], deque([mail1]))
        self.assertEqual(self.mail_manager.mails["source1"]["source2"], deque([mail2]))

    def test_send_all(self):
        mail1 = MagicMock(spec=BaseMail, sender_id="source1", recipient_id="source2")
        mail2 = MagicMock(spec=BaseMail, sender_id="source2", recipient_id="source1")
        self.mail_manager.mails["source2"]["source1"] = deque([mail1])
        self.mail_manager.mails["source1"]["source2"] = deque([mail2])

        self.mail_manager.send_all()

        self.assertEqual(self.source2.pending_ins, {"source1": deque([mail1])})
        self.assertEqual(self.source1.pending_ins, {"source2": deque([mail2])})
        self.assertEqual(self.mail_manager.mails["source2"], {})
        self.assertEqual(self.mail_manager.mails["source1"], {})

    # @patch("lionagi.libs.AsyncUtil.sleep", return_value=None)
    # def test_execute(self, mock_sleep):
    #     self.mail_manager.execute_stop = True
    #     asyncio.run(self.mail_manager.execute())
    #     mock_sleep.assert_not_called()

    #     self.mail_manager.execute_stop = False
    #     mail1 = MagicMock(spec=BaseMail, sender_id="source1", recipient_id="source2")
    #     mail2 = MagicMock(spec=BaseMail, sender_id="source2", recipient_id="source1")
    #     self.source1.pending_outs = deque([mail1])
    #     self.source2.pending_outs = deque([mail2])

    #     async def async_execute():
    #         with patch("lionagi.libs.AsyncUtil.sleep", return_value=None) as mock_sleep:
    #             self.mail_manager.execute_stop = True
    #             await self.mail_manager.execute(refresh_time=0)

    #     asyncio.run(async_execute())

    #     self.assertEqual(len(self.source1.pending_outs), 1)
    #     self.assertEqual(len(self.source2.pending_outs), 1)
    #     self.assertEqual(self.source2.pending_ins, {"source1": deque([mail1])})
    #     self.assertEqual(self.source1.pending_ins, {"source2": deque([mail2])})
    #     self.assertEqual(self.mail_manager.mails["source2"], {})
    #     self.assertEqual(self.mail_manager.mails["source1"], {})


if __name__ == "__main__":
    unittest.main()