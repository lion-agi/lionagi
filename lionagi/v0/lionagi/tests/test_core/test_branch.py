import unittest
from unittest.mock import MagicMock, patch
import lionagi as li
from lionagi.core.message import System, Instruction, AssistantResponse, ActionResponse
from lionagi.core.collections import Pile, Progression, Exchange
from lionagi.core.action.tool_manager import ToolManager


class TestBranch(unittest.TestCase):

    def setUp(self):
        self.branch = li.Branch()

    def test_initialize_branch(self):
        self.assertIsInstance(self.branch, li.Branch)
        self.assertIsInstance(self.branch.messages, Pile)
        self.assertIsInstance(self.branch.progress, Progression)
        self.assertIsInstance(self.branch.tool_manager, ToolManager)
        self.assertIsInstance(self.branch.mailbox, Exchange)
        self.assertIsInstance(self.branch.imodel, li.iModel)

    def test_add_message_system(self):
        self.branch.add_message(
            system="You are a helpful assistant, let's think step by step"
        )
        self.assertEqual(len(self.branch.messages), 1)
        self.assertEqual(
            self.branch.messages[0].content,
            {"system_info": "You are a helpful assistant, let's think step by step"},
        )

    def test_to_df(self):
        self.branch.add_message(
            system="You are a helpful assistant, let's think step by step"
        )
        df = self.branch.to_df()
        self.assertEqual(df.iloc[0]["message_type"], "System")
        self.assertEqual(df.iloc[0]["role"], "system")

    def test_to_chat_messages(self):
        self.branch.add_message(
            system="You are a helpful assistant, let's think step by step"
        )
        chat_msgs = self.branch.to_chat_messages()
        self.assertEqual(chat_msgs[0]["role"], "system")
        self.assertEqual(
            chat_msgs[0]["content"],
            "You are a helpful assistant, let's think step by step",
        )

    @patch("lionagi.Branch.chat")
    async def test_chat(self, mock_chat):
        mock_chat.return_value = (
            "Rain poured, but their love shone brighter than any storm."
        )
        response = await self.branch.chat("tell me a 10 word story", logprobs=True)
        self.assertEqual(
            response, "Rain poured, but their love shone brighter than any storm."
        )
        mock_chat.assert_called_once_with("tell me a 10 word story", logprobs=True)

    def test_metadata(self):
        self.branch.add_message(
            system="You are a helpful assistant, let's think step by step"
        )
        self.assertIn("last_updated", self.branch.messages[0].metadata)

    # def test_register_tools(self):
    #     tool = MagicMock()
    #     self.branch.register_tools([tool])
    #     self.assertIn(tool, self.branch.tool_manager.registry.values())

    # def test_delete_tools(self):
    #     tool = MagicMock()
    #     tool.schema_ = {"function": {"name": "test_tool"}}
    #     self.branch.register_tools([tool])
    #     self.branch.delete_tools([tool])
    #     self.assertNotIn("test_tool", self.branch.tool_manager.registry)

    def test_send_receive_mail(self):
        self.branch.send = MagicMock()
        self.branch.receive = MagicMock()
        package = MagicMock()
        self.branch.send(recipient="recipient_id", category="message", package=package)
        self.branch.receive(sender="recipient_id")
        self.branch.send.assert_called_once_with(
            recipient="recipient_id", category="message", package=package
        )
        self.branch.receive.assert_called_once_with(sender="recipient_id")

    async def test_chat_with_tool(self):
        async def mock_multiply(number1, number2, number3=1):
            return number1 * number2 * number3

        instruction = """
        solve the following problem
        """
        context = """
        I have 730_000 trees, with average 123 apples per tree, each weigh 0.4 lbs. 
        20 percent are bad and sold for 0.1 dollar per lbs, 30 percent are sold to 
        brewery for 0.3 dollar per apple, what is my revenue?
        """

        self.branch = li.Branch(
            "act like a calculator, invoke tool uses", tools=[mock_multiply]
        )
        response = await self.branch.chat(
            instruction=instruction, context=context, tools=True
        )
        self.assertIsNotNone(response)
        self.assertIn("revenue", response.lower())


if __name__ == "__main__":
    unittest.main()
