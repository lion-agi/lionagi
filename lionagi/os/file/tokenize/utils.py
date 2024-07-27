import tiktoken
from .disallowed_tokens import disallowed_tokens


def tokenize(
    text,
    encoding_model=None,
    encoding_name=None,
    return_byte=False,
    disallowed_tokens=disallowed_tokens,
):
    encoding = None

    if encoding_model:
        try:
            encoding_name = tiktoken.encoding_name_for_model(encoding_model)
        except:
            encoding_name = encoding_name or "cl100k_base"

    if not encoding_name or encoding_name in tiktoken.list_encoding_names():
        encoding_name = encoding_name or "cl100k_base"
        encoding = tiktoken.get_encoding(encoding_name)

    special_encodings = (
        [encoding.encode(token) for token in disallowed_tokens]
        if disallowed_tokens
        else []
    )
    codes = encoding.encode(text)
    if special_encodings and len(special_encodings) > 0:
        codes = [code for code in codes if code not in special_encodings]

    if return_byte:
        return codes

    return [encoding.decode([code]) for code in codes]
