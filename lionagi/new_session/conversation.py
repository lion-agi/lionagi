from .message import Message

class Conversation:
    def __init__(self, messages=None) -> None:
        self.messages = messages or []
        self.msg = Message()
        self.responses = []

    def initiate_conversation(self, system, instruction, context=None):
        self.messages, self.responses = [], []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context)

    def add_messages(self, system=None, instruction=None, context=None, response=None):
        msg = self.msg(system=system, instruction=instruction, response=response, context=context)
        self.messages.append(msg)

    def change_system(self, system):
        self.messages[0] = self.msg(system=system)

    def append_last_response(self):
        self.add_messages(response=self.responses[-1])

    def keep_last_n_exchanges(self, n: int):
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) if message["role"] == "assistant"
        ]
        if len(response_indices) >= n:
            first_index_to_keep = response_indices[-n] + 1
            self.messages = [self.system] + self.messages[first_index_to_keep:]