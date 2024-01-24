def sign_message(messages, sender: str):    
    df = messages.copy()
    df['content'] = df['content'].apply(lambda x: f"Sender {sender}: {x}")
    return df