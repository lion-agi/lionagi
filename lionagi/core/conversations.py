from ..objs.messenger import Messenger


class Conversation:
    response_counts = 0
    
    def __init__(self, messages=None) -> None:
        self.messages = messages or []
        self.msgr = Messenger()
        self.responses = []

    def initiate_conversation(
        self, 
        system=None, 
        instruction=None, 
        context=None, 
        name=None
        ):
        self.messages, self.responses = [], []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context, name=name)

    # modify the message adding to accomodate tools
    def add_messages(self, system=None, instruction=None, context=None, response=None, name=None):
        msg = self.msgr.create_message(
            system=system, instruction=instruction, 
            context=context, response=response, name=name
            )
        self.messages.append(msg)

    def change_system(self, system):
        self.messages[0] = self.msgr.create_message(system=system)

    def keep_last_n_exchanges(self, n: int):
        # keep last n_exchanges, one exchange is marked by one assistant response
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) if message["role"] == "assistant"
        ]
        if len(response_indices) >= n:
            first_index_to_keep = response_indices[-n] + 1
            self.messages = [self.system] + self.messages[first_index_to_keep:]
            