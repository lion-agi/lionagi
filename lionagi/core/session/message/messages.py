from ..schema import MessageType, MessageField, MessageRoleType








class Instruction(BaseMessage):

    def __init__(self, instruction: Any, context=None, sender: Optional[str] = None):
        super().__init__(
            role=MessageRoleType.USER.value,
            sender=sender or MessageSenderType.USER.value,
            content={MessageContentKey.INSTRUCTION.value: instruction}
        )
        if context:
            self.content.update({'context': context})


class System(BaseMessage):

    def __init__(self, system: Any, sender: Optional[str] = None):
        super().__init__(
            role=MessageRoleType.SYSTEM.value,
            sender=sender or MessageSenderType.SYSTEM.value,
            content={MessageContentKey.SYSTEM.value: system}
        )


class Response(BaseMessage):

    def __init__(self, response: Any, sender: Optional[str] = None) -> None:
        content_key = ''
        try:
            response = response["message"]
            if strip_lower(response[MessageField.CONTENT.value]) == "none":
                content_ = self._handle_action_request(response)
                sender = sender or MessageSenderType.ACTION_REQUEST
                content_key = content_key or "action_list"

            else:
                try:
                    if 'tool_uses' in to_dict(response['content']):
                        content_ = to_dict(response['content'])['tool_uses']
                        content_key = content_key or "action_list"
                        sender = sender or MessageSenderType.ACTION_REQUEST
                    elif 'response' in to_dict(response['content']):
                        sender = sender or "assistant"
                        content_key = content_key or "response"
                        content_ = to_dict(response['content'])['response']
                    elif 'action_list' in to_dict(response['content']):
                        sender = sender or MessageSenderType.ACTION_REQUEST
                        content_key = content_key or "action_list"
                        content_ = to_dict(response['content'])['action_list']
                    else:
                        content_ = response['content']
                        content_key = content_key or "response"
                        sender = sender or "assistant"
                except:
                    content_ = response['content']
                    content_key = content_key or "response"
                    sender = sender or "assistant"

        except:
            sender = sender or "action_response"
            content_ = response
            content_key = content_key or "action_response"

        super().__init__(
            role=MessageRoleType.ASSISTANT.value, sender=sender, content={content_key:
                                                                         content_}
        )

    @staticmethod
    def _handle_action_request(response):
        try:
            tool_count = 0
            func_list = []
            while tool_count < len(response['tool_calls']):
                _path = ['tool_calls', tool_count, 'type']

                if nget(response, _path) == 'function':
                    _path1 = ['tool_calls', tool_count, 'function', 'name']
                    _path2 = ['tool_calls', tool_count, 'function', 'arguments']

                    func_content = {
                        "action": ("action_" + nget(response, _path1)),
                        "arguments": nget(response, _path2)
                    }
                    func_list.append(func_content)
                tool_count += 1
            return func_list
        except:
            raise ValueError(
                "Response message must be one of regular response or function calling"
            )
