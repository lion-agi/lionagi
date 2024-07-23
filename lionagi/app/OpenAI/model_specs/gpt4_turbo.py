from lionagi.os.service.api.model_config import MODEL_CONFIG, ENDPOINT_CONFIG
from .config import oai_chat_schema


GPT4_TURBO_CHAT_COMPLETIONS = ENDPOINT_CONFIG(
    endpoint="chat/completions",
    pricing=(10, 30),
    batch_pricing=(-1, -1),
    token_limit=128_000,
    default_rate_limit=(60, 1_000, 5_000_000),
    default_config={'model': "gpt-4o-mini", **oai_chat_schema['config']},
    required_params=oai_chat_schema['required_params'],
    optional_params=oai_chat_schema['optional_params'],
    input_key=oai_chat_schema['input_key']
)


GPT4_TURBO = MODEL_CONFIG(
    model="gpt-4-turbo",
    alias=[
        "gpt-4-turbo", 
        "gpt-4-turbo-2024-04-09", 
        "gpt-4-turbo-2024-04-09", 
        "gpt-4-turbo-preview", 
        "gpt-4-0125-preview", 
        "gpt-4-1106-preview"
    ],
    endpoint_schema={
        "chat/completions": GPT4OMINI_CHAT_COMPLETIONS,
    }
)