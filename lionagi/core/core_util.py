import json
from ..utils.sys_util import strip_lower


def sign_message(messages, sender: str):
    """
    Sign messages with a sender identifier.

    Args:
        messages (pd.DataFrame): A DataFrame containing messages with columns 'node_id', 'role', 'sender', 'timestamp', and 'content'.
        sender (str): The sender identifier to be added to the messages.

    Returns:
        pd.DataFrame: A new DataFrame with the sender identifier added to each message.

    Raises:
        ValueError: If the 'sender' is None or 'None'.
    """
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
    """
    Validate the structure and content of a messages DataFrame.

    Args:
        messages (pd.DataFrame): A DataFrame containing messages with columns 'node_id', 'role', 'sender', 'timestamp', and 'content'.

    Returns:
        bool: True if the messages DataFrame is valid; otherwise, raises a ValueError.

    Raises:
        ValueError: If the DataFrame structure is invalid or if it contains null values, roles other than ["system", "user", "assistant"],
                    or content that cannot be parsed as JSON strings.
    """
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
