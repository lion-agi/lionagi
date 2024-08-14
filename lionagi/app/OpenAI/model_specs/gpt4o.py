from lionagi.os.service.api.specification import MODEL_CONFIG, ENDPOINT_CONFIG
from ._config import oai_chat_schema


GPT4O_CHAT_COMPLETIONS = ENDPOINT_CONFIG(
    endpoint="chat/completions",
    pricing=(5, 15),  # input_token, output_token
    batch_pricing=(2.5, 7.5),  # input_token, output_token
    token_limit=128_000,
    default_rate_limit=(60, 1_000, 5_000_000),
    default_config={"model": "gpt-4o", **oai_chat_schema["config"]},
    required_params=oai_chat_schema["required_params"],
    optional_params=oai_chat_schema["optional_params"],
    input_key=oai_chat_schema["input_key"],
)

GPT4O = MODEL_CONFIG(
    model="gpt-4o",
    alias=["gpt-4o", "gpt-4o-2024-05-13"],
    endpoint_schema={
        "chat/completions": GPT4O_CHAT_COMPLETIONS,
    },
)
