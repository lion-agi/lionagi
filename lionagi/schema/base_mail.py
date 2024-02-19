from enum import Enum


class MailCategory(str, Enum):
    MESSAGES = 'messages'
    TOOL = 'tool'
    SERVICE = 'provider'
    MODEL = 'model'


class BaseMail:

    def __init__(self, sender, recipient, category, request):
        self.sender = sender
        self.recipient = recipient
        try:
            if isinstance(category, str):
                category = MailCategory(category)
            if isinstance(category, MailCategory):
                self.title = category
            else:
                raise ValueError(f'Invalid request title. Valid titles are'
                                 f' {list(MailCategory)}')
        except Exception as e:
            raise ValueError(f'Invalid request title. Valid titles are '
                             f'{list(MailCategory)}, Error: {e}')
        self.request = request
