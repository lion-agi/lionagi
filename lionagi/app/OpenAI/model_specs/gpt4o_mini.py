from lionagi.os.service.api.specification import MODEL_CONFIG, ENDPOINT_CONFIG
from ._config import oai_chat_schema


GPT4OMINI_CHAT_COMPLETIONS = ENDPOINT_CONFIG(
    endpoint="chat/completions",
    pricing=(0.15, 0.6),
    batch_pricing=(0.075, 0.3),
    token_limit=128_000,
    default_rate_limit=(60, 1_000, 5_000_000),
    default_config={"model": "gpt-4o-mini", **oai_chat_schema["config"]},
    required_params=oai_chat_schema["required_params"],
    optional_params=oai_chat_schema["optional_params"],
    input_key=oai_chat_schema["input_key"],
)


GPT4O_MINI = MODEL_CONFIG(
    model="gpt-4o-mini",
    alias=["gpt-4o-mini", "gpt-4o-mini-2024-07-18"],
    endpoint_schema={
        "chat/completions": GPT4OMINI_CHAT_COMPLETIONS,
    },
)
