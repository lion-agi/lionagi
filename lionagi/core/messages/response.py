from lionagi.libs import nested, convert, ParseUtil
import inspect
from ..generic.component import BaseComponent
from .base import BaseMessage, MessageRole




























class AssistantResponse(BaseMessage):
    response: any = None
    
    def __init__(
        self,
        instruction=None,       # the instruction message obj that the response correlates to
        response=None, 
        sender=None,            # sender is the assistant
    ):
        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender,
            recipient=instruction.id_,
            content = {"response": response},
        )


class ActionRequest(BaseMessage):
    function: str | None = None
    arguments: dict | None = None
    
    def __init__(
        self, 
        function=None, 
        arguments=None, 
        sender=None,                 # sender is the assistant
        executor=None,               # executor is the recipient
    ):
        
        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender,
            recipient=(
                executor if isinstance(executor, str) 
                else executor.id_ if isinstance(executor, BaseComponent)
                else "executor"
            )
        )
        self.function=function if inspect.isfunction(function) else function.__name__
        self.arguments=self._prepare_arguments(arguments)
    

    def _prepare_arguments(self, arguments):
        if not isinstance(arguments, dict):
            try:
                arguments=ParseUtil.fuzzy_parse_json(convert.to_str(arguments))
            except Exception as e:
                raise ValueError(f"Invalid arguments: {e}") from e
        if isinstance(arguments, dict):
            return arguments
        raise ValueError(f"Invalid arguments: {arguments}")
    


# action response must correlates to a specific action request
class ActionResponse(BaseMessage):
    function: str | None = None
    arguments: dict | None = None
    output: any | None = None

    def __init__(
        self,
        action_request=None,
        output=None, 
        sender=None,        # the sender of action response is executor
    ):
        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "executor",
            recipient=action_request.id_,
        )
        self.function=action_request.function
        self.arguments=action_request.arguments
        self.output=output



class Response(BaseMessage):
    ...














class Response(BaseMessage):


    def __init__(
        self, response: dict | list | str, sender: str | None = None, recipient=None
    ) -> None:
        content_key = ""
        try:
            response = response["message"]
            if convert.strip_lower(response["content"]) == "none":
                content_ = self._handle_action_request(response)
                sender = sender or "action_request"
                content_key = content_key or "action_request"
                recipient = recipient or "action"

            else:
                try:
                    if "tool_uses" in convert.to_dict(response["content"]):
                        content_ = convert.to_dict(response["content"])["tool_uses"]
                        content_key = content_key or "action_request"
                        sender = sender or "action_request"
                        recipient = recipient or "action"

                    elif "response" in convert.to_dict(response["content"]):
                        sender = sender or "assistant"
                        content_key = content_key or "response"
                        content_ = convert.to_dict(response["content"])["response"]
                        recipient = recipient or "user"

                    elif "action_request" in convert.to_dict(response["content"]):
                        sender = sender or "action_request"
                        content_key = content_key or "action_request"
                        content_ = convert.to_dict(response["content"])[
                            "action_request"
                        ]
                        recipient = recipient or "action"

                    else:
                        content_ = response["content"]
                        content_key = content_key or "response"
                        sender = sender or "assistant"
                        recipient = recipient or "user"
                except Exception:
                    content_ = response["content"]
                    content_key = content_key or "response"
                    sender = sender or "assistant"
                    recipient = recipient or "user"

        except Exception:
            sender = sender or "action_response"
            content_ = response
            content_key = content_key or "action_response"
            recipient = recipient or "assistant"

        super().__init__(
            role="assistant",
            sender=sender,
            content={content_key: content_},
            recipient=recipient,
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
                        "action": f"action_{nested.nget(response, _path1)}",
                        "arguments": nested.nget(response, _path2),
                    }
                    func_list.append(func_content)
                tool_count += 1
            return func_list
        except:
            raise ValueError(
                "Response message must be one of regular response or function calling"
            )
