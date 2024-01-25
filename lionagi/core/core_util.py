from ..utils import strip_lower

def sign_message(messages, sender: str):    
    if sender is None or strip_lower(sender) == 'none':
        raise ValueError("sender cannot be None")
    df = messages.copy()
    df['content'] = df['content'].apply(
        lambda x: f"Sender {sender}: {x}" if not x.startswith('Sender') else x
    )
    return df