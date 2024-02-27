from lionagi.core.session.base.schema import BaseMessage, Response, BaseMail, MailCategory

import unittest
import json


class TestBaseMessageProperties(unittest.TestCase):

    def test_sender_property_getter_and_setter(self):
        """Test getting and setting the sender property."""
        message = BaseMessage()
        message.sender = 'test_sender'
        self.assertEqual(message.sender, 'test_sender')

    def test_msg_property(self):
        """Test the msg property for correct dictionary output."""
        message = BaseMessage(role='user', sender='test_sender', content='Hello, world!')
        expected_dict = {
            'role': 'user',
            'content': 'Hello, world!'
        }
        self.assertDictEqual(message.msg, expected_dict)

    def test_msg_content_property(self):
        """Test the msg_content property for correct content output."""
        content = 'Hello, world!'
        message = BaseMessage(content=content)
        self.assertEqual(message.msg_content, content)

    def test_message_to_string(self):
        """Test the string representation of a message."""
        content = 'This is a test message.'
        message = BaseMessage(role='user', sender='test_sender', content=content)
        string_representation = str(message)
        expected_string = f"Message(role=user, sender=test_sender, content='{content}')"
        self.assertEqual(string_representation, expected_string)


class TestMessageSerialization(unittest.TestCase):

    def test_content_serialization(self):
        """Test serialization of dictionary content to a JSON string within the msg property."""
        content = {'key': 'value'}
        message = BaseMessage(content=content)
        expected_content = json.dumps(content)
        self.assertEqual(message.msg['content'], expected_content)


class TestResponse(unittest.TestCase):

    def test_regular_response_content(self):
        """Test handling of regular response content."""
        response_content = {"message": {"content": json.dumps({"response": "Test response"})}}
        response = Response(response_content)
        self.assertEqual(response.content["response"], "Test response")
        self.assertEqual(response.sender, "assistant")

    def test_action_request_response(self):
        """Test handling of action request response."""
        response_content = {
            "message": {
                "content": json.dumps({"tool_uses": [{"action": "function_call", "arguments": {"arg": "value"}}]})
            }
        }
        response = Response(response_content)
        self.assertIn("action_request", response.content)
        self.assertEqual(response.sender, "action_request")

    def test_fallback_to_default_sender(self):
        """Test fallback to default sender based on content type."""
        response_content = {"message": {"content": "none"}}
        response = Response(response_content)
        self.assertEqual(response.sender, "action_response")

    def test_handle_action_request(self):
        """Test extraction of function calls from action request."""
        response_content = {
            "tool_calls": [
                {"type": "function", "function": {"name": "test_func", "arguments": {"arg1": "value1"}}}
            ]
        }
        func_list = Response._handle_action_request(response_content)
        self.assertEqual(len(func_list), 1)
        self.assertEqual(func_list[0]["action"], "action_test_func")


class TestBaseMail(unittest.TestCase):

    def test_base_mail_initialization(self):
        """Test initializing BaseMail with valid inputs."""
        mail = BaseMail(sender="user1", recipient="user2", category="messages", package={})
        self.assertEqual(mail.sender, "user1")
        self.assertEqual(mail.recipient, "user2")
        self.assertEqual(mail.category, MailCategory.MESSAGES)
        self.assertEqual(mail.package, {})

    def test_base_mail_initialization_with_enum(self):
        """Test initializing BaseMail with MailCategory enum."""
        mail = BaseMail(sender="user1", recipient="user2", category=MailCategory.TOOL, package={})
        self.assertEqual(mail.category, MailCategory.TOOL)

    def test_base_mail_invalid_category(self):
        """Test initializing BaseMail with an invalid category."""
        with self.assertRaises(ValueError):
            BaseMail(sender="user1", recipient="user2", category="invalid", package={})


if __name__ == '__main__':
    unittest.main()
