from lionagi.os.service.api.model_config import MODEL_CONFIG, ENDPOINT_CONFIG
from .config import oai_chat_schema


GPT35TURBO_INSTRUCT_CHAT_COMPLETIONS = ENDPOINT_CONFIG(
    endpoint="chat/completions",
    pricing=(1.5, 2),
    batch_pricing=(0.75, 1),
    token_limit=4_096,
    default_rate_limit=(60, 1_000, 50_000),
    default_config={'model': "gpt-4o-mini", **oai_chat_schema['config']},
    required_params=oai_chat_schema['required_params'],
    optional_params=oai_chat_schema['optional_params'],
    input_key=oai_chat_schema['input_key']
)

GPT35TURBO_INSTRUCT = MODEL_CONFIG(
    model="gpt-3.5-turbo-instruct",
    alias = "gpt-3.5-turbo-instruct-0914",
    endpoint_schema={
        "chat/completions": GPT35TURBO_INSTRUCT_CHAT_COMPLETIONS,
    }
)