import json
from ..utils import strip_lower


def sign_message(messages, sender: str):    
    if sender is None or strip_lower(sender) == 'none':
        raise ValueError("sender cannot be None")
    df = messages.copy()

    for i in df.index:
        if not df.loc[i, 'content'].startswith('Sender'):
            df.loc[i, 'content'] = f"Sender {sender}: {df.loc[i, 'content']}"
        else:
            content = df.loc[i, 'content'].split(':', 1)[1]
            df.loc[i, 'content'] = f"Sender {sender}: {content}"
    return df


def validate_messages(messages):
    if list(messages.columns) != ['node_id', 'role', 'sender', 'timestamp', 'content']:
        raise ValueError('Invalid messages dataframe. Unmatched columns.')
    if messages.isnull().values.any():
        raise ValueError('Invalid messages dataframe. Cannot have null.')
    if not all(role in ['system', 'user', 'assistant'] for role in messages['role'].unique()):
        raise ValueError('Invalid messages dataframe. Cannot have role other than ["system", "user", "assistant"].')
    for cont in messages['content']:
        if cont.startswith('Sender'):
            cont = cont.split(':', 1)[1]
        try:
            json.loads(cont)
        except:
            raise ValueError('Invalid messages dataframe. Content expect json string.')
    return True

