from lionagi.core.messages.base.base_message import BaseMessage
from lionagi.libs import ln_convert as convert, ln_nested as nested


class Response(BaseMessage):
    """
    Represents a response message, a specialized subclass of Message.

    Used for various types of response messages including regular responses, action requests,
    and action responses. It sets the message role to 'assistant'.

    """

    def __init__(self, response: dict | list | str, sender: str | None = None) -> None:
        content_key = ""
        try:
            response = response["message"]
            if convert.strip_lower(response["content"]) == "none":
                content_ = self._handle_action_request(response)
                sender = sender or "action_request"
                content_key = content_key or "action_request"

            else:
                try:
                    if "tool_uses" in convert.to_dict(response["content"]):
                        content_ = convert.to_dict(response["content"])["tool_uses"]
                        content_key = content_key or "action_request"
                        sender = sender or "action_request"
                    elif "response" in convert.to_dict(response["content"]):
                        sender = sender or "assistant"
                        content_key = content_key or "response"
                        content_ = convert.to_dict(response["content"])["response"]
                    elif "action_request" in convert.to_dict(response["content"]):
                        sender = sender or "action_request"
                        content_key = content_key or "action_request"
                        content_ = convert.to_dict(response["content"])[
                            "action_request"
                        ]
                    else:
                        content_ = response["content"]
                        content_key = content_key or "response"
                        sender = sender or "assistant"
                except:
                    content_ = response["content"]
                    content_key = content_key or "response"
                    sender = sender or "assistant"

        except:
            sender = sender or "action_response"
            content_ = response
            content_key = content_key or "action_response"

        try:
            content_ = convert.to_dict(content_)
            if "response" in content_.keys():
                content_ = content_["response"]
        except:
            pass

        super().__init__(
            role="assistant", sender=sender, content={content_key: content_}
        )

    @staticmethod
    def _handle_action_request(response):
        """
        Processes an action request response and extracts relevant information.

        Args:
            response (dict): The response dictionary containing tool calls and other information.

        Returns:
            list: A list of dictionaries, each representing a function call with action and arguments.

        Raises:
            ValueError: If the response does not conform to the expected format for action requests.
        """
        try:
            tool_count = 0
            func_list = []
            while tool_count < len(response["tool_calls"]):
                _path = ["tool_calls", tool_count, "type"]

                if nested.nget(response, _path) == "function":
                    _path1 = ["tool_calls", tool_count, "function", "name"]
                    _path2 = ["tool_calls", tool_count, "function", "arguments"]

                    func_content = {
                        "action": ("action_" + nested.nget(response, _path1)),
                        "arguments": nested.nget(response, _path2),
                    }
                    func_list.append(func_content)
                tool_count += 1
            return func_list
        except:
            raise ValueError(
                "Response message must be one of regular response or function calling"
            )
